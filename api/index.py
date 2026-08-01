import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dukun.settings')

# Production secrets (DATABASE_URL, SUPABASE_SERVICE_KEY, DJANGO_SECRET_KEY, ...)
# MUST be provided via Vercel Environment Variables:
#   https://vercel.com/docs/projects/environments/environment-variables
# Never hardcode credentials in source code.

import django
django.setup()

from django.core.management import call_command
try:
    call_command('migrate', '--noinput', verbosity=0)
except Exception:
    pass

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
