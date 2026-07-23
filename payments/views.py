from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db.models import Sum, Count
from datetime import datetime, timedelta
import json
import uuid

from .models import Payment, Currency, PaymentMethod, TransactionLog
from bookings.models import Booking, BookingStatusLog
from accounts.models import UserProfile
from .services import convert_currency, format_currency, get_all_currencies, CURRENCY_NAMES, CURRENCY_SYMBOLS


def payment_process(request, booking_code):
    booking = get_object_or_404(Booking, booking_code=booking_code)
    if booking.status not in ('pending_payment',):
        messages.info(request, _('Booking ini sudah diproses.'))
        return redirect('booking_detail', booking_code=booking_code)
    payment_methods = PaymentMethod.objects.filter(is_active=True)
    currencies = get_all_currencies()

    existing_payment = Payment.objects.filter(booking=booking, status='pending').first()
    if existing_payment:
        return render(request, 'payment_process.html', {
            'booking': booking,
            'payment': existing_payment,
            'payment_methods': payment_methods,
            'currencies': currencies,
        })

    currency_code = booking.currency
    currency_obj = Currency.objects.filter(code=currency_code).first()
    exchange_rate = 1.0
    if currency_obj:
        exchange_rate = float(currency_obj.rate_to_idr)

    return render(request, 'payment_process.html', {
        'booking': booking,
        'payment_methods': payment_methods,
        'currencies': currencies,
        'selected_currency': currency_code,
        'exchange_rate': exchange_rate,
    })


@csrf_exempt
def create_payment(request, booking_code):
    if request.method != 'POST':
        return JsonResponse({'error': _('Method not allowed')}, status=405)

    booking = get_object_or_404(Booking, booking_code=booking_code)
    if booking.status != 'pending_payment':
        messages.error(request, _('Booking ini tidak bisa dibayar.'))
        return redirect('booking_detail', booking_code=booking_code)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    payment_method_id = data.get('payment_method')
    currency_code = data.get('currency', booking.currency)

    payment_method = get_object_or_404(PaymentMethod, id=payment_method_id)
    currency_obj = Currency.objects.filter(code=currency_code).first()

    amount_idr = booking.total_price_idr
    exchange_rate = 1.0
    if currency_obj:
        exchange_rate = float(currency_obj.rate_to_idr)

    amount_converted = convert_currency(amount_idr, 'IDR', currency_code)

    booking.currency = currency_code
    booking.total_price_converted = amount_converted
    booking.save()

    payment = Payment.objects.create(
        booking=booking,
        payment_method=payment_method,
        amount_idr=amount_idr,
        currency=currency_obj,
        amount_converted=amount_converted,
        exchange_rate=exchange_rate,
        status='pending',
    )

    ip = request.META.get('REMOTE_ADDR', '')
    ua = request.META.get('HTTP_USER_AGENT', '')
    TransactionLog.objects.create(
        payment=payment,
        booking=booking,
        log_type='payment_created',
        action=_('Pembayaran dibuat'),
        details=_('Pembayaran %(method)s sebesar Rp %(amount)s dibuat') % {
            'method': payment_method.name,
            'amount': str(amount_idr),
        },
        ip_address=ip,
        user_agent=ua,
    )

    messages.success(request, _('Pembayaran berhasil dibuat. Silakan selesaikan pembayaran.'))

    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'success': True,
            'payment_code': payment.payment_code,
            'amount': str(payment.amount_converted),
            'currency': currency_code,
            'redirect': f'/payment/{payment.payment_code}/'
        })

    return redirect('payment_detail', payment_code=payment.payment_code)


def payment_detail(request, payment_code):
    payment = get_object_or_404(Payment, payment_code=payment_code)
    logs = payment.logs.all()

    currency_code = payment.currency.code if payment.currency else 'IDR'
    symbol = CURRENCY_SYMBOLS.get(currency_code, currency_code)

    return render(request, 'payment_detail.html', {
        'payment': payment,
        'logs': logs,
        'currency_code': currency_code,
        'currency_symbol': symbol,
    })


@csrf_exempt
def payment_simulate(request, payment_code):
    if request.method != 'POST':
        return JsonResponse({'error': _('Method not allowed')}, status=405)

    payment = get_object_or_404(Payment, payment_code=payment_code)

    action = request.POST.get('action', 'success')
    ip = request.META.get('REMOTE_ADDR', '')
    ua = request.META.get('HTTP_USER_AGENT', '')

    if action == 'success':
        if not payment.can_transition_to('success'):
            messages.error(request, _('Status pembayaran tidak valid.'))
            return redirect('payment_detail', payment_code=payment.payment_code)

        payment.status = 'success'
        payment.paid_at = timezone.now()
        payment.save()

        booking = payment.booking
        success, msg = booking.transition_to('pending_confirm', user=None, reason=_('Pembayaran berhasil'))
        if not success:
            messages.warning(request, msg)

        TransactionLog.objects.create(
            payment=payment,
            booking=booking,
            log_type='payment_success',
            action=_('Pembayaran berhasil'),
            details=_('Pembayaran %(amount)s berhasil diproses') % {
                'amount': format_currency(payment.amount_converted, payment.currency.code if payment.currency else 'IDR')
            },
            ip_address=ip,
            user_agent=ua,
        )

        messages.success(request, _('Pembayaran berhasil! Menunggu konfirmasi healer.'))

    elif action == 'fail':
        if not payment.can_transition_to('failed'):
            messages.error(request, _('Status pembayaran tidak valid.'))
            return redirect('payment_detail', payment_code=payment.payment_code)

        payment.status = 'failed'
        payment.save()

        TransactionLog.objects.create(
            payment=payment,
            booking=payment.booking,
            log_type='payment_failed',
            action=_('Pembayaran gagal'),
            details=_('Pembayaran gagal diproses'),
            ip_address=ip,
            user_agent=ua,
        )

        messages.error(request, _('Pembayaran gagal.'))

    return redirect('payment_detail', payment_code=payment.payment_code)


def payment_history(request):
    payments = Payment.objects.all().order_by('-created_at')[:20]
    return render(request, 'payment_history.html', {'payments': payments})


def currency_converter_api(request):
    from_currency = request.GET.get('from', 'IDR')
    to_currency = request.GET.get('to', 'USD')
    amount = request.GET.get('amount', 0)

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        amount = 0

    result = convert_currency(amount, from_currency, to_currency)

    return JsonResponse({
        'from': from_currency,
        'to': to_currency,
        'amount': amount,
        'result': float(result),
        'symbol': CURRENCY_SYMBOLS.get(to_currency, to_currency),
    })


@login_required
def dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        messages.error(request, _('Anda tidak memiliki akses ke dashboard ini.'))
        return redirect('home')

    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending_confirm').count()
    confirmed_bookings = Booking.objects.filter(status='confirmed').count()
    in_progress_bookings = Booking.objects.filter(status='in_progress').count()
    completed_bookings = Booking.objects.filter(status='completed').count()

    total_revenue_idr = Payment.objects.filter(status='released').aggregate(
        total=Sum('amount_idr')
    )['total'] or 0

    held_funds = Payment.objects.filter(status='held').aggregate(
        total=Sum('amount_idr')
    )['total'] or 0

    total_payments = Payment.objects.filter(status__in=('success', 'held', 'released')).count()

    recent_bookings = Booking.objects.all()[:10]
    recent_payments = Payment.objects.all()[:10]

    return render(request, 'dashboard.html', {
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'in_progress_bookings': in_progress_bookings,
        'completed_bookings': completed_bookings,
        'total_revenue_idr': total_revenue_idr,
        'held_funds': held_funds,
        'total_payments': total_payments,
        'recent_bookings': recent_bookings,
        'recent_payments': recent_payments,
    })


@csrf_exempt
def update_booking_status(request, booking_code):
    if request.method != 'POST':
        return JsonResponse({'error': _('Method not allowed')}, status=405)

    booking = get_object_or_404(Booking, booking_code=booking_code)
    data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
    new_status = data.get('status')

    valid_statuses = [c[0] for c in Booking.STATUS_CHOICES]
    if new_status in valid_statuses:
        booking.status = new_status
        booking.save()
        messages.success(request, _('Status booking diperbarui ke %(status)s') % {'status': booking.get_status_display()})

    return redirect('dashboard')
