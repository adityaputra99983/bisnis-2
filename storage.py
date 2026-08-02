import os
import io
import requests
from urllib.parse import urljoin
from django.core.files.base import File
from django.core.files.storage import Storage
from django.core.exceptions import ImproperlyConfigured

CONTENT_TYPES = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.webp': 'image/webp',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.pdf': 'application/pdf',
    '.mp4': 'video/mp4',
}


class SupabaseStorage(Storage):
    def __init__(self):
        self.project_url = 'https://vwjxhfpvcaesrfcglgex.supabase.co'
        self.api_key = os.environ.get('SUPABASE_SERVICE_KEY')
        self.bucket = os.environ.get('SUPABASE_S3_BUCKET', 'media')
        # Gunakan service role endpoint (bukan public) untuk keamanan
        self.base_url = f'{self.project_url}/storage/v1/object/{self.bucket}'
        self.public_url = f'{self.project_url}/storage/v1/object/public/{self.bucket}'
        if not self.api_key:
            raise ImproperlyConfigured(
                'SUPABASE_SERVICE_KEY environment variable is required for SupabaseStorage.'
            )
        self.headers = {
            'apikey': self.api_key,
            'Authorization': f'Bearer {self.api_key}',
        }

    def _open(self, name, mode='rb'):
        # Gunakan service role untuk baca file
        resp = requests.get(
            f'{self.base_url}/{name}',
            headers=self.headers,
        )
        resp.raise_for_status()
        return File(io.BytesIO(resp.content), name)

    def _save(self, name, content):
        ext = os.path.splitext(name)[1].lower()
        content_type = CONTENT_TYPES.get(ext, 'application/octet-stream')
        resp = requests.post(
            f'{self.base_url}/{name}',
            headers={**self.headers, 'Content-Type': content_type},
            data=content.read(),
        )
        resp.raise_for_status()
        return name

    def exists(self, name):
        resp = requests.head(
            f'{self.base_url}/{name}',
            headers=self.headers,
        )
        return resp.status_code == 200

    def url(self, name):
        # URL publik untuk diakses oleh user (gambar, dll)
        # File harus diakses via public URL untuk ditampilkan di browser
        return f'{self.public_url}/{name}'

    def delete(self, name):
        resp = requests.delete(
            f'{self.base_url}/{name}',
            headers=self.headers,
        )
        resp.raise_for_status()

    def listdir(self, path=''):
        # Disabled: prevents clients from listing all files in bucket (security)
        return [], []

    def size(self, name):
        resp = requests.head(
            f'{self.base_url}/{name}',
            headers=self.headers,
        )
        return int(resp.headers.get('Content-Length', 0))
