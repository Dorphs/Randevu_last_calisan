# Deployment Kılavuzu

## İçindekiler
1. [Sistem Gereksinimleri](#sistem-gereksinimleri)
2. [Kurulum](#kurulum)
3. [Konfigürasyon](#konfigürasyon)
4. [Güvenlik](#güvenlik)
5. [Monitoring](#monitoring)
6. [Bakım](#bakım)

## Sistem Gereksinimleri

### Minimum Donanım
- CPU: 2 çekirdek
- RAM: 4GB
- Disk: 20GB SSD

### Önerilen Donanım
- CPU: 4 çekirdek
- RAM: 8GB
- Disk: 50GB SSD

### Yazılım Gereksinimleri
- Ubuntu 20.04 LTS veya üzeri
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Nginx 1.18+
- Supervisor

## Kurulum

### 1. Sistem Paketleri

```bash
# Sistem paketlerini güncelle
sudo apt update
sudo apt upgrade -y

# Gerekli paketleri yükle
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib redis-server nginx supervisor
```

### 2. PostgreSQL Kurulumu

```bash
# PostgreSQL kullanıcısı oluştur
sudo -u postgres createuser --interactive

# Veritabanı oluştur
sudo -u postgres createdb meetings
```

### 3. Python Ortamı

```bash
# Proje dizinine git
cd /opt/meetings

# Sanal ortam oluştur
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 4. Uygulama Kurulumu

```bash
# Statik dosyaları topla
python manage.py collectstatic

# Veritabanı migration'larını uygula
python manage.py migrate

# Superuser oluştur
python manage.py createsuperuser
```

## Konfigürasyon

### 1. Environment Değişkenleri

`.env` dosyası oluşturun:

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
SECRET_KEY=your-secret-key

# Database
DB_NAME=meetings
DB_USER=dbuser
DB_PASSWORD=dbpass
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/1

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 2. Nginx Konfigürasyonu

`/etc/nginx/sites-available/meetings`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /opt/meetings;
    }

    location /media/ {
        root /opt/meetings;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

### 3. Gunicorn Konfigürasyonu

`/etc/supervisor/conf.d/meetings.conf`:

```ini
[program:meetings]
directory=/opt/meetings
command=/opt/meetings/venv/bin/gunicorn --workers 3 --bind unix:/run/gunicorn.sock meetings.wsgi:application
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/meetings/gunicorn.err.log
stdout_logfile=/var/log/meetings/gunicorn.out.log
```

### 4. Redis Konfigürasyonu

`/etc/redis/redis.conf`:

```conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```

## Güvenlik

### 1. SSL Sertifikası

Let's Encrypt ile SSL kurulumu:

```bash
# Certbot yükle
sudo apt install certbot python3-certbot-nginx

# SSL sertifikası al
sudo certbot --nginx -d yourdomain.com
```

### 2. Firewall Ayarları

```bash
# UFW aktifleştir
sudo ufw enable

# Gerekli portları aç
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
```

### 3. Security Headers

Nginx konfigürasyonuna ekleyin:

```nginx
add_header X-Frame-Options "SAMEORIGIN";
add_header X-XSS-Protection "1; mode=block";
add_header X-Content-Type-Options "nosniff";
add_header Strict-Transport-Security "max-age=31536000";
```

## Monitoring

### 1. Sentry Entegrasyonu

`settings.py`:

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

### 2. Prometheus & Grafana

```bash
# Prometheus yükle
sudo apt install -y prometheus

# Grafana yükle
sudo apt install -y grafana
```

### 3. Log Yönetimi

```bash
# Log rotasyonu ayarla
sudo nano /etc/logrotate.d/meetings

/var/log/meetings/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        supervisorctl restart meetings
    endscript
}
```

## Bakım

### 1. Yedekleme

Otomatik yedekleme script'i:

```bash
#!/bin/bash

# Veritabanı yedeği
pg_dump meetings > /backup/db/meetings_$(date +%Y%m%d).sql

# Media dosyaları yedeği
tar -czf /backup/media/media_$(date +%Y%m%d).tar.gz /opt/meetings/media/

# Eski yedekleri temizle
find /backup/db/ -mtime +30 -delete
find /backup/media/ -mtime +30 -delete
```

### 2. Güncelleme Prosedürü

```bash
# Maintenance modu aktifleştir
python manage.py maintenance_mode on

# Kod güncelle
git pull origin main

# Bağımlılıkları güncelle
pip install -r requirements.txt

# Migration'ları uygula
python manage.py migrate

# Statik dosyaları güncelle
python manage.py collectstatic --noinput

# Servisleri yeniden başlat
sudo supervisorctl restart meetings

# Maintenance modu deaktif et
python manage.py maintenance_mode off
```

### 3. Performans İzleme

```bash
# CPU ve Memory kullanımı
htop

# Disk kullanımı
df -h

# Nginx erişim logları
tail -f /var/log/nginx/access.log

# Uygulama logları
tail -f /var/log/meetings/gunicorn.out.log
```
