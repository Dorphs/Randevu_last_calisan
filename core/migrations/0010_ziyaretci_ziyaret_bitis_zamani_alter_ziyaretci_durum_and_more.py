# Generated by Django 5.1.5 on 2025-02-02 10:05

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_toplanti_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='ziyaretci',
            name='ziyaret_bitis_zamani',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Ziyaret Bitiş Zamanı'),
        ),
        migrations.AlterField(
            model_name='ziyaretci',
            name='durum',
            field=models.CharField(choices=[('BEKLIYOR', 'Bekliyor'), ('GORUSME_BASLADI', 'Görüşme Başladı'), ('TAMAMLANDI', 'Tamamlandı'), ('IPTAL', 'İptal')], default='BEKLIYOR', max_length=20, verbose_name='Durum'),
        ),
        migrations.AlterField(
            model_name='ziyaretci',
            name='ziyaret_zamani',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Ziyaret Zamanı'),
        ),
    ]
