"""Renders 4 reference layout previews (Python/matplotlib). NOT Power BI screenshots."""
import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.ticker as mt
from matplotlib.patches import FancyBboxPatch
d = pd.read_csv('data/processed/cleaned_sales.csv', parse_dates=['Order Date'])
NAVY, TEAL, RED, GOLD, GREY, BG = '#1F3A5F', '#2A9D8F', '#C0392B', '#E9A23B', '#8A94A0', '#F4F6F8'
K = mt.FuncFormatter(lambda x, p: f'${x/1000:,.0f}K')
S, P, O = d.Sales.sum(), d.Profit.sum(), d['Order ID'].nunique()
def frame(title, sub):
    fig = plt.figure(figsize=(16, 9), facecolor=BG)
    fig.text(.03, .955, title, fontsize=20, fontweight='bold', color=NAVY, va='center')
    fig.text(.03, .925, sub, fontsize=10, color=GREY, va='center')
    fig.text(.97, .955, 'REFERENCE PREVIEW (Python-rendered layout) — not a Power BI screenshot', fontsize=9, color=RED, ha='right', va='center', fontweight='bold')
    for i, t in enumerate(['Year ▾ All', 'Region ▾ All', 'Category ▾ All', 'Segment ▾ All']):
        fig.text(.03 + i * .105, .895, t, fontsize=9, color=NAVY, bbox=dict(boxstyle='round,pad=.35', fc='white', ec='#C9D2DC'))
    for i, t in enumerate(['1 Executive', '2 Products', '3 Customers & Regions', '4 Profitability']):
        fig.text(.60 + i * .098, .895, t, fontsize=8.5, color='white', bbox=dict(boxstyle='round,pad=.35', fc=NAVY if i == int(title[0]) - 1 else GREY, ec='none'))
    return fig
def card(fig, x, y, w, h, label, value, color=NAVY):
    ax = fig.add_axes([x, y, w, h]); ax.axis('off'); ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle='round,pad=0,rounding_size=.05', fc='white', ec='#D5DCE4', transform=ax.transAxes))
    ax.text(.5, .66, value, ha='center', va='center', fontsize=21, fontweight='bold', color=color); ax.text(.5, .22, label, ha='center', va='center', fontsize=9.5, color=GREY)
def panel(fig, rect, title):
    ax = fig.add_axes(rect); ax.set_facecolor('white'); ax.set_title(title, loc='left', fontsize=11, fontweight='bold', color=NAVY)
    for s in ['top', 'right']: ax.spines[s].set_visible(False)
    for s in ['left', 'bottom']: ax.spines[s].set_color('#D5DCE4')
    ax.tick_params(labelsize=8, colors='#44505C'); return ax
kpi = lambda g: g.agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum'))
# ---- Page 1
f = frame('1  Executive Overview', 'Overall sales, profitability and trend — all data 2014–2017 (public sample dataset)')
for i, (l, v, c) in enumerate([('Total Sales', f'${S/1e6:,.2f}M', NAVY), ('Total Profit', f'${P/1e3:,.0f}K', TEAL), ('Profit Margin', f'{P/S*100:.1f}%', GOLD), ('Total Orders', f'{O:,}', NAVY), ('Total Quantity', f'{d.Quantity.sum():,}', NAVY)]):
    card(f, .03 + i * .188, .76, .175, .10, l, v, c)
m = d.groupby(d['Order Date'].dt.to_period('M').dt.to_timestamp())[['Sales', 'Profit']].sum()
ax = panel(f, [.05, .08, .52, .62], 'Monthly Sales and Profit'); ax.plot(m.index, m.Sales, color=NAVY, lw=2, label='Sales'); ax.plot(m.index, m.Profit, color=TEAL, lw=2, label='Profit')
ax.plot(m.index, m.Sales.rolling(3).mean(), color=GREY, ls='--', lw=1.2, label='3M rolling avg'); ax.yaxis.set_major_formatter(K); ax.legend(frameon=False, fontsize=8); ax.grid(axis='y', alpha=.2)
c = kpi(d.groupby('Category')).sort_values('Sales'); ax = panel(f, [.64, .42, .33, .28], 'Sales by Category'); ax.barh(c.index, c.Sales, color=NAVY); ax.xaxis.set_major_formatter(K)
for i, (s, p) in enumerate(zip(c.Sales, c.Profit)): ax.text(s, i, f'  margin {p/s*100:.1f}%', va='center', fontsize=8)
ax.set_xlim(0, c.Sales.max() * 1.35)
r = kpi(d.groupby('Region')).sort_values('Sales'); ax = panel(f, [.64, .08, .33, .28], 'Sales by Region'); ax.barh(r.index, r.Sales, color=TEAL); ax.xaxis.set_major_formatter(K)
for i, (s, p) in enumerate(zip(r.Sales, r.Profit)): ax.text(s, i, f'  margin {p/s*100:.1f}%', va='center', fontsize=8)
ax.set_xlim(0, r.Sales.max() * 1.35); f.savefig('reports/dashboard_screenshots/page1_executive_overview_PREVIEW.png', dpi=110, facecolor=BG); plt.close(f)
# ---- Page 2
f = frame('2  Sales and Product Performance', 'Which categories and products drive profit — and which lose money')
sc = kpi(d.groupby('Sub-Category')).sort_values('Profit'); ax = panel(f, [.05, .08, .28, .78], 'Profit by Sub-Category (red = loss)'); ax.barh(sc.index, sc.Profit, color=[RED if v < 0 else TEAL for v in sc.Profit]); ax.xaxis.set_major_formatter(K); ax.axvline(0, color='k', lw=.8)
pr = d.groupby(['Product ID', 'Product Name'])[['Sales', 'Profit']].sum().reset_index()
t = pr.nlargest(8, 'Profit')[::-1]; ax = panel(f, [.43, .50, .28, .36], 'Top 8 Products by Profit'); ax.barh(t['Product Name'].str[:34], t.Profit, color=TEAL); ax.xaxis.set_major_formatter(K); ax.tick_params(axis='y', labelsize=7)
b = pr.nsmallest(8, 'Profit')[::-1]; ax = panel(f, [.43, .08, .28, .32], 'Bottom 8 Products by Profit (losses)'); ax.barh(b['Product Name'].str[:34], b.Profit, color=RED); ax.xaxis.set_major_formatter(K); ax.tick_params(axis='y', labelsize=7)
neg = (pr.Profit.round(2) < 0).sum(); card(f, .76, .76, .21, .10, 'Loss-making products (of 1,862)', f'{neg}', RED)
ax = panel(f, [.76, .08, .21, .60], 'Sales vs Margin by Sub-Category'); ax.scatter(sc.Sales, sc.Profit / sc.Sales * 100, s=60, color=NAVY, alpha=.8); ax.axhline(0, color='k', lw=.8); ax.xaxis.set_major_formatter(K); ax.set_ylabel('margin %', fontsize=8)
for n, row in sc.iterrows():
    if row.Profit < 0 or row.Sales > 300000: ax.annotate(n, (row.Sales, row.Profit / row.Sales * 100), fontsize=7, xytext=(3, 3), textcoords='offset points')
f.savefig('reports/dashboard_screenshots/page2_sales_product_performance_PREVIEW.png', dpi=110, facecolor=BG); plt.close(f)
# ---- Page 3
f = frame('3  Customer and Regional Analysis', 'Segment, customer and geographic contribution to sales and profit')
sg = kpi(d.groupby('Segment')).sort_values('Sales'); ax = panel(f, [.05, .52, .27, .33], 'Sales and Profit by Segment'); y = np.arange(len(sg)); ax.barh(y + .2, sg.Sales, .38, color=NAVY, label='Sales'); ax.barh(y - .2, sg.Profit, .38, color=TEAL, label='Profit'); ax.set_yticks(y); ax.set_yticklabels(sg.index); ax.xaxis.set_major_formatter(K); ax.legend(frameon=False, fontsize=8)
rg = kpi(d.groupby('Region')).sort_values('Profit'); ax = panel(f, [.05, .08, .27, .33], 'Profit by Region (label = margin)'); ax.barh(rg.index, rg.Profit, color=TEAL); ax.xaxis.set_major_formatter(K)
for i, (s, p) in enumerate(zip(rg.Sales, rg.Profit)): ax.text(p, i, f'  {p/s*100:.1f}%', va='center', fontsize=8)
st = kpi(d.groupby('State')).sort_values('Profit'); w = st.head(10); ax = panel(f, [.42, .08, .26, .78], '10 Weakest States by Profit'); ax.barh(w.index, w.Profit, color=RED); ax.xaxis.set_major_formatter(K); ax.invert_yaxis()
cu = d.groupby(['Customer Name'])[['Sales', 'Profit']].sum().nlargest(10, 'Sales')[::-1]; ax = panel(f, [.77, .08, .20, .78], 'Top 10 Customers by Sales (red = loss)'); ax.barh(cu.index, cu.Sales, color=[RED if p < 0 else NAVY for p in cu.Profit]); ax.xaxis.set_major_formatter(K); ax.tick_params(axis='y', labelsize=7)
f.savefig('reports/dashboard_screenshots/page3_customer_regional_analysis_PREVIEW.png', dpi=110, facecolor=BG); plt.close(f)
# ---- Page 4
f = frame('4  Profitability and Business Insights', 'Discounts, shipping and the factors associated with weak profit')
hi = d[d.Discount > .2]
for i, (l, v, c) in enumerate([('Loss-making lines', f'{d["Is Loss"].mean()*100:.1f}%', RED), ('Profit on discount >20% lines', f'-${abs(hi.Profit.sum())/1e3:,.0f}K', RED), ('Share of sales discounted >20%', f'{hi.Sales.sum()/S*100:.1f}%', GOLD), ('Avg shipping days', f'{d["Shipping Days"].mean():.2f}', NAVY)]):
    card(f, .03 + i * .24, .76, .22, .10, l, v, c)
order = ['No discount', '1-10%', '11-20%', '21-30%', '31-50%', '>50%']; db = kpi(d.groupby('Discount Band')).reindex(order)
ax = panel(f, [.05, .08, .30, .60], 'Profit by Discount Band'); ax.bar(order, db.Profit, color=[RED if v < 0 else TEAL for v in db.Profit]); ax.yaxis.set_major_formatter(K); ax.axhline(0, color='k', lw=.8); ax.tick_params(axis='x', rotation=25)
ax2 = ax.twinx(); ax2.plot(order, db.Profit / db.Sales * 100, color=NAVY, marker='o'); ax2.set_ylabel('margin %', fontsize=8); ax2.tick_params(labelsize=8)
mx = d.pivot_table(index='Region', columns='Category', values='Profit', aggfunc='sum') / d.pivot_table(index='Region', columns='Category', values='Sales', aggfunc='sum') * 100
ax = panel(f, [.43, .38, .25, .30], 'Profit Margin % — Region × Category'); im = ax.imshow(mx.values, cmap='RdYlGn', vmin=-20, vmax=25, aspect='auto'); ax.set_xticks(range(3)); ax.set_xticklabels(mx.columns, fontsize=8); ax.set_yticks(range(4)); ax.set_yticklabels(mx.index)
for i in range(4):
    for j in range(3): ax.text(j, i, f'{mx.values[i, j]:.1f}%', ha='center', va='center', fontsize=9)
sh = d.groupby('Ship Mode').agg(days=('Shipping Days', 'mean'), mg=('Profit', 'sum'), s=('Sales', 'sum')).sort_values('days'); ax = panel(f, [.43, .08, .25, .22], 'Average Shipping Days by Ship Mode'); ax.bar(sh.index, sh.days, color=NAVY); ax.tick_params(axis='x', labelsize=7)
ax = f.add_axes([.74, .08, .23, .60]); ax.axis('off'); ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle='round,pad=0,rounding_size=.02', fc='white', ec='#D5DCE4', transform=ax.transAxes))
txt = ('Key insights (from validated analysis)\n\n• Discounts above 20% coincide with losses:\n  lines >20% lose $135K in total.\n\n• Furniture earns a 2.5% margin vs ~17%\n  for Technology and Office Supplies.\n\n• Central has the weakest margin (7.9%)\n  and the highest average discount (24%).\n\n• Shipping speed is unrelated to margin\n  (correlation ≈ -0.01).\n\nAssociation, not proven causation.')
ax.text(.05, .95, txt, va='top', fontsize=9.5, color='#1F2933', linespacing=1.5)
f.savefig('reports/dashboard_screenshots/page4_profitability_insights_PREVIEW.png', dpi=110, facecolor=BG); plt.close(f); print('previews done')
