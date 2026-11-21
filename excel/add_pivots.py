"""Adds real Excel/LibreOffice Pivot Tables to Pivot_Analysis via LibreOffice UNO and saves initial_data_inspection.xlsx."""
import subprocess, time, os, uno
from com.sun.star.beans import PropertyValue
from com.sun.star.table import CellAddress, CellRangeAddress
from com.sun.star.sheet.DataPilotFieldOrientation import ROW, COLUMN, DATA
from com.sun.star.sheet.GeneralFunction import SUM
def pv(n, v): p = PropertyValue(); p.Name, p.Value = n, v; return p
proc = subprocess.Popen(['soffice', '--headless', '--norestore', '--accept=socket,host=localhost,port=2002;urp;'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
ctx = None
for _ in range(60):
    try:
        local = uno.getComponentContext(); res = local.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', local)
        ctx = res.resolve('uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext'); break
    except Exception: time.sleep(1)
desktop = ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', ctx)
doc = desktop.loadComponentFromURL('file://' + os.path.abspath('excel/_stage1.xlsx'), '_blank', 0, (pv('Hidden', True),))
sheets = doc.Sheets; raw = sheets.getByName('Raw_Data'); ps = sheets.getByName('Pivot_Analysis'); ps_idx = ps.RangeAddress.Sheet; raw_idx = raw.RangeAddress.Sheet
hdr = [raw.getCellByPosition(c, 0).String for c in range(28)]
src = CellRangeAddress(); src.Sheet = raw_idx; src.StartColumn = 0; src.StartRow = 0; src.EndColumn = 27; src.EndRow = 9994
def make(name, row, col, rows, data, columns=None):
    dps = ps.getDataPilotTables(); d = dps.createDataPilotDescriptor(); d.setSourceRange(src)
    flds = d.getDataPilotFields()
    for nm in rows: flds.getByIndex(hdr.index(nm)).Orientation = ROW
    if columns:
        for nm in columns: flds.getByIndex(hdr.index(nm)).Orientation = COLUMN
    for nm in data:
        f = flds.getByIndex(hdr.index(nm)); f.Orientation = DATA; f.Function = SUM
    a = CellAddress(); a.Sheet = ps_idx; a.Column = col; a.Row = row
    dps.insertNewByName(name, a, d)
def label(row, col, text, bold=True):
    c = ps.getCellByPosition(col, row); c.String = text; c.CharWeight = 150 if bold else 100; c.CharFontName = 'Arial'
label(0, 0, 'Pivot Tables built from Raw_Data!A1:AB9995 (right-click a pivot > Refresh after any data change)')
label(2, 0, 'Pivot 1 — Sales by Region');             make('PT_Sales_by_Region', 3, 0, ['Region'], ['Sales'])
label(11, 0, 'Pivot 2 — Sales by Category');          make('PT_Sales_by_Category', 12, 0, ['Category'], ['Sales'])
label(19, 0, 'Pivot 3 — Sales by Customer Segment');  make('PT_Sales_by_Segment', 20, 0, ['Segment'], ['Sales'])
label(27, 0, 'Pivot 4 — Profit by Category');         make('PT_Profit_by_Category', 28, 0, ['Category'], ['Profit'])
label(2, 4, 'Pivot 5 — Sales and Profit by Region and Sub-Category'); make('PT_Region_SubCategory', 3, 4, ['Sub-Category'], ['Sales', 'Profit'], ['Region'])
label(2, 15, 'Pivot 6 — Profit by Discount Band and Category'); make('PT_Profit_Discount_Category', 3, 15, ['Discount Band'], ['Profit'], ['Category'])
ps.getColumns().getByIndex(0).Width = 4500
for c in range(1, 25): ps.getColumns().getByIndex(c).OptimalWidth = True
n = ps.getDataPilotTables().getCount(); print('pivot tables created:', n)
out = 'file://' + os.path.abspath('excel/initial_data_inspection.xlsx')
doc.storeToURL(out, (pv('FilterName', 'Calc MS Excel 2007 XML'),)); doc.close(True)
try: desktop.terminate()
except Exception: pass
proc.terminate()
