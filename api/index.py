import os
import sys

# Pastikan root project ada di Python path
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dukun.settings')

try:
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
except Exception as e:
    import json
    def app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        yield json.dumps({
            'error': 'Django WSGI failed to initialize',
            'detail': str(e),
            'cwd': os.getcwd(),
            'sys_path': sys.path,
        }).encode()
