# Deploy Bali Healer

## Persiapan Umum

```bash
cd dukun

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env → isi DJANGO_SECRET_KEY yang aman

# Database
python manage.py migrate
python manage.py seed_data          # (opsional) isi sample data

# Static files
python manage.py collectstatic --noinput

# Buat superuser
python manage.py createsuperuser
```

---

## 1. Render (Gratis & Recommended)

1. Push ke GitHub/GitLab
2. Buka https://render.com → New → Web Service
3. Hubungkan repo
4. Settings:
   - **Build Command:** `cd dukun && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput`
   - **Start Command:** `cd dukun && gunicorn dukun.wsgi:application --bind 0.0.0.0:$PORT`
5. Environment Variables:
   ```
   DJANGO_SECRET_KEY = (klik Generate)
   DJANGO_DEBUG = False
   DJANGO_ALLOWED_HOSTS = your-app.onrender.com
   PYTHON_VERSION = 3.12.6
   ```
6. Deploy → Selesai

---

## 2. Railway

1. Push ke GitHub
2. Buka https://railway.app → New Project → Deploy from GitHub
3. Railway otomatis detect Python
4. Environment Variables:
   ```
   DJANGO_SECRET_KEY = (Generate)
   DJANGO_DEBUG = False
   DJANGO_ALLOWED_HOSTS = your-app.up.railway.app
   ```
5. Railway otomatis run migration
6. Selesai

---

## 3. Heroku

```bash
# Install Heroku CLI, lalu:
heroku create nama-app
heroku config:set DJANGO_SECRET_KEY="your-key" DJANGO_DEBUG=False DJANGO_ALLOWED_HOSTS="nama-app.herokuapp.com"
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py seed_data
heroku run python manage.py createsuperuser
```

---

## 4. Vercel

### Persiapan

1. Buat akun di [vercel.com](https://vercel.com)
2. Push project ke GitHub/GitLab/Bitbucket

### Deploy via Dashboard (Cara termudah)

1. Buka https://vercel.com/new
2. Import repository → Pilih repo yang sudah di-push
3. **Root Directory:** `dukun` (folder yang berisi `manage.py`)
4. **Framework Preset:** Other
5. **Build Command:** (biarkan kosong — otomatis baca `vercel.json`)
6. **Output Directory:** (biarkan kosong)
7. Di bagian **Environment Variables**, tambah INI WAJIB:
   ```
   DJANGO_SECRET_KEY = <isi string random 50+ karakter>
   DJANGO_DEBUG = False
   DJANGO_ALLOWED_HOSTS = .vercel.app
   DJANGO_SETTINGS_MODULE = dukun.settings
   ```
   Jika pakai PostgreSQL (recommended):
   ```
   DATABASE_URL = postgresql://user:pass@host:5432/dbname
   ```
8. Klik **Deploy** → tunggu selesai

### Jika Build Gagal — Perbaiki di Dashboard Vercel

Buka Project → **Settings** → **Build & Development Settings** → override:
- **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput --clear`
- **Output Directory:** *(kosongkan)*

### Debug Jika Error 500

1. Buka Vercel Dashboard → tab **Functions** → klik `api/index.py`
2. Pilih **Runtime Logs** → lihat error terakhir
3. Error umum:
   - `ModuleNotFoundError: No module named 'dukun.settings'` → Set `DJANGO_SETTINGS_MODULE` di env vars
   - `DisallowedHost` → Set `DJANGO_ALLOWED_HOSTS=.vercel.app`
   - `cannot open db.sqlite3` → SQLite tidak persisten di Vercel. Pakai PostgreSQL.

### ⚠️ Catatan Penting

| Masalah | Solusi |
|---|---|
| **SQLite hilang saat redeploy** | Gunakan PostgreSQL gratis di [Supabase](https://supabase.com) atau [Neon](https://neon.tech). Set `DATABASE_URL` di env vars. |
| **Upload foto tidak muncul** | Vercel tidak menyimpan file upload. Nanti perlu Cloudinary/AWS S3. |
| **Error 500 terus** | Cek logs di Vercel Dashboard → Functions → Runtime Logs |
| **Tampilan berantakan (CSS/js tidak load)** | Pastikan `collectstatic` berhasil dan WhiteNoise aktif (cek middleware) |

### Struktur file untuk Vercel

```
dukun/                         ← Root directory di Vercel
├── vercel.json                ← Config build, routes, serverless
├── .vercelignore              ← File yang di-exclude saat deploy
├── runtime.txt                ← Versi Python
├── api/
│   └── index.py               ← Entry point serverless Django
├── requirements.txt
├── manage.py
├── dukun/
│   ├── settings.py
│   ├── wsgi.py
│   └── urls.py
├── static/
├── templates/
├── locale/
└── staticfiles/               ↑ Auto-generated saat build
```

Jika database PostgreSQL belum disiapkan, aplikasi akan jalan dengan SQLite sementara (data akan hilang saat redeploy).

### ⚠️ Catatan Penting

| Masalah | Solusi |
|---|---|
| **SQLite hilang saat redeploy** | Gunakan PostgreSQL — daftar gratis di [Supabase](https://supabase.com) atau [Neon](https://neon.tech). Set `DATABASE_URL` di environment variables. |
| **Upload foto tidak muncul** | Vercel tidak menyimpan file upload. Nanti perlu Cloudinary/AWS S3. |
| **Error 500** | Cek logs di Vercel Dashboard → Functions → `api/index.py` → Runtime Logs |
| **Tampilan berantakan** | Pastikan `DJANGO_DEBUG=False` dan sudah `collectstatic` berhasil |

### Struktur file untuk Vercel

```
dukun/                         ← Root directory di Vercel
├── vercel.json                ← Config build, routes, serverless
├── .vercelignore              ← File yang di-exclude
├── api/
│   └── index.py               ← Entry point serverless Django
├── requirements.txt
├── manage.py
├── dukun/
│   ├── settings.py
│   ├── wsgi.py
│   └── urls.py
├── static/
├── templates/
├── locale/
└── staticfiles/               ← Auto-generated saat build
```

---

## 5. Hostinger (Python Hosting)

### Via hPanel:
1. Login ke Hostinger → hPanel
2. Hosting → Python → Create Application
3. Set **App Root:** `dukun`
4. Set **App Entry File:** `passenger_wsgi.py`
5. Set **Python Version:** 3.12 (atau terbaru)
6. Upload semua file project ke server (via File Manager atau FTP)
7. Buka Terminal di hPanel → jalankan:
   ```bash
   cd dukun
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py seed_data
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```

### Via Terminal (SSH):
```bash
cd ~/public_html/dukun
pip install -r requirements.txt
DJANGO_SECRET_KEY="your-key" DJANGO_DEBUG=False DJANGO_ALLOWED_HOSTS="yourdomain.com" python manage.py migrate
python manage.py collectstatic --noinput
```

---

## 6. VPS / DigitalOcean / AWS EC2

```bash
# Install Python & pip
sudo apt update && sudo apt install python3-pip python3-venv nginx -y

# Clone repo
git clone your-repo-url
cd progres-2/dukun

# Virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup
cp .env.example .env
# Edit .env → isi DJANGO_SECRET_KEY, DJANGO_DEBUG=False, DJANGO_ALLOWED_HOSTS

python manage.py migrate
python manage.py seed_data
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Jalankan dengan Gunicorn
gunicorn dukun.wsgi:application --bind 127.0.0.1:8000

# Buat systemd service (/etc/systemd/system/dukun.service):
# [Unit]
# Description=Bali Healer Django App
# After=network.target
# [Service]
# User=www-data
# WorkingDirectory=/path/to/progres-2/dukun
# ExecStart=/path/to/venv/bin/gunicorn dukun.wsgi:application --bind 127.0.0.1:8000
# [Install]
# WantedBy=multi-user.target

# Enable & start
sudo systemctl enable dukun
sudo systemctl start dukun

# Nginx config (add to /etc/nginx/sites-available/default):
# server {
#     listen 80;
#     server_name yourdomain.com;
#
#     location /static/ {
#         alias /path/to/progres-2/dukun/staticfiles/;
#     }
#     location /media/ {
#         alias /path/to/progres-2/dukun/media/;
#     }
#     location / {
#         proxy_pass http://127.0.0.1:8000;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#     }
# }

sudo nginx -t && sudo systemctl reload nginx
```

---

## 7. Hostinger VPS (CyberPanel / HestiaCP)

Sama seperti VPS di atas, tapi panel hosting biasanya sudah setup Nginx/Apache. Upload files via File Manager, lalu jalankan perintah di terminal.

---

## Environment Variables

| Variable | Default | Keterangan |
|---|---|---|
| `DJANGO_SECRET_KEY` | (insecure dev key) | **WAJIB diisi untuk production** |
| `DJANGO_DEBUG` | `True` | Set `False` untuk production |
| `DJANGO_ALLOWED_HOSTS` | `*` | Domain yang diizinkan, pisahkan koma |
| `DATABASE_URL` | (SQLite) | Format: `postgresql://user:pass@host:5432/db` |

---

## Checklist Setelah Deploy

1. Buka URL → Splash screen muncul → tampilan sama persis
2. Login `/login/` → Dashboard muncul
3. Ganti bahasa → URL berubah prefix bahasa
4. Ganti mata uang → Harga berubah
5. Cari healer → Cards muncul dengan benar
6. Upload foto profil → Berhasil
7. Buka `/admin/` → Admin panel bisa diakses
