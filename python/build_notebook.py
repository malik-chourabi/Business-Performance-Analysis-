import nbformat as nbf
nb = nbf.v4.new_notebook()
C = []
def md(t): C.append(nbf.v4.new_markdown_cell(t.strip()))
def code(t): C.append(nbf.v4.new_code_cell(t.strip()))

md("""# Business Performance Analysis — Sample Superstore
**Python notebook: data cleaning, exploratory analysis, statistics and forecasting**

*Dataset: Sample Superstore — a public sample dataset used for learning. It is NOT confidential data from a real company.*

**Role of Python in the project:** Python is the main analytical tool. In this notebook we (A) inspect the raw data, (B) clean it, (C) engineer analytical variables, (D) run exploratory analysis, (E) apply statistics, (F) test a simple forecast against a baseline, (G) produce charts and (H) export the cleaned file used by SQL and Power BI.

**Contents:** A Inspection · B Cleaning · C Feature engineering · D EDA · E Statistics · F Forecasting · G Findings summary · H Export""")

code("""import pandas as pd, numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from scipy import stats
pd.set_option('display.width', 200); pd.set_option('display.max_columns', 40)
pd.set_option('display.float_format', lambda x: f'{x:,.2f}')
plt.rcParams.update({'figure.dpi': 100, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.titlesize': 13, 'axes.titleweight': 'bold', 'axes.labelsize': 10})
import os; os.makedirs('../reports/figures', exist_ok=True)
NAVY, TEAL, RED, GREY, GOLD = '#1F3A5F', '#2A9D8F', '#C0392B', '#8A94A0', '#E9A23B'
def save(name): plt.tight_layout(); plt.savefig(f'../reports/figures/{name}.png', dpi=150, bbox_inches='tight')
money = mtick.FuncFormatter(lambda x, p: f'${x/1000:,.0f}K')""")

md("""## A. Data inspection
**What / why:** Before changing anything we look at the raw file: size, columns, types, missing values and duplicates. Never assume — verify.
Note: `Postal Code` is read as text (`dtype=str`) so we can see whether leading zeros were lost.""")
code("""raw = pd.read_csv('../data/raw/Sample_Superstore.csv', dtype={'Postal Code': str})
print('Shape (rows, columns):', raw.shape)
raw.head()""")
code("raw.tail()")
code("""print(raw.dtypes)
print('\\nMissing values per column:'); print(raw.isna().sum()[raw.isna().sum() > 0] if raw.isna().sum().sum() else 'None — 0 missing values in all 21 columns')""")
code("""print('Exact duplicate rows (all columns):', raw.duplicated().sum())
cols_wo_id = [c for c in raw.columns if c != 'Row ID']
print('Duplicates ignoring Row ID:', raw.duplicated(subset=cols_wo_id).sum())
raw[raw.duplicated(subset=cols_wo_id, keep=False)].T""")
md("""**Reading:** Row ID is unique so there are no exact duplicates, but **one pair of rows is identical in every column except Row ID** (same order, product, quantity, discount). It could be a genuine repeated order line (a customer ordering the same item twice) or a data-entry duplicate. The file gives no way to prove which, so we **keep both rows and flag one** (`Possible Duplicate`). Impact: Sales $281.37 of $2.30M (0.01%) — immaterial.""")
code("""raw.describe().T""")
code("""# Structure checks: consistency of keys and identifiers
checks = {
 'Customer ID -> >1 name': (raw.groupby('Customer ID')['Customer Name'].nunique() > 1).sum(),
 'Order ID -> >1 customer': (raw.groupby('Order ID')['Customer ID'].nunique() > 1).sum(),
 'Product ID -> >1 product name': (raw.groupby('Product ID')['Product Name'].nunique() > 1).sum(),
 'Product ID -> >1 sub-category': (raw.groupby('Product ID')['Sub-Category'].nunique() > 1).sum(),
 'State -> >1 region': (raw.groupby('State')['Region'].nunique() > 1).sum(),
 'Postal codes with 4 digits': (raw['Postal Code'].str.len() == 4).sum(),
 'Rows with Sales <= 0': (raw['Sales'] <= 0).sum(),
 'Rows with negative Profit': (raw['Profit'] < 0).sum(),
 'Countries': raw['Country'].nunique(),
}
pd.Series(checks, name='count')""")
md("""**Data-quality issues found**

| # | Issue | Evidence | Decision |
|---|---|---|---|
| 1 | Dates stored as text (`m/d/yyyy`) | dtype = object/str | Convert to datetime |
| 2 | Postal codes lost leading zeros | 438 four-digit codes in 6 states (CT, MA, ME, NH, NJ, RI); Vermont's 11 codes keep their zero, so the source file is itself inconsistent | Pad to 5 digits, store as text |
| 3 | 32 Product IDs carry more than one product name | name variants for same ID | Use most frequent name per ID as canonical; keep original column |
| 4 | One pair of identical rows (except Row ID) | see above | Keep, flag |
| 5 | `Country` is constant | only United States | Keep; no analytical value |
| 6 | No cost column | — | Derive `Cost = Sales − Profit` |
| 7 | Currency/units not stated | — | Assume USD; state as limitation |""")

md("""## B. Data cleaning
Each step is documented. **No rows are deleted**, so every total in the cleaned file equals the raw file.""")
code("""df = raw.copy()
# 1) Dates
df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y')
df['Ship Date']  = pd.to_datetime(df['Ship Date'],  format='%m/%d/%Y')
# 2) Postal code leading zeros
df['Postal Code'] = df['Postal Code'].str.zfill(5)
# 3) Canonical product name per Product ID (most frequent variant)
canon = df.groupby('Product ID')['Product Name'].agg(lambda s: s.value_counts().index[0])
df['Product Name Original'] = df['Product Name']
df['Product Name'] = df['Product ID'].map(canon)
# 4) Flag the possible duplicate
df['Possible Duplicate'] = df.drop(columns=['Row ID', 'Product Name Original']).duplicated().astype(int)
print('Ship date before order date:', (df['Ship Date'] < df['Order Date']).sum())
print('Postal codes now all 5 digits:', (df['Postal Code'].str.len() == 5).all())
print('Rows changed by product-name standardisation:', (df['Product Name'] != df['Product Name Original']).sum())""")

md("""## C. Feature engineering
| Variable | Formula | Business purpose |
|---|---|---|
| Order Year / Quarter / Month | from Order Date | Trend and seasonality |
| Shipping Days | Ship Date − Order Date | Delivery performance |
| Profit Margin | Profit ÷ Sales (blank if Sales = 0) | Profitability independent of order size |
| Cost | Sales − Profit | Implied cost base |
| Is Loss | 1 if Profit < 0 | Loss tracking |
| Discount Band | No discount, 1–10 %, 11–20 %, 21–30 %, 31–50 %, >50 % | Compare discount policies |""")
code("""df['Order Year']    = df['Order Date'].dt.year
df['Order Quarter'] = df['Order Date'].dt.quarter
df['Order Month']   = df['Order Date'].dt.month
df['Order Month Name'] = df['Order Date'].dt.strftime('%b')
df['Year-Month']    = df['Order Date'].dt.to_period('M').astype(str)
df['Shipping Days'] = (df['Ship Date'] - df['Order Date']).dt.days
df['Profit Margin'] = np.where(df['Sales'] > 0, df['Profit'] / df['Sales'], np.nan)
df['Cost']          = df['Sales'] - df['Profit']
df['Is Loss']       = (df['Profit'] < 0).astype(int)
bins   = [-0.001, 0, 0.10, 0.20, 0.30, 0.50, 1.0]
labels = ['No discount', '1-10%', '11-20%', '21-30%', '31-50%', '>50%']
df['Discount Band'] = pd.cut(df['Discount'], bins=bins, labels=labels).astype(str)
# Reconciliation: cleaning must not change the totals
assert round(df['Sales'].sum(), 4) == round(raw['Sales'].sum(), 4) and len(df) == len(raw)
print('Reconciliation OK — rows:', len(df), '| Sales:', round(df.Sales.sum(), 2), '| Profit:', round(df.Profit.sum(), 2))
df[['Order Date','Shipping Days','Profit Margin','Cost','Discount','Discount Band']].head()""")

md("""## D. Exploratory data analysis
A helper function builds the same KPI table for any grouping so that every comparison uses identical definitions:
**Profit Margin = Profit ÷ Sales** (computed on group totals, not the average of row margins) and **Orders = distinct Order IDs**.""")
code("""def kpi(by, data=df):
    t = data.groupby(by).agg(Sales=('Sales','sum'), Profit=('Profit','sum'),
                             Orders=('Order ID','nunique'), Quantity=('Quantity','sum'),
                             Avg_Discount=('Discount','mean'))
    t['Margin %'] = t['Profit'] / t['Sales'] * 100
    t['Sales share %'] = t['Sales'] / data['Sales'].sum() * 100
    return t

total_sales, total_profit = df.Sales.sum(), df.Profit.sum()
n_orders, n_cust = df['Order ID'].nunique(), df['Customer ID'].nunique()
summary = pd.Series({
 'Total Sales': total_sales, 'Total Profit': total_profit, 'Profit Margin %': total_profit/total_sales*100,
 'Distinct Orders': n_orders, 'Distinct Customers': n_cust, 'Total Quantity': df.Quantity.sum(),
 'Average Order Value': total_sales/n_orders, 'Average Discount % (row level)': df.Discount.mean()*100,
 'Average Shipping Days': df['Shipping Days'].mean(), 'Loss-making lines': df['Is Loss'].sum(),
 'Loss-making lines %': df['Is Loss'].mean()*100, 'Total losses on those lines': df.loc[df.Profit<0,'Profit'].sum()})
summary""")

md("### D1. Time trends")
code("""yearly = kpi('Order Year'); yearly['Sales growth %'] = yearly['Sales'].pct_change()*100; yearly['Profit growth %'] = yearly['Profit'].pct_change()*100
yearly""")
code("""monthly = df.groupby('Year-Month').agg(Sales=('Sales','sum'), Profit=('Profit','sum'))
monthly.index = pd.to_datetime(monthly.index)
fig, ax = plt.subplots(figsize=(11, 4.2))
ax.plot(monthly.index, monthly.Sales, color=NAVY, lw=2, label='Sales')
ax.plot(monthly.index, monthly.Profit, color=TEAL, lw=2, label='Profit')
ax.yaxis.set_major_formatter(money); ax.set_title('Monthly Sales and Profit, 2014–2017'); ax.set_ylabel('USD'); ax.legend(frameon=False)
ax.grid(axis='y', alpha=.25); save('01_monthly_sales_profit'); plt.show()""")
md("**Interpretation:** Sales are strongly seasonal — peaks every September–December and troughs in January–February — with an upward trend from 2016. Profit follows the same shape but is far more volatile and is a small fraction of sales.")
code("""season = df.groupby('Order Month')[['Sales','Profit']].sum()
season['Share of sales %'] = season.Sales/season.Sales.sum()*100
season.index = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
print(season.round(2))
fig, ax = plt.subplots(figsize=(9, 3.8)); ax.bar(season.index, season.Sales, color=[GOLD if m in ('Sep','Nov','Dec') else NAVY for m in season.index])
ax.yaxis.set_major_formatter(money); ax.set_title('Total Sales by Calendar Month (all years)'); save('02_seasonality'); plt.show()""")

md("### D2. Category and sub-category performance")
code("""cat = kpi('Category').sort_values('Sales', ascending=False); cat""")
code("""sub = kpi('Sub-Category').sort_values('Profit'); sub""")
code("""fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
c = kpi('Category').sort_values('Sales')
axes[0].barh(c.index, c.Sales, color=NAVY, label='Sales'); axes[0].barh(c.index, c.Profit, color=TEAL, label='Profit')
axes[0].xaxis.set_major_formatter(money); axes[0].set_title('Sales and Profit by Category'); axes[0].legend(frameon=False)
for i, (s, m) in enumerate(zip(c.Sales, c['Margin %'])): axes[0].text(s, i, f'  margin {m:.1f}%', va='center', fontsize=9)
axes[0].set_xlim(0, c.Sales.max()*1.3)
s = sub
axes[1].barh(s.index, s.Profit, color=[RED if v < 0 else TEAL for v in s.Profit]); axes[1].xaxis.set_major_formatter(money)
axes[1].set_title('Profit by Sub-Category (red = loss-making)'); axes[1].axvline(0, color='k', lw=.8)
save('03_category_subcategory'); plt.show()""")
md("**Interpretation:** Technology and Office Supplies earn ~17 % margins. Note that Binders, although profitable overall (14.9 % margin), carries $38.5K of line-level losses — all in the >50 % discount band. Furniture has similar sales to Office Supplies but earns only ~2.5 % margin. Three sub-categories lose money overall: **Tables, Bookcases, Supplies**. Machines are almost break-even despite $189K of sales.")

md("### D3. Best- and worst-performing products")
code("""prod = kpi(['Product ID', 'Product Name'])   # Product ID is the true product key (1,862 IDs; 1,818 distinct names)
print('Top 10 by profit'); display(prod.sort_values('Profit', ascending=False).head(10)[['Sales','Profit','Margin %','Avg_Discount']])
print('Bottom 10 by profit'); display(prod.sort_values('Profit').head(10)[['Sales','Profit','Margin %','Avg_Discount']])
# round to cents so floating-point noise (e.g. -3.6e-15) is not mistaken for a loss
neg = prod.Profit.round(2) < 0
print('Products (by Product ID) with negative total profit:', neg.sum(), 'of', len(prod), f'({neg.mean()*100:.1f}%)')
print('Total profit lost on those products: $', round(prod.loc[neg,'Profit'].sum(), 2))""")
code("""fig, axes = plt.subplots(1, 2, figsize=(13, 5))
t = prod.sort_values('Profit', ascending=False).head(10)[::-1]; b = prod.sort_values('Profit').head(10)[::-1]
axes[0].barh([n[1][:38] for n in t.index], t.Profit, color=TEAL); axes[0].set_title('Top 10 Products by Profit'); axes[0].xaxis.set_major_formatter(money)
axes[1].barh([n[1][:38] for n in b.index], b.Profit, color=RED); axes[1].set_title('Bottom 10 Products by Profit'); axes[1].xaxis.set_major_formatter(money)
save('04_top_bottom_products'); plt.show()""")

md("### D4. Regional and geographic performance")
code("""reg = kpi('Region').sort_values('Profit', ascending=False); reg""")
code("""state = kpi('State').sort_values('Profit')
print('Loss-making states:', (state.Profit < 0).sum()); display(state[state.Profit < 0][['Sales','Profit','Margin %','Avg_Discount']])
print('Top 5 states by profit'); display(state.tail(5)[['Sales','Profit','Margin %','Avg_Discount']])
city = kpi('City').sort_values('Profit'); print('Worst 5 cities'); display(city.head(5)[['Sales','Profit','Margin %']])""")
code("""rc = df.pivot_table(index='Region', columns='Category', values='Profit', aggfunc='sum')
fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
r = kpi('Region').sort_values('Profit'); axes[0].barh(r.index, r.Profit, color=TEAL); axes[0].xaxis.set_major_formatter(money); axes[0].set_title('Profit by Region')
for i, (p, m) in enumerate(zip(r.Profit, r['Margin %'])): axes[0].text(p, i, f'  {m:.1f}%', va='center', fontsize=9)
rc.plot(kind='bar', ax=axes[1], color=[NAVY, TEAL, GOLD], rot=0); axes[1].yaxis.set_major_formatter(money); axes[1].set_title('Profit by Region and Category'); axes[1].legend(frameon=False, fontsize=8); axes[1].axhline(0, color='k', lw=.8)
save('05_region_profit'); plt.show()
rc.round(0)""")
md("**Interpretation:** West is the largest and most profitable region. **Central** has the second-lowest sales but the lowest margin (7.9 %) and the highest average discount (24 %); Central Furniture loses money. Texas, Ohio, Pennsylvania and Illinois each lose $12–26K.")

md("### D5. Customer segments and purchasing behaviour")
code("""seg = kpi('Segment').sort_values('Sales', ascending=False)
seg['Avg order value'] = seg.Sales / seg.Orders
cust_cnt = df.groupby('Segment')['Customer ID'].nunique(); seg['Customers'] = cust_cnt; seg['Sales per customer'] = seg.Sales/seg.Customers
seg""")
code("""cust = df.groupby('Customer ID').agg(Name=('Customer Name','first'), Sales=('Sales','sum'), Profit=('Profit','sum'), Orders=('Order ID','nunique')).sort_values('Sales', ascending=False)
cust['Cum share %'] = cust.Sales.cumsum()/cust.Sales.sum()*100
print('Top 10 customers by sales'); display(cust.head(10))
top20 = int(len(cust)*0.2); print(f'Top 20% of customers ({top20}) generate {cust.Sales.head(top20).sum()/cust.Sales.sum()*100:.1f}% of sales')
print('Customers with negative total profit:', (cust.Profit<0).sum(), 'of', len(cust))
orders = df.groupby('Order ID').agg(Sales=('Sales','sum'), Lines=('Row ID','count'), Date=('Order Date','first'), Cust=('Customer ID','first'))
print('\\nOrder value: mean %.2f | median %.2f' % (orders.Sales.mean(), orders.Sales.median()))
oc = orders.groupby('Cust').size(); print('Orders per customer: mean %.1f, min %d, max %d' % (oc.mean(), oc.min(), oc.max()))
print('Repeat customers (>1 order): %.1f%%' % ((oc>1).mean()*100))""")
code("""fig, axes = plt.subplots(1, 2, figsize=(12, 4))
s = kpi('Segment').sort_values('Sales'); axes[0].barh(s.index, s.Sales, color=NAVY); axes[0].xaxis.set_major_formatter(money); axes[0].set_title('Sales by Customer Segment')
for i, (v, m) in enumerate(zip(s.Sales, s['Margin %'])): axes[0].text(v, i, f'  margin {m:.1f}%', va='center', fontsize=9)
axes[0].set_xlim(0, s.Sales.max()*1.3)
axes[1].plot(range(1, len(cust)+1), cust['Cum share %'], color=NAVY); axes[1].set_title('Customer Concentration (cumulative % of sales)')
axes[1].set_xlabel('Customers ranked by sales'); axes[1].set_ylabel('% of total sales'); axes[1].grid(alpha=.25)
save('06_segments_customers'); plt.show()""")

md("### D6. Discounts and profitability")
code("""disc = kpi('Discount Band').reindex(['No discount','1-10%','11-20%','21-30%','31-50%','>50%'])
disc['Avg profit per line'] = df.groupby('Discount Band').Profit.mean()
disc['% lines loss-making'] = df.groupby('Discount Band')['Is Loss'].mean()*100
disc""")
code("""fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
axes[0].bar(disc.index, disc.Profit, color=[RED if v < 0 else TEAL for v in disc.Profit]); axes[0].yaxis.set_major_formatter(money)
axes[0].set_title('Total Profit by Discount Band'); axes[0].axhline(0, color='k', lw=.8); axes[0].tick_params(axis='x', rotation=20)
axes[1].scatter(df.Discount*100, df['Profit Margin']*100, alpha=.15, s=10, color=NAVY)
axes[1].set_xlabel('Discount (%)'); axes[1].set_ylabel('Profit margin (%)'); axes[1].set_title('Discount vs Profit Margin (each dot = order line)'); axes[1].axhline(0, color='k', lw=.8)
save('07_discount_profit'); plt.show()""")
code("""# Where does the loss start? Share of lines that are loss-making by exact discount level
lv = df.groupby('Discount').agg(Lines=('Row ID','count'), Profit=('Profit','sum'), Loss_share=('Is Loss','mean'))
lv['Loss_share'] *= 100; lv""")
code("""high_disc = df[df.Discount > 0.20]
print(f'Lines with discount > 20%: {len(high_disc):,} ({len(high_disc)/len(df)*100:.1f}% of lines) | Sales ${high_disc.Sales.sum():,.0f} ({high_disc.Sales.sum()/df.Sales.sum()*100:.1f}% of sales) | Profit ${high_disc.Profit.sum():,.0f}')
print(f'Profit on all other lines: ${df[df.Discount<=0.20].Profit.sum():,.0f}')
print(f'Total profit would be ${df[df.Discount<=0.20].Profit.sum():,.0f} vs actual ${df.Profit.sum():,.0f} if no line had a discount above 20% (illustrative arithmetic only; assumes the same sales volume).')""")
md("""**Interpretation:** The pattern is stark. Lines with no discount earn a 29.5 % margin; at 11–20 % margin falls to 11.6 %; every band above 20 % loses money in total, and discounts above 50 % lose $1.19 for every $1 of sales. Every line discounted 45 % or more is loss-making, and so are 91.6 % of lines at 30 %. **Caution:** this is association, not proven causation — heavily discounted products may also be lower-margin products or clearance items. The dataset has no cost list or price history, so we cannot separate the two explanations.""")

md("### D7. Shipping performance")
code("""ship = df.groupby('Ship Mode').agg(Lines=('Row ID','count'), Avg_days=('Shipping Days','mean'), Min=('Shipping Days','min'), Max=('Shipping Days','max'), Sales=('Sales','sum'), Profit=('Profit','sum'))
ship['Margin %'] = ship.Profit/ship.Sales*100; ship['Share of lines %'] = ship.Lines/len(df)*100; ship""")
code("""print('Overall average shipping days: %.2f' % df['Shipping Days'].mean())
yr = df.groupby('Order Year')['Shipping Days'].mean(); print(yr.round(2).to_dict())
rg = df.groupby('Region')['Shipping Days'].mean(); print(rg.round(2).to_dict())
print('Correlation shipping days vs profit margin: %.3f' % df[['Shipping Days','Profit Margin']].corr().iloc[0,1])
fig, ax = plt.subplots(figsize=(8, 3.6)); ax.bar(ship.index, ship.Avg_days, color=NAVY); ax.set_title('Average Shipping Days by Ship Mode'); ax.set_ylabel('days')
for i, v in enumerate(ship.Avg_days): ax.text(i, v+.05, f'{v:.1f}', ha='center')
save('08_shipping'); plt.show()""")
md("**Interpretation:** Ship modes behave as labelled (Same Day ≈ 0 days, First Class ≈ 2, Second Class ≈ 3.2, Standard ≈ 5). Profit margin is virtually unrelated to shipping speed (correlation ≈ −0.01), so shipping is not a driver of profitability in this data. Delivery *cost* is not recorded, so shipping profitability cannot be assessed.")

md("### D8. Unusual observations and loss-making transactions")
code("""loss = df[df.Profit < 0]
print(f'Loss-making lines: {len(loss):,} ({len(loss)/len(df)*100:.1f}%) | total loss ${loss.Profit.sum():,.0f} | equals {abs(loss.Profit.sum())/df[df.Profit>0].Profit.sum()*100:.1f}% of all profit earned on profitable lines')
print('\\nLoss by sub-category (lines with Profit<0 only):'); display(loss.groupby('Sub-Category').agg(Lines=('Row ID','count'), Loss=('Profit','sum')).sort_values('Loss').head(6))
print('Ten largest single-line losses:'); display(loss.nsmallest(10, 'Profit')[['Order ID','Product Name','Region','Sales','Discount','Profit']])""")
code("""# Outliers using the IQR rule (Tukey fences) on Sales and Profit
def iqr_outliers(s):
    q1, q3 = s.quantile([.25, .75]); i = q3 - q1; lo, hi = q1 - 1.5*i, q3 + 1.5*i
    return ((s < lo) | (s > hi)).sum(), lo, hi
for col in ['Sales', 'Profit', 'Quantity']:
    n, lo, hi = iqr_outliers(df[col]); print(f'{col:9s}: {n:5,} outliers ({n/len(df)*100:4.1f}%)  fences [{lo:,.1f}, {hi:,.1f}]')
print('\\nTop 5 sales lines:'); display(df.nlargest(5, 'Sales')[['Order ID','Product Name','Sales','Discount','Profit']])
print('Top 5 profit lines:'); display(df.nlargest(5, 'Profit')[['Order ID','Product Name','Sales','Discount','Profit']])
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
axes[0].hist(np.log10(df.Sales), bins=40, color=NAVY); axes[0].set_title('Distribution of Sales per line (log10 scale)'); axes[0].set_xlabel('log10(Sales)')
axes[1].hist(df.Profit.clip(-500, 500), bins=60, color=TEAL); axes[1].set_title('Distribution of Profit per line (clipped ±$500)'); axes[1].set_xlabel('Profit')
save('09_distributions'); plt.show()""")
md("**Interpretation:** Sales and profit are heavily right-skewed: most lines are small, a handful are very large (the biggest sale is a $22.6K video-conferencing system; the biggest profit is $8.4K on a copier). Because of this skew the **median is more representative than the mean** for a typical line. IQR outliers are *real* high-value orders, not errors, so they are kept; they matter because a few large lines move totals a lot.")

md("""## E. Statistical analysis""")
code("""desc = df[['Sales','Quantity','Discount','Profit','Shipping Days']].agg(['mean','median','std','min','max','skew']).T
desc['CV (std/mean)'] = desc['std']/desc['mean']; desc""")
md("**Reading:** For Sales the mean ($229.86) is ~4× the median ($54.49) and skewness is very high — a right-skewed distribution. Profit's standard deviation ($234) is 8× its mean, i.e. very unstable per line.")
code("""corr = df[['Sales','Quantity','Discount','Profit','Profit Margin','Shipping Days']].corr()
spear = df[['Sales','Quantity','Discount','Profit','Profit Margin','Shipping Days']].corr(method='spearman')
display(corr.round(3)); print('Spearman (rank) correlation of Discount with Profit: %.3f' % spear.loc['Discount','Profit'])
fig, ax = plt.subplots(figsize=(6.5, 5)); im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)
ax.set_xticks(range(len(corr))); ax.set_xticklabels(corr.columns, rotation=40, ha='right'); ax.set_yticks(range(len(corr))); ax.set_yticklabels(corr.columns)
for i in range(len(corr)):
    for j in range(len(corr)): ax.text(j, i, f'{corr.iloc[i,j]:.2f}', ha='center', va='center', fontsize=8)
plt.colorbar(im, fraction=.046); ax.set_title('Correlation Matrix (Pearson)'); save('10_correlation'); plt.show()""")
md("""**Meaning:** Pearson correlation measures *linear* association from −1 to +1. Discount vs Profit = −0.22 (weak-to-moderate negative), Discount vs Profit Margin = −0.86 (strong negative). The relationship is much stronger for margin than for absolute profit because absolute profit is dominated by order size (Sales vs Profit = +0.48). **Correlation ≠ causation.**""")
code("""# Hypothesis tests: are profit margins different across groups?
# 1) Welch t-test: discounted vs non-discounted lines
a = df.loc[df.Discount == 0, 'Profit']; b = df.loc[df.Discount > 0, 'Profit']
t, p = stats.ttest_ind(a, b, equal_var=False); print(f'Mean profit per line — no discount ${a.mean():.2f} vs discounted ${b.mean():.2f} | Welch t={t:.2f}, p={p:.2e}')
# 2) Kruskal-Wallis (non-parametric, suits skewed data): profit margin across the 3 categories and 4 regions
for col in ['Category', 'Region', 'Segment']:
    groups = [g['Profit Margin'].values for _, g in df.groupby(col)]; h, p = stats.kruskal(*groups)
    print(f'Kruskal-Wallis on profit margin by {col:9s}: H={h:8.2f}, p={p:.2e}')
# 3) Discount vs profit within the Central region only (does the pattern hold inside a single region?)
for r, g in df.groupby('Region'): print(f'{r:8s} corr(Discount, Profit margin) = {g[["Discount","Profit Margin"]].corr().iloc[0,1]:.3f}')""")
md("**Reading the tests:** Very small p-values mean the observed differences are unlikely to be due to chance alone. They show the differences are real in this sample, **not why** they occur. Because profit is highly skewed we favour the rank-based Kruskal–Wallis test. The discount–margin correlation is strongly negative in every region (−0.76 to −0.92), so the pattern is not driven by a single region. The Segment difference is statistically significant (p = 0.008) but small in size (margins of 11.5–14.0 %).")
code("""# Is Central's weakness explained by its discount mix? Compare margins on like-for-like discount bands
mix = df.pivot_table(index='Region', columns='Discount Band', values='Sales', aggfunc='sum')
mix = mix.div(mix.sum(axis=1), axis=0)[['No discount','1-10%','11-20%','21-30%','31-50%','>50%']]*100
print('Share of each region\\'s sales by discount band (%)'); display(mix.round(1))
mg = df.pivot_table(index='Region', columns='Discount Band', values='Profit', aggfunc='sum')/df.pivot_table(index='Region', columns='Discount Band', values='Sales', aggfunc='sum')*100
print('Profit margin by region and discount band (%)'); display(mg[['No discount','11-20%','21-30%','31-50%','>50%']].round(1))""")
md("**Reading:** Central earns 25.8 % of its sales on lines discounted above 20 % (East 21.4 %, South 18.0 %, West only 2.4 %). Within the no-discount band, regional margins are similar (27–31 %), and within 11–20 % they range from 8 % to 15 %. So regional margin gaps are **partly a discount-mix effect**: West's high margin goes with very little deep discounting, and Central's weak margin goes with a heavy deep-discount share. This is association only — product mix and customer mix may also contribute and cannot be separated with this data. (East also discounts deeply yet keeps a 13.5 % margin, so discount mix is not the whole story.)")

md("""## F. Forecasting (optional — included because 48 months of data are available)
**Question:** can monthly sales be forecast better than a naive rule? **Design:** train on 2014–2016 (36 months), test on 2017 (12 months) — a chronological split, never random. **Baselines:** (1) *seasonal naive* = same month last year; (2) *naive* = last observed value. **Model:** linear regression on a time trend plus month-of-year dummies (captures growth + seasonality). **Metrics:** MAE, RMSE, MAPE.""")
code("""from sklearn.linear_model import LinearRegression
ms = df.groupby(df['Order Date'].dt.to_period('M')).Sales.sum(); ms.index = ms.index.to_timestamp()
X = pd.DataFrame({'t': np.arange(len(ms))}, index=ms.index)
X = X.join(pd.get_dummies(ms.index.month, prefix='m', drop_first=True).set_index(ms.index).astype(int))
train, test = ms.index < '2017-01-01', ms.index >= '2017-01-01'
model = LinearRegression().fit(X[train], ms[train]); pred = pd.Series(model.predict(X[test]), index=ms.index[test])
snaive = pd.Series(ms[train].values[-12:], index=ms.index[test]); naive = pd.Series(ms[train].values[-1], index=ms.index[test])
def metrics(y, yhat): return pd.Series({'MAE': np.mean(abs(y-yhat)), 'RMSE': np.sqrt(np.mean((y-yhat)**2)), 'MAPE %': np.mean(abs((y-yhat)/y))*100})
res = pd.DataFrame({'Trend + month dummies (LinearRegression)': metrics(ms[test], pred), 'Seasonal naive (same month last year)': metrics(ms[test], snaive), 'Naive (last value)': metrics(ms[test], naive)}).T
res""")
code("""fig, ax = plt.subplots(figsize=(11, 4.2)); ax.plot(ms.index, ms, color=NAVY, lw=2, label='Actual')
ax.plot(pred.index, pred, color=GOLD, lw=2, ls='--', label='Regression forecast'); ax.plot(snaive.index, snaive, color=GREY, lw=1.5, ls=':', label='Seasonal naive')
ax.axvline(pd.Timestamp('2016-12-31'), color='k', lw=.8); ax.text(pd.Timestamp('2017-01-10'), ms.max()*.95, 'test period')
ax.yaxis.set_major_formatter(money); ax.set_title('Monthly Sales Forecast vs Actual (test = 2017)'); ax.legend(frameon=False); save('11_forecast'); plt.show()
best = res['MAPE %'].idxmin(); print('Lowest MAPE:', best, '| %.1f%%' % res['MAPE %'].min())""")
md("""**Interpretation and limits:** Only the model's performance on the 12 held-out months is reported (no in-sample claims). On the 2017 test the trend + seasonality regression had a MAPE of about 17 %, versus about 25 % for the seasonal-naive rule and about 97 % for the naive rule, so it beat both baselines: it captures the seasonal shape *and* the growth that the seasonal-naive rule misses. Still, a ~17 % average monthly error is sizeable, 36 training points and 12 test points are few, and a linear trend may not continue. The forecast supports planning discussions (e.g. building inventory ahead of September–December), not precise targets.""")

md("""## G. Summary of validated findings
(All numbers below are computed from the data above and re-checked in SQL; see `sql/business_queries.sql`.)""")
code("""print(f'Sales ${total_sales:,.2f} | Profit ${total_profit:,.2f} | Margin {total_profit/total_sales*100:.2f}% | Orders {n_orders:,} | Customers {n_cust}')
print('Furniture margin %.1f%% vs Technology %.1f%% / Office Supplies %.1f%%' % tuple(kpi('Category').loc[['Furniture','Technology','Office Supplies'],'Margin %']))
print('Loss-making sub-categories:', ', '.join(sub[sub.Profit<0].index))
print('Loss-making products (by ID): %d | Loss-making states: %d | Central margin %.1f%% vs West %.1f%%' % (neg.sum(), (state.Profit<0).sum(), reg.loc['Central','Margin %'], reg.loc['West','Margin %']))
print('Discount >20%%: %d lines, profit $%s' % (len(high_disc), f'{high_disc.Profit.sum():,.0f}'))""")

md("## H. Export\nThe cleaned dataset (all 9,994 rows, 33 columns) is the single source for SQL and Power BI.")
code("""df.to_csv('../data/processed/cleaned_sales.csv', index=False)
chk = pd.read_csv('../data/processed/cleaned_sales.csv'); print('Exported:', chk.shape, '| Sales check:', round(chk.Sales.sum(), 2))""")
nb['cells'] = C
nb['metadata'] = {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}, 'language_info': {'name': 'python'}}
nbf.write(nb, 'python/business_analysis.ipynb')
