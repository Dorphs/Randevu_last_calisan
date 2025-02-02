from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class ToplantiOdasi(models.Model):
    """Toplantı odalarının bilgilerini tutan model"""
    ad = models.CharField(max_length=100, verbose_name="Oda Adı")  # Toplantı odasının adı
    kapasite = models.IntegerField(verbose_name="Kapasite")  # Odanın kapasitesi
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")  # Oda hakkında ek bilgiler
    
    class Meta:
        verbose_name = "Toplantı Odası"
        verbose_name_plural = "Toplantı Odaları"
    
    def __str__(self):
        return self.ad

class KurumDisiKatilimci(models.Model):
    """Kurum dışı toplantı katılımcısı modeli"""
    ad = models.CharField(max_length=100, verbose_name="Ad")
    soyad = models.CharField(max_length=100, verbose_name="Soyad")
    kurum_unvan = models.CharField(max_length=200, verbose_name="Kurum/Ünvan", blank=True, null=True)
    email = models.EmailField(verbose_name="E-posta", blank=True, null=True)

    def __str__(self):
        return f"{self.ad} {self.soyad}"

    class Meta:
        verbose_name = "Kurum Dışı Katılımcı"
        verbose_name_plural = "Kurum Dışı Katılımcılar"

class Toplanti(models.Model):
    """Toplantı modeli"""
    DURUM_CHOICES = [
        ('BEKLIYOR', 'Bekliyor'),
        ('DEVAM_EDIYOR', 'Devam Ediyor'),
        ('TAMAMLANDI', 'Tamamlandı'),
        ('IPTAL', 'İptal'),
    ]

    TUR_CHOICES = [
        ('KURUM_ICI', 'Kurum İçi'),
        ('KURUM_DISI', 'Kurum Dışı'),
    ]

    baslik = models.CharField(max_length=200, verbose_name="Başlık")
    konu = models.TextField(verbose_name="Konu")
    baslangic_zamani = models.DateTimeField(verbose_name="Başlangıç Zamanı")
    bitis_zamani = models.DateTimeField(verbose_name="Bitiş Zamanı", null=True, blank=True)
    oda = models.ForeignKey(ToplantiOdasi, on_delete=models.PROTECT, verbose_name="Toplantı Odası")
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='BEKLIYOR', verbose_name="Durum")
    tur = models.CharField(max_length=20, choices=TUR_CHOICES, default='KURUM_ICI', verbose_name="Tür")
    olusturan = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Oluşturan", related_name="olusturan_toplantilar")
    katilimcilar = models.ManyToManyField(User, verbose_name="Katılımcılar", related_name="katildigi_toplantilar", blank=True)
    kurum_disi_katilimcilar = models.ManyToManyField(KurumDisiKatilimci, verbose_name="Kurum Dışı Katılımcılar", related_name="katildigi_toplantilar", blank=True)
    notlar = models.TextField(blank=True, null=True, verbose_name="Notlar")

    def __str__(self):
        return f"{self.baslik} - {self.baslangic_zamani.strftime('%d/%m/%Y %H:%M')}"

    def save(self, *args, **kwargs):
        # Durum tamamlandı olduğunda ve bitiş zamanı yoksa, varsayılan olarak 1 saat sonrasını ayarla
        if self.durum == 'TAMAMLANDI' and not self.bitis_zamani:
            if not hasattr(self, '_bitis_zamani_set'):  # Sonsuz döngüyü önlemek için
                self._bitis_zamani_set = True
                # Eğer başlangıç zamanı varsa ondan 1 saat sonra, yoksa şu andan 1 saat sonra
                if self.baslangic_zamani:
                    self.bitis_zamani = self.baslangic_zamani + timedelta(hours=1)
                else:
                    self.bitis_zamani = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Toplantı"
        verbose_name_plural = "Toplantılar"

class KurumDisiZiyaretci(models.Model):
    """Kurum dışı ziyaretçi modeli"""
    ad = models.CharField(max_length=100, verbose_name="Ad")
    soyad = models.CharField(max_length=100, verbose_name="Soyad")
    telefon = models.CharField(max_length=20, verbose_name="Telefon", blank=True, null=True)
    kurum_unvan = models.CharField(max_length=200, verbose_name="Kurum/Ünvan", blank=True, null=True)

    def __str__(self):
        return f"{self.ad} {self.soyad}"

    class Meta:
        verbose_name = "Kurum Dışı Ziyaretçi"
        verbose_name_plural = "Kurum Dışı Ziyaretçiler"

class Ziyaretci(models.Model):
    """Ziyaretçi modeli"""
    DURUM_CHOICES = [
        ('BEKLIYOR', 'Bekliyor'),
        ('GORUSME_BASLADI', 'Görüşme Başladı'),
        ('TAMAMLANDI', 'Tamamlandı'),
        ('IPTAL', 'İptal'),
    ]

    TUR_CHOICES = [
        ('KURUM_ICI', 'Kurum İçi'),
        ('KURUM_DISI', 'Kurum Dışı'),
    ]

    ziyaret_nedeni = models.TextField(verbose_name="Ziyaret Nedeni")
    randevulu = models.BooleanField(default=False, verbose_name="Randevulu")
    randevu_zamani = models.DateTimeField(null=True, blank=True, verbose_name="Randevu Zamanı")
    ziyaret_zamani = models.DateTimeField(verbose_name="Ziyaret Zamanı", default=timezone.now)
    ziyaret_bitis_zamani = models.DateTimeField(verbose_name="Ziyaret Bitiş Zamanı", null=True, blank=True)
    ziyaret_edilen = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        verbose_name="Ziyaret Edilen", 
        related_name="ziyaret_edilen",
        default=1  # Admin kullanıcısı
    )
    durum = models.CharField(max_length=20, choices=DURUM_CHOICES, default='BEKLIYOR', verbose_name="Durum")
    tur = models.CharField(max_length=20, choices=TUR_CHOICES, default='KURUM_DISI', verbose_name="Tür")
    kurum_ici_ziyaretciler = models.ManyToManyField(
        User, 
        verbose_name="Kurum İçi Ziyaretçiler", 
        related_name="kurum_ici_ziyaretler", 
        blank=True
    )
    kurum_disi_ziyaretciler = models.ManyToManyField(
        KurumDisiZiyaretci,
        verbose_name="Kurum Dışı Ziyaretçiler",
        related_name="ziyaretler",
        blank=True
    )
    notlar = models.TextField(blank=True, null=True, verbose_name="Notlar")

    def __str__(self):
        if self.tur == 'KURUM_ICI':
            ziyaretciler = ", ".join([f"{user.get_full_name()}" for user in self.kurum_ici_ziyaretciler.all()])
            return f"Kurum İçi: {ziyaretciler}"
        else:
            ziyaretciler = ", ".join([str(z) for z in self.kurum_disi_ziyaretciler.all()])
            return f"Kurum Dışı: {ziyaretciler}"

    def save(self, *args, **kwargs):
        # Durum tamamlandı olduğunda ve bitiş zamanı yoksa, varsayılan olarak 1 saat sonrasını ayarla
        if self.durum == 'TAMAMLANDI' and not self.ziyaret_bitis_zamani:
            if not hasattr(self, '_bitis_zamani_set'):  # Sonsuz döngüyü önlemek için
                self._bitis_zamani_set = True
                # Eğer ziyaret zamanı varsa ondan 1 saat sonra, yoksa şu andan 1 saat sonra
                if self.ziyaret_zamani:
                    self.ziyaret_bitis_zamani = self.ziyaret_zamani + timedelta(hours=1)
                else:
                    self.ziyaret_bitis_zamani = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Ziyaretçi"
        verbose_name_plural = "Ziyaretçiler"
