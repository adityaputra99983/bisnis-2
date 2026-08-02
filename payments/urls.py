from django.urls import path
from . import views

urlpatterns = [
    path('payment/<str:booking_code>/', views.payment_process, name='payment_process'),
    path('payment/<str:booking_code>/create/', views.create_payment, name='create_payment'),
    path('payment/detail/<str:payment_code>/', views.payment_detail, name='payment_detail'),
    path('payment/<str:payment_code>/proof/', views.upload_payment_proof, name='upload_payment_proof'),
    path('payment/<str:payment_code>/simulate/', views.payment_simulate, name='payment_simulate'),
    path('payments/', views.payment_history, name='payment_history'),
    path('api/currency/', views.currency_converter_api, name='currency_converter_api'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/booking/<str:booking_code>/status/', views.update_booking_status, name='update_booking_status'),
]
