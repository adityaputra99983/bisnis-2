from django.contrib import admin
from .models import (HealerCategory, Healer, HealerSchedule, HealerReview,
    Location, HealingCenter, Speciality, Testimonial,
    HealerService, HealerMessage, HealerPaymentSetting)


@admin.register(HealerCategory)
class HealerCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Healer)
class HealerAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'experience_years', 'price_idr', 'rating', 'is_available']
    list_filter = ['category', 'is_available']
    search_fields = ['name', 'specializations']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(HealerSchedule)
class HealerScheduleAdmin(admin.ModelAdmin):
    list_display = ['healer', 'day_of_week', 'start_time', 'end_time']
    list_filter = ['day_of_week']


@admin.register(HealerReview)
class HealerReviewAdmin(admin.ModelAdmin):
    list_display = ['healer', 'customer_name', 'rating', 'created_at']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'healer_count', 'center_count']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(HealingCenter)
class HealingCenterAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'rating', 'review_count', 'is_active']
    list_filter = ['is_active', 'location']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    list_display = ['name', 'emoji', 'order']
    ordering = ['order']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'rating', 'date', 'is_featured']
    list_filter = ['rating', 'is_featured']


@admin.register(HealerService)
class HealerServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'healer', 'price_idr', 'duration_minutes', 'is_active']
    list_filter = ['is_active', 'healer']


@admin.register(HealerMessage)
class HealerMessageAdmin(admin.ModelAdmin):
    list_display = ['healer', 'sender_name', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'healer']


@admin.register(HealerPaymentSetting)
class HealerPaymentSettingAdmin(admin.ModelAdmin):
    list_display = ['healer', 'bank_name', 'bank_account_number']
