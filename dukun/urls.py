from django.contrib import admin
from django.urls import path, include
from dukun import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('robots.txt', views.robots_txt),
    path('.well-known/security.txt', views.security_txt),
]

urlpatterns += i18n_patterns(
    path('', include('healers.urls')),
    path('', include('bookings.urls')),
    path('', include('payments.urls')),
    path('', include('accounts.urls')),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
