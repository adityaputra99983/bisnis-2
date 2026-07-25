from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from healers.models import Healer
from django.utils import timezone
import uuid


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending_payment', 'Menunggu Pembayaran'),
        ('pending_confirm', 'Menunggu Konfirmasi Healer'),
        ('confirmed', 'Dikonfirmasi'),
        ('in_progress', 'Sedang Dikerjakan'),
        ('completed', 'Selesai'),
        ('cancelled', 'Dibatalkan'),
        ('expired', 'Kadaluarsa'),
        ('refunded', 'Dikembalikan'),
    ]

    VALID_TRANSITIONS = {
        'pending_payment': ['pending_confirm', 'cancelled', 'expired'],
        'pending_confirm': ['confirmed', 'cancelled', 'refunded'],
        'confirmed': ['in_progress', 'cancelled', 'refunded'],
        'in_progress': ['completed', 'refunded'],
        'completed': [],
        'cancelled': [],
        'expired': [],
        'refunded': [],
    }

    booking_code = models.CharField(max_length=20, unique=True, default=uuid.uuid4)
    healer = models.ForeignKey(Healer, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    service_type = models.CharField(max_length=200)
    service_price_idr = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    notes = models.TextField(blank=True)
    total_price_idr = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='IDR')
    total_price_converted = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment', db_index=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.booking_code} - {self.customer_name} - {self.healer.name}'

    def save(self, *args, **kwargs):
        if not self.booking_code or self.booking_code == '':
            self.booking_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def can_transition_to(self, new_status):
        allowed = self.VALID_TRANSITIONS.get(self.status, [])
        return new_status in allowed

    def transition_to(self, new_status, user=None, reason=''):
        if not self.can_transition_to(new_status):
            return False, _('Transisi status tidak valid: %(from)s → %(to)s') % {
                'from': self.get_status_display(),
                'to': dict(self.STATUS_CHOICES).get(new_status, new_status),
            }
        now = timezone.now()
        old_status = self.status
        self.status = new_status

        if new_status == 'pending_confirm':
            pass
        elif new_status == 'confirmed':
            self.confirmed_at = now
        elif new_status == 'in_progress':
            self.started_at = now
        elif new_status == 'completed':
            self.completed_at = now
        elif new_status == 'cancelled':
            self.cancelled_at = now
            self.cancel_reason = reason
        elif new_status == 'refunded':
            self.cancelled_at = now
            self.cancel_reason = reason

        self.save()
        BookingStatusLog.objects.create(
            booking=self,
            old_status=old_status,
            new_status=new_status,
            changed_by=user,
            reason=reason,
        )
        return True, _('Status berhasil diperbarui.')


class BookingStatusLog(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_logs')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.booking.booking_code}: {self.old_status} → {self.new_status}'


class BookingTimeSlot(models.Model):
    healer = models.ForeignKey(Healer, on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ['healer', 'date', 'start_time']

    def __str__(self):
        return f'{self.healer.name} - {self.date} {self.start_time}-{self.end_time}'
