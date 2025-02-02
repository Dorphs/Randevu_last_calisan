from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ToplantiOdasi, Toplanti, Ziyaretci, KurumDisiZiyaretci, KurumDisiKatilimci

class UserSerializer(serializers.ModelSerializer):
    """Kullanıcı bilgilerini serialize eden sınıf"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class ToplantiOdasiSerializer(serializers.ModelSerializer):
    """Toplantı odası bilgilerini serialize eden sınıf"""
    class Meta:
        model = ToplantiOdasi
        fields = '__all__'

class KurumDisiKatilimciSerializer(serializers.ModelSerializer):
    """Kurum dışı katılımcı serializer"""
    class Meta:
        model = KurumDisiKatilimci
        fields = ['id', 'ad', 'soyad', 'kurum_unvan']

class KurumDisiZiyaretciSerializer(serializers.ModelSerializer):
    """Kurum dışı ziyaretçi serializer"""
    class Meta:
        model = KurumDisiZiyaretci
        fields = ['id', 'ad', 'soyad', 'telefon', 'kurum_unvan']

class ToplantiSerializer(serializers.ModelSerializer):
    """Toplantı serializer"""
    oda = ToplantiOdasiSerializer(read_only=True)
    oda_id = serializers.PrimaryKeyRelatedField(
        queryset=ToplantiOdasi.objects.all(),
        write_only=True,
        source='oda'
    )
    olusturan = UserSerializer(read_only=True)
    olusturan_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='olusturan'
    )
    katilimcilar = UserSerializer(many=True, read_only=True)
    katilimci_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        source='katilimcilar',
        required=False
    )
    kurum_disi_katilimcilar = KurumDisiKatilimciSerializer(many=True, read_only=True)
    kurum_disi_katilimcilar_data = serializers.ListField(
        child=KurumDisiKatilimciSerializer(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Toplanti
        fields = [
            'id', 'baslik', 'konu', 'baslangic_zamani', 'bitis_zamani',
            'oda', 'oda_id', 'durum', 'tur', 'olusturan', 'olusturan_id',
            'katilimcilar', 'katilimci_ids',
            'kurum_disi_katilimcilar', 'kurum_disi_katilimcilar_data',
            'notlar'
        ]

    def create(self, validated_data):
        """Toplantı oluştur"""
        kurum_disi_data = validated_data.pop('kurum_disi_katilimcilar_data', [])
        toplanti = super().create(validated_data)

        # Kurum dışı katılımcıları oluştur ve ilişkilendir
        for katilimci_data in kurum_disi_data:
            katilimci = KurumDisiKatilimci.objects.create(**katilimci_data)
            toplanti.kurum_disi_katilimcilar.add(katilimci)

        return toplanti

    def update(self, instance, validated_data):
        """Toplantı güncelle"""
        kurum_disi_data = validated_data.pop('kurum_disi_katilimcilar_data', [])
        toplanti = super().update(instance, validated_data)

        # Mevcut kurum dışı katılımcıları temizle
        toplanti.kurum_disi_katilimcilar.clear()

        # Yeni kurum dışı katılımcıları oluştur ve ilişkilendir
        for katilimci_data in kurum_disi_data:
            katilimci = KurumDisiKatilimci.objects.create(**katilimci_data)
            toplanti.kurum_disi_katilimcilar.add(katilimci)

        return toplanti

class ZiyaretciSerializer(serializers.ModelSerializer):
    """Ziyaretçi serializer"""
    ziyaret_edilen = UserSerializer(read_only=True)
    ziyaret_edilen_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='ziyaret_edilen'
    )
    kurum_ici_ziyaretciler = UserSerializer(many=True, read_only=True)
    kurum_ici_ziyaretci_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        source='kurum_ici_ziyaretciler',
        required=False
    )
    kurum_disi_ziyaretciler = KurumDisiZiyaretciSerializer(many=True, read_only=True)
    kurum_disi_ziyaretciler_data = serializers.ListField(
        child=KurumDisiZiyaretciSerializer(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Ziyaretci
        fields = [
            'id', 'ziyaret_nedeni', 'randevulu', 'randevu_zamani', 'ziyaret_zamani',
            'ziyaret_bitis_zamani', 'ziyaret_edilen', 'ziyaret_edilen_id', 'durum', 'tur',
            'kurum_ici_ziyaretciler', 'kurum_ici_ziyaretci_ids',
            'kurum_disi_ziyaretciler', 'kurum_disi_ziyaretciler_data',
            'notlar'
        ]
        read_only_fields = ['ziyaret_zamani']

    def validate(self, data):
        """Özel validasyon kuralları"""
        if not data.get('ziyaret_edilen'):
            raise serializers.ValidationError({'ziyaret_edilen': 'Ziyaret edilen kişi seçilmelidir.'})

        if not data.get('ziyaret_nedeni'):
            raise serializers.ValidationError({'ziyaret_nedeni': 'Ziyaret nedeni belirtilmelidir.'})

        if data.get('tur') == 'KURUM_ICI':
            if not data.get('kurum_ici_ziyaretciler', []):
                raise serializers.ValidationError(
                    {'kurum_ici_ziyaretciler': 'En az bir kurum içi ziyaretçi seçilmelidir.'}
                )
            # Kurum içi ziyaretçi için kurum dışı ziyaretçiler boş olmalı
            data['kurum_disi_ziyaretciler_data'] = []
        else:  # KURUM_DISI
            if not data.get('kurum_disi_ziyaretciler_data', []):
                raise serializers.ValidationError(
                    {'kurum_disi_ziyaretciler': 'En az bir kurum dışı ziyaretçi eklenmelidir.'}
                )
            # Kurum dışı ziyaretçi için kurum içi ziyaretçiler boş olmalı
            data['kurum_ici_ziyaretciler'] = []

        return data

    def create(self, validated_data):
        """Ziyaretçi oluştur"""
        kurum_disi_data = validated_data.pop('kurum_disi_ziyaretciler_data', [])
        ziyaretci = super().create(validated_data)

        # Kurum dışı ziyaretçileri oluştur ve ilişkilendir
        for ziyaretci_data in kurum_disi_data:
            kurum_disi = KurumDisiZiyaretci.objects.create(**ziyaretci_data)
            ziyaretci.kurum_disi_ziyaretciler.add(kurum_disi)

        return ziyaretci

    def update(self, instance, validated_data):
        """Ziyaretçi güncelle"""
        kurum_disi_data = validated_data.pop('kurum_disi_ziyaretciler_data', [])
        ziyaretci = super().update(instance, validated_data)

        # Mevcut kurum dışı ziyaretçileri temizle
        ziyaretci.kurum_disi_ziyaretciler.clear()

        # Yeni kurum dışı ziyaretçileri oluştur ve ilişkilendir
        for ziyaretci_data in kurum_disi_data:
            kurum_disi = KurumDisiZiyaretci.objects.create(**ziyaretci_data)
            ziyaretci.kurum_disi_ziyaretciler.add(kurum_disi)

        return ziyaretci
