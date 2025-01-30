from django.test import TestCase
from django.core.files.storage import default_storage
from django.utils import timezone
from ..services.export_service import ExportService
import os
import pandas as pd

class ExportServiceTests(TestCase):
    def setUp(self):
        self.test_data = {
            'dashboard_info': {
                'title': 'Test Dashboard',
                'owner': 'Test User',
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            },
            'widgets': [
                {
                    'title': 'Test Widget 1',
                    'type': 'MEETING_TREND',
                    'data': {
                        'labels': ['01.01', '02.01', '03.01'],
                        'meetings': [5, 8, 3]
                    }
                },
                {
                    'title': 'Test Widget 2',
                    'type': 'MEETING_STATUS',
                    'data': {
                        'completed': 10,
                        'planned': 5,
                        'cancelled': 2
                    }
                }
            ]
        }
    
    def tearDown(self):
        # Test dosyalarını temizle
        for filename in default_storage.listdir('exports')[1]:
            if filename.startswith('export_'):
                default_storage.delete(f'exports/{filename}')
    
    def test_export_to_excel(self):
        """Excel export testi"""
        file_url = ExportService._export_to_excel(self.test_data)
        
        self.assertTrue(file_url.endswith('.xlsx'))
        self.assertTrue(default_storage.exists(file_url.split('/')[-1]))
        
        # Excel dosyasını kontrol et
        file_path = default_storage.path(file_url.split('/')[-1])
        df = pd.read_excel(file_path, sheet_name=None)
        
        # Genel bilgiler sayfasını kontrol et
        self.assertIn('Genel Bilgiler', df)
        
        # Widget sayfalarını kontrol et
        self.assertIn('Widget_1', df)
        self.assertIn('Widget_2', df)
        
    def test_export_to_pdf(self):
        """PDF export testi"""
        file_url = ExportService._export_to_pdf(self.test_data)
        
        self.assertTrue(file_url.endswith('.pdf'))
        self.assertTrue(default_storage.exists(file_url.split('/')[-1]))
        
    def test_export_data_invalid_format(self):
        """Geçersiz format testi"""
        with self.assertRaises(ValueError):
            ExportService.export_data(self.test_data, 'invalid_format')
            
    def test_export_empty_data(self):
        """Boş veri export testi"""
        empty_data = {
            'dashboard_info': {
                'title': 'Empty Dashboard',
                'owner': 'Test User',
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            },
            'widgets': []
        }
        
        # Excel
        excel_url = ExportService.export_data(empty_data, 'excel')
        self.assertTrue(excel_url.endswith('.xlsx'))
        
        # PDF
        pdf_url = ExportService.export_data(empty_data, 'pdf')
        self.assertTrue(pdf_url.endswith('.pdf'))
        
    def test_export_large_dataset(self):
        """Büyük veri seti export testi"""
        large_data = {
            'dashboard_info': self.test_data['dashboard_info'],
            'widgets': [
                {
                    'title': 'Large Widget',
                    'type': 'MEETING_TREND',
                    'data': {
                        'labels': [f'Day {i}' for i in range(100)],
                        'meetings': [i * 2 for i in range(100)]
                    }
                }
            ]
        }
        
        # Excel
        excel_url = ExportService.export_data(large_data, 'excel')
        self.assertTrue(excel_url.endswith('.xlsx'))
        
        # PDF
        pdf_url = ExportService.export_data(large_data, 'pdf')
        self.assertTrue(pdf_url.endswith('.pdf'))
        
    def test_export_special_characters(self):
        """Özel karakterler ile export testi"""
        special_data = {
            'dashboard_info': {
                'title': 'Özel Karakterli Dashboard !@#$%^&*()',
                'owner': 'Test Kullanıcı ğüşiöç',
                'created_at': timezone.now(),
                'updated_at': timezone.now()
            },
            'widgets': self.test_data['widgets']
        }
        
        # Excel
        excel_url = ExportService.export_data(special_data, 'excel')
        self.assertTrue(excel_url.endswith('.xlsx'))
        
        # PDF
        pdf_url = ExportService.export_data(special_data, 'pdf')
        self.assertTrue(pdf_url.endswith('.pdf'))
