from django.db import models
from bookings.models import Booking
from django.contrib.auth.models import User
import uuid


class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    rate_to_idr = models.DecimalField(max_digits=15, decimal_places=6, default=1.0,
        help_text='Kurs terhadap 1 IDR')
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Currencies'
        ordering = ['code']

    def __str__(self):
        return f'{self.code} - {self.name}'


class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='credit-card')
    is_active = models.BooleanField(default=True)
    instructions = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Menunggu Pembayaran'),
        ('processing', 'Sedang Diproses'),
        ('success', 'Pembayaran Berhasil'),
        ('held', 'Dana Ditahan (Escrow)'),
        ('released', 'Dana Dirilis ke Healer'),
        ('failed', 'Gagal'),
        ('refunded', 'Dikembalikan'),
        ('expired', 'Kadaluarsa'),
    ]

    VALID_PAYMENT_TRANSITIONS = {
        'pending': ['processing', 'success', 'failed', 'expired'],
        'processing': ['success', 'failed'],
        'success': ['held', 'refunded'],
        'held': ['released', 'refunded'],
        'released': [],
        'failed': [],
        'refunded': [],
        'expired': [],
    }

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    payment_code = models.CharField(max_length=40, unique=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    amount_idr = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    amount_converted = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    exchange_rate = models.DecimalField(max_digits=15, decimal_places=6, default=1.0)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', db_index=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    held_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    refund_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    proof_image = models.ImageField(upload_to='payment_proofs/', blank=True, null=True,
        help_text='Bukti pembayaran berupa screenshot/struk transfer')
    proof_note = models.TextField(blank=True, verbose_name='Catatan bukti pembayaran')
    proof_uploaded_at = models.DateTimeField(null=True, blank=True, verbose_name='Waktu unggah bukti')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.payment_code} - {self.booking.customer_name} - {self.status}'

    def save(self, *args, **kwargs):
        if not self.payment_code:
            self.payment_code = str(uuid.uuid4())[:12].upper()
        super().save(*args, **kwargs)

    def can_transition_to(self, new_status):
        allowed = self.VALID_PAYMENT_TRANSITIONS.get(self.status, [])
        return new_status in allowed

    def has_proof(self):
        return bool(self.proof_image)


class TransactionLog(models.Model):
    LOG_TYPES = [
        ('payment_created', 'Pembayaran Dibuat'),
        ('payment_success', 'Pembayaran Berhasil'),
        ('payment_held', 'Dana Ditahan'),
        ('payment_released', 'Dana Dirilis'),
        ('payment_refunded', 'Pembayaran Dikembalikan'),
        ('payment_failed', 'Pembayaran Gagal'),
        ('booking_status_change', 'Status Booking Berubah'),
        ('security_alert', 'Peringatan Keamanan'),
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='logs', null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='transaction_logs', null=True, blank=True)
    log_type = models.CharField(max_length=30, choices=LOG_TYPES, default='payment_created', db_index=True)
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.log_type} - {self.action}'
