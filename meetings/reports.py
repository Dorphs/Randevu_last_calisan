from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.utils import timezone
import io

def create_meeting_report_pdf(meetings, title="Toplantı Raporu"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    styles = getSampleStyleSheet()
    
    # Başlık
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))
    
    # Tablo başlıkları
    headers = ['Başlık', 'Ziyaretçi', 'Oda', 'Başlangıç', 'Bitiş', 'Durum', 'Tür']
    data = [headers]
    
    # Toplantı verileri
    for meeting in meetings:
        data.append([
            meeting.title,
            meeting.visitor.name,
            meeting.location.name,
            meeting.start_time.strftime("%Y-%m-%d %H:%M"),
            meeting.end_time.strftime("%Y-%m-%d %H:%M"),
            meeting.get_status_display(),
            meeting.get_meeting_type_display()
        ])
    
    # Tablo stili
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    # Tablo oluştur
    table = Table(data)
    table.setStyle(table_style)
    elements.append(table)
    
    # Rapor altbilgisi
    footer_text = f"Rapor oluşturma tarihi: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    # PDF oluştur
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf

def create_visitor_report_pdf(visitors, title="Ziyaretçi Raporu"):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    styles = getSampleStyleSheet()
    
    # Başlık
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))
    
    # Tablo başlıkları
    headers = ['İsim', 'Email', 'Şirket', 'Telefon', 'Toplantı Sayısı']
    data = [headers]
    
    # Ziyaretçi verileri
    for visitor in visitors:
        data.append([
            visitor.name,
            visitor.email,
            visitor.company,
            visitor.phone,
            visitor.meetings.count()
        ])
    
    # Tablo stili
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    # Tablo oluştur
    table = Table(data)
    table.setStyle(table_style)
    elements.append(table)
    
    # Rapor altbilgisi
    footer_text = f"Rapor oluşturma tarihi: {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    # PDF oluştur
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf
