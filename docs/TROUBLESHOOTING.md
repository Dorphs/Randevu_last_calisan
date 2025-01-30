# Troubleshooting Rehberi

## Genel Sorunlar ve Çözümleri

### 1. Authentication Sorunları

#### Token Geçersiz
```json
{
    "code": "token_invalid",
    "message": "Token geçersiz veya süresi dolmuş"
}
```

**Çözüm:**
1. Refresh token ile yeni token alın
2. Refresh token da geçersizse yeniden login olun
3. Sorun devam ederse:
   - Browser cache'i temizleyin
   - Çerezleri temizleyin
   - Local storage'ı temizleyin

#### Rate Limit Aşıldı
```json
{
    "code": "rate_limit_exceeded",
    "message": "Çok fazla istek gönderildi",
    "retry_after": 300
}
```

**Çözüm:**
1. `retry_after` süresini bekleyin
2. İstek sayısını azaltın
3. Caching mekanizması kullanın

### 2. Toplantı İşlemleri

#### Toplantı Çakışması
```json
{
    "code": "meeting_conflict",
    "message": "Toplantı çakışması tespit edildi",
    "conflict_details": {
        "existing_meeting": {
            "id": 1,
            "title": "Mevcut Toplantı",
            "start_time": "2025-02-01T10:00:00Z"
        }
    }
}
```

**Çözüm:**
1. Farklı bir zaman seçin
2. Farklı bir toplantı odası seçin
3. Mevcut toplantıyı düzenleyin

#### Katılımcı Müsait Değil
```json
{
    "code": "participant_unavailable",
    "message": "Katılımcı(lar) müsait değil",
    "unavailable_participants": [
        {
            "id": 1,
            "name": "John Doe",
            "conflict_meeting": {
                "id": 2,
                "title": "Diğer Toplantı"
            }
        }
    ]
}
```

**Çözüm:**
1. Farklı bir zaman seçin
2. Katılımcı listesini güncelleyin
3. Katılımcıların takvimlerini kontrol edin

### 3. Senkronizasyon Sorunları

#### Veri Çakışması
```json
{
    "code": "sync_conflict",
    "message": "Veri çakışması tespit edildi",
    "conflicts": [
        {
            "entity_id": 1,
            "entity_type": "meeting",
            "server_version": "2025-01-30T20:25:00Z",
            "local_version": "2025-01-30T20:24:00Z"
        }
    ]
}
```

**Çözüm:**
1. Çakışma çözümleme API'sini kullanın
2. Manuel olarak hangi versiyonu tutmak istediğinizi seçin
3. Gerekirse her iki versiyonu da kaydedin

#### Senkronizasyon Hatası
```json
{
    "code": "sync_failed",
    "message": "Senkronizasyon başarısız",
    "details": "Network error"
}
```

**Çözüm:**
1. İnternet bağlantısını kontrol edin
2. Offline modda çalışmaya devam edin
3. Bağlantı geldiğinde otomatik senkronizasyonu bekleyin

### 4. Performans Sorunları

#### Yavaş Yükleme
Semptomlar:
- Sayfa yüklenme süresi > 3 saniye
- API yanıt süresi > 1 saniye
- Tarayıcı CPU kullanımı yüksek

**Çözüm:**
1. Browser cache'i temizleyin
2. Gereksiz sekmeleri kapatın
3. Ağ bağlantısını kontrol edin
4. DevTools Network tab'ını kontrol edin

#### Bellek Kullanımı
Semptomlar:
- Uygulama yavaşlıyor
- Browser crash ediyor
- Sayfa yeniden yükleniyor

**Çözüm:**
1. Browser'ı yeniden başlatın
2. Cache'i temizleyin
3. Açık sekme sayısını azaltın
4. RAM kullanımını monitör edin

### 5. Takvim Entegrasyonu

#### Google Calendar Sync Hatası
```json
{
    "code": "calendar_sync_failed",
    "message": "Google Calendar senkronizasyonu başarısız",
    "details": "Invalid credentials"
}
```

**Çözüm:**
1. Google Calendar izinlerini kontrol edin
2. Yeniden yetkilendirme yapın
3. Token'ı yenileyin

#### Outlook Sync Hatası
```json
{
    "code": "outlook_sync_failed",
    "message": "Outlook senkronizasyonu başarısız",
    "details": "Connection refused"
}
```

**Çözüm:**
1. Outlook API erişimini kontrol edin
2. Firewall ayarlarını kontrol edin
3. Exchange server durumunu kontrol edin

## Logging ve Monitoring

### Log Dosyaları

Önemli log dosyaları:
```
/logs/
  ├── error.log     # Hata logları
  ├── access.log    # Erişim logları
  ├── sync.log      # Senkronizasyon logları
  └── audit.log     # Audit logları
```

### Monitoring Metrikleri

Prometheus endpoint'i: `/metrics`

Önemli metrikler:
- `http_requests_total`
- `http_request_duration_seconds`
- `db_query_duration_seconds`
- `sync_operations_total`
- `sync_errors_total`

### Debug Modu

Debug modu aktif etmek için:
```python
# settings.py
DEBUG = True
LOGGING['handlers']['console']['level'] = 'DEBUG'
```

## Sistem Gereksinimleri

### Minimum Gereksinimler
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- 2GB RAM
- 2 CPU core

### Önerilen Gereksinimler
- Python 3.10+
- PostgreSQL 14+
- Redis 7+
- 4GB RAM
- 4 CPU core

## Yaygın Hatalar ve Çözümleri

### 1. Database Bağlantı Hataları

Hata:
```
django.db.utils.OperationalError: could not connect to server
```

Çözüm:
1. PostgreSQL servisinin çalıştığını kontrol edin
2. Database credentials'ları kontrol edin
3. Firewall ayarlarını kontrol edin

### 2. Redis Bağlantı Hataları

Hata:
```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379
```

Çözüm:
1. Redis servisinin çalıştığını kontrol edin
2. Redis port'unu kontrol edin
3. Redis password'unu kontrol edin

### 3. Celery Worker Hataları

Hata:
```
kombu.exceptions.OperationalError: [Errno 111] Connection refused
```

Çözüm:
1. RabbitMQ/Redis broker'ının çalıştığını kontrol edin
2. Celery worker'ı yeniden başlatın
3. Broker URL'ini kontrol edin

## Güvenlik Kontrolleri

### 1. Token Güvenliği
- Token süresinin doğru ayarlandığını kontrol edin
- Refresh token rotasyonunu kontrol edin
- Token blacklist mekanizmasını kontrol edin

### 2. Rate Limiting
- IP bazlı rate limit'i kontrol edin
- User bazlı rate limit'i kontrol edin
- Endpoint bazlı rate limit'i kontrol edin

### 3. Input Validation
- XSS korumasını kontrol edin
- SQL injection korumasını kontrol edin
- File upload validasyonunu kontrol edin

## Yedekleme ve Recovery

### Database Yedekleme
```bash
pg_dump dbname > backup.sql
```

### Database Recovery
```bash
psql dbname < backup.sql
```

### Media Dosyaları Yedekleme
```bash
rsync -av media/ backup/media/
```

## İletişim ve Destek

### Teknik Destek
- Email: support@example.com
- Telefon: +90 xxx xxx xx xx
- Mesai saatleri: 09:00-18:00

### Acil Durumlar
- 7/24 Acil hat: +90 xxx xxx xx xx
- On-call mühendis: oncall@example.com
