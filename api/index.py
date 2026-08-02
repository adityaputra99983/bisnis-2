import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dukun.settings')
# Kredensial database tidak pernah di-hardcode di sini.
# Set DATABASE_URL (PostgreSQL/Supabase) dan SUPABASE_SERVICE_KEY lewat
# Environment Variables pada platform deploy (Vercel/Render/Railway).

import django
django.setup()

from django.core.management import call_command
if os.environ.get('DATABASE_URL'):
    try:
        call_command('migrate', '--noinput', verbosity=0)
    except Exception:
        pass

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
