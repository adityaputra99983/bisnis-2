from django.contrib import admin
from .models import Currency, PaymentMethod, Payment, TransactionLog


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol', 'rate_to_idr', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_code', 'booking', 'amount_idr', 'currency', 'amount_converted', 'status', 'proof_uploaded_at', 'created_at']
    list_filter = ['status', 'currency']
    search_fields = ['payment_code', 'booking__customer_name']
    readonly_fields = ['payment_code', 'created_at', 'updated_at', 'proof_uploaded_at']


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ['payment', 'action', 'created_at']
    list_filter = ['action']
