from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from meetings.models import Visitor, MeetingRoom, Meeting
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Örnek veriler oluşturur'

    def handle(self, *args, **kwargs):
        # Admin kullanıcısını al veya oluştur
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'email': 'admin@example.com'
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        # Toplantı Odaları
        meeting_rooms_data = [
            {'name': 'Yönetim Kurulu Salonu', 'capacity': 20, 'floor': '5', 'room_number': '501', 
             'equipment': 'Projeksiyon, Video konferans sistemi, Akıllı tahta'},
            {'name': 'Genel Müdür Toplantı Odası', 'capacity': 10, 'floor': '5', 'room_number': '502',
             'equipment': 'Video konferans sistemi, LCD Ekran'},
            {'name': 'Küçük Toplantı Odası 1', 'capacity': 6, 'floor': '4', 'room_number': '401',
             'equipment': 'LCD Ekran, Whiteboard'},
            {'name': 'Küçük Toplantı Odası 2', 'capacity': 6, 'floor': '4', 'room_number': '402',
             'equipment': 'LCD Ekran, Whiteboard'},
            {'name': 'Orta Toplantı Salonu', 'capacity': 12, 'floor': '4', 'room_number': '403',
             'equipment': 'Projeksiyon, Ses sistemi'},
            {'name': 'AR-GE Toplantı Odası', 'capacity': 8, 'floor': '3', 'room_number': '301',
             'equipment': 'Akıllı tahta, Video konferans sistemi'},
            {'name': 'Satış Toplantı Odası', 'capacity': 8, 'floor': '3', 'room_number': '302',
             'equipment': 'LCD Ekran, Whiteboard'},
            {'name': 'Eğitim Salonu', 'capacity': 30, 'floor': '2', 'room_number': '201',
             'equipment': 'Projeksiyon, Ses sistemi, Whiteboard'},
            {'name': 'Görüşme Odası 1', 'capacity': 4, 'floor': '5', 'room_number': '503',
             'equipment': 'LCD Ekran'},
            {'name': 'Görüşme Odası 2', 'capacity': 4, 'floor': '5', 'room_number': '504',
             'equipment': 'LCD Ekran'},
        ]

        for room_data in meeting_rooms_data:
            MeetingRoom.objects.get_or_create(
                name=room_data['name'],
                defaults=room_data
            )

        # Ziyaretçiler
        visitors_data = [
            {'name': 'Ahmet Yılmaz', 'company': 'Tekno A.Ş.', 'phone': '0532 111 2233', 'email': 'ahmet@tekno.com'},
            {'name': 'Mehmet Kaya', 'company': 'İnşaat Ltd.', 'phone': '0533 222 3344', 'email': 'mehmet@insaat.com'},
            {'name': 'Ayşe Demir', 'company': 'Yazılım Corp.', 'phone': '0534 333 4455', 'email': 'ayse@yazilim.com'},
            {'name': 'Fatma Çelik', 'company': 'Danışmanlık A.Ş.', 'phone': '0535 444 5566', 'email': 'fatma@danismanlik.com'},
            {'name': 'Ali Öztürk', 'company': 'Finans Bank', 'phone': '0536 555 6677', 'email': 'ali@finans.com'},
            {'name': 'Zeynep Aydın', 'company': 'Medya Group', 'phone': '0537 666 7788', 'email': 'zeynep@medya.com'},
            {'name': 'Mustafa Şahin', 'company': 'Enerji Ltd.', 'phone': '0538 777 8899', 'email': 'mustafa@enerji.com'},
            {'name': 'Elif Yıldız', 'company': 'Eğitim A.Ş.', 'phone': '0539 888 9900', 'email': 'elif@egitim.com'},
            {'name': 'Can Aksoy', 'company': 'Lojistik Ltd.', 'phone': '0530 999 0011', 'email': 'can@lojistik.com'},
            {'name': 'Deniz Korkmaz', 'company': 'Sağlık Corp.', 'phone': '0531 000 1122', 'email': 'deniz@saglik.com'},
        ]

        created_visitors = []
        for visitor_data in visitors_data:
            visitor, _ = Visitor.objects.get_or_create(
                email=visitor_data['email'],
                defaults=visitor_data
            )
            created_visitors.append(visitor)

        # Toplantılar
        meeting_types = ['SCHEDULED', 'UNSCHEDULED', 'EXTERNAL', 'INTERNAL']
        meeting_titles = [
            'Proje Değerlendirme', 'İş Görüşmesi', 'Strateji Toplantısı', 'Satış Görüşmesi',
            'Yıllık Değerlendirme', 'Ürün Tanıtımı', 'Müşteri Görüşmesi', 'Eğitim Toplantısı',
            'Bütçe Görüşmesi', 'AR-GE Toplantısı'
        ]

        now = timezone.now()
        rooms = list(MeetingRoom.objects.all())

        for i in range(10):
            start_time = now + timedelta(days=random.randint(0, 30), hours=random.randint(9, 16))
            end_time = start_time + timedelta(hours=random.randint(1, 3))
            
            Meeting.objects.create(
                title=random.choice(meeting_titles),
                visitor=random.choice(created_visitors),
                meeting_type=random.choice(meeting_types),
                status='APPROVED',
                priority=random.choice(['LOW', 'MEDIUM', 'HIGH']),
                start_time=start_time,
                end_time=end_time,
                location=random.choice(rooms),
                description=f'Örnek toplantı açıklaması {i+1}',
                agenda=f'1. Gündem maddesi\n2. Gündem maddesi\n3. Gündem maddesi',
                created_by=admin_user
            )

        self.stdout.write(self.style.SUCCESS('Örnek veriler başarıyla oluşturuldu'))
