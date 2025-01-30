# Toplantı Yönetim Sistemi API Dokümantasyonu

## Genel Bilgiler

### Kimlik Doğrulama

API JWT token tabanlı kimlik doğrulama kullanmaktadır. Her istek için `Authorization` header'ında token gönderilmelidir.

```
Authorization: Bearer <your_token>
```

Token almak için:

```http
POST /api/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

### Rate Limiting

API'de aşağıdaki rate limit kuralları uygulanmaktadır:

* Rapor Oluşturma: 10/saat
* Dashboard Yenileme: 30/dakika
* Export İşlemleri: 20/saat
* Widget Yenileme: 60/dakika

## Endpoints

### Raporlar

#### Rapor Listesi

```http
GET /api/reports/
```

Kullanıcının erişimi olan raporları listeler.

#### Rapor Oluşturma

```http
POST /api/reports/
Content-Type: application/json

{
    "title": "Aylık Toplantı Raporu",
    "report_type": "MEETING_SUMMARY",
    "parameters": {
        "include_cancelled": true
    },
    "start_date": "2025-01-01",
    "end_date": "2025-01-31",
    "is_scheduled": false
}
```

#### Rapor Oluşturma (Generate)

```http
POST /api/reports/{id}/generate/
Content-Type: application/json

{
    "start_date": "2025-01-01",
    "end_date": "2025-01-31",
    "parameters": {
        "include_cancelled": true
    }
}
```

#### Rapor Dışa Aktarma

```http
POST /api/reports/{id}/export/
Content-Type: application/json

{
    "execution_id": "123",
    "format": "excel"  // veya "pdf"
}
```

### Dashboard

#### Dashboard Listesi

```http
GET /api/dashboards/
```

Kullanıcının erişimi olan dashboard'ları listeler.

#### Dashboard Oluşturma

```http
POST /api/dashboards/
Content-Type: application/json

{
    "title": "Yönetici Dashboard'u",
    "layout": {
        "widgets": [
            {"id": 1, "x": 0, "y": 0, "w": 6, "h": 4},
            {"id": 2, "x": 6, "y": 0, "w": 6, "h": 4}
        ]
    },
    "is_public": false
}
```

#### Widget Ekleme

```http
POST /api/dashboards/{id}/add-widget/
Content-Type: application/json

{
    "title": "Toplantı İstatistikleri",
    "widget_type": "CHART",
    "data_source": {
        "type": "meeting_summary",
        "chart_type": "bar",
        "start_date": "2025-01-01",
        "end_date": "2025-01-31"
    },
    "refresh_interval": 300
}
```

### Widgets

#### Widget Güncelleme

```http
PUT /api/dashboard-widgets/{id}/
Content-Type: application/json

{
    "title": "Yeni Başlık",
    "refresh_interval": 600,
    "position": {"x": 0, "y": 0, "w": 6, "h": 4}
}
```

#### Widget Yenileme

```http
POST /api/dashboard-widgets/{id}/refresh/
```

## Hata Kodları

| Kod | Açıklama |
|-----|-----------|
| 400 | Geçersiz istek |
| 401 | Kimlik doğrulama hatası |
| 403 | Yetkisiz erişim |
| 404 | Kaynak bulunamadı |
| 429 | Rate limit aşıldı |

## Örnekler

### Rapor Oluşturma ve Export

```python
import requests

# Token al
response = requests.post('http://api/token/', json={
    'username': 'user',
    'password': 'pass'
})
token = response.json()['access']

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Rapor oluştur
report_data = {
    'title': 'Aylık Rapor',
    'report_type': 'MEETING_SUMMARY',
    'start_date': '2025-01-01',
    'end_date': '2025-01-31'
}
response = requests.post('http://api/reports/', 
                        json=report_data,
                        headers=headers)
report_id = response.json()['id']

# Raporu generate et
generate_data = {
    'start_date': '2025-01-01',
    'end_date': '2025-01-31'
}
response = requests.post(f'http://api/reports/{report_id}/generate/',
                        json=generate_data,
                        headers=headers)
execution_id = response.json()['execution_id']

# Excel olarak export et
export_data = {
    'execution_id': execution_id,
    'format': 'excel'
}
response = requests.post(f'http://api/reports/{report_id}/export/',
                        json=export_data,
                        headers=headers)
file_url = response.json()['file_url']
```

### Dashboard Widget Ekleme

```python
import requests

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Dashboard oluştur
dashboard_data = {
    'title': 'Ana Dashboard',
    'is_public': False
}
response = requests.post('http://api/dashboards/',
                        json=dashboard_data,
                        headers=headers)
dashboard_id = response.json()['id']

# Widget ekle
widget_data = {
    'title': 'Toplantı Grafiği',
    'widget_type': 'CHART',
    'data_source': {
        'type': 'meeting_summary',
        'chart_type': 'bar'
    },
    'refresh_interval': 300
}
response = requests.post(f'http://api/dashboards/{dashboard_id}/add-widget/',
                        json=widget_data,
                        headers=headers)
```
