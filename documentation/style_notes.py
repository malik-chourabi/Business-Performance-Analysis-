from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
doc = Document('_raw.docx')
for sec in doc.sections: sec.left_margin = sec.right_margin = Cm(2.2); sec.top_margin = sec.bottom_margin = Cm(2)
navy = RGBColor(0x1F, 0x3A, 0x5F)
for st in doc.styles:
    try:
        if st.font is not None: st.font.name = 'Arial'
    except Exception: pass
for n, sz in [('Heading 1', 20), ('Heading 2', 14), ('Heading 3', 12), ('Title', 26), ('Subtitle', 14)]:
    try: f = doc.styles[n].font; f.size = Pt(sz); f.color.rgb = navy; f.bold = True
    except KeyError: pass
for n in ['Normal', 'Body Text', 'First Paragraph', 'Compact']:
    try: doc.styles[n].font.size = Pt(10.5)
    except KeyError: pass
try: c = doc.styles['Source Code'].font; c.name = 'Consolas'; c.size = Pt(8.5)
except KeyError: pass
def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement('w:shd'); sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto'); sh.set(qn('w:fill'), color); tcPr.append(sh)
for t in doc.tables:
    b = OxmlElement('w:tblBorders')
    for e in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        x = OxmlElement(f'w:{e}'); x.set(qn('w:val'), 'single'); x.set(qn('w:sz'), '4'); x.set(qn('w:color'), 'BFC7D1'); b.append(x)
    t._tbl.tblPr.append(b)
    for i, row in enumerate(t.rows):
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(9); r.font.name = 'Arial'
                    if i == 0: r.font.bold = True; r.font.color.rgb = RGBColor(255, 255, 255)
            if i == 0: shade(cell, '1F3A5F')
            elif i % 2 == 0: shade(cell, 'E8EEF4')
doc.save('Business_Performance_Analysis_Complete_Notes.docx')
