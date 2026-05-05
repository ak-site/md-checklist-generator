#!/usr/bin/env python3
"""
Markdown to Checklist PDF Generator

md-checklist-generator v1.0.0
@license MIT
@author Andrey Kalinin
@repo https://github.com/ak-site/md-checklist-generator
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, Line
from datetime import datetime
import os
import sys

# ============================================
# SETTINGS
# ============================================
CHECKBOX_SIZE = 5 * mm
FONT_DIR = "fonts"
FONT_PATH = os.path.join(FONT_DIR, "PTSans-Regular.ttf")
FONT_BOLD_PATH = os.path.join(FONT_DIR, "PTSans-Bold.ttf")

def register_fonts():
    """Register custom fonts"""
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont('PTSans', FONT_PATH))
        if os.path.exists(FONT_BOLD_PATH):
            pdfmetrics.registerFont(TTFont('PTSansBold', FONT_BOLD_PATH))
            return {'regular': 'PTSans', 'bold': 'PTSansBold'}
        return {'regular': 'PTSans', 'bold': 'PTSans'}
    return {'regular': 'Helvetica', 'bold': 'Helvetica-Bold'}

def create_checkbox(checked=False):
    """Create checkbox (empty or with checkmark)"""
    drawing = Drawing(CHECKBOX_SIZE, CHECKBOX_SIZE)
    color = '#4CAF50' if checked else '#999999'
    drawing.add(Rect(0, 0, CHECKBOX_SIZE, CHECKBOX_SIZE, 
                     fillColor=None if checked else white, 
                     strokeColor=HexColor(color), strokeWidth=1))
    
    if checked:
        # Add checkmark symbol inside the box with manual adjustment
        from reportlab.graphics.shapes import String
        # Adjust y-offset (0 is bottom, CHECKBOX_SIZE is top)
        y_offset = CHECKBOX_SIZE * -0.20
        drawing.add(String(CHECKBOX_SIZE/2, CHECKBOX_SIZE/2 + y_offset, "✓", 
                          fontName='Helvetica', fontSize=CHECKBOX_SIZE * 0.65,
                          fillColor=HexColor(color), textAnchor='middle'))
    return drawing

def parse_markdown(filepath):
    """Parse Markdown file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.rstrip() for line in f.readlines()]
    
    data = {'title': '', 'sections': [], 'notes': ''}
    current_section = None
    current_items = []
    
    for line in lines:
        if line.startswith('# ') and not data['title']:
            data['title'] = line[2:].strip()
        elif line.startswith('## '):
            if current_section and current_items:
                data['sections'].append({'name': current_section, 'items': current_items})
            current_section = line[3:].strip()
            current_items = []
        elif line.startswith('- ['):
            is_checked = '[x]' in line[:5]
            text = line[6:].strip()
            if text:
                current_items.append({'text': text, 'checked': is_checked})
        elif line.strip() and not line.startswith('#') and not line.startswith('- ['):
            data['notes'] += ('\n' + line) if data['notes'] else line
    
    if current_section and current_items:
        data['sections'].append({'name': current_section, 'items': current_items})
    
    return data

def generate_pdf(md_file, output_pdf=None):
    """Generate PDF checklist"""
    output_pdf = output_pdf or md_file.replace('.md', '.pdf')
    fonts = register_fonts()
    checklist = parse_markdown(md_file)
    
    # Build content
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Normal'], fontName=fonts['bold'], 
                                  fontSize=24, textColor=HexColor('#1a1a2e'), alignment=TA_CENTER, spaceAfter=20)
    section_style = ParagraphStyle('Section', parent=styles['Normal'], fontName=fonts['bold'],
                                    fontSize=14, textColor=HexColor('#e94560'), spaceBefore=15, spaceAfter=8)
    date_style = ParagraphStyle('Date', parent=styles['Normal'], fontName=fonts['regular'],
                                 fontSize=10, textColor=HexColor('#999999'), alignment=TA_CENTER)
    item_style = ParagraphStyle('Item', parent=styles['Normal'], fontName=fonts['regular'],
                                 fontSize=11, textColor=HexColor('#2c3e50'), leading=15)
    notes_style = ParagraphStyle('Notes', parent=styles['Normal'], fontName=fonts['regular'],
                                  fontSize=10, textColor=HexColor('#666666'), spaceBefore=15, spaceAfter=20)
    
    # Build content
    story = []
    story.append(Paragraph(checklist['title'] or "Checklist", title_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", date_style))
    story.append(Spacer(1, 15))
    
    # Add sections and items
    for section in checklist['sections']:
        story.append(Paragraph(section['name'], section_style))
        for item in section['items']:
            checkbox = create_checkbox(item['checked'])
            text = Paragraph(f'<strike>{item["text"]}</strike>' if item['checked'] else item['text'], item_style)
            
            table = Table([[checkbox, text]], colWidths=[CHECKBOX_SIZE + 5, None])
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('LEFTPADDING', (1, 0), (1, 0), 0),
                ('TOPPADDING', (1, 0), (1, 0), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            story.append(table)
        story.append(Spacer(1, 5))
    
    # Add notes
    if checklist['notes']:
        story.extend([Spacer(1, 30), Paragraph("Notes:", section_style), Spacer(1, 10)])
        story.append(Paragraph(checklist['notes'].replace('\n', '<br/><br/>'), notes_style))
        story.append(Spacer(1, 20))
    
    # Add signature lines
    story.append(Spacer(1, 60))
    doc_width = A4[0] - 40*mm
    story.append(Table([["_________________________", "_________________________"]], 
                       colWidths=[doc_width/2, doc_width/2],
                       style=[('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
    story.append(Table([["Signature", "Date"]], colWidths=[doc_width/2, doc_width/2],
                       style=[('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                              ('FONTNAME', (0, 0), (-1, -1), fonts['regular']),
                              ('FONTSIZE', (0, 0), (-1, -1), 10),
                              ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#666666'))]))
    
    # Generate PDF
    def add_page_elements(canvas, doc):
        canvas.saveState()
        canvas.setFont(fonts['regular'], 9)
        canvas.setFillColor(HexColor('#999999'))
        canvas.drawCentredString(doc.width/2 + doc.leftMargin, doc.bottomMargin - 10*mm, 
                                f"- {canvas.getPageNumber()} -")
        canvas.setFont(fonts['regular'], 8)
        canvas.setFillColor(HexColor('#4CAF50'))
        canvas.drawCentredString(doc.width/2 + doc.leftMargin, doc.bottomMargin - 15*mm, "https://github.com/ak-site/md-checklist-generator/")
        canvas.restoreState()
    
    doc = SimpleDocTemplate(output_pdf, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm,
                           topMargin=20*mm, bottomMargin=20*mm)
    doc.build(story, onFirstPage=add_page_elements, onLaterPages=add_page_elements)
    
    print(f"PDF created: {output_pdf}")
    return output_pdf

if __name__ == "__main__":
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        generate_pdf(sys.argv[1])
    elif os.path.exists("checklist.md"):
        generate_pdf("checklist.md")
    else:
        print(f"Usage: python {sys.argv[0]} <file.md>")
        sys.exit(1)