from django.shortcuts import render
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.db.models import Count, Avg, F, Q
from django.db.models.functions import TruncDate, TruncMonth, ExtractHour, ExtractYear, ExtractMonth
from django.utils import timezone
from datetime import timedelta
from .models import ToplantiOdasi, Toplanti, Ziyaretci
from .serializers import UserSerializer, ToplantiOdasiSerializer, ToplantiSerializer, ZiyaretciSerializer

# Create your views here.

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    Kullanıcı girişi için API endpoint'i
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if username is None or password is None:
        return Response({'error': 'Lütfen kullanıcı adı ve şifre giriniz'},
                      status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Geçersiz kullanıcı adı veya şifre'},
                      status=status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user_id': user.pk,
        'username': user.username
    })

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Kullanıcı listesi ve detaylarını görüntüleme API'si
    Sadece okuma izni vardır, değişiklik yapılamaz
    """
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']

class ToplantiOdasiViewSet(viewsets.ModelViewSet):
    """
    Toplantı odası CRUD işlemleri için API
    """
    queryset = ToplantiOdasi.objects.all().order_by('ad')
    serializer_class = ToplantiOdasiSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['ad']
    filterset_fields = ['kapasite']

class ToplantiViewSet(viewsets.ModelViewSet):
    """
    Toplantı CRUD işlemleri için API
    """
    queryset = Toplanti.objects.all().order_by('-baslangic_zamani')
    serializer_class = ToplantiSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['baslik', 'konu']
    filterset_fields = ['durum', 'tur', 'oda', 'olusturan', 'katilimcilar']
    
    def perform_create(self, serializer):
        """Toplantı oluşturan kişiyi otomatik olarak ayarla"""
        serializer.save(olusturan=self.request.user)

class ZiyaretciViewSet(viewsets.ModelViewSet):
    """
    Ziyaretçi CRUD işlemleri için API
    """
    queryset = Ziyaretci.objects.all().order_by('-ziyaret_zamani')
    serializer_class = ZiyaretciSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['ad', 'soyad', 'kurum']
    filterset_fields = ['durum', 'randevulu', 'ziyaret_edilen']

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def ziyaretci_raporlari(request):
    """Ziyaretçi istatistiklerini ve raporlarını döndürür"""
    try:
        # Tarih filtresi parametrelerini al
        baslangic_str = request.GET.get('baslangic')
        bitis_str = request.GET.get('bitis')

        # Varsayılan olarak bu ayın başlangıcı ve sonu
        if not baslangic_str:
            bugun = timezone.now()
            baslangic = bugun.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            baslangic = timezone.datetime.strptime(baslangic_str, '%Y-%m-%d')
            baslangic = timezone.make_aware(baslangic)

        if not bitis_str:
            bitis = timezone.now()
        else:
            bitis = timezone.datetime.strptime(bitis_str, '%Y-%m-%d')
            bitis = timezone.make_aware(bitis.replace(hour=23, minute=59, second=59, microsecond=999999))
        
        # Günlük ziyaretçi sayıları
        gunluk_ziyaretler = Ziyaretci.objects.filter(
            ziyaret_zamani__gte=baslangic,
            ziyaret_zamani__lte=bitis
        ).annotate(
            tarih=TruncDate('ziyaret_zamani')
        ).values('tarih').annotate(
            toplam=Count('id'),
            kurum_ici=Count('id', filter=Q(tur='KURUM_ICI')),
            kurum_disi=Count('id', filter=Q(tur='KURUM_DISI'))
        ).order_by('tarih')

        # Ziyaret saatlerine göre dağılım
        saat_dagilimi = Ziyaretci.objects.filter(
            ziyaret_zamani__gte=baslangic,
            ziyaret_zamani__lte=bitis
        ).annotate(
            saat=ExtractHour('ziyaret_zamani')
        ).values('saat').annotate(
            toplam=Count('id')
        ).order_by('saat')

        # En çok ziyaret edilen kişiler
        en_cok_ziyaret_edilenler = Ziyaretci.objects.filter(
            ziyaret_zamani__gte=baslangic,
            ziyaret_zamani__lte=bitis
        ).values(
            'ziyaret_edilen__username',
            'ziyaret_edilen__first_name',
            'ziyaret_edilen__last_name'
        ).annotate(
            toplam_ziyaret=Count('id')
        ).order_by('-toplam_ziyaret')[:10]

        # Randevulu/Randevusuz oranı
        randevu_durumu = {
            'randevulu': Ziyaretci.objects.filter(
                ziyaret_zamani__gte=baslangic,
                ziyaret_zamani__lte=bitis,
                randevulu=True
            ).count(),
            'randevusuz': Ziyaretci.objects.filter(
                ziyaret_zamani__gte=baslangic,
                ziyaret_zamani__lte=bitis,
                randevulu=False
            ).count()
        }

        return Response({
            'gunluk_ziyaretler': list(gunluk_ziyaretler),
            'saat_dagilimi': list(saat_dagilimi),
            'en_cok_ziyaret_edilenler': list(en_cok_ziyaret_edilenler),
            'randevu_durumu': randevu_durumu,
            'filtre': {
                'baslangic': baslangic.strftime('%Y-%m-%d'),
                'bitis': bitis.strftime('%Y-%m-%d')
            }
        })
    except Exception as e:
        print(f"Hata: {str(e)}")
        return Response(
            {'error': f'Rapor oluşturulurken hata oluştu: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def toplanti_raporlari(request):
    """Toplantı istatistiklerini ve raporlarını döndürür"""
    try:
        # Tarih filtresi parametrelerini al
        baslangic_str = request.GET.get('baslangic')
        bitis_str = request.GET.get('bitis')

        # Varsayılan olarak bu ayın başlangıcı ve sonu
        if not baslangic_str:
            bugun = timezone.now()
            baslangic = bugun.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            baslangic = timezone.datetime.strptime(baslangic_str, '%Y-%m-%d')
            baslangic = timezone.make_aware(baslangic)

        if not bitis_str:
            bitis = timezone.now()
        else:
            bitis = timezone.datetime.strptime(bitis_str, '%Y-%m-%d')
            bitis = timezone.make_aware(bitis.replace(hour=23, minute=59, second=59, microsecond=999999))
        
        # Günlük toplantı sayıları
        gunluk_toplantilar = Toplanti.objects.filter(
            baslangic_zamani__gte=baslangic,
            baslangic_zamani__lte=bitis
        ).annotate(
            tarih=TruncDate('baslangic_zamani')
        ).values('tarih').annotate(
            toplam=Count('id'),
            kurum_ici=Count('id', filter=Q(tur='KURUM_ICI')),
            kurum_disi=Count('id', filter=Q(tur='KURUM_DISI'))
        ).order_by('tarih')

        # Toplantı odası kullanım istatistikleri
        oda_kullanimi = Toplanti.objects.filter(
            baslangic_zamani__gte=baslangic,
            baslangic_zamani__lte=bitis
        ).values(
            'oda__ad'
        ).annotate(
            toplam_toplanti=Count('id'),
            ortalama_sure=Avg(
                F('bitis_zamani') - F('baslangic_zamani'),
                filter=Q(bitis_zamani__isnull=False)
            )
        ).order_by('-toplam_toplanti')

        # Toplantı saatlerine göre dağılım
        saat_dagilimi = Toplanti.objects.filter(
            baslangic_zamani__gte=baslangic,
            baslangic_zamani__lte=bitis
        ).annotate(
            saat=ExtractHour('baslangic_zamani')
        ).values('saat').annotate(
            toplam=Count('id')
        ).order_by('saat')

        # Aylık toplantı istatistikleri
        aylik_istatistikler = Toplanti.objects.filter(
            baslangic_zamani__gte=baslangic,
            baslangic_zamani__lte=bitis
        ).annotate(
            ay=TruncMonth('baslangic_zamani')
        ).values('ay').annotate(
            toplam=Count('id'),
            kurum_ici=Count('id', filter=Q(tur='KURUM_ICI')),
            kurum_disi=Count('id', filter=Q(tur='KURUM_DISI'))
        ).order_by('ay')

        return Response({
            'gunluk_toplantilar': list(gunluk_toplantilar),
            'oda_kullanimi': list(oda_kullanimi),
            'saat_dagilimi': list(saat_dagilimi),
            'aylik_istatistikler': list(aylik_istatistikler),
            'filtre': {
                'baslangic': baslangic.strftime('%Y-%m-%d'),
                'bitis': bitis.strftime('%Y-%m-%d')
            }
        })
    except Exception as e:
        print(f"Hata: {str(e)}")
        return Response(
            {'error': f'Rapor oluşturulurken hata oluştu: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mevcut_tarihler(request):
    """Veritabanında kayıtlı olan yıl ve ayları döndürür"""
    try:
        # Ziyaretçi kayıtlarından mevcut yıl ve ayları al
        ziyaretci_tarihler = Ziyaretci.objects.annotate(
            yil=ExtractYear('ziyaret_zamani'),
            ay=ExtractMonth('ziyaret_zamani')
        ).values('yil', 'ay').distinct().order_by('-yil', '-ay')

        # Toplantı kayıtlarından mevcut yıl ve ayları al
        toplanti_tarihler = Toplanti.objects.annotate(
            yil=ExtractYear('baslangic_zamani'),
            ay=ExtractMonth('baslangic_zamani')
        ).values('yil', 'ay').distinct().order_by('-yil', '-ay')

        # İki queryset'i birleştir ve tekrar eden kayıtları kaldır
        tum_tarihler = []
        tarih_seti = set()

        for kayit in list(ziyaretci_tarihler) + list(toplanti_tarihler):
            tarih_tuple = (kayit['yil'], kayit['ay'])
            if tarih_tuple not in tarih_seti:
                tarih_seti.add(tarih_tuple)
                tum_tarihler.append({
                    'yil': kayit['yil'],
                    'ay': kayit['ay'],
                    'ay_adi': [
                        'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                        'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'
                    ][kayit['ay'] - 1]
                })

        # Tarihleri sırala (yıla göre azalan, aya göre azalan)
        tum_tarihler.sort(key=lambda x: (-x['yil'], -x['ay']))

        return Response({
            'tarihler': tum_tarihler
        })
    except Exception as e:
        print(f"Hata: {str(e)}")
        return Response(
            {'error': f'Tarihler alınırken hata oluştu: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
