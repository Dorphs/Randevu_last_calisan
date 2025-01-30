# Geliştirici Kılavuzu

## İçindekiler
1. [Proje Yapısı](#proje-yapısı)
2. [Kurulum](#kurulum)
3. [Geliştirme Ortamı](#geliştirme-ortamı)
4. [API Mimarisi](#api-mimarisi)
5. [Servisler](#servisler)
6. [Önbellekleme](#önbellekleme)
7. [Test](#test)

## Proje Yapısı

```
meetings/
├── api/
│   ├── permissions.py    # Özel izin sınıfları
│   ├── serializers/      # API serializer'ları
│   ├── throttling.py     # Rate limiting ayarları
│   ├── urls.py          # API URL tanımlamaları
│   └── views/           # API view'ları
├── models/
│   ├── meetings.py      # Toplantı modelleri
│   ├── reports.py       # Rapor ve dashboard modelleri
│   ├── user_roles.py    # Kullanıcı ve rol modelleri
│   └── visitors.py      # Ziyaretçi modelleri
├── services/
│   ├── cache.py         # Önbellekleme servisi
│   ├── dashboard.py     # Dashboard işlemleri
│   ├── export.py        # Dışa aktarma servisi
│   ├── email.py         # Email servisi
│   └── report.py        # Rapor servisi
├── templates/
│   ├── dashboard/       # Dashboard şablonları
│   └── emails/          # Email şablonları
├── static/
│   ├── css/            # Stil dosyaları
│   └── js/             # JavaScript dosyaları
└── tests/
    ├── unit/           # Birim testler
    └── integration/    # Entegrasyon testleri
```

## Kurulum

### Gereksinimler

- Python 3.8+
- PostgreSQL 12+
- Redis 6+

### Adımlar

1. Sanal ortam oluşturun:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

3. Veritabanını oluşturun:
```bash
python manage.py migrate
```

4. Geliştirme sunucusunu başlatın:
```bash
python manage.py runserver
```

## Geliştirme Ortamı

### IDE Ayarları

VS Code için önerilen ayarlar:

```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

### Git Hooks

Pre-commit hook'ları:

```bash
pre-commit install
```

## API Mimarisi

### RESTful Endpoints

- `/api/dashboards/`: Dashboard CRUD işlemleri
- `/api/widgets/`: Widget yönetimi
- `/api/reports/`: Rapor işlemleri

### Yetkilendirme

- JWT tabanlı kimlik doğrulama
- Role-based access control (RBAC)
- Custom permission sınıfları

### Rate Limiting

- Dashboard işlemleri: 100/saat
- Widget işlemleri: 300/saat
- Export işlemleri: 20/saat

## Servisler

### DashboardService

```python
class DashboardService:
    def refresh_widget(widget_id)
    def update_widget_position(widget_id, position)
    def share_dashboard(dashboard_id, user_ids)
```

### ExportService

```python
class ExportService:
    def export_to_excel(data)
    def export_to_pdf(data)
```

### CacheService

```python
class CacheService:
    def get_cache_key(prefix, id, params={})
    def invalidate_widget_cache(widget_id)
```

## Önbellekleme

### Cache Stratejisi

1. Widget Verisi
   - Key format: `widget_{id}_{type}`
   - TTL: 5 dakika
   - Invalidation: Veri değişikliğinde

2. Dashboard Verisi
   - Key format: `dashboard_{id}`
   - TTL: 15 dakika
   - Invalidation: Widget güncellemelerinde

### Redis Ayarları

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## Test

### Unit Testler

```bash
python manage.py test meetings.tests.unit
```

### Entegrasyon Testleri

```bash
python manage.py test meetings.tests.integration
```

### Coverage Raporu

```bash
coverage run manage.py test
coverage report
coverage html  # Detaylı HTML raporu
```

## En İyi Uygulamalar

1. **Kod Stili**
   - PEP 8 kurallarına uyun
   - Type hints kullanın
   - Docstring ekleyin

2. **Performans**
   - N+1 sorgularından kaçının
   - Uygun index'ler kullanın
   - Önbellekleme stratejisini optimize edin

3. **Güvenlik**
   - SQL injection'dan korunun
   - XSS kontrolü yapın
   - CSRF token kullanın

4. **Hata Yönetimi**
   - Custom exception sınıfları kullanın
   - Hataları loglayın
   - Kullanıcı dostu hata mesajları döndürün
