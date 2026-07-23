from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('healers/', views.healer_list, name='healer_list'),
    path('healer/<slug:slug>/', views.healer_detail, name='healer_detail'),
    path('centers/', views.center_list, name='center_list'),
    path('center/<slug:slug>/', views.center_detail, name='center_detail'),
    path('specialities/', views.speciality_list, name='speciality_list'),
    path('locations/', views.location_list, name='location_list'),
    path('api/healer/<int:healer_id>/schedule/', views.healer_schedule_api, name='healer_schedule_api'),
]
