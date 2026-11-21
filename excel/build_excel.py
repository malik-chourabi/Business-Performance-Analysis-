"""Builds excel/initial_data_inspection.xlsx (run from project root). Pivot tables are added afterwards by add_pivots.py (LibreOffice)."""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as L

raw = pd.read_csv('data/raw/Sample_Superstore.csv')
raw['Order Date'] = pd.to_datetime(raw['Order Date'], format='%m/%d/%Y'); raw['Ship Date'] = pd.to_datetime(raw['Ship Date'], format='%m/%d/%Y')
N = len(raw); LAST = N + 1
F = 'Arial'; NAVY = '1F3A5F'
hf = Font(name=F, bold=True, color='FFFFFF', size=10); hfill = PatternFill('solid', fgColor=NAVY)
helper_fill = PatternFill('solid', fgColor='2A9D8F'); sub = PatternFill('solid', fgColor='E8EEF4')
base = Font(name=F, size=10); bold = Font(name=F, size=10, bold=True); title = Font(name=F, size=14, bold=True, color=NAVY)
thin = Side(style='thin', color='BFC7D1'); box = Border(top=thin, bottom=thin, left=thin, right=thin)
USD = '$#,##0.00;[Red]-$#,##0.00'; PCT = '0.0%'; INT = '#,##0'

wb = Workbook()
# ---------------- Raw_Data ----------------
ws = wb.active; ws.title = 'Raw_Data'
cols = list(raw.columns)
for j, c in enumerate(cols, 1):
    x = ws.cell(1, j, c); x.font = hf; x.fill = hfill; x.alignment = Alignment(wrap_text=True, vertical='center')
helpers = ['Shipping Days', 'Profit Margin', 'Loss Flag', 'Discount Band', 'New Order Flag', 'Order Year', 'Possible Duplicate']
for k, h in enumerate(helpers, len(cols) + 1):
    x = ws.cell(1, k, h); x.font = hf; x.fill = helper_fill; x.alignment = Alignment(wrap_text=True, vertical='center')
for i, row in enumerate(raw.itertuples(index=False), 2):
    for j, v in enumerate(row, 1):
        if isinstance(v, pd.Timestamp): v = v.to_pydatetime()
        ws.cell(i, j, v)
    ws.cell(i, 22, f'=D{i}-C{i}')                                          # V Shipping Days
    ws.cell(i, 23, f'=IF(R{i}=0,0,U{i}/R{i})')                             # W Profit Margin (handles zero sales)
    ws.cell(i, 24, f'=IF(U{i}<0,1,0)')                                     # X Loss Flag
    ws.cell(i, 25, f'=IF(T{i}=0,"No discount",IF(T{i}<=0.1,"1-10%",IF(T{i}<=0.2,"11-20%",IF(T{i}<=0.3,"21-30%",IF(T{i}<=0.5,"31-50%",">50%")))))')  # Y
    ws.cell(i, 26, '=1' if i == 2 else f'=IF(B{i}<>B{i-1},1,0)')           # Z New Order Flag (lines of an order are adjacent)
    ws.cell(i, 27, f'=YEAR(C{i})')                                         # AA
    ws.cell(i, 28, '=""' if i == 2 else f'=IF(AND(B{i}=B{i-1},N{i}=N{i-1},R{i}=R{i-1},S{i}=S{i-1},T{i}=T{i-1},U{i}=U{i-1}),"Possible duplicate","")')  # AB
for r in range(2, LAST + 1):
    for col, fmt in ((3, 'm/d/yyyy'), (4, 'm/d/yyyy'), (18, '#,##0.00'), (20, '0.00'), (21, '#,##0.00'), (23, '0.0%')): ws.cell(r, col).number_format = fmt
ws.freeze_panes = 'C2'; ws.auto_filter.ref = f'A1:{L(len(cols)+len(helpers))}{LAST}'
for j in range(1, len(cols) + len(helpers) + 1): ws.column_dimensions[L(j)].width = 14
for j, w in {2: 16, 7: 20, 17: 42, 16: 14, 15: 16}.items(): ws.column_dimensions[L(j)].width = w
ws.row_dimensions[1].height = 32

def R(col): return f'Raw_Data!${col}$2:${col}${LAST}'
def hdr(w, r, vals, c0=1, fill=hfill):
    for k, v in enumerate(vals): x = w.cell(r, c0 + k, v); x.font = hf; x.fill = fill; x.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center'); x.border = box
def put(w, r, c, v, fmt=None, f=base):
    x = w.cell(r, c, v); x.font = f; x.border = box
    if fmt: x.number_format = fmt
    return x

# ---------------- Data_Inspection ----------------
di = wb.create_sheet('Data_Inspection')
di['A1'] = 'Data Inspection — Sample Superstore (public sample dataset, not confidential company data)'; di['A1'].font = title
di['A2'] = 'Raw_Data holds the untouched CSV (columns A–U). Teal-headed columns V–AB are helper columns added by the analyst (formulas). All figures below are live formulas on Raw_Data.'; di['A2'].font = base
di['A4'] = '1. Dataset size and integrity checks'; di['A4'].font = bold
hdr(di, 5, ['Check', 'Result', 'How it is calculated / comment'])
checks = [
 ('Number of records (rows)', f'=COUNTA({R("A")})', INT, 'COUNTA counts non-empty cells in Row ID'),
 ('Number of variables (columns)', len(cols), INT, 'Original CSV columns (hard-coded: counted from the header row A1:U1)'),
 ('Total missing cells in original 21 columns', f'=COUNTBLANK(Raw_Data!$A$2:$U${LAST})', INT, 'COUNTBLANK over the whole original block'),
 ('Row ID is unique and sequential?', f'=IF(AND(MAX({R("A")})=COUNT({R("A")}),MIN({R("A")})=1),"Yes","No")', None, 'MAX = COUNT = rows when IDs run 1..n without gaps'),
 ('Possible duplicate lines (identical to the row above except Row ID)', f'=COUNTIF({R("AB")},"Possible duplicate")', INT, 'Helper column AB; works because lines of one order are adjacent. Kept and flagged, not deleted'),
 ('Distinct orders', f'=SUM({R("Z")})', INT, 'Helper column Z marks the first line of each order; SUM = number of distinct Order IDs'),
 ('Order lines with negative profit (losses)', f'=COUNTIF({R("U")},"<0")', INT, 'COUNTIF with a condition'),
 ('Postal codes below 10000 (a leading zero is missing)', f'=COUNTIF({R("L")},"<10000")', INT, '449 = 438 codes already stored without the zero in the CSV (CT, MA, ME, NH, NJ, RI) + 11 Vermont codes (05408) that keep the zero in the CSV but lose it when Excel reads them as numbers. Data-format issue'),
 ('Rows where Ship Date is before Order Date', f'=SUMPRODUCT(--({R("D")}<{R("C")}))', INT, 'Logical consistency check; should be 0'),
 ('Rows with Sales <= 0', f'=COUNTIF({R("R")},"<=0")', INT, 'Zero/negative sales would break margin calculations'),
 ('Earliest order date', f'=MIN({R("C")})', 'm/d/yyyy', 'MIN of Order Date'),
 ('Latest order date', f'=MAX({R("C")})', 'm/d/yyyy', 'MAX of Order Date'),
]
for k, (a, b, fmt, c) in enumerate(checks, 6): put(di, k, 1, a); put(di, k, 2, b, fmt); put(di, k, 3, c)
r0 = 6 + len(checks) + 1
di.cell(r0, 1, '2. Variable dictionary and completeness').font = bold
hdr(di, r0 + 1, ['Variable', 'Excel column', 'Type', 'Role', 'Non-blank cells', 'Missing cells', 'Meaning'])
meaning = {'Row ID': ('Number', 'Identifier', 'Sequential line number'), 'Order ID': ('Text', 'Identifier', 'Order reference; one order can have several lines'),
 'Order Date': ('Date', 'Date', 'Date the order was placed'), 'Ship Date': ('Date', 'Date', 'Date the order was shipped'),
 'Ship Mode': ('Text', 'Categorical', 'Delivery service level'), 'Customer ID': ('Text', 'Identifier', 'Customer reference'), 'Customer Name': ('Text', 'Identifier', 'Customer full name'),
 'Segment': ('Text', 'Categorical', 'Consumer / Corporate / Home Office'), 'Country': ('Text', 'Categorical', 'Always United States'), 'City': ('Text', 'Categorical', 'Delivery city'),
 'State': ('Text', 'Categorical', 'Delivery state'), 'Postal Code': ('Number (should be text)', 'Geographic code', 'ZIP code; leading zeros lost'), 'Region': ('Text', 'Categorical', 'East / West / Central / South'),
 'Product ID': ('Text', 'Identifier', 'Product reference'), 'Category': ('Text', 'Categorical', 'Furniture / Office Supplies / Technology'), 'Sub-Category': ('Text', 'Categorical', '17 sub-categories'),
 'Product Name': ('Text', 'Identifier', 'Product description'), 'Sales': ('Number', 'Numerical', 'Revenue of the line after discount (USD assumed)'), 'Quantity': ('Number', 'Numerical', 'Units sold'),
 'Discount': ('Number', 'Numerical', 'Discount rate applied (0–0.8)'), 'Profit': ('Number', 'Numerical', 'Profit of the line; negative = loss')}
for k, c in enumerate(cols):
    rr = r0 + 2 + k; t, ro, m = meaning[c]
    put(di, rr, 1, c); put(di, rr, 2, L(k + 1)); put(di, rr, 3, t); put(di, rr, 4, ro)
    put(di, rr, 5, f'=COUNTA({R(L(k+1))})', INT); put(di, rr, 6, f'=COUNTBLANK({R(L(k+1))})', INT); put(di, rr, 7, m)
r1 = r0 + 2 + len(cols) + 1
di.cell(r1, 1, '3. Descriptive statistics of numerical variables').font = bold
hdr(di, r1 + 1, ['Statistic', 'Sales', 'Quantity', 'Discount', 'Profit', 'Shipping Days (helper)'])
stats = [('Count', 'COUNT'), ('Mean (AVERAGE)', 'AVERAGE'), ('Median', 'MEDIAN'), ('Standard deviation (STDEV)', 'STDEV'), ('Minimum', 'MIN'), ('1st quartile', 'Q1'), ('3rd quartile', 'Q3'), ('Maximum', 'MAX')]
for k, (nm, fn) in enumerate(stats):
    rr = r1 + 2 + k; put(di, rr, 1, nm)
    for j, col in enumerate(['R', 'S', 'T', 'U', 'V'], 2):
        f = f'=QUARTILE({R(col)},1)' if fn == 'Q1' else f'=QUARTILE({R(col)},3)' if fn == 'Q3' else f'={fn}({R(col)})'
        put(di, rr, j, f, INT if fn == 'COUNT' else '#,##0.00')
r2 = r1 + 2 + len(stats) + 1
di.cell(r2, 1, '4. Data-quality log').font = bold
hdr(di, r2 + 1, ['#', 'Issue', 'Evidence (see checks above)', 'Decision'])
dq = [(1, 'Dates are text in the CSV (m/d/yyyy)', 'Excel converts them to dates on import; Python converts explicitly', 'Convert to date type'),
      (2, 'Postal codes lose leading zeros', 'Check "Postal codes below 10000"', 'Treat as text with 5 digits in Python/SQL/Power BI'),
      (3, 'One possible duplicate line', 'Check "Possible duplicate lines"', 'Keep and flag; impact 0.01% of sales'),
      (4, 'No missing values', 'Check "Total missing cells" = 0', 'No imputation needed'),
      (5, 'No cost column', 'Only Sales and Profit are given', 'Implied cost = Sales − Profit (Python)'),
      (6, 'Country is constant', 'Always United States', 'No analytical value; kept')]
for k, row in enumerate(dq):
    for j, v in enumerate(row, 1): put(di, r2 + 2 + k, j, v)
for col, w in zip('ABCDEFG', [62, 20, 70, 22, 16, 14, 50]): di.column_dimensions[col].width = w

# ---------------- Basic_Analysis ----------------
ba = wb.create_sheet('Basic_Analysis')
ba['A1'] = 'Basic Analysis — formulas: SUM, AVERAGE, COUNTIF(S), SUMIF(S), IF'; ba['A1'].font = title
ba['A3'] = '1. Headline KPIs'; ba['A3'].font = bold; hdr(ba, 4, ['KPI', 'Value', 'Formula used'])
kp = [('Total Sales', f'=SUM({R("R")})', USD, 'SUM'), ('Total Profit', f'=SUM({R("U")})', USD, 'SUM'),
      ('Profit Margin', '=IF(B5=0,0,B6/B5)', PCT, 'IF + division (guards against zero sales)'), ('Distinct Orders', f'=SUM({R("Z")})', INT, 'SUM of new-order flag'),
      ('Total Quantity', f'=SUM({R("S")})', INT, 'SUM'), ('Average Order Value', '=IF(B8=0,0,B5/B8)', USD, 'Sales ÷ distinct orders'),
      ('Average Discount (per line)', f'=AVERAGE({R("T")})', PCT, 'AVERAGE'), ('Average Shipping Days', f'=AVERAGE({R("V")})', '0.00', 'AVERAGE of helper V'),
      ('Loss-making lines', f'=COUNTIF({R("X")},1)', INT, 'COUNTIF'), ('Share of lines that are loss-making', f'=B13/COUNTA({R("A")})', PCT, 'COUNTIF ÷ COUNTA'),
      ('Total of all losses', f'=SUMIF({R("U")},"<0")', USD, 'SUMIF with a condition'), ('Margin status', '=IF(B7>=0.15,"Healthy (>=15%)",IF(B7>=0.08,"Moderate (8–15%)","Weak (<8%)"))', None, 'IF: thresholds are an assumption for illustration')]
for k, (a, b, fmt, c) in enumerate(kp, 5): put(ba, k, 1, a); put(ba, k, 2, b, fmt); put(ba, k, 3, c)

def block(r, ttl, dim_col, items, extra_note=None):
    ba.cell(r, 1, ttl).font = bold; hdr(ba, r + 1, [ttl.split('by ')[-1].title(), 'Sales', 'Profit', 'Profit Margin', 'Order lines', 'Distinct orders (from Pivot)' if False else 'Quantity', 'Avg Discount', 'Share of sales'])
    for k, it in enumerate(items):
        rr = r + 2 + k; put(ba, rr, 1, it)
        put(ba, rr, 2, f'=SUMIFS({R("R")},{R(dim_col)},"="&$A{rr})', USD); put(ba, rr, 3, f'=SUMIFS({R("U")},{R(dim_col)},"="&$A{rr})', USD)
        put(ba, rr, 4, f'=IF(B{rr}=0,0,C{rr}/B{rr})', PCT); put(ba, rr, 5, f'=COUNTIF({R(dim_col)},"="&$A{rr})', INT)
        put(ba, rr, 6, f'=SUMIFS({R("S")},{R(dim_col)},"="&$A{rr})', INT); put(ba, rr, 7, f'=AVERAGEIFS({R("T")},{R(dim_col)},"="&$A{rr})', PCT); put(ba, rr, 8, f'=B{rr}/$B$5', PCT)
    rt = r + 2 + len(items); put(ba, rt, 1, 'Total', f=bold)
    for c, fmt in ((2, USD), (3, USD), (5, INT), (6, INT)): put(ba, rt, c, f'=SUM({L(c)}{r+2}:{L(c)}{rt-1})', fmt, bold)
    put(ba, rt, 4, f'=IF(B{rt}=0,0,C{rt}/B{rt})', PCT, bold); put(ba, rt, 8, f'=SUM(H{r+2}:H{rt-1})', PCT, bold)
    return rt + 2
r = 18
r = block(r, '2. Performance by Region', 'M', ['West', 'East', 'Central', 'South'])
r = block(r, '3. Performance by Category', 'O', ['Technology', 'Furniture', 'Office Supplies'])
r = block(r, '4. Performance by Customer Segment', 'H', ['Consumer', 'Corporate', 'Home Office'])
r = block(r, '5. Performance by Ship Mode', 'E', ['Standard Class', 'Second Class', 'First Class', 'Same Day'])
r = block(r, '6. Performance by Discount Band', 'Y', ['No discount', '1-10%', '11-20%', '21-30%', '31-50%', '>50%'])
ba.cell(r, 1, '7. Performance by Order Year').font = bold; hdr(ba, r + 1, ['Year', 'Sales', 'Profit', 'Profit Margin', 'Sales growth vs previous year'])
for k, y in enumerate([2014, 2015, 2016, 2017]):
    rr = r + 2 + k; put(ba, rr, 1, y)
    put(ba, rr, 2, f'=SUMIFS({R("R")},{R("AA")},$A{rr})', USD); put(ba, rr, 3, f'=SUMIFS({R("U")},{R("AA")},$A{rr})', USD); put(ba, rr, 4, f'=IF(B{rr}=0,0,C{rr}/B{rr})', PCT)
    put(ba, rr, 5, 'n/a' if k == 0 else f'=IF(B{rr-1}=0,0,B{rr}/B{rr-1}-1)', PCT)
for col, w in zip('ABCDEFGH', [36, 18, 18, 14, 14, 14, 14, 14]): ba.column_dimensions[col].width = w
ba.column_dimensions['C'].width = 38 if False else 20

# ---------------- Pivot_Analysis & Findings placeholders (filled later) ----------------
pv = wb.create_sheet('Pivot_Analysis'); pv['A1'] = 'Pivot Tables (built from Raw_Data!A1:AB%d)' % LAST; pv['A1'].font = title
pf = wb.create_sheet('Preliminary_Findings')

pf['A1'] = 'Preliminary Findings (Excel stage) — to be confirmed in Python and SQL'; pf['A1'].font = title
pf['A2'] = 'Numbers in the Evidence column are live formulas linked to Basic_Analysis. Explanations are hypotheses to test, not conclusions. The dataset is a public sample dataset, not confidential company data.'; pf['A2'].font = base
hdr(pf, 4, ['#', 'Observation', 'Evidence (live)', 'Possible explanation (hypothesis only)', 'Next step'])
BA = 'Basic_Analysis!'
rowsF = [
 ('Overall profitability is moderate', f'="Sales "&TEXT({BA}B5,"$#,##0")&", profit "&TEXT({BA}B6,"$#,##0")&", margin "&TEXT({BA}B7,"0.0%")', 'Healthy gross sales but a thin margin leaves little room for error', 'Find which segments of the business pull the margin down'),
 ('Furniture earns far less profit than other categories despite similar sales', f'="Furniture margin "&TEXT({BA}D29,"0.0%")&" vs Technology "&TEXT({BA}D28,"0.0%")&" and Office Supplies "&TEXT({BA}D30,"0.0%")', 'Pricing, discounting or product cost structure of some furniture lines', 'Drill into sub-categories and discounts (Python, SQL)'),
 ('Central region is the weakest on margin', f'="Central margin "&TEXT({BA}D22,"0.0%")&" vs West "&TEXT({BA}D20,"0.0%")&"; Central average discount "&TEXT({BA}G22,"0.0%")&" vs West "&TEXT({BA}G20,"0.0%")', 'Higher discounting in Central (association seen here; not proven as the cause)', 'Compare discount mix by region and state'),
 ('Discounts above 20% coincide with losses', f'="Margin: no discount "&TEXT({BA}D50,"0.0%")&", 11-20% "&TEXT({BA}D52,"0.0%")&", 31-50% "&TEXT({BA}D54,"0.0%")&", >50% "&TEXT({BA}D55,"0.0%")', 'Deep discounts may push prices below cost, or be used on already low-margin items', 'Quantify with correlation and discount bands (Python); confirm with SQL'),
 ('A large part of order lines lose money', f'=TEXT({BA}B13,"#,##0")&" loss-making lines ("&TEXT({BA}B14,"0.0%")&" of lines), total losses "&TEXT({BA}B15,"$#,##0")', 'Concentrated in specific products/discount levels', 'Identify loss-making products and states'),
 ('Consumer is the biggest segment, Home Office the most profitable by margin', f'="Consumer sales share "&TEXT({BA}H35,"0.0%")&", margin "&TEXT({BA}D35,"0.0%")&"; Home Office margin "&TEXT({BA}D37,"0.0%")', 'Segment size differs more than profitability; differences are small', 'Test whether the margin differences are statistically meaningful (Python)'),
 ('Sales grew strongly after 2015', f'="2015 growth "&TEXT({BA}E61,"0.0%")&", 2016 "&TEXT({BA}E62,"0.0%")&", 2017 "&TEXT({BA}E63,"0.0%")', 'Growth in orders; seasonality not yet examined', 'Monthly trend and seasonality (Python, Power BI)'),
 ('Shipping speed does not obviously change margin', f'="Standard Class margin "&TEXT({BA}D42,"0.0%")&" vs First Class "&TEXT({BA}D44,"0.0%")&"; average shipping days "&TEXT({BA}B12,"0.00")', 'Shipping cost is not in the data, so cost effects cannot be seen', 'Correlation check (Python)'),
 ('Data quality is good but needs format fixes', '="Missing cells: "&TEXT(Data_Inspection!B8,"0")&"; possible duplicate lines: "&TEXT(Data_Inspection!B10,"0")&"; postal codes below 10000: "&TEXT(Data_Inspection!B13,"#,##0")', 'Postal-code leading zeros lost; text dates', 'Clean in Python; keep Raw_Data untouched'),
]
for k, (a, b, c, d) in enumerate(rowsF, 1):
    rr = 4 + k
    put(pf, rr, 1, k); put(pf, rr, 2, a); put(pf, rr, 3, b); put(pf, rr, 4, c); put(pf, rr, 5, d)
    for cc in range(1, 6): pf.cell(rr, cc).alignment = Alignment(wrap_text=True, vertical='top')
    pf.row_dimensions[rr].height = 48
for col, w in zip('ABCDE', [5, 44, 62, 48, 44]): pf.column_dimensions[col].width = w

wb.save('excel/_stage1.xlsx'); print('stage1 saved')
