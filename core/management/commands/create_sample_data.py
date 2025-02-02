from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import Toplanti, Ziyaretci, ToplantiOdasi, KurumDisiKatilimci, KurumDisiZiyaretci
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Örnek veriler oluşturur'

    def handle(self, *args, **kwargs):
        # Örnek toplantılar oluştur
        users = User.objects.all()
        odalar = ToplantiOdasi.objects.all()
        kurum_disi_katilimcilar = KurumDisiKatilimci.objects.all()
        
        # Son 30 gün için rastgele toplantılar
        for _ in range(20):
            baslangic = timezone.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            toplanti = Toplanti.objects.create(
                baslik=f"Örnek Toplantı {random.randint(1, 100)}",
                konu=f"Örnek toplantı konusu {random.randint(1, 100)}",
                baslangic_zamani=baslangic,
                bitis_zamani=baslangic + timedelta(hours=random.randint(1, 3)),
                oda=random.choice(odalar),
                durum=random.choice(['BEKLIYOR', 'DEVAM_EDIYOR', 'TAMAMLANDI']),
                tur=random.choice(['KURUM_ICI', 'KURUM_DISI']),
                olusturan=random.choice(users)
            )
            
            # Katılımcılar ekle
            katilimci_sayisi = random.randint(1, 3)
            toplanti.katilimcilar.add(*random.sample(list(users), katilimci_sayisi))
            
            if toplanti.tur == 'KURUM_DISI':
                kurum_disi_katilimci_sayisi = random.randint(1, 2)
                toplanti.kurum_disi_katilimcilar.add(
                    *random.sample(list(kurum_disi_katilimcilar), kurum_disi_katilimci_sayisi)
                )

        # Örnek ziyaretçiler oluştur
        kurum_disi_ziyaretciler = KurumDisiZiyaretci.objects.all()
        
        # Son 30 gün için rastgele ziyaretçiler
        for _ in range(30):
            ziyaret_zamani = timezone.now() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            ziyaretci = Ziyaretci.objects.create(
                ziyaret_nedeni=f"Örnek ziyaret nedeni {random.randint(1, 100)}",
                randevulu=random.choice([True, False]),
                ziyaret_zamani=ziyaret_zamani,
                ziyaret_bitis_zamani=ziyaret_zamani + timedelta(hours=random.randint(1, 2)),
                ziyaret_edilen=random.choice(users),
                durum=random.choice(['BEKLIYOR', 'GORUSME_BASLADI', 'TAMAMLANDI']),
                tur=random.choice(['KURUM_ICI', 'KURUM_DISI'])
            )
            
            if ziyaretci.tur == 'KURUM_ICI':
                ziyaretci_sayisi = random.randint(1, 2)
                ziyaretci.kurum_ici_ziyaretciler.add(*random.sample(list(users), ziyaretci_sayisi))
            else:
                ziyaretci_sayisi = random.randint(1, 2)
                ziyaretci.kurum_disi_ziyaretciler.add(
                    *random.sample(list(kurum_disi_ziyaretciler), ziyaretci_sayisi)
                )

        self.stdout.write(self.style.SUCCESS('Örnek veriler başarıyla oluşturuldu'))
