from django.contrib import admin
from .models import Booking, BookingTimeSlot


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_code', 'healer', 'customer_name', 'booking_date', 'status', 'currency', 'total_price_converted']
    list_filter = ['status', 'currency', 'booking_date']
    search_fields = ['booking_code', 'customer_name', 'customer_email']
    readonly_fields = ['booking_code', 'created_at', 'updated_at']


@admin.register(BookingTimeSlot)
class BookingTimeSlotAdmin(admin.ModelAdmin):
    list_display = ['healer', 'date', 'start_time', 'end_time', 'is_booked']
    list_filter = ['is_booked', 'date']
