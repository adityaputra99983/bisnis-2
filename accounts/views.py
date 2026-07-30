import decimal
from functools import wraps
from django.db.models import Subquery, OuterRef, Count, Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.utils.translation import gettext as _
from .models import UserProfile
from .forms import CustomerRegistrationForm, HealerRegistrationForm
from healers.models import Healer as HealerModel, HealerSchedule, HealerService, HealerMessage, HealerPaymentSetting, ChatRoom, ChatMessage, Notification
from healers.notifications import create_notification, get_unread_count, get_recent_notifications
from bookings.models import Booking
from payments.models import Payment, TransactionLog


def require_healer_profile(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        profile, _created = UserProfile.objects.get_or_create(user=request.user)
        if not profile.is_healer:
            messages.error(request, _('Anda tidak memiliki akses.'))
            return redirect('home')
        healer = profile.get_healer_profile()
        if not healer:
            messages.error(request, _('Profil healer tidak ditemukan.'))
            return redirect('home')
        return view_func(request, profile, healer, *args, **kwargs)
    return wrapper


def register_choose(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'register_choose.html')


def register_customer(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            request.session.cycle_key()
            login(request, user)
            messages.success(request, _('Selamat datang, %(name)s!') % {'name': user.first_name})
            return redirect('home')
        else:
            messages.error(request, _('Terjadi kesalahan. Silakan periksa form Anda.'))
    else:
        form = CustomerRegistrationForm()
    return render(request, 'register_customer.html', {'form': form})


def register_healer(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = HealerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            request.session.cycle_key()
            login(request, user)
            messages.success(request, _('Selamat datang, %(name)s! Profil healer Anda berhasil dibuat.') % {'name': user.first_name})
            return redirect('healer_dashboard')
        else:
            messages.error(request, _('Terjadi kesalahan. Silakan periksa form Anda.'))
    else:
        form = HealerRegistrationForm()
    return render(request, 'register_healer.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', next_url)

        ip = request.META.get('REMOTE_ADDR', '')
        cache_key = f'login_attempts_{ip}'
        attempts = cache.get(cache_key, 0)
        if attempts >= 5:
            messages.error(request, _('Terlalu banyak percobaan login. Coba lagi dalam 15 menit.'))
            return render(request, 'login.html', {'next_url': next_url})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            cache.delete(cache_key)
            request.session.cycle_key()
            login(request, user)
            profile, _created = UserProfile.objects.get_or_create(user=user)
            if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
                return redirect(next_url)
            if profile.is_healer:
                return redirect('healer_dashboard')
            else:
                return redirect('home')
        else:
            cache.set(cache_key, attempts + 1, timeout=900)
            messages.error(request, _('Username atau password salah.'))
    return render(request, 'login.html', {'next_url': next_url})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, _('Anda berhasil logout.'))
    return redirect('home')


@login_required
def customer_dashboard(request):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    bookings = Booking.objects.filter(
        customer_email=request.user.email
    ).select_related('healer').order_by('-created_at')[:20]
    unread_notifications = get_unread_count(request.user)
    recent_notifications = get_recent_notifications(request.user, 5)
    return render(request, 'customer_dashboard.html', {
        'profile': profile,
        'bookings': bookings,
        'unread_notifications': unread_notifications,
        'recent_notifications': recent_notifications,
    })


@login_required
def healer_dashboard(request):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        messages.error(request, _('Anda tidak memiliki akses ke dashboard healer.'))
        return redirect('home')
    healer = profile.get_healer_profile()
    schedules_list = [None] * 7
    services = []
    recent_bookings = []
    pending_count = 0
    in_progress_count = 0
    completed_count = 0
    total_revenue = 0
    held_funds = 0
    if healer:
        for s in healer.schedules.filter(is_active=True):
            schedules_list[s.day_of_week] = s
        services = healer.services.filter(is_active=True)
        recent_bookings = Booking.objects.filter(
            healer=healer
        ).select_related('customer').order_by('-created_at')[:10]
        booking_stats = Booking.objects.filter(healer=healer).aggregate(
            pending_count=Count('id', filter=Q(status='pending_confirm')),
            in_progress_count=Count('id', filter=Q(status='in_progress')),
            completed_count=Count('id', filter=Q(status='completed')),
        )
        pending_count = booking_stats['pending_count']
        in_progress_count = booking_stats['in_progress_count']
        completed_count = booking_stats['completed_count']
        payment_stats = Payment.objects.filter(booking__healer=healer).aggregate(
            total_revenue=Sum('amount_idr', filter=Q(status='released')),
            held_funds=Sum('amount_idr', filter=Q(status='held')),
        )
        total_revenue = payment_stats['total_revenue'] or 0
        held_funds = payment_stats['held_funds'] or 0
    return render(request, 'healer_dashboard.html', {
        'profile': profile,
        'healer': healer,
        'schedules': schedules_list,
        'services': services,
        'recent_bookings': recent_bookings,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'total_revenue': total_revenue,
        'held_funds': held_funds,
        'unread_notifications': get_unread_count(request.user),
        'recent_notifications': get_recent_notifications(request.user, 5),
    })


@require_healer_profile
def healer_profile_edit(request, profile, healer):
    if request.method == 'POST':
        healer.name = request.POST.get('name', healer.name)
        healer.bio = request.POST.get('bio', healer.bio)
        healer.experience_years = request.POST.get('experience_years', healer.experience_years)
        healer.phone = request.POST.get('phone', healer.phone)
        healer.address = request.POST.get('address', healer.address)
        healer.specializations = request.POST.get('specializations', healer.specializations)
        price = request.POST.get('price_idr')
        if price:
            try:
                healer.price_idr = decimal.Decimal(price.strip())
            except (decimal.InvalidOperation, ValueError, TypeError):
                messages.error(request, _('Harga harus berupa angka yang valid.'))
                return redirect('healer_profile_edit')
        healer.save()
        messages.success(request, _('Profil healer berhasil diperbarui.'))
        return redirect('healer_dashboard')
    return render(request, 'healer_profile_edit.html', {'healer': healer})


@require_healer_profile
def healer_schedule_edit(request, profile, healer):
    if request.method == 'POST':
        healer.schedules.all().update(is_active=False)
        for day in range(7):
            start = request.POST.get(f'day_{day}_start')
            end = request.POST.get(f'day_{day}_end')
            if start and end:
                HealerSchedule.objects.update_or_create(
                    healer=healer, day_of_week=day,
                    defaults={'start_time': start, 'end_time': end, 'is_active': True}
                )
        messages.success(request, _('Jadwal berhasil diperbarui.'))
        return redirect('healer_dashboard')
    schedules = [None] * 7
    for s in healer.schedules.all():
        schedules[s.day_of_week] = s
    return render(request, 'healer_schedule_edit.html', {'healer': healer, 'schedules': schedules})


@require_healer_profile
def healer_services(request, profile, healer):
    try:
        services = healer.services.all()
    except (decimal.InvalidOperation, ValueError):
        services = HealerService.objects.none()
        messages.warning(request, _('Terdapat data layanan yang rusak. Silakan hubungi administrator.'))
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name', '').strip()
            desc = request.POST.get('description', '').strip()
            price_raw = request.POST.get('price_idr', '').strip()
            duration_raw = request.POST.get('duration_minutes', '60').strip()
            if not name:
                messages.error(request, _('Nama layanan wajib diisi.'))
                return redirect('healer_services')
            try:
                price = decimal.Decimal(price_raw)
            except (decimal.InvalidOperation, ValueError, TypeError):
                messages.error(request, _('Harga harus berupa angka yang valid.'))
                return redirect('healer_services')
            if price < 0:
                messages.error(request, _('Harga tidak boleh negatif.'))
                return redirect('healer_services')
            try:
                duration = int(duration_raw)
            except (ValueError, TypeError):
                duration = 60
            if duration < 15:
                duration = 15
            HealerService.objects.create(
                healer=healer, name=name, description=desc,
                price_idr=price, duration_minutes=duration)
            messages.success(request, _('Layanan "%(name)s" berhasil ditambahkan.') % {'name': name})
        elif action == 'delete':
            svc_id = request.POST.get('service_id')
            HealerService.objects.filter(id=svc_id, healer=healer).delete()
            messages.success(request, _('Layanan berhasil dihapus.'))
        elif action == 'toggle':
            svc_id = request.POST.get('service_id')
            svc = HealerService.objects.filter(id=svc_id, healer=healer).first()
            if svc:
                svc.is_active = not svc.is_active
                svc.save()
        return redirect('healer_services')
    return render(request, 'healer_services.html', {'healer': healer, 'services': services})


@require_healer_profile
def healer_messages(request, profile, healer):
    all_messages = healer.messages.all()
    unread_count = all_messages.filter(is_read=False).count()
    return render(request, 'healer_messages.html', {
        'healer': healer, 'messages_list': all_messages, 'unread_count': unread_count,
    })


@require_healer_profile
def healer_message_detail(request, profile, healer, msg_id):
    msg = get_object_or_404(HealerMessage, id=msg_id, healer=healer)
    if not msg.is_read:
        msg.is_read = True
        msg.save()
    if request.method == 'POST':
        reply = request.POST.get('reply', '').strip()
        if reply:
            msg.reply = reply
            msg.replied_at = timezone.now()
            msg.save()
            messages.success(request, _('Balasan berhasil dikirim.'))
        return redirect('healer_messages')
    return render(request, 'healer_message_detail.html', {'healer': healer, 'msg': msg})


@require_healer_profile
def healer_payments(request, profile, healer):
    from healers.models import HealerPaymentSetting, BankTransactionSetting, BANK_CHOICES
    settings, _created = HealerPaymentSetting.objects.get_or_create(healer=healer)
    if request.method == 'POST':
        settings.bank_name = request.POST.get('bank_name', '')
        settings.bank_account_name = request.POST.get('bank_account_name', '')
        settings.bank_account_number = request.POST.get('bank_account_number', '')
        settings.swift_code = request.POST.get('swift_code', '')
        settings.gopay_number = request.POST.get('gopay_number', '')
        settings.ovo_number = request.POST.get('ovo_number', '')
        settings.dana_number = request.POST.get('dana_number', '')
        settings.shopeepay_number = request.POST.get('shopeepay_number', '')
        settings.linkaja_number = request.POST.get('linkaja_number', '')
        settings.isaku_number = request.POST.get('isaku_number', '')
        settings.qris_merchant_name = request.POST.get('qris_merchant_name', '')
        settings.qris_id = request.POST.get('qris_id', '')
        settings.paypal_email = request.POST.get('paypal_email', '')
        settings.visa_mc_enabled = 'visa_mc_enabled' in request.POST
        # Payment Gateway
        settings.payment_gateway = request.POST.get('payment_gateway', 'manual')
        settings.pg_midtrans_server_key = request.POST.get('pg_midtrans_server_key', '')
        settings.pg_midtrans_client_key = request.POST.get('pg_midtrans_client_key', '')
        settings.pg_midtrans_merchant_id = request.POST.get('pg_midtrans_merchant_id', '')
        settings.pg_xendit_secret_key = request.POST.get('pg_xendit_secret_key', '')
        settings.pg_xendit_api_key = request.POST.get('pg_xendit_api_key', '')
        settings.pg_doku_client_key = request.POST.get('pg_doku_client_key', '')
        settings.pg_doku_merchant_id = request.POST.get('pg_doku_merchant_id', '')
        settings.pg_tripay_api_key = request.POST.get('pg_tripay_api_key', '')
        settings.pg_tripay_private_key = request.POST.get('pg_tripay_private_key', '')
        settings.pg_tripay_merchant_code = request.POST.get('pg_tripay_merchant_code', '')
        # VA Bank
        settings.va_bank_enabled = 'va_bank_enabled' in request.POST
        va_banks_list = request.POST.getlist('va_banks')
        settings.va_banks = ','.join(va_banks_list)
        # Accept toggles
        settings.accept_cash = 'accept_cash' in request.POST
        settings.accept_transfer = 'accept_transfer' in request.POST
        settings.accept_gopay = 'accept_gopay' in request.POST
        settings.accept_ovo = 'accept_ovo' in request.POST
        settings.accept_dana = 'accept_dana' in request.POST
        settings.accept_shopeepay = 'accept_shopeepay' in request.POST
        settings.accept_linkaja = 'accept_linkaja' in request.POST
        settings.accept_isaku = 'accept_isaku' in request.POST
        settings.accept_qris = 'accept_qris' in request.POST
        settings.accept_paypal = 'accept_paypal' in request.POST
        settings.accept_visa_mc = 'accept_visa_mc' in request.POST
        # Security settings
        min_payment = request.POST.get('min_payment_idr', '0')
        try:
            settings.min_payment_idr = decimal.Decimal(min_payment.strip())
        except (decimal.InvalidOperation, ValueError, TypeError):
            settings.min_payment_idr = 0
        settings.require_deposit = 'require_deposit' in request.POST
        deposit_pct = request.POST.get('deposit_percent', '50')
        try:
            settings.deposit_percent = int(deposit_pct)
        except (ValueError, TypeError):
            settings.deposit_percent = 50
        settings.auto_confirm = 'auto_confirm' in request.POST
        timeout = request.POST.get('payment_timeout_hours', '24')
        try:
            settings.payment_timeout_hours = int(timeout)
        except (ValueError, TypeError):
            settings.payment_timeout_hours = 24
        settings.enable_escrow = 'enable_escrow' in request.POST
        settings.enable_refund = 'enable_refund' in request.POST
        settings.require_proof = 'require_proof' in request.POST
        settings.save()

        # Save per-bank transaction settings
        for bank_code, bank_label in BANK_CHOICES:
            is_active = f'bt_active_{bank_code}' in request.POST
            account_number = request.POST.get(f'bt_account_{bank_code}', '')
            account_name = request.POST.get(f'bt_name_{bank_code}', '')
            branch = request.POST.get(f'bt_branch_{bank_code}', '')
            accept_va = f'bt_va_{bank_code}' in request.POST
            accept_transfer = f'bt_transfer_{bank_code}' in request.POST
            accept_qris = f'bt_qris_{bank_code}' in request.POST
            va_code = request.POST.get(f'bt_vacode_{bank_code}', '')
            admin_fee = request.POST.get(f'bt_admin_{bank_code}', '0')
            timeout_min = request.POST.get(f'bt_timeout_{bank_code}', '60')
            sop_va = request.POST.get(f'bt_sop_va_{bank_code}', '')
            sop_transfer = request.POST.get(f'bt_sop_transfer_{bank_code}', '')
            sop_qris = request.POST.get(f'bt_sop_qris_{bank_code}', '')
            auto_cancel = f'bt_autocancel_{bank_code}' in request.POST

            try:
                admin_fee_val = decimal.Decimal(admin_fee.strip())
            except (decimal.InvalidOperation, ValueError, TypeError):
                admin_fee_val = 0
            try:
                timeout_val = int(timeout_min)
            except (ValueError, TypeError):
                timeout_val = 60

            if is_active or account_number or sop_va or sop_transfer:
                bs, _created_bs = BankTransactionSetting.objects.update_or_create(
                    healer=healer, bank_code=bank_code,
                    defaults={
                        'is_active': is_active,
                        'account_number': account_number,
                        'account_name': account_name,
                        'branch': branch,
                        'accept_va': accept_va,
                        'accept_transfer': accept_transfer,
                        'accept_qris': accept_qris,
                        'va_code': va_code,
                        'admin_fee': admin_fee_val,
                        'payment_timeout_minutes': timeout_val,
                        'sop_va': sop_va,
                        'sop_transfer': sop_transfer,
                        'sop_qris': sop_qris,
                        'auto_cancel': auto_cancel,
                    }
                )
            else:
                BankTransactionSetting.objects.filter(healer=healer, bank_code=bank_code).delete()

        messages.success(request, _('Pengaturan pembayaran berhasil diperbarui.'))
        return redirect('healer_payments')

    # GET: build bank_settings_dict for template
    bank_settings_qs = BankTransactionSetting.objects.filter(healer=healer)
    bank_settings_dict = {bs.bank_code: bs for bs in bank_settings_qs}
    return render(request, 'healer_payments.html', {
        'healer': healer,
        'settings': settings,
        'bank_choices': BANK_CHOICES,
        'bank_settings_dict': bank_settings_dict,
    })


@login_required
def healer_booking_update(request, booking_code):
    if request.method != 'POST':
        return redirect('healer_dashboard')
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        return redirect('home')
    healer = profile.get_healer_profile()
    if not healer:
        return redirect('home')
    booking = Booking.objects.filter(
        healer=healer, booking_code=booking_code
    ).select_related('healer').first()
    if booking:
        action = request.POST.get('action', '')
        if action == 'confirm':
            success, msg = booking.transition_to('confirmed', user=request.user)
        elif action == 'start':
            success, msg = booking.transition_to('in_progress', user=request.user)
        elif action == 'complete':
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
                            details=_('Pembayaran Rp %(amount)s dirilis ke healer %(healer)s') % {
                                'amount': str(payment.amount_idr),
                                'healer': healer.name,
                            },
                            created_by=request.user,
                        )
                except Exception:
                    pass
        else:
            success, msg = False, _('Aksi tidak dikenali.')
        if success:
            messages.success(request, msg)
        else:
            messages.error(request, msg)
    return redirect('healer_dashboard')


@login_required
def chat_with_healer(request, healer_id):
    healer = get_object_or_404(HealerModel.objects.select_related('category'), id=healer_id)
    room, created = ChatRoom.objects.get_or_create(healer=healer, customer=request.user)
    if created:
        ChatMessage.objects.create(
            room=room, sender=request.user,
            message=_('Halo, saya ingin bertanya tentang layanan Anda.')
        )
    services = healer.services.filter(is_active=True)
    return render(request, 'chat_room.html', {
        'room': room,
        'healer': healer,
        'chat_messages': room.messages.select_related('sender').all(),
        'services': services,
        'chat_role': 'customer',
    })


@login_required
def chat_send(request, room_id):
    if request.method != 'POST':
        return redirect('customer_dashboard')
    room = get_object_or_404(ChatRoom, id=room_id, customer=request.user)
    text = request.POST.get('message', '').strip()
    if text:
        ChatMessage.objects.create(room=room, sender=request.user, message=text)
        room.save()
        healer_user = getattr(room.healer, 'user', None)
        if healer_user:
            create_notification(
                user=healer_user,
                title=_('Pesan Baru dari Pelanggan'),
                message=_('%(name)s: %(msg)s') % {
                    'name': request.user.get_full_name() or request.user.username,
                    'msg': text[:100],
                },
                notification_type='chat',
                link=f'/dashboard/healer/chat/{room.id}/',
            )
    return redirect('chat_with_healer', healer_id=room.healer.id)


@login_required
def chat_messages_api(request, room_id):
    from django.http import JsonResponse
    room = get_object_or_404(ChatRoom.objects.select_related('healer', 'customer'), id=room_id)
    if request.user != room.customer and request.user != getattr(room.healer, 'user', None):
        return JsonResponse({'error': 'forbidden'}, status=403)
    last_id = request.GET.get('last_id', 0)
    try:
        last_id = int(last_id)
    except (ValueError, TypeError):
        last_id = 0
    new_msgs = room.messages.filter(id__gt=last_id).select_related('sender')
    data = [{
        'id': m.id,
        'sender': m.sender.username,
        'sender_name': m.sender.get_full_name() or m.sender.username,
        'message': m.message,
        'created_at': m.created_at.strftime('%H:%M'),
        'is_mine': m.sender == request.user,
    } for m in new_msgs]
    return JsonResponse({'messages': data})


@login_required
def customer_chat_list(request):
    last_msg_subquery = ChatMessage.objects.filter(
        room=OuterRef('pk')
    ).order_by('-created_at')

    rooms = ChatRoom.objects.filter(
        customer=request.user
    ).select_related('healer').annotate(
        _last_msg_id=Subquery(last_msg_subquery.values('id')[:1]),
        _last_msg_text=Subquery(last_msg_subquery.values('message')[:1]),
        _last_msg_time=Subquery(last_msg_subquery.values('created_at')[:1]),
        _unread_count=Count(
            'messages',
            filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)
        ),
    )

    room_data = []
    for room in rooms:
        room_data.append({
            'room': room,
            'last_message_text': getattr(room, '_last_msg_text', None),
            'last_message_time': getattr(room, '_last_msg_time', None),
            'unread': getattr(room, '_unread_count', 0),
        })
    return render(request, 'customer_chat_list.html', {'rooms': room_data})


@require_healer_profile
def healer_chat_list(request, profile, healer):
    last_msg_subquery = ChatMessage.objects.filter(
        room=OuterRef('pk')
    ).order_by('-created_at')

    rooms = ChatRoom.objects.filter(
        healer=healer
    ).select_related('customer').annotate(
        _last_msg_id=Subquery(last_msg_subquery.values('id')[:1]),
        _last_msg_text=Subquery(last_msg_subquery.values('message')[:1]),
        _last_msg_time=Subquery(last_msg_subquery.values('created_at')[:1]),
        _unread_count=Count(
            'messages',
            filter=Q(messages__is_read=False) & ~Q(messages__sender=request.user)
        ),
    )

    room_data = []
    for room in rooms:
        room_data.append({
            'room': room,
            'last_message_text': getattr(room, '_last_msg_text', None),
            'last_message_time': getattr(room, '_last_msg_time', None),
            'unread': getattr(room, '_unread_count', 0),
        })
    return render(request, 'healer_chat_list.html', {'healer': healer, 'rooms': room_data})


@require_healer_profile
def healer_chat_room(request, profile, healer, room_id):
    room = get_object_or_404(
        ChatRoom.objects.select_related('customer', 'healer'),
        id=room_id, healer=healer
    )
    room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    services = healer.services.filter(is_active=True)
    customer_bookings = Booking.objects.filter(
        healer=healer,
        customer_email=room.customer.email,
    ).select_related('healer').order_by('-created_at')[:5]
    return render(request, 'chat_room.html', {
        'room': room,
        'healer': healer,
        'chat_messages': room.messages.select_related('sender').all(),
        'services': services,
        'chat_role': 'healer',
        'customer_bookings': customer_bookings,
    })


@require_healer_profile
def healer_chat_send(request, profile, healer, room_id):
    if request.method != 'POST':
        return redirect('healer_chat_list')
    room = get_object_or_404(ChatRoom, id=room_id, healer=healer)
    text = request.POST.get('message', '').strip()
    if text:
        ChatMessage.objects.create(room=room, sender=request.user, message=text)
        room.save()
        create_notification(
            user=room.customer,
            title=_('Pesan Baru dari Healer'),
            message=_('%(name)s: %(msg)s') % {
                'name': healer.name,
                'msg': text[:100],
            },
            notification_type='chat',
            link=f'/chat/healer/{healer.id}/',
        )
    return redirect('healer_chat_room', room_id=room.id)


@login_required
def notification_list(request):
    all_notifications = Notification.objects.filter(user=request.user)[:50]
    return render(request, 'notification_list.html', {
        'notifications': all_notifications,
    })


@login_required
def notification_read(request, notification_id):
    notif = get_object_or_404(Notification, id=notification_id, user=request.user)
    notif.mark_as_read()
    if notif.link:
        return redirect(notif.link)
    return redirect('notification_list')


@login_required
def notification_read_all(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notification_list')


@login_required
def notification_api(request):
    from django.http import JsonResponse
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})