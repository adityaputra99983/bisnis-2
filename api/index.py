import os
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dukun.settings')
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres.vwjxhfpvcaesrfcglgex:%2B%3FV%2FQxPVcU%24y93c@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres?sslmode=require')
os.environ.setdefault('SUPABASE_S3_ACCESS_KEY', '2eb42062debed0f97dccd3a4e62d84976d8b4544178aac5a9156d18ecad3882f')
os.environ.setdefault('SUPABASE_S3_SECRET_KEY', 'e39e46dcb06c5cebd48e0cd09a700eb9')

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
