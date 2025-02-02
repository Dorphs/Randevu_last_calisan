from django.contrib import admin
from .models import ToplantiOdasi, Toplanti, Ziyaretci

# Register your models here.

@admin.register(ToplantiOdasi)
class ToplantiOdasiAdmin(admin.ModelAdmin):
    """Toplantı odası admin paneli"""
    list_display = ('ad', 'kapasite')
    search_fields = ('ad',)

@admin.register(Toplanti)
class ToplantiAdmin(admin.ModelAdmin):
    """Toplantı admin paneli"""
    list_display = ('baslik', 'baslangic_zamani', 'bitis_zamani', 'oda', 'durum', 'tur')
    list_filter = ('durum', 'tur', 'oda')
    search_fields = ('baslik', 'konu')
    filter_horizontal = ('katilimcilar',)

@admin.register(Ziyaretci)
class ZiyaretciAdmin(admin.ModelAdmin):
    """Ziyaretçi admin paneli"""
    list_display = ('get_ziyaretci_adi', 'ziyaret_edilen', 'ziyaret_zamani', 'durum', 'tur')
    list_filter = ('durum', 'tur', 'randevulu')
    search_fields = ('kurum_disi_ziyaretciler__ad', 'kurum_disi_ziyaretciler__soyad', 'kurum_ici_ziyaretciler__first_name', 'kurum_ici_ziyaretciler__last_name')
    filter_horizontal = ('kurum_ici_ziyaretciler', 'kurum_disi_ziyaretciler')

    def get_ziyaretci_adi(self, obj):
        """Ziyaretçi adını döndürür"""
        if obj.tur == 'KURUM_ICI':
            ziyaretciler = ", ".join([f"{user.get_full_name()}" for user in obj.kurum_ici_ziyaretciler.all()])
            return f"Kurum İçi: {ziyaretciler}"
        else:
            ziyaretciler = ", ".join([str(z) for z in obj.kurum_disi_ziyaretciler.all()])
            return f"Kurum Dışı: {ziyaretciler}"
    get_ziyaretci_adi.short_description = 'Ziyaretçi'
