from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Subquery, OuterRef
import uuid


class HealerCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='spa')

    class Meta:
        verbose_name_plural = 'Healer Categories'

    def __str__(self):
        return self.name


class Healer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, default=uuid.uuid1)
    category = models.ForeignKey(HealerCategory, on_delete=models.SET_NULL, null=True)
    bio = models.TextField()
    experience_years = models.PositiveIntegerField(default=0)
    photo = models.ImageField(upload_to='healer_photos/', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='healer_covers/', blank=True, null=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField()
    price_idr = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    is_available = models.BooleanField(default=True, db_index=True)
    specializations = models.TextField(blank=True, help_text='Pisahkan dengan koma')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rating', '-experience_years']

    def clean(self):
        super().clean()
        if self.price_idr is not None and self.price_idr < 0:
            raise ValidationError({'price_idr': 'Harga tidak boleh negatif.'})
        if self.rating is not None and (self.rating < 0 or self.rating > 99.99):
            raise ValidationError({'rating': 'Rating harus antara 0 dan 99.99.'})

    def __str__(self):
        return f'{self.name} - {self.category}'

    def get_price_in_currency(self, currency_code):
        from payments.services import convert_currency
        return convert_currency(self.price_idr, 'IDR', currency_code)


class HealerSchedule(models.Model):
    healer = models.ForeignKey(Healer, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=[
        (0, 'Senin'), (1, 'Selasa'), (2, 'Rabu'),
        (3, 'Kamis'), (4, 'Jumat'), (5, 'Sabtu'), (6, 'Minggu'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Healer Schedules'
        unique_together = ['healer', 'day_of_week']

    def __str__(self):
        return f'{self.healer.name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}'


class HealerReview(models.Model):
    healer = models.ForeignKey(Healer, on_delete=models.CASCADE, related_name='reviews')
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer_name} - {self.healer.name} ({self.rating}*)'


class Location(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, default=uuid.uuid1)
    description = models.TextField(blank=True)
    gradient = models.CharField(max_length=200, default='from-emerald-900 via-teal-800 to-green-900',
        help_text='CSS gradient classes for card background')
    healer_count = models.PositiveIntegerField(default=0)
    center_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class HealingCenter(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, default=uuid.uuid1)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.TextField()
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    photo = models.ImageField(upload_to='center_photos/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    review_count = models.PositiveIntegerField(default=0)
    specializations = models.TextField(blank=True, help_text='Pisahkan dengan koma')
    price_range = models.CharField(max_length=100, blank=True, help_text='Contoh: Rp 300.000 - Rp 1.500.000')
    min_price_idr = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Harga minimum dalam IDR')
    max_price_idr = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Harga maksimum dalam IDR')
    has_google_badge = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    gradient = models.CharField(max_length=200, default='from-cyan-800 to-teal-700')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rating']

    def __str__(self):
        return self.name


class Speciality(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, default=uuid.uuid1)
    emoji = models.CharField(max_length=10, default='🔮')
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.emoji} {self.name}'


class Testimonial(models.Model):
    customer_name = models.CharField(max_length=100)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    comment = models.TextField()
    date = models.DateField(auto_now_add=True)
    is_featured = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.customer_name} - {self.rating}*'


class HealerService(models.Model):
    healer = models.ForeignKey(Healer, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price_idr = models.DecimalField(max_digits=12, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=60)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']

    def clean(self):
        super().clean()
        if self.price_idr is not None and self.price_idr < 0:
            raise ValidationError({'price_idr': 'Harga tidak boleh negatif.'})

    def __str__(self):
        return f'{self.name} - {self.healer.name}'


class HealerMessage(models.Model):
    healer = models.ForeignKey(Healer, on_delete=models.CASCADE, related_name='messages')
    sender_name = models.CharField(max_length=100)
    sender_email = models.EmailField()
    sender_phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    reply = models.TextField(blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.sender_name} → {self.healer.name}: {self.subject}'


class HealerPaymentSetting(models.Model):
    healer = models.OneToOneField(Healer, on_delete=models.CASCADE, related_name='payment_settings')

    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_name = models.CharField(max_length=200, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    swift_code = models.CharField(max_length=20, blank=True, help_text='Kode SWIFT/BIC untuk transfer internasional')

    gopay_number = models.CharField(max_length=20, blank=True)
    ovo_number = models.CharField(max_length=20, blank=True)
    dana_number = models.CharField(max_length=20, blank=True)
    shopeepay_number = models.CharField(max_length=20, blank=True, help_text='Nomor ShopeePay')
    linkaja_number = models.CharField(max_length=20, blank=True, help_text='Nomor LinkAja')
    isaku_number = models.CharField(max_length=20, blank=True, help_text='Nomor iSaku')

    qris_merchant_name = models.CharField(max_length=200, blank=True, help_text='Nama merchant QRIS')
    qris_id = models.CharField(max_length=50, blank=True, help_text='ID Merchant QRIS')

    paypal_email = models.EmailField(blank=True)
    visa_mc_enabled = models.BooleanField(default=False, help_text='Aktifkan pembayaran Visa/Mastercard via PayPal')

    # Payment Gateway
    payment_gateway = models.CharField(max_length=50, blank=True, help_text='Payment gateway: midtrans, xendit, doku, tripay, manual')
    pg_midtrans_server_key = models.CharField(max_length=200, blank=True, help_text='Midtrans Server Key')
    pg_midtrans_client_key = models.CharField(max_length=200, blank=True, help_text='Midtrans Client Key')
    pg_midtrans_merchant_id = models.CharField(max_length=100, blank=True, help_text='Midtrans Merchant ID')
    pg_xendit_secret_key = models.CharField(max_length=200, blank=True, help_text='Xendit Secret Key')
    pg_xendit_api_key = models.CharField(max_length=200, blank=True, help_text='Xendit API Key')
    pg_doku_client_key = models.CharField(max_length=200, blank=True, help_text='DOKU Client Key')
    pg_doku_merchant_id = models.CharField(max_length=100, blank=True, help_text='DOKU Merchant ID')
    pg_tripay_api_key = models.CharField(max_length=200, blank=True, help_text='Tripay API Key')
    pg_tripay_private_key = models.CharField(max_length=200, blank=True, help_text='Tripay Private Key')
    pg_tripay_merchant_code = models.CharField(max_length=100, blank=True, help_text='Tripay Merchant Code')

    # VA Bank Settings
    va_bank_enabled = models.BooleanField(default=False, help_text='Aktifkan pembayaran Virtual Account')
    va_banks = models.CharField(max_length=500, blank=True, help_text='Daftar bank VA: BCA,Mandiri,BRI,BNI,BSI, dll')

    accept_cash = models.BooleanField(default=True)
    accept_transfer = models.BooleanField(default=True)
    accept_gopay = models.BooleanField(default=False)
    accept_ovo = models.BooleanField(default=False)
    accept_dana = models.BooleanField(default=False)
    accept_shopeepay = models.BooleanField(default=False)
    accept_linkaja = models.BooleanField(default=False)
    accept_isaku = models.BooleanField(default=False)
    accept_qris = models.BooleanField(default=False)
    accept_paypal = models.BooleanField(default=False)
    accept_visa_mc = models.BooleanField(default=False)

    min_payment_idr = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Minimum pembayaran dalam IDR (0 = tanpa minimum)')
    require_deposit = models.BooleanField(default=False, help_text='Wajibkan deposit sebelum booking')
    deposit_percent = models.PositiveIntegerField(default=50, help_text='Persentase deposit (1-100)')
    auto_confirm = models.BooleanField(default=False, help_text='Konfirmasi otomatis setelah pembayaran berhasil')
    payment_timeout_hours = models.PositiveIntegerField(default=24, help_text='Batas waktu pembayaran dalam jam')
    enable_escrow = models.BooleanField(default=True, help_text='Aktifkan escrow (dana ditahan hingga pekerjaan selesai)')
    enable_refund = models.BooleanField(default=True, help_text='Aktifkan pengembalian dana')
    require_proof = models.BooleanField(default=False, help_text='Wajibkan bukti transfer dari customer')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Healer Payment Settings'

    def __str__(self):
        return f'Payment Settings - {self.healer.name}'

    def get_accepted_methods(self):
        methods = []
        if self.accept_transfer and self.bank_name and self.bank_account_number:
            methods.append('transfer')
        if self.va_bank_enabled and self.va_banks:
            methods.append('va_transfer')
        if self.accept_gopay and self.gopay_number:
            methods.append('gopay')
        if self.accept_ovo and self.ovo_number:
            methods.append('ovo')
        if self.accept_dana and self.dana_number:
            methods.append('dana')
        if self.accept_shopeepay and self.shopeepay_number:
            methods.append('shopeepay')
        if self.accept_linkaja and self.linkaja_number:
            methods.append('linkaja')
        if self.accept_isaku and self.isaku_number:
            methods.append('isaku')
        if self.accept_qris and self.qris_id:
            methods.append('qris')
        if self.accept_paypal and self.paypal_email:
            methods.append('paypal')
        if self.accept_visa_mc and self.visa_mc_enabled:
            methods.append('visa_mc')
        if self.payment_gateway and self.payment_gateway != 'manual':
            methods.append('payment_gateway')
        if self.accept_cash:
            methods.append('cash')
        return methods

    def is_method_accepted(self, method):
        return method in self.get_accepted_methods()


BANK_CHOICES = [
    ('BCA', 'Bank BCA'),
    ('Mandiri', 'Bank Mandiri'),
    ('BRI', 'Bank BRI'),
    ('BNI', 'Bank BNI'),
    ('BTN', 'Bank BTN'),
    ('BSI', 'Bank BSI (Syariah)'),
    ('BRIS', 'Bank BRI Syariah'),
    ('BNIS', 'Bank BNI Syariah'),
    ('CIMB', 'CIMB Niaga'),
    ('Danamon', 'Bank Danamon'),
    ('Permata', 'Bank Permata'),
    ('OCBC', 'OCBC NISP'),
    ('Maybank', 'Maybank'),
    ('Mega', 'Bank Mega'),
    ('Panin', 'Bank Panin'),
    ('Bukopin', 'Bank Bukopin'),
    ('Sinarmas', 'Bank Sinarmas'),
    ('Commonwealth', 'Bank Commonwealth'),
    ('Muamalat', 'Bank Muamalat'),
    ('Jago', 'Bank Jago'),
    ('NeoCommerce', 'Bank Neo Commerce'),
    ('Seabank', 'Sea Bank'),
    ('Digibank', 'Digibank (DBS)'),
    ('BJP', 'BJB'),
    ('MandiriSyariah', 'Bank Mandiri Syariah'),
]

METHOD_CHOICES = [
    ('va', 'Virtual Account'),
    ('transfer', 'Manual Transfer'),
    ('qris', 'QRIS'),
    ('ewallet', 'E-Wallet'),
]


class BankTransactionSetting(models.Model):
    healer = models.ForeignKey(Healer, on_delete=models.CASCADE, related_name='bank_transaction_settings')
    bank_code = models.CharField(max_length=50, choices=BANK_CHOICES)
    is_active = models.BooleanField(default=False, help_text='Aktifkan bank ini untuk transaksi')

    account_number = models.CharField(max_length=50, blank=True, help_text='Nomor rekening / Virtual Account')
    account_name = models.CharField(max_length=200, blank=True, help_text='Nama pemegang rekening')
    branch = models.CharField(max_length=100, blank=True, help_text='Cabang bank')

    accept_va = models.BooleanField(default=False, help_text='Terima pembayaran via Virtual Account')
    accept_transfer = models.BooleanField(default=True, help_text='Terima transfer manual')
    accept_qris = models.BooleanField(default=False, help_text='Terima QRIS via bank ini')

    sop_va = models.TextField(blank=True, help_text='SOP instruksi Virtual Account')
    sop_transfer = models.TextField(blank=True, help_text='SOP instruksi transfer manual')
    sop_qris = models.TextField(blank=True, help_text='SOP instruksi QRIS')

    va_code = models.CharField(max_length=50, blank=True, help_text='Kode prefix VA (contoh: 1234 untuk BCA VA 1234xxxxxx)')
    admin_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Biaya admin tambahan (0 = gratis)')
    min_transfer = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Minimum transfer')
    max_transfer = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Maximum transfer (0 = tanpa batas)')

    payment_timeout_minutes = models.PositiveIntegerField(default=60, help_text='Batas waktu pembayaran dalam menit')
    auto_cancel = models.BooleanField(default=True, help_text='Batalkan otomatis jika timeout')

    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'bank_code']
        unique_together = ['healer', 'bank_code']

    def __str__(self):
        return f'{self.bank_code} - {self.healer.name}'

    def get_methods_display(self):
        methods = []
        if self.accept_va:
            methods.append('Virtual Account')
        if self.accept_transfer:
            methods.append('Transfer Manual')
        if self.accept_qris:
            methods.append('QRIS')
        return ', '.join(methods) if methods else '-'

    def get_default_sop(self, method='transfer'):
        defaults = {
            'va': f"""Cara Pembayaran Virtual Account {self.bank_code}:
1. Buka aplikasi mobile banking {self.bank_code} atau ATM
2. Pilih menu Virtual Account / Bayar Virtual Account
3. Masukkan nomor VA: {self.va_code}xxxxxxxx
4. Pastikan nama dan jumlah pembayaran benar
5. Konfirmasi pembayaran
6. Simpan bukti pembayaran
7. Upload bukti pembayaran di halaman booking
8. Tunggu konfirmasi dari healer""",
            'transfer': f"""Cara Transfer Manual {self.bank_code}:
1. Buka aplikasi mobile banking {self.bank_code} atau ATM
2. Pilih menu Transfer ke Rekening Tujuan
3. Masukkan nomor rekening: {self.account_number}
4. Atas nama: {self.account_name}
5. Masukkan jumlah yang tepat sesuai total pembayaran
6. Konfirmasi dan selesaikan transfer
7. Simpan bukti transfer (screenshot/receipt)
8. Upload bukti transfer di halaman booking
9. Tunggu konfirmasi dari healer""",
            'qris': f"""Cara Pembayaran QRIS {self.bank_code}:
1. Buka aplikasi mobile banking {self.bank_code} atau e-wallet
2. Pilih menu Scan QR / QRIS
3. Scan kode QR yang diberikan
4. Pastikan nama merchant dan jumlah benar
5. Konfirmasi pembayaran
6. Pembayaran otomatis terkonfirmasi""",
        }
        return defaults.get(method, '')


class ChatRoomQuerySet(models.QuerySet):
    def with_last_message(self):
        last_msg = ChatMessage.objects.filter(
            room=OuterRef('pk')
        ).order_by('-created_at')
        return self.annotate(
            _last_message_id=Subquery(last_msg.values('id')[:1]),
            _last_message_text=Subquery(last_msg.values('message')[:1]),
            _last_message_time=Subquery(last_msg.values('created_at')[:1]),
            _last_message_sender_id=Subquery(last_msg.values('sender_id')[:1]),
        )


class ChatRoom(models.Model):
    healer = models.ForeignKey(Healer, on_delete=models.CASCADE, related_name='chat_rooms')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ChatRoomQuerySet.as_manager()

    class Meta:
        unique_together = ['healer', 'customer']
        ordering = ['-updated_at']

    def __str__(self):
        return f'Chat: {self.customer.username} → {self.healer.name}'

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender.username}: {self.message[:50]}'


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('booking', 'Booking'),
        ('chat', 'Chat'),
        ('system', 'System'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.title}'

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])
