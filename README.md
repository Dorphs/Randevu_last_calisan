# Toplantı Yönetim Sistemi

Bu proje, organizasyonlar için kapsamlı bir toplantı ve randevu yönetim sistemidir. Django REST Framework kullanılarak geliştirilmiştir.

## Özellikler

### 1. Temel Özellikler
- Toplantı oluşturma, düzenleme ve silme
- Ziyaretçi yönetimi
- Toplantı odası yönetimi
- Toplantı notu tutma
- Durum takibi (Beklemede, Onaylandı, Reddedildi, İptal, Tamamlandı)

### 2. API ve Dokümantasyon
- RESTful API endpoints
- Swagger/OpenAPI entegrasyonu
- API versiyonlama
- Detaylı API dokümantasyonu

### 3. Arama ve Filtreleme
- Gelişmiş arama özellikleri
- Çoklu filtreleme seçenekleri
- Tarih aralığı filtreleme
- Sıralama seçenekleri

### 4. Hata Yönetimi
- Özel exception sınıfları
- Global exception handler
- Detaylı hata loglama
- Kullanıcı dostu hata mesajları

### 5. Bulk İşlemler
- Toplu toplantı oluşturma
- Excel import/export
- Toplu ziyaretçi yönetimi
- Batch processing

### 6. Raporlama Sistemi
- PDF rapor oluşturma
- Excel raporları
- Özelleştirilebilir raporlar
- İstatistik raporları

### 7. Test Altyapısı
- Unit testler
- API testleri
- Test coverage raporlaması
- Integration testler

### 8. Monitoring Sistemi
- Request süresi takibi
- Yavaş sorgu tespiti
- Prometheus metrikler
- Performans izleme

### 9. Bildirim Sistemi
- Email bildirimleri
- SMS bildirimleri (Twilio)
- Push notifications (iOS/Android)
- Bildirim şablonları

### 10. Mobil API Desteği
- Özel mobil endpointler
- Push notification yönetimi
- Offline sync desteği
- Device yönetimi

## Son Eklenen Özellikler 🎉

### 1. Dashboard Sistemi
- Özelleştirilebilir dashboard'lar
- Sürükle-bırak widget yerleşimi
- Gerçek zamanlı veri güncelleme
- Excel ve PDF export

### 2. Raporlama Sistemi
- Özelleştirilebilir raporlar
- Zamanlanmış raporlar
- Email bildirimleri
- Veri görselleştirme

### 3. Performans İyileştirmeleri
- Redis önbellekleme
- Widget optimizasyonu
- API rate limiting
- Query optimizasyonları

## Teknolojiler

- **Backend**: Django, Django REST Framework
- **Veritabanı**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **Dokümantasyon**: Swagger/OpenAPI
- **Monitoring**: Prometheus
- **Testing**: Pytest
- **Bildirimler**: SMTP, Twilio, Firebase

## API Endpoints

### Toplantı Endpoints
- `GET /api/meetings/`: Toplantı listesi
- `POST /api/meetings/`: Yeni toplantı oluştur
- `GET /api/meetings/{id}/`: Toplantı detayı
- `PUT /api/meetings/{id}/`: Toplantı güncelle
- `DELETE /api/meetings/{id}/`: Toplantı sil
- `GET /api/meetings/today/`: Bugünkü toplantılar
- `GET /api/meetings/upcoming/`: Yaklaşan toplantılar
- `GET /api/meetings/statistics/`: Toplantı istatistikleri

### Ziyaretçi Endpoints
- `GET /api/visitors/`: Ziyaretçi listesi
- `POST /api/visitors/`: Yeni ziyaretçi ekle
- `GET /api/visitors/{id}/`: Ziyaretçi detayı
- `GET /api/visitors/statistics/`: Ziyaretçi istatistikleri

### Mobil API Endpoints
- `GET /api/v1/mobile/meetings/upcoming/`: Yaklaşan toplantılar
- `GET /api/v1/mobile/meetings/today/`: Bugünkü toplantılar
- `POST /api/v1/mobile/meetings/register_device/`: Cihaz kaydı
- `GET /api/v1/mobile/meetings/calendar_view/`: Aylık takvim görünümü
  ```json
  {
    "year": "2025",
    "month": "1"
  }
  ```
- `GET /api/v1/mobile/meetings/week_view/`: Haftalık görünüm
  ```json
  {
    "date": "2025-01-30"  // Hafta başlangıç tarihi
  }
  ```
- `POST /api/v1/mobile/meetings/{id}/reschedule/`: Toplantı yeniden planlama
  ```json
  {
    "new_start_time": "2025-02-01T10:00:00Z",
    "new_end_time": "2025-02-01T11:00:00Z"
  }
  ```
- `GET /api/v1/mobile/meetings/search/`: Toplantılarda arama
  ```json
  {
    "q": "arama terimi"  // Başlık, açıklama, ziyaretçi veya lokasyonda arar
  }
  ```
- `GET /api/v1/mobile/meetings/offline_sync/`: Offline senkronizasyon
  ```json
  {
    "last_sync": "2025-01-30T20:25:00Z"  // Son senkronizasyon zamanı
  }
  ```
- `POST /api/v1/mobile/meetings/bulk_status_update/`: Toplu durum güncelleme
  ```json
  {
    "updates": [
      {
        "id": 1,
        "status": "COMPLETED"
      },
      {
        "id": 2,
        "status": "CANCELLED"
      }
    ]
  }
  ```

### Raporlama Endpoints
- `GET /api/meetings/report_pdf/`: PDF rapor oluştur
- `GET /api/meetings/export_excel/`: Excel export
- `POST /api/meetings/import_excel/`: Excel import

## Kurulum

1. Sanal ortam oluştur ve aktive et:
```bash
python -m venv venv
.\venv\Scripts\activate
```

2. Bağımlılıkları yükle:
```bash
pip install -r requirements.txt
```

3. Veritabanı migrasyonlarını uygula:
```bash
python manage.py migrate
```

4. Örnek verileri yükle:
```bash
python manage.py create_sample_data
```

5. Sunucuyu başlat:
```bash
python manage.py runserver
```

## Test

```bash
# Tüm testleri çalıştır
pytest

# Coverage raporu oluştur
pytest --cov=meetings --cov-report=html
```

## API Dokümantasyonu

- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## Monitoring

- Prometheus Metrics: http://localhost:8000/metrics
- Hata Logları: logs/error.log

## Notlar

- Email bildirimleri için SMTP ayarlarını yapılandırın
- SMS bildirimleri için Twilio hesabı oluşturun
- Push notifications için Firebase/APNS sertifikalarını ekleyin
- Redis kurulumu için admin yetkileri gereklidir

## Mobil Uygulama Özellikleri

### 1. Takvim ve Görünümler
- Aylık takvim görünümü
- Haftalık detaylı görünüm
- Günlük toplantı listesi
- Yaklaşan toplantılar widget'ı

### 2. Offline Çalışma
- Offline veri senkronizasyonu
- Çevrimdışı toplantı oluşturma
- Otomatik senkronizasyon
- Çakışma çözümleme

### 3. Bildirimler
- Push notification desteği
- Özelleştirilebilir bildirim tercihleri
- Toplantı hatırlatmaları
- Durum değişikliği bildirimleri

### 4. Arama ve Filtreleme
- Tam metin arama
- Gelişmiş filtreleme seçenekleri
- Tarih bazlı filtreleme
- Etiket bazlı arama

### 5. Toplantı Yönetimi
- Hızlı toplantı oluşturma
- Toplantı yeniden planlama
- Toplu durum güncelleme
- Katılımcı yönetimi

### 6. Optimizasyonlar
- Lazy loading
- Response caching
- Batch işlemler
- Görsel optimizasyonu

## Yapılan İşler

### 1. Temel Özellikler 
- Toplantı CRUD işlemleri
- Ziyaretçi yönetimi
- Toplantı odası yönetimi
- Toplantı notu tutma
- Durum takibi

### 2. API ve Dokümantasyon 
- RESTful API endpoints
- Swagger/OpenAPI entegrasyonu
- API versiyonlama
- Detaylı API dokümantasyonu

### 3. Güvenlik İyileştirmeleri 
- JWT authentication
- Rate limiting
- Input validation
- Error handling
- Logging ve monitoring

### 4. Bildirim Sistemi 
- Email bildirimleri
- SMS bildirimleri (Twilio)
- Push notifications (iOS/Android)
- Bildirim şablonları

### 5. Mobil Özellikler 
- Offline sync
- Push notifications
- Takvim görünümü
- Mobil-specific API'ler

### 6. Gelişmiş Özellikler 
- Tekrarlanan toplantılar
- Toplantı şablonları
- Dosya eki sistemi
- Takvim entegrasyonları

### 7. Dokümantasyon 
- API kullanım kılavuzu
- Mobil entegrasyon rehberi
- Troubleshooting rehberi
- Örnek kodlar

## Yapılabilecek İşler

### 1. AI Entegrasyonu 
- Toplantı özetleme
- Otomatik not çıkarma
- Konuşma tanıma
- Akıllı toplantı önerileri
- Sentiment analizi

### 2. Video Konferans 
- Zoom entegrasyonu
- Google Meet entegrasyonu
- Microsoft Teams entegrasyonu
- Toplantı kaydı
- Ekran paylaşımı

### 3. İleri Analitik 
- Toplantı verimliliği analizi
- Katılımcı analizi
- Maliyet takibi
- Tahminleme ve öneriler
- Dashboard'lar

### 4. Otomasyon 
- Otomatik toplantı planlaması
- Akıllı oda önerisi
- Email yanıtlama botları
- Workflow otomasyonu
- Hatırlatıcı botları

### 5. Gelişmiş Entegrasyonlar 
- Slack entegrasyonu
- Jira entegrasyonu
- CRM sistemleri
- ERP sistemleri
- HR sistemleri

### 6. Lokalizasyon ve Özelleştirme 
- Çoklu dil desteği
- Zaman dilimi yönetimi
- Özelleştirilebilir temalar
- Şirket bazlı özelleştirmeler
- Rol bazlı özelleştirmeler

### 7. Blockchain Entegrasyonu 
- Toplantı doğrulama
- Akıllı kontratlar
- NFT tabanlı toplantı tokenları
- Merkezi olmayan kimlik doğrulama
- Blockchain tabanlı oylama

### 8. AR/VR Desteği 
- Sanal toplantı odaları
- AR tabanlı yön bulma
- VR toplantı deneyimi
- 3D ofis turu
- Holografik görüşmeler

### 9. IoT Entegrasyonu 
- Akıllı oda sensörleri
- Otomatik ışık kontrolü
- Sıcaklık ve havalandırma kontrolü
- Hareket sensörleri
- QR kod ile oda check-in

### 10. Gelişmiş Güvenlik 
- Biyometrik doğrulama
- İki faktörlü doğrulama
- Uçtan uca şifreleme
- GDPR uyumluluğu
- Güvenlik denetimi

## Teknik Detaylar

### Sistem Gereksinimleri
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Node.js 14+ (Frontend için)

### Kurulum
```bash
# Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt

# Veritabanını hazırla
python manage.py migrate

# Sunucuyu başlat
python manage.py runserver
```

### API Dokümantasyonu
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

### Monitoring
- Prometheus Metrics: http://localhost:8000/metrics
- Grafana Dashboard: http://localhost:3000

## Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun
3. Değişikliklerinizi commit'leyin
4. Branch'inizi push'layın
5. Pull Request açın

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## İletişim

- Email: support@example.com
- Website: https://example.com
- Twitter: @example
- LinkedIn: /company/example

## Teknik Detaylar 
### Sistem Gereksinimleri

#### Backend
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Celery 5+
- RabbitMQ 3.8+
- Nginx 1.18+

#### Frontend
- Node.js 14+
- React 18+
- TypeScript 4.5+
- Webpack 5+

#### Mobile
- iOS 13+
- Android API Level 26+ (Android 8.0)
- React Native 0.70+

#### DevOps
- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.22+
- Helm 3+

### Kurulum Adımları

#### 1. Backend Kurulumu
```bash
# Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt

# Ortam değişkenlerini ayarla
cp .env.example .env
# .env dosyasını düzenle

# Veritabanını hazırla
python manage.py migrate
python manage.py createsuperuser

# Test verilerini yükle (opsiyonel)
python manage.py loaddata initial_data.json

# Sunucuyu başlat
python manage.py runserver
```

#### 2. Frontend Kurulumu
```bash
# Node.js bağımlılıklarını yükle
cd frontend
npm install

# Geliştirme sunucusunu başlat
npm run dev

# Üretime hazır build al
npm run build
```

#### 3. Docker ile Kurulum
```bash
# Docker imajlarını oluştur
docker-compose build

# Servisleri başlat
docker-compose up -d

# Veritabanı migrasyonlarını uygula
docker-compose exec backend python manage.py migrate
```

### Veritabanı Şeması

#### Ana Tablolar
- `meetings_meeting`: Toplantı kayıtları
- `meetings_visitor`: Ziyaretçi bilgileri
- `meetings_room`: Toplantı odaları
- `meetings_note`: Toplantı notları
- `meetings_attachment`: Dosya ekleri

#### İlişki Tabloları
- `meetings_meeting_participants`: Toplantı katılımcıları
- `meetings_room_features`: Oda özellikleri
- `meetings_meeting_tags`: Toplantı etiketleri

### API Endpoints

#### Authentication
```http
POST /api/token/ - JWT token al
POST /api/token/refresh/ - Token yenile
POST /api/token/verify/ - Token doğrula
```

#### Toplantı İşlemleri
```http
GET /api/meetings/ - Toplantı listesi
POST /api/meetings/ - Yeni toplantı oluştur
GET /api/meetings/{id}/ - Toplantı detayı
PUT /api/meetings/{id}/ - Toplantı güncelle
DELETE /api/meetings/{id}/ - Toplantı sil
```

#### Ziyaretçi İşlemleri
```http
GET /api/visitors/ - Ziyaretçi listesi
POST /api/visitors/ - Yeni ziyaretçi ekle
GET /api/visitors/{id}/ - Ziyaretçi detayı
```

### Güvenlik Ayarları

#### JWT Konfigürasyonu
```python
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': timedelta(hours=1),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
}
```

#### CORS Ayarları
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://example.com",
]
```

#### Rate Limiting
```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}
```

### Monitoring ve Logging

#### Prometheus Metrics
- `http_requests_total`: Toplam istek sayısı
- `http_request_duration_seconds`: İstek süreleri
- `db_query_duration_seconds`: Veritabanı sorgu süreleri
- `api_error_total`: API hata sayısı

#### Log Formatı
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/debug.log',
            'formatter': 'verbose',
        },
    },
}
```

### Performans Optimizasyonları

#### Caching
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

#### Database Optimizasyonları
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'meetings_db',
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'statement_timeout': 3000,
        }
    }
}
```

### CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Tests
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          python manage.py test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Production
        if: github.ref == 'refs/heads/main'
        run: |
          # Deployment steps
```

### Geliştirme Ortamı

#### VS Code Ayarları
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "editor.formatOnSave": true,
    "python.formatting.provider": "black"
}
```

#### Git Hooks
```bash
#!/bin/sh
# pre-commit hook
python manage.py test
black .
pylint meetings/
```

### Troubleshooting

#### Yaygın Hatalar ve Çözümleri
1. Database bağlantı hatası
   ```bash
   # PostgreSQL servisini kontrol et
   sudo service postgresql status
   
   # Log dosyalarını kontrol et
   tail -f /var/log/postgresql/postgresql-12-main.log
   ```

2. Redis bağlantı hatası
   ```bash
   # Redis servisini kontrol et
   redis-cli ping
   
   # Redis loglarını kontrol et
   tail -f /var/log/redis/redis-server.log
   ```

3. Celery worker hatası
   ```bash
   # Celery worker'ı yeniden başlat
   celery -A project worker -l info
   
   # RabbitMQ durumunu kontrol et
   rabbitmqctl status
   ```

### Yedekleme ve Recovery

#### Database Yedekleme
```bash
# Tam yedek al
pg_dump meetings_db > backup.sql

# Sadece şema yedekle
pg_dump -s meetings_db > schema.sql

# Sadece veri yedekle
pg_dump -a meetings_db > data.sql
```

#### Media Dosyaları Yedekleme
```bash
# rsync ile yedekle
rsync -avz media/ backup/media/

# AWS S3'e yedekle
aws s3 sync media/ s3://bucket-name/media/
```

### Ölçeklendirme

#### Horizontal Scaling
- Load Balancer konfigürasyonu
- Session yönetimi
- Caching stratejisi
- Database replication

#### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: meetings-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: meetings
  template:
    metadata:
      labels:
        app: meetings
    spec:
      containers:
      - name: meetings
        image: meetings:latest
        ports:
        - containerPort: 8000

```
