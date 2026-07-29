import os
import sys
import traceback

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dukun.settings')

try:
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
except Exception:
    import json

    def app(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        tb = traceback.format_exc()
        yield json.dumps({
            'error': 'Django WSGI failed to initialize',
            'traceback': tb,
            'cwd': os.getcwd(),
            'sys_path': [p for p in sys.path if 'dukun' in p.lower()],
            'files_root': os.listdir(_root) if os.path.isdir(_root) else [],
        }).encode()
