from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:healer_id>/', views.create_booking, name='create_booking'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('booking/track/', views.booking_track, name='booking_track'),
    path('booking/<str:booking_code>/', views.booking_detail, name='booking_detail'),
    path('booking/<str:booking_code>/cancel/', views.booking_cancel, name='booking_cancel'),
    path('booking/<str:booking_code>/confirm/', views.booking_confirm, name='booking_confirm'),
    path('booking/<str:booking_code>/start/', views.booking_start_work, name='booking_start_work'),
    path('booking/<str:booking_code>/complete/', views.booking_complete_work, name='booking_complete_work'),
]
