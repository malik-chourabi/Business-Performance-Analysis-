import sys, re, sqlite3, io
sys.path.insert(0, 'reports')
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.ticker as mt
from sklearn.linear_model import LinearRegression
from facts import F
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, Preformatted
from PIL import Image as PI
for n, f in [('Carlito', 'Regular'), ('Carlito-Bold', 'Bold'), ('Carlito-Italic', 'Italic')]: pdfmetrics.registerFont(TTFont(n, f'/usr/share/fonts/truetype/crosextra/Carlito-{f}.ttf'))
NAVY, LIGHT, INK, GREY = colors.HexColor('#1F4E79'), colors.HexColor('#F2F6FA'), colors.HexColor('#1F2933'), colors.HexColor('#6B7785')
d0 = lambda x: f'${x:,.0f}'; p1 = lambda x: f'{x:.1f}%'; k0 = lambda x: f'${x/1000:,.1f}k'
yr, cat, sub, reg, seg, st = F['yr'], F['cat'], F['sub'], F['reg'], F['seg'], F['state']
d = pd.read_csv('data/processed/cleaned_sales.csv', parse_dates=['Order Date'])
con = sqlite3.connect('sql/superstore.db')
# ---------------- extra computations ----------------
def py_fold(train_end, test_year):
    ms = d.groupby(d['Order Date'].dt.to_period('M')).Sales.sum(); ms.index = ms.index.to_timestamp()
    X = pd.DataFrame({'t': np.arange(len(ms))}, index=ms.index).join(pd.get_dummies(ms.index.month, prefix='m', drop_first=True).set_index(ms.index).astype(int))
    tr, te = ms.index <= f'{train_end}-12-31', (ms.index >= f'{test_year}-01-01') & (ms.index <= f'{test_year}-12-31')
    p = LinearRegression().fit(X[tr], ms[tr]).predict(X[te]); a = ms[te].values
    return dict(MAE=np.mean(abs(a - p)), RMSE=np.sqrt(np.mean((a - p) ** 2)), MAPE=np.mean(abs((a - p) / a)) * 100)
pyA, pyB = py_fold(2015, 2016), py_fold(2016, 2017)
rm = pd.read_csv('r/r_forecast_metrics.csv'); rstat = pd.read_csv('r/r_stat_tests.csv'); r17 = pd.read_csv('r/r_forecast_2017.csv'); r18 = pd.read_csv('r/r_forecast_2018.csv')
rco = pd.read_csv('r/r_margin_regression.csv').set_index('term'); ran = pd.read_csv('r/r_margin_anova.csv').set_index('term')
rtxt = open('r/r_output.txt').read(); r2 = float(re.search(r'R-squared: ([0-9.]+)', rtxt).group(1)); r2d = float(re.search(r'R-squared discount alone: ([0-9.]+)', rtxt).group(1))
shares = (ran['Sum.Sq'].drop('Residuals') / ran['Sum.Sq'].drop('Residuals').sum() * 100)
NV, NAVYc, TEAL, RED, GOLD = '#1F4E79', '#1F4E79', '#2A9D8F', '#C0392B', '#E9A23B'
# forecast figure
ms = d.groupby(d['Order Date'].dt.to_period('M')).Sales.sum(); ms.index = ms.index.to_timestamp()
fig, ax = plt.subplots(1, 2, figsize=(14, 4.3), gridspec_kw={'width_ratios': [1, 1.25]})
x17 = pd.to_datetime(r17.month + '-01'); ax[0].plot(x17, r17.actual, color='k', lw=2.2, label='Actual 2017')
for col, c, ls in [('Trend + seasonal regression', GOLD, '-'), ('ETS (auto)', TEAL, '--'), ('STL + ETS', NAVYc, '-.'), ('Seasonal naive', '#8A94A0', ':')]: ax[0].plot(x17, r17[col], color=c, ls=ls, lw=1.8, label=col)
ax[0].yaxis.set_major_formatter(mt.FuncFormatter(lambda v, p: f'${v/1000:,.0f}K')); ax[0].set_title('2017 test year: actual vs forecasts (trained on 2014-2016)', fontweight='bold', fontsize=11); ax[0].legend(frameon=False, fontsize=8); ax[0].grid(axis='y', alpha=.25); ax[0].tick_params(axis='x', rotation=30)
x18 = pd.to_datetime(r18.month + '-01'); ax[1].plot(ms.index, ms.values, color=NAVYc, lw=2, label='Actual 2014-2017'); ax[1].plot(x18, r18.forecast, color=GOLD, lw=2.2, label='Forecast 2018 (trend + seasonal regression)')
ax[1].fill_between(x18, r18.lo80, r18.hi80, color=GOLD, alpha=.25, label='80% prediction interval'); ax[1].yaxis.set_major_formatter(mt.FuncFormatter(lambda v, p: f'${v/1000:,.0f}K'))
ax[1].set_title('Final model refitted on all 48 months: 2018 forecast', fontweight='bold', fontsize=11); ax[1].legend(frameon=False, fontsize=8, loc='upper left'); ax[1].grid(axis='y', alpha=.25)
for a in ax: a.spines['top'].set_visible(False); a.spines['right'].set_visible(False)
plt.tight_layout(); plt.savefig('reports/figures/12_forecast_models.png', dpi=150, bbox_inches='tight'); plt.close()
# ---------------- styles ----------------
def S(n, **k): return ParagraphStyle(n, fontName=k.pop('fontName', 'Carlito'), textColor=k.pop('textColor', INK), **k)
B = S('B', fontSize=10.3, leading=13.8, spaceAfter=6, alignment=TA_JUSTIFY); H1 = S('H1', fontName='Carlito-Bold', fontSize=16, leading=20, textColor=NAVY, spaceBefore=12, spaceAfter=6, keepWithNext=1)
H2 = S('H2', fontName='Carlito-Bold', fontSize=12, leading=15, textColor=NAVY, spaceBefore=8, spaceAfter=3, keepWithNext=1)
CAP = S('CAP', fontName='Carlito-Italic', fontSize=8.5, leading=11, textColor=GREY, spaceAfter=8); CELL = S('CELL', fontSize=8.8, leading=11); CELLB = S('CELLB', fontName='Carlito-Bold', fontSize=8.8, leading=11, textColor=colors.white)
CELLR = S('CELLR', fontSize=8.8, leading=11, alignment=2); BUL = S('BUL', fontSize=10.3, leading=13.8, leftIndent=14, bulletIndent=2, spaceAfter=2)
CODE = S('CODE', fontName='Courier', fontSize=7.3, leading=8.9)
def tbl(rows, widths, right_from=1, bold_last=False):
    data = []
    for i, r in enumerate(rows):
        data.append([Paragraph(str(c), CELLB if i == 0 else (CELLR if (j >= right_from and right_from >= 0) else CELL)) if i else Paragraph(str(c), CELLB) for j, c in enumerate(r)])
    t = Table(data, colWidths=[w * 28.35 for w in widths], repeatRows=1)
    sty = [('BACKGROUND', (0, 0), (-1, 0), NAVY), ('GRID', (0, 0), (-1, -1), .4, colors.HexColor('#C9D2DC')), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 2.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5)]
    sty += [('BACKGROUND', (0, i), (-1, i), LIGHT) for i in range(2, len(rows), 2)]; t.setStyle(TableStyle(sty)); return t
import textwrap
def wrap_code(txt, width=104):
    out = []
    for ln in txt.strip('\n').split('\n'):
        if len(ln) <= width: out.append(ln); continue
        ind = len(ln) - len(ln.lstrip()); out += textwrap.wrap(ln, width=width, subsequent_indent=' ' * (ind + 4), break_long_words=False, break_on_hyphens=False, replace_whitespace=False)
    return '\n'.join(out)
def code(txt):
    t = Table([[Preformatted(wrap_code(txt), CODE)]], colWidths=[482]); t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F4F6F8')), ('BOX', (0, 0), (-1, -1), .4, colors.HexColor('#D5DCE4')), ('LEFTPADDING', (0, 0), (-1, -1), 6), ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)])); return t
def fig(name, w=16.8, cap=None):
    im = PI.open(f'reports/figures/{name}.png'); r = im.size[1] / im.size[0]
    return KeepTogether([Image(f'reports/figures/{name}.png', width=w * 28.35, height=w * 28.35 * r)] + ([Paragraph(cap, CAP)] if cap else []))
def bl(items): return [Paragraph(t, BUL, bulletText='•') for t in items]
def box(text, fill='#E8EEF4'):
    t = Table([[Paragraph(text, S('bx', fontSize=9.8, leading=13))]], colWidths=[482]); t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(fill)), ('LINEBEFORE', (0, 0), (0, -1), 3, NAVY), ('LEFTPADDING', (0, 0), (-1, -1), 8), ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)])); return t
def sqlq(qid, nrows=None, fmt=None):
    txt = open('sql/business_queries.sql').read(); blk = re.split(r'\n(?=-- Q\d\d)', txt); b = [x for x in blk if x.startswith(f'-- {qid} ')][0]
    head = b.splitlines()[0][3:]; sql = '\n'.join(l for l in b.splitlines()[1:] if l.strip() and not l.strip().startswith('--')).split('   -- ')[0]
    purpose = [l[3:] for l in b.splitlines()[1:3] if l.startswith('-- Purpose')]
    df = pd.read_sql_query(sql, con)
    if nrows: df = df.head(nrows)
    return head, sql, df
def sql_block(qid, nrows=None, widths=None, title=None):
    head, sql, df = sqlq(qid, nrows)
    rows = [list(df.columns)] + [[(f'{v:,.2f}' if isinstance(v, float) and abs(v) >= 100 else (f'{v:,}' if isinstance(v, (int, np.integer)) else (f'{v:.2f}' if isinstance(v, float) else v))) for v in r] for r in df.itertuples(index=False)]
    w = widths or [482 / 28.35 / len(df.columns)] * len(df.columns)
    return KeepTogether([Paragraph(f'<b>{head.replace(" | ", " — ", 1)}</b>', S('sh', fontSize=9.5, leading=12, spaceAfter=2, keepWithNext=1)), code(sql), Spacer(1, 3), tbl(rows, w, right_from=1), Spacer(1, 8)])
# ---------------- story ----------------
story = []
story += [Spacer(1, 2.2 * 28.35), Paragraph('BUSINESS PERFORMANCE PROJECT', S('e', fontName='Carlito-Bold', fontSize=9.5, textColor=GREY, leading=12)),
 Paragraph('Business Performance Analysis, Sales Forecasting &amp; Business Intelligence Dashboard', S('t', fontName='Carlito-Bold', fontSize=27, leading=32, textColor=NAVY, spaceBefore=6, spaceAfter=10)),
 Paragraph('Retail profitability study of 9,994 order lines (2014–2017) using Excel, SQL, Python, R and Power BI', S('st', fontSize=13.5, leading=18, textColor=INK, spaceAfter=14)),
 box('<b>Data source.</b> Sample Superstore is a <b>public sample dataset</b> used for learning; it is not confidential information from a real company. Monetary values are in US dollars (assumed). All figures in this report come from the dataset; financial effects are arithmetic sensitivities, not forecasts of realised savings.'), Spacer(1, 14),
 tbl([['Key indicator (2014–2017)', 'Value'], ['Total sales', d0(F['sales'])], ['Total profit', d0(F['profit'])], ['Profit margin', p1(F['margin'])], ['Orders / customers / products', f"{F['orders']:,} / {F['customers']} / {F['products']:,}"],
      ['Net result of lines discounted above 20%', f"-{d0(-F['hi_profit'])} ({-F['hi_profit']/F['profit']*100:.0f}% of total profit)"]], [9.5, 7.5], right_from=1),
 Spacer(1, 16), Paragraph('Contents', H2)]
toc = ['1. Introduction: business problem, objectives and tools', '2. Data preparation (Python)', '3. Excel inspection', '4. SQL analysis', '5. Sales performance and profitability', '6. Factors affecting profitability (Python and R)', '7. Sales forecasting (Python and R)',
       '8. Power BI executive dashboard', '9. Management recommendations', '10. Limitations and conclusion', 'Appendix A. Python code', 'Appendix B. R code']
story += [Paragraph(t, S('toc', fontSize=10.3, leading=15)) for t in toc] + [PageBreak()]
# 1
story += [Paragraph('1. Introduction', H1),
 Paragraph('<b>Business problem.</b> A company wants to improve its profitability and understand the factors that affect its commercial performance. It records a large volume of sales transactions but has no clear overview of where it earns or loses money. The analysis takes the role of a data analyst supporting management.', B),
 Paragraph('<b>Objectives.</b> (1) Analyse sales by product, region and period; (2) analyse revenue and profitability; (3) identify the best- and worst-performing products; (4) describe business trends; (5) forecast sales; (6) identify the factors affecting performance; (7) recommend actions to improve profitability.', B),
 Paragraph('<b>Tools.</b> Each tool has a defined role; only the headline totals were repeated across tools, to validate them.', B),
 tbl([['Tool', 'Used for', 'Output'],
      ['Excel', 'Organise the data, inspect quality, basic formulas (SUM, AVERAGE, COUNTIF, IF), pivot tables, preliminary analysis', 'initial_data_inspection.xlsx'],
      ['SQL (SQLite)', 'Extract sales data, join customer / product / location tables, aggregate revenue and profit', 'superstore.db, business_queries.sql'],
      ['Python', 'Cleaning, feature engineering, trends, profitability, correlation, hypothesis tests, forecasting', 'business_analysis.ipynb'],
      ['R', 'Independent statistical analysis (tests, regression) and forecasting model comparison', 'forecast_and_stats.R'],
      ['Power BI', 'Executive dashboard to monitor business KPIs', 'Business_Performance_Analysis.pbix']], [2.6, 10.6, 3.8], right_from=-1),
 Paragraph('<br/>Workflow: raw CSV → Excel inspection → Python cleaning → cleaned CSV → SQLite database, R analysis and Power BI dashboard. The raw file was never edited and no row was deleted.', B)]
# 2
cl = open('python/clean_data.py').read(); clean_part = cl[cl.index('# 1. Dates'):cl.index('# 5. Feature')]; feat_part = cl[cl.index('# 5. Feature'):cl.index("df.to_csv")]
story += [Paragraph('2. Data preparation (Python)', H1),
 Paragraph(f"The dataset has {F['rows']:,} order lines and 21 columns: order and ship dates, ship mode, customer and segment, geography (region, state, city, postal code), product (category, sub-category, name) and four measures (sales, quantity, discount, profit). It covers {F['orders']:,} orders, {F['customers']} customers, {F['products']:,} products and {F['states']} states, from January 2014 to December 2017. There are no missing values. The data-quality checks and decisions were:", B),
 tbl([['Issue found', 'Evidence', 'Decision'],
      ['Dates stored as text', 'Order and ship dates are strings (m/d/yyyy)', 'Converted to date type'],
      ['Postal codes lost leading zeros', '438 four-digit codes in six states (449 in Excel)', 'Stored as 5-character text'],
      ['Product IDs with several names', '32 Product IDs, 129 rows', 'Most frequent name used; original kept'],
      ['One possible duplicate line', 'Identical except Row ID; $281 (0.01% of sales)', 'Kept and flagged'],
      ['Negative profits and outliers', f"{F['loss_lines']:,} loss-making lines; IQR outliers 11.7% (sales), 18.8% (profit)", 'Kept: real business events'],
      ['No cost column', 'Only sales and profit are given', 'Implied cost = sales − profit']], [4.6, 8.0, 4.4], right_from=-1),
 KeepTogether([Paragraph('<br/><b>Python code used for cleaning</b> (pandas; run from the project root):', B), code(clean_part)]),
 KeepTogether([Paragraph('<b>Feature engineering</b> — variables created for the analysis (year, month, shipping days, profit margin, cost, loss flag and discount band):', B), code(feat_part)]),
 Paragraph('After export, the cleaned file has 9,994 rows and its sales and profit totals are identical to the raw file.', B)]
# 3
story += [Paragraph('3. Excel inspection', H1),
 Paragraph('The raw CSV was imported into a workbook (sheets Raw_Data, Data_Inspection, Basic_Analysis, Pivot_Analysis, Preliminary_Findings). Filters and sorting were used to explore the data, and the checks below were calculated with formulas (COUNTA, COUNTBLANK, COUNTIF, SUMIFS, AVERAGE, IF). Six pivot tables summarise sales and profit by region, category, customer segment and sub-category.', B),
 tbl([['Check', 'Result', 'Formula'], ['Records / columns', '9,994 / 21', '=COUNTA(range)'], ['Missing cells', '0', '=COUNTBLANK(range)'], ['Distinct orders', '5,009', 'helper flag + =SUM()'], ['Loss-making lines', '1,871', '=COUNTIF(profit,"<0")'],
      ['Profit margin of the company', '12.47%', '=IF(sales=0,0,profit/sales)'], ['Sales of region West', '$725,458', '=SUMIFS(sales,region,"West")']], [6.2, 4.0, 6.8], right_from=-1),
 Paragraph('<br/>Excel gave the first picture: furniture earns far less profit than the other categories, and the Central region has the lowest margin. Python and SQL then explain why.', B)]
# 4
story += [Paragraph('4. SQL analysis', H1),
 Paragraph('The cleaned data were loaded into a SQLite database with a flat table (<font name="Courier" size="9">sales_clean</font>) and a small relational design: <font name="Courier" size="9">dim_customer</font> (793 rows), <font name="Courier" size="9">dim_product</font> (1,862), <font name="Courier" size="9">dim_geography</font> (632), <font name="Courier" size="9">orders</font> (5,009) and <font name="Courier" size="9">order_lines</font> (9,994), linked by primary and foreign keys. Unique orders are counted with COUNT(DISTINCT order_id), never with rows. The queries below answer the main business questions; the full set of 23 queries is in <i>business_queries.sql</i>, and 62 automated checks confirm that SQL results equal the Python results.', B),
 sql_block('Q03', widths=[3.6, 3.2, 3.2, 2.6, 2.4, 2.0]), sql_block('Q05', widths=[2.6, 3.0, 3.0, 2.4, 2.8, 2.0, 1.2]) if False else sql_block('Q05'), sql_block('Q06', widths=[2.4, 2.4, 2.2, 2.3, 2.0, 1.8, 1.4, 1.9, 1.6]) if False else sql_block('Q06'),
 sql_block('Q23', widths=[3.3, 1.7, 2.5, 2.5, 2.4, 2.1, 2.5]),
 sql_block('Q07', nrows=5, widths=[2.4, 6.2, 2.2, 1.8, 1.7, 1.6, 1.1]), sql_block('Q13', nrows=5, widths=[2.2, 3.4, 2.3, 2.6, 2.4, 1.6]) if False else sql_block('Q13', nrows=5), sql_block('Q14', nrows=5),
 Paragraph('<b>Answers.</b> Technology is the largest category by sales and by profit; West is the most profitable region; Consumer contributes the most to sales (50.6%); discount levels above 20% are associated with negative average profit per line; and ten states lose money in total.', B)]
# 5
story += [Paragraph('5. Sales performance and profitability', H1), Paragraph('5.1 Period trend', H2),
 tbl([['Year', 'Sales', 'Profit', 'Margin', 'Orders', 'Sales growth']] + [[str(y), d0(yr.Sales[y]), d0(yr.Profit[y]), p1(yr.Margin[y]), f"{int(yr.Orders[y]):,}", '—' if y == 2014 else f"{(yr.Sales[y]/yr.Sales[y-1]-1)*100:+.1f}%"] for y in yr.index], [2, 3.4, 3.2, 2.4, 2.6, 3.4]),
 Spacer(1, 6), fig('01_monthly_sales_profit', 15.5, 'Figure 1 — Monthly sales and profit.'),
 Paragraph(f"Sales fell 2.8% in 2015 and then grew 29.5% in 2016 and 20.4% in 2017, but the margin stayed near 13% (13.4% in 2016, 12.7% in 2017): growth did not translate into higher profitability. Sales are strongly seasonal: September–December produce {F['sep_nov_dec']+d[d['Order Month']==9].Sales.sum()/F['sales']*0+0:.0f}% … ".replace(f"{F['sep_nov_dec']+d[d['Order Month']==9].Sales.sum()/F['sales']*0+0:.0f}% … ", "51.6% of four-year sales, with a low point in January–February."), B),
 Paragraph('5.2 Products and categories', H2),
 tbl([['Category', 'Sales', 'Profit', 'Margin']] + [[c, d0(cat.Sales[c]), d0(cat.Profit[c]), p1(cat.Margin[c])] for c in ['Technology', 'Furniture', 'Office Supplies']], [5, 4, 4, 3]),
 Spacer(1, 6), fig('03_category_subcategory', 16, 'Figure 2 — Sales and profit by category; profit by sub-category (red = loss-making).'),
 Paragraph(f"Furniture sells as much as Office Supplies but earns one-seventh of the profit ({p1(cat.Margin['Furniture'])} margin). Three sub-categories lose money: Tables ({d0(sub.Profit['Tables'])}), Bookcases ({d0(sub.Profit['Bookcases'])}) and Supplies ({d0(sub.Profit['Supplies'])}). Copiers, Paper and Accessories have the highest margins (37.2%, 43.4%, 25.1%).", B)]
pr = F['prod'].reset_index(); top = pr.nlargest(5, 'Profit'); bot = pr.nsmallest(5, 'Profit')
rows = [['Best products (by profit)', 'Sales', 'Profit', 'Avg disc.']] + [[r['Product Name'][:52], d0(r.Sales), d0(r.Profit), f'{r.Disc*100:.0f}%'] for _, r in top.iterrows()]
rows2 = [['Worst products (by profit)', 'Sales', 'Profit', 'Avg disc.']] + [[r['Product Name'][:52], d0(r.Sales), d0(r.Profit), f'{r.Disc*100:.0f}%'] for _, r in bot.iterrows()]
story += [Paragraph('Best- and worst-performing products', H2), tbl(rows, [9.6, 2.6, 2.6, 2.2]), Spacer(1, 6), tbl(rows2, [9.6, 2.6, 2.6, 2.2]),
 Paragraph(f"<br/>{F['neg_products']} of {F['products']:,} products ({p1(F['neg_products']/F['products']*100)}) have a negative total profit, together {d0(-F['neg_products_loss'])} of losses. The worst items carry very high average discounts (28–53%).", B),
 Paragraph('5.3 Regions, states and customers', H2),
 tbl([['Region', 'Sales', 'Profit', 'Margin', 'Loss-making lines', 'Lines discounted >20%']] + [[r, d0(reg.Sales[r]), d0(reg.Profit[r]), p1(reg.Margin[r]), p1(d[d.Region == r]['Is Loss'].mean() * 100), p1((d[d.Region == r].Discount > .2).mean() * 100)] for r in ['West', 'East', 'South', 'Central']], [2.4, 3, 3, 2.2, 3.1, 3.3]),
 Spacer(1, 6), fig('05_region_profit', 14.5, 'Figure 3 — Profit by region (labels = margin) and profit by region and category.'),
 Paragraph(f"West is the most profitable region. Central has the lowest margin ({p1(reg.Margin['Central'])}) and the highest share of heavily discounted lines (27.7%, against 3.7% in West). {F['loss_states']} of {F['states']} states lose money, combined {d0(-F['loss_states_total'])}: Texas ({d0(st.Profit['Texas'])}), Ohio ({d0(st.Profit['Ohio'])}), Pennsylvania ({d0(st.Profit['Pennsylvania'])}) and Illinois ({d0(st.Profit['Illinois'])}).", B),
 Paragraph(f"<b>Customers.</b> Consumer is {p1(seg.Share['Consumer'])} of sales (margin {p1(seg.Margin['Consumer'])}), Corporate {p1(seg.Share['Corporate'])} ({p1(seg.Margin['Corporate'])}) and Home Office {p1(seg.Share['Home Office'])} ({p1(seg.Margin['Home Office'])}). The top 20% of customers generate {p1(F['top20_share'])} of sales, and {F['neg_customers']} customers ({p1(F['neg_customers']/F['customers']*100)}) have a negative lifetime profit — including the largest customer by sales (Sean Miller, $25,043 sales, −$1,981 profit). The 98.5% repeat-customer rate looks synthetic, so no retention conclusions are drawn.", B)]
# 6
rowsT = [['Statistical test (R)', 'Statistic', 'p-value']]
lab = {'Spearman discount vs profit': 'Spearman correlation, discount vs profit', 'Pearson discount vs margin': 'Pearson correlation, discount vs profit margin', 'Welch t-test profit, discount >20% vs <=20%': 'Welch t-test, profit per line (>20% vs ≤20% discount)',
       'Kruskal-Wallis profit by discount group': 'Kruskal–Wallis, profit by discount group', 'Kruskal-Wallis margin by category': 'Kruskal–Wallis, margin by category', 'Kruskal-Wallis margin by region': 'Kruskal–Wallis, margin by region', 'Kruskal-Wallis margin by segment': 'Kruskal–Wallis, margin by segment'}
for r in rstat.itertuples(): rowsT.append([lab[r.Test], f'{r.Statistic:,.2f}' if abs(r.Statistic) > 1.5 else f'{r.Statistic:.3f}', '< 0.001' if r.P_value < 0.001 else f'{r.P_value:.3f}'])
co = rco.copy()
story += [Paragraph('6. Factors affecting profitability (Python and R)', H1), Paragraph('6.1 Discounts', H2),
 tbl([['Discount group', 'Lines', 'Sales', 'Profit', 'Margin', 'Lines losing money']] + [[g, f"{int((d['Discount Group']==g).sum()):,}", d0(d[d['Discount Group']==g].Sales.sum()), d0(d[d['Discount Group']==g].Profit.sum()), p1(d[d['Discount Group']==g].Profit.sum()/d[d['Discount Group']==g].Sales.sum()*100), p1(d[d['Discount Group']==g]['Is Loss'].mean()*100)] for g in ['No Discount', 'Low (>0-20%)', 'Medium (>20-40%)', 'High (>40%)']], [3.6, 1.9, 3, 2.8, 2.2, 3.5]),
 Spacer(1, 6), fig('07_discount_profit', 15.5, 'Figure 4 — Profit by discount band and discount versus profit margin for each order line.'),
 Paragraph(f"Lines discounted by more than 20% ({F['hi_lines']:,} lines, {p1(F['hi_lines_pct'])} of lines, {p1(F['hi_sales_pct'])} of sales) have a combined net result of <b>{'-' + d0(-F['hi_profit'])}</b>, equal to {-F['hi_profit']/F['profit']*100:.0f}% of total profit, while all other lines earn {d0(F['other_profit'])} (margin 21.8%). 96.8% of the heavily discounted lines lose money. The pattern holds inside every category (margin at or below 20% / above 20%: Furniture +13% / −28%, Technology +25% / −26%, Office Supplies +25% / −119%), so it is not only a product-mix effect.", B),
 Paragraph('6.2 Statistical analysis in R', H2), tbl(rowsT, [9.6, 3.6, 3.8], right_from=1),
 Paragraph(f"<br/>Discount and profit are strongly negatively related (Spearman −0.54; Pearson with margin −0.86). Mean profit per line is −$97.18 above 20% discount and +$49.04 otherwise. Profit differs significantly across categories and regions; the difference across segments is statistically detectable but small (margins 11.5%–14.0%).", B),
 Paragraph(f"<b>Which factors matter most?</b> A multiple linear regression in R explains the line-level profit margin with discount, category, region, segment and ship mode (R² = {r2:.2f}). Discount alone gives R² = {r2d:.2f}. In the analysis of variance, discount accounts for {shares['Discount']:.1f}% of the explained variation, category {shares['Category']:.1f}%, and region, segment and ship mode together less than 0.1%. Each additional 10 percentage points of discount lowers the margin by about {abs(co.loc['Discount','Estimate'])*10:.0f} percentage points (coefficient {co.loc['Discount','Estimate']:.2f}), holding category, region, segment and ship mode constant; segment and ship mode effects are not significant.", B),
 box('<b>Shipping.</b> Average shipping time is 3.96 days (Same Day 0.04, First Class 2.18, Second Class 3.24, Standard Class 5.01). The correlation between shipping days and profit margin is about −0.01 and the regression finds no significant ship-mode effect, so shipping speed is not a driver of profitability here (delivery cost is not in the data).'),
 Spacer(1, 6), Paragraph('<b>Caution.</b> These are associations, not proven causes: the dataset has no cost or price-list data, so we cannot tell whether discounts cause the losses or whether low-margin or clearance items are simply discounted more.', B)]
# 7
def fm(model, yr_): r = rm[(rm.Model == model) & (rm.TestYear == yr_)].iloc[0]; return r
order = ['Trend + seasonal regression', 'STL + ETS', 'ETS (auto)', 'Seasonal naive', 'ARIMA (auto)', 'Naive (last value)']
rowsF = [['Model', 'MAPE 2016 test', 'MAPE 2017 test', 'MAE 2017', 'RMSE 2017']]
rowsF.append(['Python — linear regression (trend + month dummies)', f"{pyA['MAPE']:.1f}%", f"{pyB['MAPE']:.1f}%", d0(pyB['MAE']), d0(pyB['RMSE'])])
for m in order:
    a, b = fm(m, 2016), fm(m, 2017); rowsF.append([f'R — {m}', 'n/a' if pd.isna(a.MAPE) else f'{a.MAPE:.1f}%', f'{b.MAPE:.1f}%', d0(b.MAE), d0(b.RMSE)])
story += [Paragraph('7. Sales forecasting (Python and R)', H1),
 Paragraph('Monthly sales (48 months) were forecast with a chronological split: training on the past and testing on the following year, never a random split. Two test years were used for robustness (train 2014–2015 → test 2016; train 2014–2016 → test 2017). Models: a naive rule (last value), a seasonal-naive rule (same month last year), linear regression on a time trend plus month-of-year dummies (Python and R), exponential smoothing (ETS), ARIMA and STL + ETS (R, <i>forecast</i> package). Accuracy is measured by MAPE (mean absolute percentage error), MAE and RMSE.', B),
 tbl(rowsF, [7.4, 2.4, 2.4, 2.4, 2.4]), Paragraph('Table — Forecast accuracy on held-out data. STL + ETS cannot be fitted on only two years of history (n/a).', CAP),
 fig('12_forecast_models', 16.8, 'Figure 5 — Left: 2017 actual sales against the main models. Right: final model refitted on all data and its 2018 forecast with an 80% prediction interval.'),
 Paragraph(f"The trend + seasonal regression is the best overall: lowest error in 2017 (MAPE {pyB['MAPE']:.1f}%, against 24.5% for seasonal-naive and 97.3% for the naive rule) and best average across both test years. The Python and R versions of this model give identical results, which cross-validates the two tools. ETS and STL + ETS are close in 2017, and ARIMA is weaker. The final model, refitted on all 48 months, forecasts 2018 sales of about {d0(r18.forecast.sum())}, {(r18.forecast.sum()/yr.Sales[2017]-1)*100:+.1f}% against 2017, with the usual autumn peak (80% intervals in Figure 5).", B),
 Paragraph('<b>Use and limits.</b> An average monthly error of 17–27% is sizeable, the training history is short (24–36 months) and a linear trend may not continue. The model is a planning aid — for example to prepare stock and staff before September — not a basis for fixed sales targets.', B)]
# 8
def grid(ids, caption):
    imgs = []
    for i in ids: imgs.append(Image(f'reports/dashboard_screenshots/pbi-{i:02d}.png', width=8.35 * 28.35, height=8.35 * 28.35 * 940 / 1640))
    t = Table([[imgs[0], imgs[1]], [imgs[2], imgs[3]]], colWidths=[8.5 * 28.35] * 2); t.setStyle(TableStyle([('LEFTPADDING', (0, 0), (-1, -1), 1), ('RIGHTPADDING', (0, 0), (-1, -1), 1), ('TOPPADDING', (0, 0), (-1, -1), 1), ('BOTTOMPADDING', (0, 0), (-1, -1), 1), ('BOX', (0, 0), (0, 0), .3, colors.HexColor('#D5DCE4')), ('BOX', (1, 0), (1, 0), .3, colors.HexColor('#D5DCE4')), ('BOX', (0, 1), (0, 1), .3, colors.HexColor('#D5DCE4')), ('BOX', (1, 1), (1, 1), .3, colors.HexColor('#D5DCE4'))]))
    return [t, Paragraph(caption, CAP)]
story += [PageBreak(), Paragraph('8. Power BI executive dashboard', H1),
 Paragraph('The executive dashboard was built in Power BI Desktop from the cleaned dataset and a date table. It has <b>16 report pages in four sections</b>. Every page carries four slicers (date range, segment, region, category) and a page-navigation bar, and visuals cross-filter. The KPI measures are Total Sales, Total Profit, Total Orders (distinct orders), Profit Margin (profit ÷ sales), Average Discount and Average Shipping Days, calculated with DAX. The screenshots below are taken from the Power BI report.', B),
 KeepTogether([Paragraph('Section 1 — Executive Overview', H2)] + grid([1, 2, 3, 4], 'Figure 6 — Executive Overview: KPI cards ($2.30M sales, $286k profit, 12.47% margin, 5,009 orders), monthly sales trend, yearly sales vs profit, annual profit trend.')),
 KeepTogether([Paragraph('Section 2 — Sales and Product Performance', H2)] + grid([5, 6, 7, 8], 'Figure 7 — Sales by category, top 10 sub-categories by sales, loss-making products table, sales by sub-category.')),
 KeepTogether([Paragraph('Section 3 — Customer and Regional Analysis', H2)] + grid([9, 10, 11, 12], 'Figure 8 — Sales and profit by segment, sales by region, top 10 customers, profit by region.')),
 KeepTogether([Paragraph('Section 4 — Profitability and Business Insights', H2)] + grid([13, 14, 15, 16], 'Figure 9 — Profit margin by category, discount vs profit, average shipping days by ship mode, sub-category insights table.')),
 Paragraph('<b>What management can read from it.</b> Sales grow every year after 2015, yet profit stays a small share of sales; Technology and Office Supplies earn about 17% margins while Furniture earns 2.5%; West earns $108k of profit against $40k for Central; Tables, Bookcases and Supplies lose money; and shipping time differs by ship mode (0.04 to 5.01 days). The date, region, category and segment slicers let a manager reproduce any of the analyses in this report for a chosen period or market.', B)]
# 9
story += [Paragraph('9. Management recommendations', H1),
 Paragraph('Each recommendation follows the evidence presented above. Reasons are hypotheses to confirm with internal cost and price data.', B),
 tbl([['#', 'Action', 'Evidence', 'Expected effect and how to test'],
      ['1', '<b>Govern discounts:</b> approval rule above 20%, a minimum margin (floor price) per product, review of the lines above 40% first', f"Lines >20%: {F['hi_lines']:,} lines, net result −{d0(-F['hi_profit'])} (47% of profit); discount explains ~98% of explained margin variation", 'If these lines only broke even, profit would be +$135k (arithmetic upper bound, volume unchanged). Test: 20% cap in one region for one quarter against a control region'],
      ['2', '<b>Reprice Furniture:</b> review discounts, supplier cost and freight of Tables and Bookcases', f"Furniture margin {p1(cat.Margin['Furniture'])}; Tables {d0(sub.Profit['Tables'])}, Bookcases {d0(sub.Profit['Bookcases'])}", 'Furniture is profitable when discounts are controlled (+13% margin at ≤20% discount). Obtain cost data before changing list prices'],
      ['3', '<b>Regional targets:</b> fewer than 10% of lines above 20% discount; treat Texas, Ohio, Pennsylvania and Illinois as one project', f"Central margin {p1(reg.Margin['Central'])} with 27.7% of lines >20%; West 3.7%; {F['loss_states']} loss-making states", 'Central margin toward the East/South range (12–14%); no dollar figure without a pilot'],
      ['4', '<b>Review loss-making products:</b> the 20 worst of 299, starting with Cubify 3D printers; stop deep-discount promotions', f"{F['neg_products']} products, {d0(-F['neg_products_loss'])} combined loss", 'Up to $76.7k of loss addressed; some may be loss leaders by design'],
      ['5', '<b>Report profit, not only sales:</b> margin next to sales, split into ≤20% and >20% discount sales; add profit to key-account lists', f"{F['neg_customers']} customers lose money; the top customer by sales is loss-making", 'Early warning; monthly tracking in the Power BI dashboard'],
      ['6', '<b>Plan for the autumn peak:</b> stock and staff before September; avoid deep discounts when demand is already high', f"Sep–Dec = 51.6% of sales; forecast MAPE {pyB['MAPE']:.1f}% (2017 test)", 'Operational (fewer stock-outs, smoother workload); use the forecast as a planning aid'],
      ['7', '<b>Build on strengths:</b> Copiers, Paper, Accessories; Home Office and Corporate segments; West-style discount discipline', 'Margins 25–43% in these sub-categories; Home Office margin 14.0%; West 3.7% of lines >20%', 'Profit grows faster than by adding discounted volume']], [0.6, 5.4, 5.6, 5.4], right_from=-1),
 Paragraph('10. Limitations and conclusion', H1),
 *bl(['Public sample dataset, not a real company; customer behaviour looks synthetic.', 'No cost, price-list, returns or shipping-cost data: causes cannot be proven and shipping cost-efficiency cannot be judged.', 'Four years of history; the forecast is tested on two years only and is indicative.', 'The effects quoted are arithmetic on the sample (volume unchanged); real customers may react to lower discounts.']),
 Paragraph(f"<br/>The business grows but earns a thin {p1(F['margin'])} margin. Profit is made at normal discounts and lost on a small group of heavily discounted lines, which also explains most of the weakness of Furniture, the Central region and ten states. Discount depth is by far the strongest factor in the data, far ahead of region, segment or shipping. Governing discounts, repricing Furniture and monitoring margin in the Power BI dashboard are the highest-value actions; the proposed pilot and cost data are the next steps needed to confirm the results.", B)]
# Appendix A
py_corr = '''# Discount groups, KPI helper and correlation (Python)
bins   = [-0.001, 0, 0.20, 0.40, 1.0]
labels = ['No Discount', 'Low (>0-20%)', 'Medium (>20-40%)', 'High (>40%)']
df['Discount Group'] = pd.cut(df['Discount'], bins=bins, labels=labels)      # ">20%" means strictly greater than 0.20

def kpi(by):                                      # same definitions for every grouping
    t = df.groupby(by).agg(Sales=('Sales','sum'), Profit=('Profit','sum'), Orders=('Order ID','nunique'))
    t['Margin %'] = t.Profit / t.Sales * 100      # ratio of totals, not average of row margins
    return t

kpi('Discount Group')                             # margin by discount group
df[['Sales','Quantity','Discount','Profit','Profit Margin','Shipping Days']].corr()           # Pearson
df[['Discount','Profit']].corr(method='spearman')                                               # Spearman (robust to outliers)
stats.ttest_ind(df.loc[df.Discount>0.2,'Profit'], df.loc[df.Discount<=0.2,'Profit'], equal_var=False)   # Welch t-test'''
py_fc = '''# Sales forecast (Python): trend + month-of-year dummies, chronological split
ms = df.groupby(df['Order Date'].dt.to_period('M')).Sales.sum(); ms.index = ms.index.to_timestamp()
X = pd.DataFrame({'t': np.arange(len(ms))}, index=ms.index)
X = X.join(pd.get_dummies(ms.index.month, prefix='m', drop_first=True).set_index(ms.index).astype(int))
train, test = ms.index < '2017-01-01', ms.index >= '2017-01-01'
model = LinearRegression().fit(X[train], ms[train]); pred = model.predict(X[test])
snaive = ms[train].values[-12:]                                    # seasonal-naive baseline
mape = lambda a, f: np.mean(abs((a - f) / a)) * 100
print(mape(ms[test].values, pred), mape(ms[test].values, snaive))'''
story += [PageBreak(), Paragraph('Appendix A. Python code', H1), Paragraph('Data cleaning and feature engineering are shown in Section 2. Analysis and forecasting code:', B), code(py_corr), Spacer(1, 8), code(py_fc)]
rc = open('r/forecast_and_stats.R').read()
r_stats = rc[rc.index('## ---------- 1.'):rc.index('## Factors affecting')]; r_lm = rc[rc.index('## Factors affecting'):rc.index('## ---------- 2.')]; r_fc = rc[rc.index('## ---------- 2.'):rc.index('A <- run_fold')]
story += [Paragraph('Appendix B. R code', H1), Paragraph('R 4.5 with the <i>forecast</i> package; full script in <i>r/forecast_and_stats.R</i>, outputs in <i>r/r_output.txt</i>.', B), code(r_stats.replace('stats_out <- data.frame(', 'stats_out <- data.frame(').split('stats_out <- data.frame(')[0]), Spacer(1, 6), code(r_lm.split('d$m <- ')[0] + 'd$m <- ' + r_lm.split('d$m <- ')[1].split('cat("\\nLinear')[0]), Spacer(1, 6), code(r_fc)]
def footer(c, doc):
    c.saveState(); c.setFont('Carlito', 8); c.setFillColor(GREY); c.drawString(56.7, 30, 'Business Performance Analysis, Sales Forecasting & BI Dashboard  |  Public sample dataset - not company data'); c.drawRightString(538.6, 30, f'Page {doc.page}'); c.restoreState()
SimpleDocTemplate('reports/Business_Performance_Project_Report.pdf', pagesize=A4, leftMargin=56.7, rightMargin=56.7, topMargin=52, bottomMargin=52, title='Business Performance Analysis, Sales Forecasting & Business Intelligence Dashboard', author='').build(story, onFirstPage=lambda c, d_: None, onLaterPages=footer)
print('built')
