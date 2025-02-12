# Generated by Django 5.1.5 on 2025-02-02 10:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_kurumdisiziyaretci_remove_ziyaretci_ad_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='KurumDisiKatilimci',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad', models.CharField(max_length=100, verbose_name='Ad')),
                ('soyad', models.CharField(max_length=100, verbose_name='Soyad')),
                ('kurum_unvan', models.CharField(blank=True, max_length=200, null=True, verbose_name='Kurum/Ünvan')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='E-posta')),
            ],
            options={
                'verbose_name': 'Kurum Dışı Katılımcı',
                'verbose_name_plural': 'Kurum Dışı Katılımcılar',
            },
        ),
        migrations.AlterModelOptions(
            name='toplanti',
            options={},
        ),
        migrations.AlterField(
            model_name='toplanti',
            name='bitis_zamani',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Bitiş Zamanı'),
        ),
        migrations.AlterField(
            model_name='toplanti',
            name='durum',
            field=models.CharField(choices=[('BEKLIYOR', 'Bekliyor'), ('DEVAM_EDIYOR', 'Devam Ediyor'), ('TAMAMLANDI', 'Tamamlandı'), ('IPTAL', 'İptal')], default='BEKLIYOR', max_length=20, verbose_name='Durum'),
        ),
        migrations.AlterField(
            model_name='toplanti',
            name='katilimcilar',
            field=models.ManyToManyField(blank=True, related_name='katildigi_toplantilar', to=settings.AUTH_USER_MODEL, verbose_name='Katılımcılar'),
        ),
        migrations.AlterField(
            model_name='toplanti',
            name='olusturan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='olusturan_toplantilar', to=settings.AUTH_USER_MODEL, verbose_name='Oluşturan'),
        ),
        migrations.AlterField(
            model_name='toplanti',
            name='tur',
            field=models.CharField(choices=[('KURUM_ICI', 'Kurum İçi'), ('KURUM_DISI', 'Kurum Dışı')], default='KURUM_ICI', max_length=20, verbose_name='Tür'),
        ),
        migrations.AddField(
            model_name='toplanti',
            name='kurum_disi_katilimcilar',
            field=models.ManyToManyField(blank=True, related_name='katildigi_toplantilar', to='core.kurumdisikatilimci', verbose_name='Kurum Dışı Katılımcılar'),
        ),
    ]
