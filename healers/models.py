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
    paypal_email = models.EmailField(blank=True)
    visa_mc_enabled = models.BooleanField(default=False, help_text='Aktifkan pembayaran Visa/Mastercard via PayPal')
    accept_cash = models.BooleanField(default=True)
    accept_transfer = models.BooleanField(default=True)
    accept_gopay = models.BooleanField(default=False)
    accept_ovo = models.BooleanField(default=False)
    accept_dana = models.BooleanField(default=False)
    accept_paypal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Payment Settings - {self.healer.name}'


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
