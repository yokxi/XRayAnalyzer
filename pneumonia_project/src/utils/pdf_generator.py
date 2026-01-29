from fpdf import FPDF
from datetime import datetime
import io


class MedicalReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(37, 99, 235)
        self.cell(0, 10, 'XRayAnalyzer', 0, 1, 'C')
        self.set_font('Helvetica', '', 11)
        self.set_text_color(100, 116, 139)
        self.cell(0, 6, 'Report Diagnostico AI', 0, 1, 'C')
        self.set_font('Helvetica', '', 9)
        self.cell(0, 5, f'Generato il: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        self.ln(8)
        self.set_draw_color(226, 232, 240)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

    def add_diagnosis_summary(self, cls_data, detections):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(30, 41, 59)
        self.cell(0, 10, 'Sintesi Diagnostica', 0, 1)
        self.ln(2)

        is_positive = cls_data['is_positive']
        confidence = cls_data['confidence'] * 100

        # Diagnosis box
        if is_positive:
            self.set_fill_color(254, 226, 226)
            self.set_text_color(153, 27, 27)
            status = "POSITIVO - Polmonite Rilevata"
        else:
            self.set_fill_color(220, 252, 231)
            self.set_text_color(22, 101, 52)
            status = "NEGATIVO - Reperti Normali"

        self.set_font('Helvetica', 'B', 11)
        self.cell(0, 10, f'  Diagnosi: {status}', 0, 1, 'L', fill=True)
        self.ln(3)

        self.set_text_color(30, 41, 59)
        self.set_font('Helvetica', '', 11)
        self.cell(0, 8, f'Punteggio di Confidenza: {confidence:.1f}%', 0, 1)
        self.cell(0, 8, f'Anomalie Focali Rilevate: {len(detections)} aree', 0, 1)
        self.ln(8)

    def add_reasoning_step(self, step_number, title, content, image=None):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(37, 99, 235)
        self.cell(0, 10, f'{step_number}. {title}', 0, 1)

        self.set_font('Helvetica', '', 10)
        self.set_text_color(30, 41, 59)

        # Clean markdown formatting for PDF
        clean_content = content.replace('**', '').replace('*', '').replace('#', '')
        self.multi_cell(0, 6, clean_content)

        if image is not None:
            try:
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                # Center the image: page width 210mm, image width 70mm -> x = (210-70)/2 = 70
                self.image(img_buffer, x=70, w=70)
            except Exception:
                pass

        self.ln(6)

    def add_disclaimer(self):
        self.ln(10)
        self.set_draw_color(226, 232, 240)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

        self.set_fill_color(254, 252, 232)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(133, 77, 14)
        self.cell(0, 6, '  DISCLAIMER MEDICO', 0, 1, fill=True)

        self.set_font('Helvetica', '', 8)
        disclaimer = (
            "Questo report e generato da un sistema di Intelligenza Artificiale "
            "ed e inteso esclusivamente come supporto alla decisione clinica. "
            "Non sostituisce il giudizio di un radiologo qualificato. "
            "Consultare sempre un professionista medico per la diagnosi finale."
        )
        self.multi_cell(0, 5, disclaimer)


def generate_pdf_report(reasoning_data, cls_data, detections):
    """
    Genera il PDF completo del report diagnostico.

    Args:
        reasoning_data: dict con 'steps' e 'full_markdown'
        cls_data: dict con 'is_positive' e 'confidence'
        detections: lista di rilevamenti

    Returns:
        bytes: contenuto del PDF
    """
    pdf = MedicalReportPDF()
    pdf.add_page()

    pdf.add_diagnosis_summary(cls_data, detections)

    for i, step in enumerate(reasoning_data['steps'], 1):
        pdf.add_reasoning_step(
            step_number=i,
            title=step['title'],
            content=step['content'],
            image=step.get('image')
        )

    pdf.add_disclaimer()

    return bytes(pdf.output())
