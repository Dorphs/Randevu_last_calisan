# Generated by Django 5.1.5 on 2025-02-01 18:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ToplantiOdasi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad', models.CharField(max_length=100, verbose_name='Oda Adı')),
                ('kapasite', models.IntegerField(verbose_name='Kapasite')),
                ('aciklama', models.TextField(blank=True, null=True, verbose_name='Açıklama')),
            ],
            options={
                'verbose_name': 'Toplantı Odası',
                'verbose_name_plural': 'Toplantı Odaları',
            },
        ),
        migrations.CreateModel(
            name='Toplanti',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('baslik', models.CharField(max_length=200, verbose_name='Başlık')),
                ('konu', models.TextField(verbose_name='Konu')),
                ('baslangic_zamani', models.DateTimeField(verbose_name='Başlangıç Zamanı')),
                ('bitis_zamani', models.DateTimeField(verbose_name='Bitiş Zamanı')),
                ('durum', models.CharField(choices=[('PLANLI', 'Planlandı'), ('DEVAM', 'Devam Ediyor'), ('TAMAMLANDI', 'Tamamlandı'), ('IPTAL', 'İptal Edildi')], default='PLANLI', max_length=20, verbose_name='Durum')),
                ('tur', models.CharField(choices=[('KURUM_ICI', 'Kurum İçi'), ('KURUM_DISI', 'Kurum Dışı')], max_length=20, verbose_name='Toplantı Türü')),
                ('notlar', models.TextField(blank=True, null=True, verbose_name='Notlar')),
                ('katilimcilar', models.ManyToManyField(related_name='katildigi_toplantilar', to=settings.AUTH_USER_MODEL, verbose_name='Katılımcılar')),
                ('olusturan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='olusturulan_toplantilar', to=settings.AUTH_USER_MODEL, verbose_name='Oluşturan')),
                ('oda', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.toplantiodasi', verbose_name='Toplantı Odası')),
            ],
            options={
                'verbose_name': 'Toplantı',
                'verbose_name_plural': 'Toplantılar',
            },
        ),
        migrations.CreateModel(
            name='Ziyaretci',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad', models.CharField(max_length=100, verbose_name='Ad')),
                ('soyad', models.CharField(max_length=100, verbose_name='Soyad')),
                ('tc_no', models.CharField(max_length=11, verbose_name='T.C. Kimlik No')),
                ('telefon', models.CharField(max_length=20, verbose_name='Telefon')),
                ('kurum', models.CharField(max_length=200, verbose_name='Kurum')),
                ('ziyaret_nedeni', models.TextField(verbose_name='Ziyaret Nedeni')),
                ('randevulu', models.BooleanField(default=False, verbose_name='Randevulu mu?')),
                ('randevu_zamani', models.DateTimeField(blank=True, null=True, verbose_name='Randevu Zamanı')),
                ('ziyaret_zamani', models.DateTimeField(auto_now_add=True, verbose_name='Ziyaret Zamanı')),
                ('durum', models.CharField(choices=[('BEKLIYOR', 'Bekliyor'), ('GORUSME', 'Görüşmede'), ('TAMAMLANDI', 'Tamamlandı'), ('IPTAL', 'İptal Edildi')], default='BEKLIYOR', max_length=20, verbose_name='Durum')),
                ('notlar', models.TextField(blank=True, null=True, verbose_name='Notlar')),
                ('ziyaret_edilen', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ziyaret_edilen', to=settings.AUTH_USER_MODEL, verbose_name='Ziyaret Edilen')),
            ],
            options={
                'verbose_name': 'Ziyaretçi',
                'verbose_name_plural': 'Ziyaretçiler',
            },
        ),
    ]
