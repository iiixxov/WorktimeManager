from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle


class Report:
    def __init__(self, name: str):
        self._name = name
        self._elements = []

        self._styles = getSampleStyleSheet()
        self._filename = f"reports/{self._name}.pdf".replace(' ', '_')
        self._doc = SimpleDocTemplate(self._filename, pagesize=landscape(letter))

        pdfmetrics.registerFont(TTFont("basic", "font.ttf"))
        for style_name, style in self._styles.byName.items():
            style.fontName = "basic"

    def add_h1(self, text: str):
        title_text = Paragraph(text, self._styles['Title'])
        self._elements.append(title_text)

    def add_h2(self, text: str):
        subtitle_text = Paragraph(text, self._styles['Heading2'])
        self._elements.append(subtitle_text)

    def add_table(self, headers: list, data: list):
        table = Table([headers] + data)
        table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black), ('FONT', (0, 0), (-1, -1), 'basic')]))
        self._elements.append(table)

    def create_pdf(self):
        self._doc.build(self._elements)
        return self._filename
