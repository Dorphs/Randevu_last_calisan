# Toplantı Yönetim Sistemi API Dokümantasyonu

## Genel Bilgiler

### Authentication

API JWT (JSON Web Token) authentication kullanmaktadır. Her istek için `Authorization` header'ında token gönderilmelidir.

```http
Authorization: Bearer <access_token>
```

Token almak için:

```http
POST /api/token/
{
    "username": "user@example.com",
    "password": "password123"
}

Response:
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Rate Limiting

API rate limiting uygulanmaktadır:
- Anonim kullanıcılar: 100 istek/saat
- Authentike kullanıcılar: 1000 istek/saat

### Hata Kodları

- 200: Başarılı
- 201: Oluşturuldu
- 400: Hatalı istek
- 401: Yetkisiz erişim
- 403: Erişim engellendi
- 404: Bulunamadı
- 409: Çakışma
- 429: Çok fazla istek
- 500: Sunucu hatası

## Endpoints

### Toplantılar

#### Toplantı Listesi

```http
GET /api/meetings/

Query Parameters:
- page: Sayfa numarası
- status: Toplantı durumu (PENDING, APPROVED, CANCELLED, COMPLETED)
- start_date: Başlangıç tarihi (YYYY-MM-DD)
- end_date: Bitiş tarihi (YYYY-MM-DD)
- search: Arama terimi

Response:
{
    "count": 100,
    "next": "http://api.example.org/meetings/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Proje Toplantısı",
            "start_time": "2025-02-01T10:00:00Z",
            "end_time": "2025-02-01T11:00:00Z",
            "status": "PENDING",
            "visitor": {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com"
            },
            "location": {
                "id": 1,
                "name": "Toplantı Odası 1"
            }
        }
    ]
}
```

#### Tekrarlanan Toplantı Oluşturma

```http
POST /api/meetings/recurring/

Request:
{
    "title": "Haftalık Toplantı",
    "description": "Her hafta Pazartesi",
    "start_time": "2025-02-01T10:00:00Z",
    "end_time": "2025-02-01T11:00:00Z",
    "visitor_id": 1,
    "location_id": 1,
    "meeting_type": "INTERNAL",
    "recurrence": {
        "frequency": "WEEKLY",
        "repeat_until": "2025-03-01",
        "days_of_week": "1"  // Pazartesi
    }
}

Response:
{
    "id": 1,
    "recurring_meetings": [
        {
            "id": 2,
            "start_time": "2025-02-08T10:00:00Z",
            "end_time": "2025-02-08T11:00:00Z"
        },
        {
            "id": 3,
            "start_time": "2025-02-15T10:00:00Z",
            "end_time": "2025-02-15T11:00:00Z"
        }
    ]
}
```

#### Toplantı Şablonu Oluşturma

```http
POST /api/meeting-templates/

Request:
{
    "name": "Müşteri Görüşmesi",
    "description": "Standart müşteri görüşme şablonu",
    "duration": "01:00:00",
    "meeting_type": "CUSTOMER"
}

Response:
{
    "id": 1,
    "name": "Müşteri Görüşmesi",
    "duration": "01:00:00",
    "meeting_type": "CUSTOMER",
    "created_at": "2025-01-30T20:25:00Z"
}
```

#### Dosya Ekleme

```http
POST /api/meetings/{id}/attachments/

Request: multipart/form-data
- file: Dosya
- description: Açıklama

Response:
{
    "id": 1,
    "file_name": "sunum.pdf",
    "file_type": "application/pdf",
    "file_size": 1024576,
    "uploaded_at": "2025-01-30T20:25:00Z"
}
```

### Mobil API

#### Offline Sync

```http
GET /api/v1/mobile/meetings/offline_sync/

Query Parameters:
- last_sync: Son senkronizasyon zamanı (ISO 8601)

Response:
{
    "meetings": [
        {
            "id": 1,
            "title": "Toplantı",
            "modified_at": "2025-01-30T20:25:00Z",
            "is_deleted": false
        }
    ],
    "sync_time": "2025-01-30T20:26:00Z"
}
```

## WebSocket Events

Gerçek zamanlı güncellemeler için WebSocket kullanılmaktadır:

```javascript
// Bağlantı
const ws = new WebSocket('ws://api.example.org/ws/meetings/');

// Event örnekleri
{
    "type": "meeting.created",
    "data": { ... }
}

{
    "type": "meeting.updated",
    "data": { ... }
}

{
    "type": "meeting.deleted",
    "data": { ... }
}
```

## Örnek Kodlar

### Python

```python
import requests

# Token al
response = requests.post('http://api.example.org/api/token/', {
    'username': 'user@example.com',
    'password': 'password123'
})
token = response.json()['access']

# Toplantı oluştur
headers = {'Authorization': f'Bearer {token}'}
response = requests.post('http://api.example.org/api/meetings/', {
    'title': 'Yeni Toplantı',
    'start_time': '2025-02-01T10:00:00Z',
    'end_time': '2025-02-01T11:00:00Z',
    'visitor_id': 1,
    'location_id': 1
}, headers=headers)
```

### JavaScript

```javascript
// Token al
const response = await fetch('http://api.example.org/api/token/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username: 'user@example.com',
        password: 'password123'
    })
});
const { access } = await response.json();

// Toplantı oluştur
const meeting = await fetch('http://api.example.org/api/meetings/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${access}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        title: 'Yeni Toplantı',
        start_time: '2025-02-01T10:00:00Z',
        end_time: '2025-02-01T11:00:00Z',
        visitor_id: 1,
        location_id: 1
    })
});
```
