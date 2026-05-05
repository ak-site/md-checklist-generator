#!/usr/bin/env python3
"""
Markdown to Checklist PDF Generator
С поддержкой кастомных шрифтов и графических чекбоксов
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics import renderPDF
from datetime import datetime
import os

# ============================================
# НАСТРОЙКИ
# ============================================

# Путь к шрифту PT Sans (положите файл в ту же папку)
FONT_PATH = "PTSans-Regular.ttf"
FONT_BOLD_PATH = "PTSans-Bold.ttf"  # если есть, опционально

# Путь к иконке для чекбокса (PNG с галочкой)
CHECK_ICON_PATH = "check.png"  # положите картинку 10x10px или 15x15px

# Размер чекбокса в мм
CHECKBOX_SIZE = 5 * mm

def register_custom_fonts():
    """Регистрирует кастомные шрифты"""
    fonts = {}
    
    # Пробуем загрузить PT Sans
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont('PTSans', FONT_PATH))
        fonts['regular'] = 'PTSans'
        print("Загружен шрифт: PT Sans")
        
        # Пробуем загрузить жирный вариант
        if os.path.exists(FONT_BOLD_PATH):
            pdfmetrics.registerFont(TTFont('PTSansBold', FONT_BOLD_PATH))
            fonts['bold'] = 'PTSansBold'
        else:
            fonts['bold'] = 'PTSans'
    else:
        # Fallback на Arial
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
            fonts['regular'] = 'Arial'
            fonts['bold'] = 'Arial'
            print("Используется шрифт: Arial (системный)")
        except:
            fonts['regular'] = 'Helvetica'
            fonts['bold'] = 'Helvetica'
            print("Используется шрифт по умолчанию")
    
    return fonts

def load_checkbox_icon():
    """Загружает иконку для чекбокса или создает графическую"""
    if os.path.exists(CHECK_ICON_PATH):
        try:
            # Загружаем PNG иконку
            img = Image(CHECK_ICON_PATH, width=CHECKBOX_SIZE, height=CHECKBOX_SIZE)
            return img
        except Exception as e:
            print(f"Не удалось загрузить иконку: {e}")
    
    # Создаем простую графическую галочку (если нет PNG)
    print("Создаю графическую галочку (нет файла check.png)")
    drawing = Drawing(CHECKBOX_SIZE, CHECKBOX_SIZE)
    
    # Фон (белый или прозрачный)
    drawing.add(Rect(0, 0, CHECKBOX_SIZE, CHECKBOX_SIZE, 
                     fillColor=None, strokeColor=HexColor('#4CAF50'), 
                     strokeWidth=0.5))
    
    # Рисуем галочку
    line1 = Line(2, CHECKBOX_SIZE/2, CHECKBOX_SIZE/2.5, CHECKBOX_SIZE-3)
    line1.strokeColor = HexColor('#4CAF50')
    line1.strokeWidth = 1.2
    drawing.add(line1)
    
    line2 = Line(CHECKBOX_SIZE/2.5, CHECKBOX_SIZE-3, CHECKBOX_SIZE-2, 2)
    line2.strokeColor = HexColor('#4CAF50')
    line2.strokeWidth = 1.2
    drawing.add(line2)
    
    return drawing

def create_empty_checkbox():
    """Создает пустой чекбокс (квадрат)"""
    drawing = Drawing(CHECKBOX_SIZE, CHECKBOX_SIZE)
    drawing.add(Rect(0, 0, CHECKBOX_SIZE, CHECKBOX_SIZE,
                     fillColor=white, strokeColor=HexColor('#999999'),
                     strokeWidth=1))
    return drawing

def parse_markdown(md_file):
    """Парсит Markdown файл и возвращает структуру чек-листа"""
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    checklist = {
        'title': '',
        'sections': [],
        'notes': ''
    }
    
    current_section = None
    current_items = []
    
    for line in lines:
        line = line.rstrip()
        
        # Заголовок чек-листа
        if line.startswith('# ') and not checklist['title']:
            checklist['title'] = line[2:].strip()
        
        # Подзаголовки разделов
        elif line.startswith('## '):
            if current_section and current_items:
                checklist['sections'].append({
                    'name': current_section,
                    'items': current_items
                })
            current_section = line[3:].strip()
            current_items = []
        
        # Пункты чек-листа
        elif line.startswith('- [ ]'):
            item_text = line[6:].strip()
            if item_text:
                current_items.append({'text': item_text, 'checked': False})
        elif line.startswith('- [x]'):
            item_text = line[6:].strip()
            if item_text:
                current_items.append({'text': item_text, 'checked': True})
        
        # Примечания
        elif line.strip() and not line.startswith('#') and not line.startswith('- ['):
            if checklist['notes']:
                checklist['notes'] += '\n' + line
            else:
                checklist['notes'] = line
    
    # Добавляем последнюю секцию
    if current_section and current_items:
        checklist['sections'].append({
            'name': current_section,
            'items': current_items
        })
    
    return checklist

def create_checklist_pdf(md_file, output_pdf=None):
    """Создает PDF чек-лист с кастомным шрифтом и графическими чекбоксами"""
    
    if output_pdf is None:
        output_pdf = md_file.replace('.md', '.pdf')
    
    # Регистрируем шрифты
    fonts = register_custom_fonts()
    
    # Загружаем иконки для чекбоксов
    checked_icon = load_checkbox_icon()
    empty_icon = create_empty_checkbox()
    
    # Парсим Markdown
    checklist = parse_markdown(md_file)
    
    # Создаем PDF
    doc = SimpleDocTemplate(output_pdf, pagesize=A4,
                           rightMargin=20*mm, leftMargin=20*mm,
                           topMargin=20*mm, bottomMargin=20*mm)
    
    story = []
    
    # Стили
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ChecklistTitle',
        parent=styles['Normal'],
        fontName=fonts['bold'],
        fontSize=24,
        textColor=HexColor('#1a1a2e'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Normal'],
        fontName=fonts['bold'],
        fontSize=14,
        textColor=HexColor('#e94560'),
        spaceBefore=15,
        spaceAfter=8
    )
    
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontName=fonts['regular'],
        fontSize=10,
        textColor=HexColor('#999999'),
        alignment=TA_RIGHT
    )
    
    notes_style = ParagraphStyle(
        'NotesStyle',
        parent=styles['Normal'],
        fontName=fonts['regular'],
        fontSize=10,
        textColor=HexColor('#666666'),
        leftIndent=0,
        spaceBefore=15
    )
    
    signature_style = ParagraphStyle(
        'SignatureStyle',
        parent=styles['Normal'],
        fontName=fonts['regular'],
        fontSize=10,
        textColor=HexColor('#666666'),
        alignment=TA_RIGHT
    )
    
    # Заголовок
    if checklist['title']:
        story.append(Paragraph(checklist['title'], title_style))
    else:
        story.append(Paragraph("Checklist", title_style))
    
    story.append(Spacer(1, 5))
    
    # Дата
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", date_style))
    story.append(Spacer(1, 15))
    
    # Секции и пункты с графическими чекбоксами
    for section in checklist['sections']:
        story.append(Paragraph(section['name'], section_style))
        
        for item in section['items']:
            # Создаем таблицу для каждой строки: [чекбокс] [текст]
            checkbox = checked_icon if item['checked'] else empty_icon
            
            # Стиль для текста С ИСПРАВЛЕННЫМ ВЫРАВНИВАНИЕМ
            item_text_style = ParagraphStyle(
                'ItemTextStyle',
                parent=styles['Normal'],
                fontName=fonts['regular'],
                fontSize=11,
                textColor=HexColor('#2c3e50'),
                leftIndent=0,
                leading=15  # Межстрочный интервал
            )
            
            # Если задача выполнена, делаем текст серым и зачеркнутым
            if item['checked']:
                item_text = Paragraph(f'<strike>{item["text"]}</strike>', item_text_style)
            else:
                item_text = Paragraph(item['text'], item_text_style)
            
            # Таблица: чекбокс + текст с ПРАВИЛЬНЫМ ВЫРАВНИВАНИЕМ
            row_data = [[checkbox, item_text]]
            row_table = Table(row_data, colWidths=[CHECKBOX_SIZE + 5, None])
            row_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Вертикальное выравнивание по центру
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),     # Чекбокс по центру по горизонтали
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),       # Текст по левому краю
                ('LEFTPADDING', (0, 0), (0, 0), 0),
                ('RIGHTPADDING', (0, 0), (0, 0), 3),
                ('LEFTPADDING', (1, 0), (1, 0), 0),
                ('TOPPADDING', (1, 0), (1, 0), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            
            story.append(row_table)
        
        story.append(Spacer(1, 5))
    
    # Примечания
    if checklist['notes']:
        story.append(Spacer(1, 20))
        story.append(Paragraph("Notes:", section_style))
        story.append(Spacer(1, 5))
        
        notes_text = checklist['notes'].replace('\n', '<br/>')
        story.append(Paragraph(notes_text, notes_style))
    
    # Подпись
    story.append(Spacer(1, 40))
    story.append(Paragraph("_________________________", signature_style))
    story.append(Paragraph("Signature / Date", signature_style))
    
    # Нумерация страниц
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        canvas.saveState()
        canvas.setFont(fonts['regular'], 9)
        canvas.setFillColor(HexColor('#999999'))
        canvas.drawCentredString(doc.width/2 + doc.leftMargin, 
                                doc.bottomMargin - 10*mm, 
                                f"- {page_num} -")
        canvas.restoreState()
    
    # Строим PDF
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    
    print(f"PDF создан: {output_pdf}")
    return output_pdf

def main():
    """Пример использования"""
    
    # Проверяем наличие файлов
    if not os.path.exists(FONT_PATH):
        print(f"Файл шрифта не найден: {FONT_PATH}")
        print("   Скачайте PT Sans с Google Fonts и переименуйте в PTSans-Regular.ttf")
    
    if not os.path.exists(CHECK_ICON_PATH):
        print(f"Файл иконки не найден: {CHECK_ICON_PATH}")
        print("   Будет создана графическая галочка")
    
    # Создаем пример Markdown файла
    example_md = "checklist.md"
    if not os.path.exists(example_md):
        print("Создаю пример Markdown файла...")
        with open(example_md, 'w', encoding='utf-8') as f:
            f.write("""# Мой чек-лист

## Утренние дела
- [ ] Встать в 7:00
- [ ] Сделать зарядку 15 минут
- [ ] Принять душ
- [ ] Позавтракать

## Рабочие задачи
- [ ] Проверить почту
- [ ] Составить план на день
- [ ] Выполнить 3 главные задачи
- [x] Ответить на сообщения

## Вечерние дела
- [ ] Подвести итоги
- [ ] Подготовиться ко сну
- [ ] Лечь спать до 23:00

## Заметки
Не забывать пить воду
Сделать перерыв каждый час
""")
        print("Создан файл: checklist.md")
    
    # Генерируем PDF
    print("Генерация PDF чек-листа...")
    pdf_file = create_checklist_pdf(example_md)
    print(f"Готово! Откройте {pdf_file}")

if __name__ == "__main__":
    main()