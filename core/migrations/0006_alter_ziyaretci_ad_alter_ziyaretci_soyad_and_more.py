# Generated by Django 5.1.5 on 2025-02-01 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_ziyaretci_kurum_ici_ziyaretci_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ziyaretci',
            name='ad',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Ad'),
        ),
        migrations.AlterField(
            model_name='ziyaretci',
            name='soyad',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Soyad'),
        ),
        migrations.AlterField(
            model_name='ziyaretci',
            name='telefon',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Telefon'),
        ),
    ]
