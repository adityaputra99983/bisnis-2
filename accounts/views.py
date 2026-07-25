import decimal
from django.db.models import Subquery, OuterRef, Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from .models import UserProfile
from .forms import CustomerRegistrationForm, HealerRegistrationForm


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
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            profile, _created = UserProfile.objects.get_or_create(user=user)
            if profile.is_healer:
                return redirect('healer_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, _('Username atau password salah.'))
    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, _('Anda berhasil logout.'))
    return redirect('home')


@login_required
def customer_dashboard(request):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    from bookings.models import Booking
    bookings = Booking.objects.filter(
        customer_email=request.user.email
    ).select_related('healer').order_by('-created_at')[:20]
    return render(request, 'customer_dashboard.html', {
        'profile': profile,
        'bookings': bookings,
    })


@login_required
def healer_dashboard(request):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        messages.error(request, _('Anda tidak memiliki akses ke dashboard healer.'))
        return redirect('home')
    from healers.models import Healer, HealerSchedule, HealerService
    from bookings.models import Booking
    from payments.models import Payment
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
        pending_count = Booking.objects.filter(healer=healer, status='pending_confirm').count()
        in_progress_count = Booking.objects.filter(healer=healer, status='in_progress').count()
        completed_count = Booking.objects.filter(healer=healer, status='completed').count()
        from django.db.models import Sum
        total_revenue = Payment.objects.filter(booking__healer=healer, status='released').aggregate(
            total=Sum('amount_idr'))['total'] or 0
        held_funds = Payment.objects.filter(booking__healer=healer, status='held').aggregate(
            total=Sum('amount_idr'))['total'] or 0
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
    })


@login_required
def healer_profile_edit(request):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        messages.error(request, _('Anda tidak memiliki akses.'))
        return redirect('home')
    from healers.models import Healer
    healer = profile.get_healer_profile()
    if not healer:
        messages.error(request, _('Profil healer tidak ditemukan.'))
        return redirect('home')
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


@login_required
def healer_schedule_edit(request):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        messages.error(request, _('Anda tidak memiliki akses.'))
        return redirect('home')
    from healers.models import Healer, HealerSchedule
    healer = profile.get_healer_profile()
    if not healer:
        messages.error(request, _('Profil healer tidak ditemukan.'))
        return redirect('home')
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


@login_required
def healer_services(request):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        return redirect('home')
    from healers.models import Healer, HealerService
    healer = profile.get_healer_profile()
    if not healer:
        return redirect('home')
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


@login_required
def healer_messages(request):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        return redirect('home')
    from healers.models import Healer, HealerMessage
    healer = profile.get_healer_profile()
    if not healer:
        return redirect('home')
    all_messages = healer.messages.all()
    unread_count = all_messages.filter(is_read=False).count()
    return render(request, 'healer_messages.html', {
        'healer': healer, 'messages_list': all_messages, 'unread_count': unread_count,
    })


@login_required
def healer_message_detail(request, msg_id):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        return redirect('home')
    from healers.models import Healer, HealerMessage
    healer = profile.get_healer_profile()
    if not healer:
        return redirect('home')
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


@login_required
def healer_payments(request):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        return redirect('home')
    from healers.models import Healer, HealerPaymentSetting
    healer = profile.get_healer_profile()
    if not healer:
        return redirect('home')
    settings, _created = HealerPaymentSetting.objects.get_or_create(healer=healer)
    if request.method == 'POST':
        settings.bank_name = request.POST.get('bank_name', '')
        settings.bank_account_name = request.POST.get('bank_account_name', '')
        settings.bank_account_number = request.POST.get('bank_account_number', '')
        settings.swift_code = request.POST.get('swift_code', '')
        settings.gopay_number = request.POST.get('gopay_number', '')
        settings.ovo_number = request.POST.get('ovo_number', '')
        settings.dana_number = request.POST.get('dana_number', '')
        settings.paypal_email = request.POST.get('paypal_email', '')
        settings.visa_mc_enabled = 'visa_mc_enabled' in request.POST
        settings.accept_cash = 'accept_cash' in request.POST
        settings.accept_transfer = 'accept_transfer' in request.POST
        settings.accept_gopay = 'accept_gopay' in request.POST
        settings.accept_ovo = 'accept_ovo' in request.POST
        settings.accept_dana = 'accept_dana' in request.POST
        settings.accept_paypal = 'accept_paypal' in request.POST
        settings.save()
        messages.success(request, _('Pengaturan pembayaran berhasil diperbarui.'))
        return redirect('healer_payments')
    return render(request, 'healer_payments.html', {'healer': healer, 'settings': settings})


@login_required
def healer_booking_update(request, booking_code):
    from bookings.models import Booking
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
                        from django.utils import timezone
                        from payments.models import TransactionLog
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
    from healers.models import Healer, ChatRoom, ChatMessage, HealerService
    healer = get_object_or_404(Healer.objects.select_related('category'), id=healer_id)
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
        'messages': room.messages.select_related('sender').all(),
        'services': services,
        'chat_role': 'customer',
    })


@login_required
def chat_send(request, room_id):
    from healers.models import ChatRoom, ChatMessage
    if request.method != 'POST':
        return redirect('customer_dashboard')
    room = get_object_or_404(ChatRoom, id=room_id, customer=request.user)
    text = request.POST.get('message', '').strip()
    if text:
        ChatMessage.objects.create(room=room, sender=request.user, message=text)
        room.save()
    return redirect('chat_with_healer', healer_id=room.healer.id)


@login_required
def chat_messages_api(request, room_id):
    from django.http import JsonResponse
    from healers.models import ChatRoom
    import json
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
    from healers.models import ChatRoom, ChatMessage
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


@login_required
def healer_chat_list(request):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        return redirect('home')
    healer = profile.get_healer_profile()
    if not healer:
        return redirect('home')
    from healers.models import ChatRoom, ChatMessage
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


@login_required
def healer_chat_room(request, room_id):
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        return redirect('home')
    healer = profile.get_healer_profile()
    if not healer:
        return redirect('home')
    from healers.models import ChatRoom, ChatMessage, HealerService
    from bookings.models import Booking
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
        'messages': room.messages.select_related('sender').all(),
        'services': services,
        'chat_role': 'healer',
        'customer_bookings': customer_bookings,
    })


@login_required
def healer_chat_send(request, room_id):
    if request.method != 'POST':
        return redirect('healer_chat_list')
    profile, _created = UserProfile.objects.get_or_create(user=request.user)
    if not profile.is_healer:
        return redirect('home')
    healer = profile.get_healer_profile()
    if not healer:
        return redirect('home')
    from healers.models import ChatRoom, ChatMessage
    room = get_object_or_404(ChatRoom, id=room_id, healer=healer)
    text = request.POST.get('message', '').strip()
    if text:
        ChatMessage.objects.create(room=room, sender=request.user, message=text)
        room.save()
    return redirect('healer_chat_room', room_id=room.id)