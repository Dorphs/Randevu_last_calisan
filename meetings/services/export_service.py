import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
import seaborn as sns
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import json

class ExportService:
    @staticmethod
    def export_data(data, format='excel'):
        """Veriyi belirtilen formatta dışa aktar"""
        if format == 'excel':
            return ExportService._export_to_excel(data)
        elif format == 'pdf':
            return ExportService._export_to_pdf(data)
        else:
            raise ValueError(f'Desteklenmeyen format: {format}')

    @staticmethod
    def _export_to_excel(data):
        """Veriyi Excel formatında dışa aktar"""
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'export_{timestamp}.xlsx'
        
        # Excel writer oluştur
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        workbook = writer.book
        
        # Genel bilgiler sayfası
        if 'dashboard_info' in data:
            info_df = pd.DataFrame([data['dashboard_info']])
            info_df.to_excel(writer, sheet_name='Genel Bilgiler', index=False)
        
        # Widget verileri
        if 'widgets' in data:
            for idx, widget in enumerate(data['widgets'], 1):
                sheet_name = f"Widget_{idx}"
                
                # Widget meta verileri
                meta_df = pd.DataFrame([{
                    'Başlık': widget['title'],
                    'Tip': widget['type']
                }])
                meta_df.to_excel(writer, sheet_name=sheet_name, startrow=0, index=False)
                
                # Widget verileri
                widget_data = widget['data']
                if isinstance(widget_data, dict):
                    if 'labels' in widget_data and any(
                        key in widget_data for key in ['meetings', 'participants', 'durations', 'visitors']
                    ):
                        # Zaman serisi verisi
                        series_data = {}
                        series_data['Tarih'] = widget_data['labels']
                        
                        for key in ['meetings', 'participants', 'durations', 'visitors']:
                            if key in widget_data:
                                series_data[key.capitalize()] = widget_data[key]
                        
                        df = pd.DataFrame(series_data)
                        df.to_excel(writer, sheet_name=sheet_name, startrow=3, index=False)
                        
                        # Grafik ekle
                        chart = workbook.add_chart({'type': 'line'})
                        for col in range(1, len(df.columns)):
                            chart.add_series({
                                'name': [sheet_name, 3, col],
                                'categories': [sheet_name, 4, 0, 4 + len(df) - 1, 0],
                                'values': [sheet_name, 4, col, 4 + len(df) - 1, col]
                            })
                        
                        worksheet = writer.sheets[sheet_name]
                        worksheet.insert_chart('H2', chart)
        
        # Excel dosyasını kaydet
        writer.close()
        output.seek(0)
        
        # Storage'a kaydet
        file_path = f'exports/{filename}'
        default_storage.save(file_path, output)
        
        return default_storage.url(file_path)

    @staticmethod
    def _export_to_pdf(data):
        """Veriyi PDF formatında dışa aktar"""
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f'export_{timestamp}.pdf'
        file_path = f'exports/{filename}'
        
        # PDF buffer
        buffer = BytesIO()
        
        # PDF dökümanı oluştur
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Stil tanımlamaları
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20
        )
        
        # PDF elementleri
        elements = []
        
        # Başlık
        if 'dashboard_info' in data:
            title = data['dashboard_info']['title']
            elements.append(Paragraph(title, title_style))
            
            # Dashboard bilgileri
            info_data = [
                ['Oluşturan', data['dashboard_info']['owner']],
                ['Oluşturma Tarihi', data['dashboard_info']['created_at'].strftime('%d.%m.%Y %H:%M')],
                ['Son Güncelleme', data['dashboard_info']['updated_at'].strftime('%d.%m.%Y %H:%M')]
            ]
            
            info_table = Table(info_data)
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (-1, -1), colors.beige),
                ('TEXTCOLOR', (1, 0), (-1, -1), colors.black),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 20))
        
        # Widget verileri
        if 'widgets' in data:
            for widget in data['widgets']:
                # Widget başlığı
                elements.append(Paragraph(widget['title'], heading_style))
                
                # Widget verilerini tabloya dönüştür
                widget_data = widget['data']
                if isinstance(widget_data, dict):
                    if 'labels' in widget_data:
                        # Grafik verisi
                        plt.figure(figsize=(8, 4))
                        sns.set_style("whitegrid")
                        
                        for key in ['meetings', 'participants', 'durations', 'visitors']:
                            if key in widget_data:
                                plt.plot(
                                    widget_data['labels'],
                                    widget_data[key],
                                    marker='o',
                                    label=key.capitalize()
                                )
                        
                        plt.title(widget['title'])
                        plt.xticks(rotation=45)
                        plt.legend()
                        plt.tight_layout()
                        
                        # Grafiği PDF'e ekle
                        img_buffer = BytesIO()
                        plt.savefig(img_buffer, format='png')
                        img_buffer.seek(0)
                        
                        elements.append(Image(img_buffer))
                        elements.append(Spacer(1, 20))
                        
                        plt.close()
        
        # PDF oluştur
        doc.build(elements)
        buffer.seek(0)
        
        # Storage'a kaydet
        default_storage.save(file_path, buffer)
        
        return default_storage.url(file_path)
