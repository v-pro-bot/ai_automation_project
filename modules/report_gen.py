from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

def create_pdf_report(summary_text, title, client_name):
    filename = f"reports/{client_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(f"<b>{title}</b>", styles['Title']),
        Spacer(1, 12),
        Paragraph(f"Client: {client_name}", styles['Normal']),
        Spacer(1, 12),
        Paragraph(summary_text.replace("\n", "<br/>"), styles['Normal']),
    ]
    doc.build(elements)
    return filename
