import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dukun.settings')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres.vwjxhfpvcaesrfcglgex:%2B%3FV%2FQxPVcU%24y93c@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?sslmode=require')
os.environ.setdefault('SUPABASE_SERVICE_KEY', '')
# Catatan: nilai di atas hanya fallback saat env vars Vercel belum di-set.
# Env vars (jika ada) selalu menang. Jangan commit perubahan kredensial di file ini.

import django
django.setup()

from django.core.management import call_command
try:
    call_command('migrate', '--noinput', verbosity=0)
except Exception:
    pass

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
