# Toplantı ve Ziyaretçi Takip Sistemi

Modern ve kullanıcı dostu bir toplantı ve ziyaretçi yönetim sistemi. Django backend ve React frontend ile geliştirilmiştir.

## 🚀 Özellikler

### Toplantı Yönetimi
- Toplantı oluşturma ve düzenleme
- Toplantı odası seçimi
- Katılımcı ekleme ve yönetimi
- Toplantı durumu takibi
- Takvim görünümü

### Ziyaretçi Yönetimi
- Ziyaretçi kaydı oluşturma
- Ziyaretçi bilgilerini düzenleme
- Ziyaret geçmişi takibi
- Aktif ziyaretçi listesi

### Raporlama
- Detaylı toplantı raporları
- Ziyaretçi istatistikleri
- Tarih aralığı veya ay bazlı filtreleme
- Grafik ve tablo görünümleri
- Sadece veri olan dönemleri gösterme
- PDF export özelliği

### Güvenlik
- Token tabanlı kimlik doğrulama
- Rol bazlı yetkilendirme
- Güvenli API endpoints

## 🛠️ Teknolojiler

### Backend
- Python 3.11+
- Django 5.1
- Django REST Framework
- SQLite veritabanı

### Frontend
- React 18
- Material-UI (MUI)
- Axios
- date-fns
- Recharts (grafikler için)

## 📦 Kurulum

### Backend Kurulumu
1. Python 3.11 veya üstü sürümü yükleyin
2. Proje dizinine gidin:
   ```bash
   cd Proje
   ```
3. Sanal ortam oluşturun ve aktif edin:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows için
   ```
4. Gereksinimleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
5. Veritabanı migrasyonlarını yapın:
   ```bash
   python manage.py migrate
   ```
6. Sunucuyu başlatın:
   ```bash
   python manage.py runserver
   ```

### Frontend Kurulumu
1. Node.js 18 veya üstü sürümü yükleyin
2. Frontend dizinine gidin:
   ```bash
   cd frontend
   ```
3. Bağımlılıkları yükleyin:
   ```bash
   npm install
   ```
4. Geliştirme sunucusunu başlatın:
   ```bash
   npm start
   ```

## 🌐 Kullanım

1. Tarayıcıda `http://localhost:3000` adresine gidin
2. Admin hesabı ile giriş yapın
3. Sol menüden istediğiniz modülü seçin:
   - Toplantılar
   - Ziyaretçiler
   - Raporlar
   - Ayarlar

## 📊 Raporlama Özellikleri

### Tarih Filtreleme
- İki farklı filtreleme seçeneği:
  1. Tarih Aralığı: İki tarih arasındaki verileri gösterir
  2. Ay Seçimi: Belirli bir ay için verileri gösterir
- Sadece veri olan tarihler seçilebilir
- Otomatik tarih optimizasyonu

### Görselleştirmeler
- Çizgi grafikleri
- Pasta grafikleri
- Bar grafikleri
- Detaylı tablolar

## 👥 Katkıda Bulunma

1. Bu repository'yi fork edin
2. Feature branch'i oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📧 İletişim

Proje Sahibi - [@Dorphs](https://github.com/Dorphs)

Proje Linki: [https://github.com/Dorphs/Randevu_last_calisan](https://github.com/Dorphs/Randevu_last_calisan)
