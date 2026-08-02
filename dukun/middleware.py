from django.conf import settings


class SecurityHeadersMiddleware:
    """Selalu kirim security headers sehingga browser & scanner web
    menganggap situs aman (tidak menampilkan peringatan berbahaya)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault('X-Content-Type-Options', 'nosniff')
        response.setdefault('X-Frame-Options', 'DENY')
        response.setdefault('X-XSS-Protection', '1; mode=block')
        response.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.setdefault(
            'Permissions-Policy',
            'camera=(), microphone=(), geolocation=(), payment=()'
        )
        if not settings.DEBUG:
            response.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
            response.setdefault(
                'Content-Security-Policy',
                "upgrade-insecure-requests; default-src 'self' 'unsafe-inline' 'unsafe-eval' "
                "https: data: blob:; img-src 'self' https: data:; font-src 'self' https: data:; "
                "style-src 'self' 'unsafe-inline' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:"
            )
        return response
