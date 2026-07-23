from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_choose, name='register_choose'),
    path('register/customer/', views.register_customer, name='register_customer'),
    path('register/healer/', views.register_healer, name='register_healer'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/healer/', views.healer_dashboard, name='healer_dashboard'),
    path('dashboard/healer/profil/', views.healer_profile_edit, name='healer_profile_edit'),
    path('dashboard/healer/jadwal/', views.healer_schedule_edit, name='healer_schedule_edit'),
    path('dashboard/healer/layanan/', views.healer_services, name='healer_services'),
    path('dashboard/healer/pesan/', views.healer_messages, name='healer_messages'),
    path('dashboard/healer/pesan/<int:msg_id>/', views.healer_message_detail, name='healer_message_detail'),
    path('dashboard/healer/pembayaran/', views.healer_payments, name='healer_payments'),
    path('dashboard/healer/booking/<str:booking_code>/status/', views.healer_booking_update, name='healer_booking_update'),
    path('chat/healer/<int:healer_id>/', views.chat_with_healer, name='chat_with_healer'),
    path('chat/<int:room_id>/send/', views.chat_send, name='chat_send'),
    path('chat/<int:room_id>/api/', views.chat_messages_api, name='chat_messages_api'),
    path('dashboard/customer/chat/', views.customer_chat_list, name='customer_chat_list'),
    path('dashboard/healer/chat/', views.healer_chat_list, name='healer_chat_list'),
    path('dashboard/healer/chat/<int:room_id>/', views.healer_chat_room, name='healer_chat_room'),
    path('dashboard/healer/chat/<int:room_id>/send/', views.healer_chat_send, name='healer_chat_send'),
]
