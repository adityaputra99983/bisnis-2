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

1. Push ke GitHub
2. Buka https://vercel.com → New Project → Import
3. Framework: Other
4. Root Directory: `dukun`
5. Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput`
6. Output Directory: `staticfiles`
7. Environment Variables:
   ```
   DJANGO_SECRET_KEY = (Generate)
   DJANGO_DEBUG = False
   DJANGO_ALLOWED_HOSTS = your-app.vercel.app
   ```

**Catatan:** Vercel menggunakan serverless functions. Database SQLite tidak cocok untuk Vercel — gunakan PostgreSQL via Supabase/Neon.

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
