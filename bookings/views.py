from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
from django.utils import timezone
import json
from .models import Booking, BookingTimeSlot, BookingStatusLog
from healers.models import Healer, HealerService
from payments.services import convert_currency, format_currency, get_all_currencies, CURRENCY_NAMES
from payments.models import Payment, TransactionLog


def create_booking(request, healer_id):
    healer = get_object_or_404(Healer.objects.select_related('category'), id=healer_id)
    services = healer.services.filter(is_active=True)
    currencies = get_all_currencies()

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        customer_email = request.POST.get('customer_email', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        service_id = request.POST.get('service_type', '')
        booking_date = request.POST.get('booking_date')
        booking_time = request.POST.get('booking_time')
        notes = request.POST.get('notes', '')
        currency = request.POST.get('currency', 'IDR')

        if not all([customer_name, customer_email, customer_phone, booking_date, booking_time]):
            messages.error(request, _('Mohon lengkapi semua field yang wajib diisi.'))
            return render(request, 'booking_form.html', {
                'healer': healer,
                'services': services,
                'currencies': currencies,
                'form_data': request.POST,
            })

        selected_service = None
        service_name = ''
        service_price = healer.price_idr

        if service_id:
            try:
                selected_service = HealerService.objects.get(id=service_id, healer=healer, is_active=True)
                service_name = selected_service.name
                service_price = selected_service.price_idr
            except (HealerService.DoesNotExist, ValueError):
                pass

        if not service_name:
            service_name = healer.specializations.split(',')[0].strip() if healer.specializations else _('General Consultation')

        total_price_converted = convert_currency(service_price, 'IDR', currency)

        customer_user = request.user if request.user.is_authenticated else None

        booking = Booking.objects.create(
            healer=healer,
            customer=customer_user,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            service_type=service_name,
            service_price_idr=service_price,
            booking_date=booking_date,
            booking_time=booking_time,
            notes=notes,
            total_price_idr=service_price,
            currency=currency,
            total_price_converted=total_price_converted,
            status='pending_payment',
        )

        BookingStatusLog.objects.create(
            booking=booking,
            old_status='',
            new_status='pending_payment',
            changed_by=customer_user,
            reason=_('Booking dibuat oleh pelanggan'),
        )

        messages.success(request, _('Booking berhasil dibuat! Kode booking: %(code)s') % {'code': booking.booking_code})
        return redirect('payment_process', booking_code=booking.booking_code)

    return render(request, 'booking_form.html', {
        'healer': healer,
        'services': services,
        'currencies': currencies,
    })


def booking_list(request):
    bookings = Booking.objects.select_related('healer', 'customer').order_by('-created_at')[:20]
    return render(request, 'booking_list.html', {'bookings': bookings})


def booking_detail(request, booking_code):
    booking = get_object_or_404(
        Booking.objects.select_related('healer', 'customer'),
        booking_code=booking_code
    )
    status_logs = booking.status_logs.select_related('changed_by').all()[:10]
    try:
        payment = booking.payment
    except Payment.DoesNotExist:
        payment = None
    currency_info = {
        'code': booking.currency,
        'name': CURRENCY_NAMES.get(booking.currency, booking.currency),
    }
    return render(request, 'booking_detail.html', {
        'booking': booking,
        'payment': payment,
        'status_logs': status_logs,
        'currency_info': currency_info,
    })


def booking_track(request):
    if request.method == 'POST':
        booking_code = request.POST.get('booking_code', '').strip()
        if booking_code:
            try:
                booking = Booking.objects.get(booking_code=booking_code)
                return redirect('booking_detail', booking_code=booking.booking_code)
            except Booking.DoesNotExist:
                messages.error(request, _('Kode booking tidak ditemukan.'))
    return render(request, 'booking_track.html')


@login_required
def booking_cancel(request, booking_code):
    if request.method != 'POST':
        return redirect('booking_detail', booking_code=booking_code)
    booking = get_object_or_404(Booking, booking_code=booking_code)
    reason = request.POST.get('reason', '').strip()
    success, msg = booking.transition_to('cancelled', user=request.user, reason=reason)
    if success:
        try:
            payment = booking.payment
            if payment.status in ('pending', 'processing'):
                payment.status = 'refunded'
                payment.refunded_at = timezone.now()
                payment.refund_reason = reason
                payment.save()
                TransactionLog.objects.create(
                    payment=payment,
                    booking=booking,
                    log_type='payment_refunded',
                    action=_('Pembayaran dikembalikan'),
                    details=_('Pembayaran dikembalikan karena pembatalan booking: %(reason)s') % {'reason': reason or '-'},
                    created_by=request.user,
                )
        except Payment.DoesNotExist:
            pass
        messages.success(request, msg)
    else:
        messages.error(request, msg)
    return redirect('booking_detail', booking_code=booking_code)


@login_required
def booking_confirm(request, booking_code):
    if request.method != 'POST':
        return redirect('healer_dashboard')
    from accounts.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        return redirect('home')
    healer = profile.get_healer_profile()
    if not healer:
        return redirect('home')
    booking = get_object_or_404(Booking, booking_code=booking_code, healer=healer)
    success, msg = booking.transition_to('confirmed', user=request.user)
    if success:
        try:
            payment = booking.payment
            if payment.status == 'success':
                payment.status = 'held'
                payment.held_at = timezone.now()
                payment.save()
                TransactionLog.objects.create(
                    payment=payment,
                    booking=booking,
                    log_type='payment_held',
                    action=_('Dana ditahan (escrow)'),
                    details=_('Pembayaran Rp %(amount)s ditahan hingga pekerjaan selesai') % {
                        'amount': str(payment.amount_idr)
                    },
                    created_by=request.user,
                )
        except Payment.DoesNotExist:
            pass
        messages.success(request, _('Booking %(code)s dikonfirmasi. Silakan kerjakan.') % {'code': booking.booking_code})
    else:
        messages.error(request, msg)
    return redirect('healer_dashboard')


@login_required
def booking_start_work(request, booking_code):
    if request.method != 'POST':
        return redirect('healer_dashboard')
    from accounts.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        return redirect('home')
    healer = profile.get_healer_profile()
    if not healer:
        return redirect('home')
    booking = get_object_or_404(Booking, booking_code=booking_code, healer=healer)
    success, msg = booking.transition_to('in_progress', user=request.user)
    if success:
        messages.success(request, _('Pekerjaan dimulai untuk booking %(code)s.') % {'code': booking.booking_code})
    else:
        messages.error(request, msg)
    return redirect('healer_dashboard')


@login_required
def booking_complete_work(request, booking_code):
    if request.method != 'POST':
        return redirect('healer_dashboard')
    from accounts.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        return redirect('home')
    healer = profile.get_healer_profile()
    if not healer:
        return redirect('home')
    booking = get_object_or_404(Booking, booking_code=booking_code, healer=healer)
    success, msg = booking.transition_to('completed', user=request.user)
    if success:
        try:
            payment = booking.payment
            if payment.status == 'held':
                payment.status = 'released'
                payment.released_at = timezone.now()
                payment.save()
                TransactionLog.objects.create(
                    payment=payment,
                    booking=booking,
                    log_type='payment_released',
                    action=_('Dana dirilis ke healer'),
                    details=_('Pembayaran Rp %(amount)s telah dirilis ke healer %(healer)s') % {
                        'amount': str(payment.amount_idr),
                        'healer': healer.name,
                    },
                    created_by=request.user,
                )
        except Payment.DoesNotExist:
            pass
        messages.success(request, _('Booking %(code)s selesai. Dana telah dirilis.') % {'code': booking.booking_code})
    else:
        messages.error(request, msg)
    return redirect('healer_dashboard')