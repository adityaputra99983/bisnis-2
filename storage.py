import os
import io
import requests
from urllib.parse import urljoin
from django.core.files.base import File
from django.core.files.storage import Storage
from django.conf import settings


class SupabaseStorage(Storage):
    def __init__(self):
        self.project_url = 'https://vwjxhfpvcaesrfcglgex.supabase.co'
        self.api_key = os.environ.get('SUPABASE_SERVICE_KEY')
        self.bucket = os.environ.get('SUPABASE_S3_BUCKET', 'media')
        self.base_url = f'{self.project_url}/storage/v1/object/public/{self.bucket}'
        self.headers = {
            'apikey': self.api_key,
            'Authorization': f'Bearer {self.api_key}',
        }

    def _open(self, name, mode='rb'):
        resp = requests.get(f'{self.project_url}/storage/v1/object/public/{self.bucket}/{name}')
        resp.raise_for_status()
        return File(io.BytesIO(resp.content), name)

    def _save(self, name, content):
        resp = requests.post(
            f'{self.project_url}/storage/v1/object/{self.bucket}/{name}',
            headers=self.headers,
            data=content.read(),
        )
        resp.raise_for_status()
        return name

    def exists(self, name):
        resp = requests.head(f'{self.base_url}/{name}')
        return resp.status_code == 200

    def url(self, name):
        return f'{self.base_url}/{name}'

    def delete(self, name):
        requests.delete(
            f'{self.project_url}/storage/v1/object/{self.bucket}/{name}',
            headers=self.headers,
        )

    def listdir(self, path=''):
        resp = requests.get(
            f'{self.project_url}/storage/v1/object/list/{self.bucket}',
            headers={**self.headers, 'Content-Type': 'application/json'},
            json={'prefix': path, 'limit': 100},
        )
        if resp.status_code == 200:
            items = resp.json()
            dirs = list(set(i['name'].split('/')[0] for i in items if '/' in i['name']))
            files = [i['name'] for i in items if '/' not in i['name']]
            return dirs, files
        return [], []

    def size(self, name):
        resp = requests.head(f'{self.base_url}/{name}')
        return int(resp.headers.get('Content-Length', 0))
