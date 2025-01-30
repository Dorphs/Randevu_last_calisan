# Mobil Entegrasyon Rehberi

## Genel Bakış

Bu rehber, Toplantı Yönetim Sistemi'nin mobil uygulamasını entegre etmek için gereken tüm bilgileri içerir.

## Başlangıç

### 1. API Anahtarları

Mobil uygulama için gerekli anahtarlar:
```json
{
    "api_base_url": "https://api.example.org",
    "api_version": "v1",
    "push_notification": {
        "firebase_config": "firebase_config.json",
        "apns_certificate": "apns_cert.pem"
    }
}
```

### 2. Authentication

JWT token alma:
```http
POST /api/token/
Content-Type: application/json

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

Token yenileme:
```http
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Offline Sync

### 1. İlk Senkronizasyon

```http
GET /api/v1/mobile/meetings/offline_sync/
Authorization: Bearer <token>

Response:
{
    "meetings": [
        {
            "id": 1,
            "title": "Toplantı",
            "start_time": "2025-02-01T10:00:00Z",
            "end_time": "2025-02-01T11:00:00Z",
            "status": "PENDING",
            "modified_at": "2025-01-30T20:25:00Z",
            "is_deleted": false
        }
    ],
    "sync_time": "2025-01-30T20:26:00Z"
}
```

### 2. Değişiklikleri Gönderme

```http
POST /api/v1/mobile/meetings/sync/
Authorization: Bearer <token>
Content-Type: application/json

{
    "changes": [
        {
            "id": "local_1",
            "action": "create",
            "data": {
                "title": "Yeni Toplantı",
                "start_time": "2025-02-01T10:00:00Z"
            }
        },
        {
            "id": 2,
            "action": "update",
            "data": {
                "status": "CANCELLED"
            }
        }
    ],
    "last_sync": "2025-01-30T20:25:00Z"
}
```

### 3. Çakışma Çözümleme

```http
POST /api/v1/mobile/meetings/resolve_conflict/
Authorization: Bearer <token>
Content-Type: application/json

{
    "meeting_id": 1,
    "resolution": "keep_server",  // veya "keep_local"
    "local_changes": {
        "title": "Yerel Değişiklik"
    },
    "server_changes": {
        "title": "Sunucu Değişikliği"
    }
}
```

## Push Notifications

### 1. Device Kaydı

```http
POST /api/v1/mobile/meetings/register_device/
Authorization: Bearer <token>
Content-Type: application/json

{
    "device_token": "firebase_token_or_apns_token",
    "device_type": "android",  // veya "ios"
    "app_version": "1.0.0"
}
```

### 2. Bildirim Tercihleri

```http
PUT /api/v1/mobile/meetings/notification_preferences/
Authorization: Bearer <token>
Content-Type: application/json

{
    "meeting_created": true,
    "meeting_updated": true,
    "meeting_cancelled": true,
    "meeting_reminder": {
        "enabled": true,
        "minutes_before": 30
    }
}
```

## Örnek Kodlar

### iOS (Swift)

```swift
// Authentication
func login(email: String, password: String) {
    let url = URL(string: "\(baseUrl)/api/token/")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let body = [
        "username": email,
        "password": password
    ]
    
    request.httpBody = try? JSONSerialization.data(withJSONObject: body)
    
    URLSession.shared.dataTask(with: request) { data, response, error in
        if let data = data {
            let token = try? JSONDecoder().decode(Token.self, from: data)
            // Token'ı kaydet
        }
    }.resume()
}

// Offline Sync
class OfflineSync {
    func syncChanges() {
        guard let lastSync = UserDefaults.standard.object(forKey: "lastSyncTime") as? Date else {
            return
        }
        
        let changes = DatabaseManager.shared.getChanges(since: lastSync)
        
        let url = URL(string: "\(baseUrl)/api/v1/mobile/meetings/sync/")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let body = [
            "changes": changes,
            "last_sync": ISO8601DateFormatter().string(from: lastSync)
        ]
        
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let data = data {
                // Sunucu değişikliklerini uygula
                self.applyServerChanges(data)
            }
        }.resume()
    }
}
```

### Android (Kotlin)

```kotlin
// Authentication
class AuthRepository {
    suspend fun login(email: String, password: String): Token {
        return apiService.login(LoginRequest(email, password))
    }
    
    suspend fun refreshToken(refreshToken: String): Token {
        return apiService.refreshToken(RefreshRequest(refreshToken))
    }
}

// Offline Sync
class SyncWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val lastSync = preferences.getLastSyncTime()
        val changes = database.getChangesSince(lastSync)
        
        try {
            val response = apiService.syncChanges(SyncRequest(changes, lastSync))
            database.applyServerChanges(response.changes)
            preferences.setLastSyncTime(response.syncTime)
            return Result.success()
        } catch (e: Exception) {
            return Result.retry()
        }
    }
}

// Push Notifications
class FirebaseMessagingService : FirebaseMessagingService() {
    override fun onNewToken(token: String) {
        GlobalScope.launch {
            try {
                apiService.registerDevice(DeviceRegistration(token, "android"))
            } catch (e: Exception) {
                // Token kaydı başarısız
            }
        }
    }
    
    override fun onMessageReceived(message: RemoteMessage) {
        // Bildirimi göster
        NotificationHelper.showNotification(
            context = this,
            title = message.data["title"],
            body = message.data["body"]
        )
    }
}
```

## Hata Kodları ve Çözümleri

### Authentication Hataları

- `401 Unauthorized`: Token geçersiz veya süresi dolmuş
  ```json
  {
    "code": "token_invalid",
    "message": "Token geçersiz veya süresi dolmuş"
  }
  ```
  Çözüm: Refresh token ile yeni token alın

### Sync Hataları

- `409 Conflict`: Senkronizasyon çakışması
  ```json
  {
    "code": "sync_conflict",
    "message": "Veri çakışması tespit edildi",
    "conflicts": [
      {
        "id": 1,
        "server_version": "2025-01-30T20:25:00Z",
        "local_version": "2025-01-30T20:24:00Z"
      }
    ]
  }
  ```
  Çözüm: Çakışma çözümleme API'sini kullanın

### Network Hataları

- `timeout`: Sunucu yanıt vermiyor
  Çözüm: Offline moda geç, daha sonra tekrar dene

- `no_connection`: İnternet bağlantısı yok
  Çözüm: Offline moda geç, bağlantı geldiğinde senkronize et

## Best Practices

1. **Offline First Yaklaşımı**
   - Tüm verileri lokalde sakla
   - Önce lokale yaz, sonra senkronize et
   - Bağlantı olmadığında da çalışabilmeli

2. **Battery Friendly**
   - Senkronizasyonu akıllıca planla
   - Background işlemleri minimize et
   - Push notification yerine polling kullanma

3. **Error Handling**
   - Her hatayı kullanıcıya gösterme
   - Kritik hataları log'la
   - Otomatik recovery mekanizmaları kur

4. **Security**
   - Token'ları güvenli şekilde sakla
   - Hassas verileri encrypt et
   - Certificate pinning kullan

5. **Performance**
   - Büyük veriyi sayfalı indir
   - Görüntüleri cache'le
   - Response'ları compress et
