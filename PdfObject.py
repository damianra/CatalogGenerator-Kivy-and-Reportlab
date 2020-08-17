# -*- coding:utf-8 -*-
import os
# Librerias reportlab a usar:
from reportlab.lib import styles
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (BaseDocTemplate, Frame, Paragraph, NextPageTemplate, PageBreak, PageTemplate, Spacer,
                                Image)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, _baseFontNameB
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4


def encabezado(canvas, doc):
    canvas.saveState()
    canvas.setFont('Times-Roman', 9)
    canvas.drawString(inch, A4[1] - 40, "Products Catalog")
    canvas.drawString(450, 800, "WhatsApp: xxxxxxxxx")
    canvas.drawString(450, 780, "Email: xxxxxxxx@gmail.com")
    canvas.drawImage('ubuntu.png', 240, 680)
    canvas.restoreState()


class CreatePDF:
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.story = []
        self.style = getSampleStyleSheet()

    def add_data(self):
        sty = ParagraphStyle(name='Heading2',
                             parent=self.style['Normal'],
                             fontName=_baseFontNameB,
                             fontSize=10,
                             spaceAfter=5,
                             alignment=TA_CENTER)
        for p in self.data:
            self.story.append(Image(p[4], width=150, height=150))
            self.story.append(Spacer(0, 10))
            self.story.append(Paragraph(p[1], sty))
            self.story.append(Paragraph(p[2], sty))
            self.story.append(Paragraph('Precio: '+p[3], sty))
        frame1 = Frame(inch, inch-100, 100, 697, id='col1')
        frame2 = Frame(inch + 175, inch-100, 100, 697, id='col2')
        frame3 = Frame(inch + 350, inch-100, 100, 697, id='col3')
        PTUnaColumna = PageTemplate(id='UnaColumna', frames=[frame1, frame2, frame3],
                                    onPage=encabezado)
        doc = BaseDocTemplate(self.name, pageTemplates=[PTUnaColumna],
                              pagesize=A4)
        doc.build(self.story)

