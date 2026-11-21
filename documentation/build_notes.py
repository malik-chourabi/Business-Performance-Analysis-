import sys; sys.path.insert(0, 'reports')
from facts import F
import pandas as pd
yr, cat, sub, reg, seg, band, sm, st = F['yr'], F['cat'], F['sub'], F['reg'], F['seg'], F['band'], F['ship_mode'], F['state']
d0 = lambda x: f'${x:,.0f}'; p1 = lambda x: f'{x:.1f}%'
def mdt(df, fmt=None):
    cols = list(df.columns); out = '| ' + ' | '.join(['']+cols) + ' |\n|' + '---|' * (len(cols)+1) + '\n'
    for i, r in df.iterrows(): out += '| ' + ' | '.join([str(i)] + [fmt(c, r[c]) if fmt else str(r[c]) for c in cols]) + ' |\n'
    return out
def f_(c, v): return f'{v:,.2f}' if isinstance(v, float) else f'{v:,}' if isinstance(v, int) else str(v)
T = lambda t: t
d = pd.read_csv('data/processed/cleaned_sales.csv'); lines = d.groupby('Discount Band').size()
sqlres = open('sql/query_results.md').read()
fc = F['fc']
N = []
a = N.append
a(f"""---
title: "Business Performance Analysis — Complete Project Notes"
subtitle: "Study, reproduction and interview-defence guide (Sample Superstore, 2014–2017)"
---

::: {{custom-style="Note"}}
**How to use these notes.** They explain what was actually done, why, and what the results mean, so you can study without the chat. All numbers were computed from the dataset and checked across tools. The Power BI dashboard (`powerbi/Business_Performance_Analysis.pbix`) was built by the project author in Power BI Desktop; its report pages and visuals were inspected for these notes, while the on-screen values should be confirmed against the validation table in Chapter 5. Sample Superstore is a **public sample dataset**, not confidential company data.
:::

\\newpage

# Chapter 1 — Project overview

## 1.1 Background and business problem
You act as a data analyst for a retail company that records many sales transactions but has no clear picture of its commercial performance. Management wants to know: overall sales and profit; best and worst products; most profitable regions; customer purchasing behaviour; sales trends; how discounts relate to profit; and what factors drive performance.

## 1.2 Objectives
1. Measure sales and profitability with fixed KPI definitions.
2. Rank products, categories, regions and segments.
3. Quantify the discount–profit relationship.
4. Describe trend and seasonality and test a forecast against a baseline.
5. Build a reproducible Excel → Python → SQL → Power BI workflow with cross-tool validation.
6. Give evidence-based recommendations.

## 1.3 Business questions and where they are answered
| Question | Answer in this project |
|---|---|
| Overall sales and profit? | {d0(F['sales'])} sales, {d0(F['profit'])} profit, margin {p1(F['margin'])} (Python, SQL Q02) |
| Best/worst products? | Top: Canon imageCLASS 2200 Copier ($25,200 profit). Worst: Cubify CubeX 3D Printer Double Head (−$8,880). {F['neg_products']} of {F['products']:,} products lose money |
| Most profitable regions? | West {d0(reg.Profit['West'])}, East {d0(reg.Profit['East'])}, South {d0(reg.Profit['South'])}, Central {d0(reg.Profit['Central'])} |
| Customer behaviour? | {F['orders_per_cust']:.1f} orders/customer; top 20% of customers = {p1(F['top20_share'])} of sales |
| Trends? | 2015 −2.8%, 2016 +29.5%, 2017 +20.4%; Q4 peak |
| Discounts vs profit? | Margin {p1(band.Margin['No discount'])} with no discount → {p1(band.Margin['>50%'])} above 50% |
| Performance factors? | Discount depth, product mix (Furniture), region |

## 1.4 Dataset source, characteristics and limitations
Sample Superstore: {F['rows']:,} order lines × 21 columns; {F['orders']:,} orders; {F['customers']} customers; {F['products']:,} products; 3 categories, 17 sub-categories; 4 regions; {F['states']} states; orders from 2014-01-03 to 2017-12-30; USD assumed. **Limitations:** public/sample data; only four years; no cost, price list, returns or shipping-cost columns (so causes can't be proven); discount reasons unknown; one unverifiable possible duplicate; inconsistent postal codes. **Association is not causation.**

## 1.5 Methodology and role of each tool
| Tool | Role | Why this tool |
|---|---|---|
| Excel | First look: structure, quality, formulas, pivots | Fastest way to *see* data; every analyst/manager reads Excel |
| Python | Main analysis: cleaning, EDA, statistics, forecast | Handles any size, reproducible, rich statistics |
| SQL (SQLite) | Structured storage and business queries; validates Python | Standard business-data skill; SQLite needs no server |
| Power BI | Model, KPIs (DAX), interactive dashboard | Management-facing monitoring |

Data flow: raw CSV (never edited) → Excel inspection → Python cleaning → `cleaned_sales.csv` → SQLite database **and** star-schema CSVs → Power BI.

**Project folder:** `data/raw`, `data/processed`, `excel/`, `python/`, `sql/`, `powerbi/`, `reports/`, `documentation/`, `README.md`.

# Chapter 2 — Excel

## 2.1 What was done
Workbook `excel/initial_data_inspection.xlsx` has five sheets: **Raw_Data** (untouched 21 columns + 7 teal helper columns with formulas), **Data_Inspection**, **Basic_Analysis**, **Pivot_Analysis** (six real pivot tables), **Preliminary_Findings**. It contains 70,257 formulas and recalculates with 0 errors; headline figures match Python and SQL.

## 2.2 Inspection results
| Check | Result | How |
|---|---|---|
| Rows / columns | 9,994 / 21 | `COUNTA` |
| Missing cells | 0 | `COUNTBLANK` |
| Row ID unique & sequential | Yes | `MAX = COUNT` |
| Possible duplicate lines | 1 | helper column compares a row with the row above |
| Distinct orders | 5,009 | helper "New Order Flag" then `SUM` |
| Loss-making lines | 1,871 | `COUNTIF(profit,"<0")` |
| Postal codes < 10000 | 449 | `COUNTIF` (438 stored without zero + 11 Vermont codes whose zero Excel strips) |
| Ship date before order date | 0 | `SUMPRODUCT` |

**Variable types:** numeric (Sales, Quantity, Discount, Profit), categorical (Ship Mode, Segment, Region, Category, Sub-Category, State, City), dates (Order/Ship Date), identifiers (Row/Order/Customer/Product ID). Postal Code is a code and should be text.

## 2.3 Sorting and filtering
`Raw_Data` has AutoFilter and a frozen header (Data → Filter / Sort). Examples: sort Profit ascending to see the biggest losses; filter Discount ≥ 0.5 and Category = Furniture to see deep-discounted furniture.

## 2.4 Formulas used (purpose · syntax · example)
| Formula | Purpose | Syntax | Example in the workbook |
|---|---|---|---|
| SUM | Add numbers | `=SUM(range)` | `=SUM(Raw_Data!$R$2:$R$9995)` → total sales |
| AVERAGE | Mean | `=AVERAGE(range)` | average discount 15.6% |
| COUNTIF | Count cells meeting a condition | `=COUNTIF(range,criteria)` | `=COUNTIF(U:U,"<0")` → 1,871 loss lines |
| SUMIF / SUMIFS | Sum with one / several conditions | `=SUMIFS(sum_range,crit_range,crit)` | sales per region |
| AVERAGEIFS | Conditional mean | `=AVERAGEIFS(avg_range,crit_range,crit)` | avg discount per region |
| IF | Decision | `=IF(test,if_true,if_false)` | `=IF(R2=0,0,U2/R2)` profit margin, guarded against zero sales |
| MEDIAN, STDEV, QUARTILE | Descriptive statistics | `=MEDIAN(range)` | median sales $54.49 |
| YEAR | Extract year | `=YEAR(C2)` | helper Order Year |

**Gotcha learned:** criteria beginning with `>` are read as operators, so the discount band ">50%" must be matched with `"="&A55`; otherwise the formula counted values greater than 0.5.

## 2.5 Pivot tables
A pivot table summarises a table without formulas: drag fields to Rows/Columns/Values. Built: Sales by Region, Sales by Category, Sales by Segment, Profit by Category, Sales and Profit by Sub-Category × Region, Profit by Discount Band × Category. Pivots must be refreshed after data changes.

## 2.6 Key results and interpretation
| Region | Sales | Profit | Margin |
|---|---|---|---|
""" + ''.join(f"| {r} | {d0(reg.Sales[r])} | {d0(reg.Profit[r])} | {p1(reg.Margin[r])} |\n" for r in reg.sort_values('Sales', ascending=False).index) + f"""
Furniture margin is {p1(cat.Margin['Furniture'])} versus {p1(cat.Margin['Technology'])} (Technology). Interpretation: Excel shows *where* to look; Python and SQL then explain why. Excel stayed deliberately basic (no macros/Power Pivot) because it supports, rather than replaces, Python.

# Chapter 3 — Python

## 3.1 Role and libraries
Python is the main analytical tool. **pandas** (tables, grouping), **NumPy** (numerics, `np.where`), **Matplotlib** (charts), **SciPy** (t-test, Kruskal–Wallis), **scikit-learn** (`LinearRegression` for the forecast). Notebook: `python/business_analysis.ipynb` (70 cells, executed top-to-bottom with 0 errors); script versions `clean_data.py`.

## 3.2 Import and inspection
```python
raw = pd.read_csv('../data/raw/Sample_Superstore.csv', dtype={{'Postal Code': str}})
raw.shape            # (9994, 21)
raw.isna().sum()     # no missing values
raw.duplicated().sum()   # 0 exact duplicates
```
Reading Postal Code as text lets us *see* the lost leading zeros instead of hiding them.

## 3.3 Cleaning (each decision documented; no row deleted)
```python
df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y')
df['Postal Code'] = df['Postal Code'].str.zfill(5)
canon = df.groupby('Product ID')['Product Name'].agg(lambda s: s.value_counts().index[0])
df['Product Name'] = df['Product ID'].map(canon)       # one name per product ID
df['Possible Duplicate'] = df.drop(columns=['Row ID','Product Name Original']).duplicated().astype(int)
assert round(df.Sales.sum(),4) == round(raw.Sales.sum(),4) and len(df) == len(raw)   # reconciliation
```
Why keep the possible duplicate? Two identical lines in one order may be a customer ordering the same item twice; the file cannot tell. Impact is $281 (0.01%).

## 3.4 Feature engineering
```python
df['Shipping Days'] = (df['Ship Date'] - df['Order Date']).dt.days
df['Profit Margin'] = np.where(df['Sales'] > 0, df['Profit'] / df['Sales'], np.nan)   # zero-sales guard
df['Discount Band'] = pd.cut(df['Discount'], bins=[-0.001,0,0.10,0.20,0.30,0.50,1.0], labels=[...])
```
`Profit Margin` lets us compare a $10 order with a $10,000 order; `Discount Band` turns a continuous variable into comparable groups.

## 3.5 The KPI helper
```python
def kpi(by):
    t = df.groupby(by).agg(Sales=('Sales','sum'), Profit=('Profit','sum'), Orders=('Order ID','nunique'))
    t['Margin %'] = t.Profit / t.Sales * 100      # ratio of totals, not mean of row margins
    return t
```
Using one function guarantees identical definitions everywhere.

## 3.6 Descriptive statistics
Sales: mean ${d['Sales'].mean():.2f}, **median ${d['Sales'].median():.2f}**, standard deviation $623.25, skewness 12.97 → very right-skewed; Profit mean $28.66, median $8.67, SD $234.26 (CV 8.2). *Why it matters:* a few huge orders pull the mean up, so the median describes a typical line better.

## 3.7 Exploratory results
**Overall:** {d0(F['sales'])} sales; {d0(F['profit'])} profit; margin {p1(F['margin'])}; AOV ${F['aov']:.2f} (median order ${F['median_order']:.2f}); {F['loss_lines']:,} loss-making lines ({p1(F['loss_pct'])}), total loss {d0(-F['loss_total'])}.

**Yearly:**

""" + mdt(yr[['Sales','Profit','Margin']].round(2), f_) + f"""
**Seasonality:** Sep+Nov+Dec = {p1(F['sep_nov_dec'])} of sales; Jan+Feb = {p1(F['jan_feb'])}.

**Categories:**

""" + mdt(cat[['Sales','Profit','Margin','Disc']].round(2), f_) + f"""
**Loss-making sub-categories:** Tables ({d0(sub.Profit['Tables'])}), Bookcases ({d0(sub.Profit['Bookcases'])}), Supplies ({d0(sub.Profit['Supplies'])}). Binders are profitable overall but carry $38,510 of losses, all in the >50% discount band.

**Products:** {F['neg_products']} of {F['products']:,} products (by Product ID) have negative total profit, together {d0(F['neg_products_loss'])}. (Totals are rounded to cents so floating-point noise like −3.6×10⁻¹⁵ isn't mistaken for a loss — a real bug found during SQL/Python validation.)

**Regions/states:** {F['loss_states']} loss-making states, {d0(F['loss_states_total'])} combined; Texas {d0(st.Profit['Texas'])}, Ohio {d0(st.Profit['Ohio'])}, Pennsylvania {d0(st.Profit['Pennsylvania'])}, Illinois {d0(st.Profit['Illinois'])}. Central Furniture margin {p1(F['furn_central_margin'])}.

**Segments:** Consumer {p1(seg.Share['Consumer'])} of sales ({p1(seg.Margin['Consumer'])} margin), Corporate {p1(seg.Share['Corporate'])} ({p1(seg.Margin['Corporate'])}), Home Office {p1(seg.Share['Home Office'])} ({p1(seg.Margin['Home Office'])}).

**Customers:** {F['orders_per_cust']:.1f} orders per customer, {p1(F['repeat_pct'])} repeat; top 20% ({F['top20_n']}) = {p1(F['top20_share'])} of sales; {F['neg_customers']} customers have negative total profit; top customer Sean Miller $25,043 sales but −$1,981 profit.

**Discount bands:**

""" + ''.join([f"| {b} | {lines[b]:,} | {d0(band.Sales[b])} | {d0(band.Profit[b])} | {p1(band.Margin[b])} |\n" for b in band.index]).join(['| Band | Lines | Sales | Profit | Margin |\n|---|---|---|---|---|\n', '']) + f"""
**Shipping:** average {F['ship']:.2f} days; Same Day {sm.days['Same Day']:.2f}, First {sm.days['First Class']:.2f}, Second {sm.days['Second Class']:.2f}, Standard {sm.days['Standard Class']:.2f}. Correlation of shipping days with margin {F['corr'].loc['Shipping Days','Profit Margin']:.2f}.

## 3.8 Statistical methods and what they mean
* **Pearson correlation** (−1…+1): linear association. Discount vs margin {F['corr'].loc['Discount','Profit Margin']:.2f} (strong negative); discount vs profit {F['corr'].loc['Discount','Profit']:.2f}; sales vs profit {F['corr'].loc['Sales','Profit']:.2f}. Spearman (rank) discount–profit {F['spearman_dp']:.2f}. Correlation ≠ causation.
* **Outliers (IQR rule):** values beyond Q1−1.5·IQR or Q3+1.5·IQR. 11.7% of Sales and 18.8% of Profit lines are flagged; they are real large/small orders, so they are kept.
* **Welch t-test:** mean profit/line {F['mean_nodisc']:.2f} (no discount) vs {F['mean_disc']:.2f} (discounted); t = {F['welch_t']:.1f}, p < 0.001. Welch's version doesn't assume equal variances.
* **Kruskal–Wallis:** rank-based test of margin differences across groups: Category H ≈ {F['kw']['Category'][0]:.0f}, Region H ≈ {F['kw']['Region'][0]:.0f}, Segment H ≈ {F['kw']['Segment'][0]:.1f} (p = 0.008, small effect). A small p-value means the difference is unlikely to be chance — **not** that it's large or causal.
* **Discount mix by region:** share of sales on lines discounted >20%: Central {p1(F['reg_hi_share']['Central'])}, East {p1(F['reg_hi_share']['East'])}, South {p1(F['reg_hi_share']['South'])}, West {p1(F['reg_hi_share']['West'])}. Regional margin gaps are partly a discount-mix effect (East discounts deeply yet keeps a 13.5% margin, so it's not the whole story).

## 3.9 Forecasting (implemented because there are 48 months)
Train 2014–2016, test 2017 (chronological split). Model: `LinearRegression` on a time index plus month dummies. Baselines: seasonal naïve (same month last year) and naïve (last value).

| Model | MAE | RMSE | MAPE |
|---|---|---|---|
""" + ''.join(f"| {k} | {v['MAE']:,.0f} | {v['RMSE']:,.0f} | {v['MAPE']:.1f}% |\n" for k, v in fc.items()) + f"""
MAE = average absolute error; RMSE penalises big errors; MAPE = average % error. The regression beat both baselines, but ~17% monthly error, 36 training and 12 test points, and the assumption that a linear trend continues mean it's a planning aid, not a target-setting tool.

## 3.10 Visualisations
Eleven charts in `reports/figures/` (monthly trend, seasonality, category/sub-category, top/bottom products, region, segments/customer concentration, discount vs profit, shipping, distributions, correlation matrix, forecast). Each has a title, labels, units and an interpretation cell in the notebook.

# Chapter 4 — SQL

## 4.1 Concepts
A **database** stores tables of rows/columns with defined types and keys, and **SQL** asks questions of it. **SQLite** was chosen because it is a single file (`sql/superstore.db`), needs no server, and supports standard SQL.

## 4.2 Design
Six tables: `sales_clean` (flat copy of the cleaned CSV, 9,994 rows) plus a simple star-style design — `dim_customer` (793), `dim_product` (1,862), `dim_geography` (632), `orders` (5,009), `order_lines` (9,994) with primary and foreign keys (foreign-key check: no violations). This enables JOINs without unnecessary complexity.

## 4.3 Syntax used
* `SELECT … FROM … WHERE` filter rows; `GROUP BY` aggregate groups; `HAVING` filters *after* aggregation; `ORDER BY … DESC` sorts; `LIMIT` caps rows.
* `SUM`, `AVG`, `COUNT`; **`COUNT(DISTINCT order_id)`** for unique orders — `COUNT(*)` would return 9,994 lines, not 5,009 orders.
* `CASE WHEN … THEN … END` builds bands/conditional sums; `JOIN … ON` links tables; `WITH` (CTE) for readable steps.

## 4.4 Key queries (full set of 22 in `sql/business_queries.sql`; outputs in `sql/query_results.md`)
```sql
-- Q06: which segment contributes most to sales?
SELECT segment, ROUND(SUM(sales),2) AS sales,
       ROUND(SUM(sales)*100.0/(SELECT SUM(sales) FROM sales_clean),2) AS sales_share_pct,
       COUNT(DISTINCT order_id) AS orders
FROM sales_clean GROUP BY segment ORDER BY sales DESC;
```
*Meaning:* the subquery supplies the grand total so each segment's share can be computed → Consumer {p1(seg.Share['Consumer'])}.
```sql
-- Q09: average profit by discount band (CASE WHEN)
SELECT CASE WHEN discount=0 THEN '1. No discount' WHEN discount<=0.10 THEN '2. 1-10%'
            WHEN discount<=0.20 THEN '3. 11-20%' WHEN discount<=0.30 THEN '4. 21-30%'
            WHEN discount<=0.50 THEN '5. 31-50%' ELSE '6. >50%' END AS discount_band,
       COUNT(*) AS lines, ROUND(AVG(profit),2) AS avg_profit_per_line
FROM sales_clean GROUP BY discount_band ORDER BY discount_band;
```
*Result:* average profit per line is $66.90 with no discount, $96.06 at 1–10%, $24.74 at 11–20%, then −$45.68, −$156.28 and −$89.44 above 20%.
```sql
-- Q13: top customers (JOIN across three tables)
SELECT c.customer_name, ROUND(SUM(l.sales),2) AS sales, ROUND(SUM(l.profit),2) AS profit
FROM order_lines l JOIN orders o ON o.order_id=l.order_id JOIN dim_customer c ON c.customer_id=o.customer_id
GROUP BY c.customer_id, c.customer_name ORDER BY sales DESC LIMIT 10;
```
**Answers to the required questions:** total revenue {d0(F['sales'])}; profit {d0(F['profit'])}; highest-revenue category Technology ($836,154); highest-profit category Technology ($145,455); most profitable region West; largest segment Consumer; loss-making products: {F['neg_products']}; lowest-profit discount levels: above 20%; top customer Sean Miller.

## 4.5 Validation against Python
`sql/run_queries.py` runs every query and compares 54 values with pandas (totals, KPIs, category/region/segment sales and profit, discount bands, months, years, top customers, loss-making states/products/customers). Result: **{F['sql_checks'].strip('*')}** One check initially failed (302 vs 301 loss-making products): a product summing to −3.6×10⁻¹⁵ was counted as a loss in SQL. Fix: round to cents in both tools. Lesson: always validate across tools and treat floating-point noise.

# Chapter 5 — Power BI

> **Status:** the dashboard file `Business_Performance_Analysis.pbix` is part of the project (16 report pages, two model tables: `sales data` and `Date_Table`). This chapter explains the concepts, the prepared star-schema assets and the measures.

## 5.1 Concepts
**Business intelligence** turns data into monitored indicators for decisions. **Power BI** has three layers: *Power Query* (load/transform), *the model* (tables + relationships + DAX), and *report pages* (visuals).

## 5.2 Power Query
`powerbi/power_query_steps.m` has one M query per table: promote headers, set types (Postal Code as text; en-US culture so decimals parse), safety row filter. Parameter `DataFolder` makes paths portable. Each step is recorded as an "applied step", so refresh is repeatable.

## 5.3 Data model (star schema)
Fact_Sales (one row per order line) with Dim_Date, Dim_Product, Dim_Customer, Dim_Geography, Dim_DiscountBand; all relationships one-to-many, single direction, from dimension to fact; Ship Date relationship inactive (used via `USERELATIONSHIP`). A date table is required for time intelligence and must be marked as such. *Why a star schema?* Filters flow cleanly from descriptive tables to numbers; calculations are fast and unambiguous.

## 5.4 Measures vs calculated columns
A **measure** is evaluated at query time in the current filter context (e.g. total sales for the selected region); it stores no data. A **calculated column** is computed row by row when data refresh happens and stored. Use measures for KPIs, columns for labels/sorting.

## 5.5 The DAX measures (file `powerbi/dax_measures.txt`)
| Measure | DAX | Business meaning |
|---|---|---|
| Total Sales | `SUM(Fact_Sales[Sales])` | Revenue after discount |
| Total Profit | `SUM(Fact_Sales[Profit])` | Money earned after costs |
| Total Orders | `DISTINCTCOUNT(Fact_Sales[Order ID])` | Unique orders (5,009, not 9,994 lines) |
| Total Quantity | `SUM(Fact_Sales[Quantity])` | Units sold |
| Profit Margin | `DIVIDE([Total Profit],[Total Sales],0)` | Profit per $1 of sales; DIVIDE avoids divide-by-zero |
| Average Order Value | `DIVIDE([Total Sales],[Total Orders],0)` | Typical basket size |
| Average Discount | `AVERAGE(Fact_Sales[Discount])` | Average discount rate |
| Average Shipping Days | `AVERAGE(Fact_Sales[Shipping Days])` | Delivery speed |
| Sales LY / YoY % | `CALCULATE([Total Sales], SAMEPERIODLASTYEAR(Dim_Date[Date]))` | Growth vs previous year |
| Loss-Making Products | `COUNTROWS(FILTER(VALUES(Dim_Product[Product ID]),[Total Profit] < -0.005))` | Products with total loss; threshold ignores rounding noise |
| Sales Share % | `DIVIDE([Total Sales], CALCULATE([Total Sales], ALLSELECTED()))` | Contribution to selected total |

Key DAX ideas: **filter context** (slicers/rows/columns restrict what a measure sees), **CALCULATE** (changes the filter context), **ALLSELECTED** (ignore the visual's grouping but keep the user's slicers).

## 5.6 Dashboard design and interactivity
The delivered dashboard has four sections of four report pages each (16 pages, 1920×1080): Executive Overview, Sales and Product Performance, Customer and Regional Analysis, Profitability and Business Insights. Every page has Date, Region, Category and Segment slicers and a page navigator; visuals cross-filter by default. The delivered model uses one flat table (`sales data`, the cleaned file) plus `Date_Table`; the star-schema CSVs in `data/processed/powerbi/` are the optional, more scalable design. Page-by-page contents: Appendix B of the final report.

## 5.7 KPI validation plan
`powerbi/validation_targets.csv` lists expected values (Python-calculated) for 17 slicer selections, e.g. no filter → Sales 2,297,200.86; Orders 5,009; Margin 12.47%. Compare each card with this table; cards must match to the cent. Check also that **Total Quantity** and **Average Order Value** exist as measures (required by the guidelines, not displayed on any visual).

# Chapter 6 — Dashboard interpretation

## 6.1 Page 1 — Executive Overview
*Objective:* immediate view of business health. *KPIs:* Sales {d0(F['sales'])}, Profit {d0(F['profit'])}, Margin {p1(F['margin'])}, Orders {F['orders']:,}, Quantity {F['qty']:,}. *Visuals:* monthly sales/profit line, sales by category and region. *Questions:* are we growing? Is it profitable? Where? *Insight:* growth after 2015, Q4 seasonality, thin margin. *Use:* weekly review; spot a margin drop quickly.

## 6.2 Page 2 — Sales and Product Performance
*Objective:* which products make/lose money. *Visuals:* sub-category profit (red negatives), top/bottom 10 products, loss-making product card ({F['neg_products']}). *Insight:* Tables, Bookcases, Supplies lose money; copiers and paper-type products have the highest margins. *Use:* range reviews, delisting/repricing.

## 6.3 Page 3 — Customer and Regional Analysis
*Objective:* who buys and where profitably. *Visuals:* segment comparison, region bars, state map coloured by margin, top-10 customers. *Insight:* Consumer is half of sales; Central margin {p1(reg.Margin['Central'])}; 10 loss-making states; top customer is unprofitable. *Use:* account reviews, regional targets.

## 6.4 Page 4 — Profitability and Business Insights
*Objective:* explain weak profitability. *Visuals:* profit/margin by discount band, region × category margin matrix, shipping by ship mode, loss KPIs, insight text. *Insight:* all discount bands above 20% lose money; shipping speed isn't linked to margin. *Use:* discount policy decisions.

Note: the files in `reports/dashboard_screenshots/` named `_PREVIEW` are Python-drawn layout previews, not screenshots of the delivered `.pbix`; add real exports there.

# Chapter 7 — Business analysis and recommendations

For each finding: **evidence** (from the data) is separate from **possible explanation** (hypothesis).

| # | Finding | Evidence | Possible explanation | Recommendation |
|---|---|---|---|---|
| 1 | Deep discounts destroy profit | >20% lines: {F['hi_lines']:,} lines, {p1(F['hi_sales_pct'])} of sales, profit {d0(F['hi_profit'])}; other lines {d0(F['other_profit'])} | Below-cost pricing, clearance, no approval rules | Cap discounts at 20%, approval + margin-floor check |
| 2 | Furniture earns almost nothing | Margin {p1(cat.Margin['Furniture'])}; Tables {d0(sub.Profit['Tables'])}; Bookcases {d0(sub.Profit['Bookcases'])} | Discounting, logistics/product cost (not in data) | Reprice, cut discounts, review suppliers |
| 3 | Central/states lose money | Central margin {p1(reg.Margin['Central'])}; {F['loss_states']} loss-making states | Discount practices, product mix | West-style discipline, state targets |
| 4 | Loss-making products/customers | {F['neg_products']} products, {F['neg_customers']} customers negative | Deep discounts on large orders | Profit-based reporting, renegotiate, delist |
| 5 | Seasonality | Sep+Nov+Dec = {p1(F['sep_nov_dec'])} of sales | Year-end buying | Plan inventory/staffing; use forecast cautiously |
| 6 | Opportunities | Copiers 37.2% margin, Home Office best segment margin, low-discount states >23% | Low discounting/favourable mix | Target these; use as benchmarks |

**Weaknesses:** discount governance, Furniture pricing, Central region. **Opportunities:** high-margin Technology/Paper/Accessories, Home Office, benchmark states. **Shipping:** no profit link found; shipping cost not recorded.

*Illustrative arithmetic only:* if the >20% lines had merely broken even, profit would be {d0(-F['hi_profit'])} higher ({p1(-F['hi_profit']/F['profit']*100)}), before any loss of volume.

# Chapter 8 — Concepts for revision (with Superstore examples)

| Concept | Explanation | Example |
|---|---|---|
| Data cleaning | Fixing format/consistency problems without destroying valid data | Padding postal codes; keeping the possible duplicate flagged |
| EDA | Looking at the data to find patterns before modelling | Discount bands showed losses above 20% |
| Mean / median / SD | Average / middle value / spread | Mean sales $229.86 vs median $54.49 — skew |
| Correlation | Strength of linear association (−1…1) | Discount vs margin {F['corr'].loc['Discount','Profit Margin']:.2f}; not proof of cause |
| Outlier | Value far from the rest | $22,638 sale; kept because real |
| Profit margin | Profit ÷ Sales | {p1(F['margin'])} overall |
| Average order value | Sales ÷ distinct orders | ${F['aov']:.2f} |
| Distinct orders | Unique order IDs | 5,009 orders vs 9,994 lines |
| Aggregation | Summarising many rows | Sales by region |
| Data model | Tables + relationships | Fact + dimensions |
| KPI | Key indicator tied to a goal | Margin, AOV, loss-line % |
| DAX measure | Formula recalculated under filters | `DIVIDE([Total Profit],[Total Sales],0)` |
| SQL aggregation | `GROUP BY` with `SUM/COUNT` | Q05 region profit |
| Interactivity | Slicers and cross-filtering | Choose Region = Central → every visual updates |
| Forecasting | Predicting future values; judged on held-out data vs baselines | MAPE 17.3% vs 24.5% seasonal naïve |
| Skewness | Asymmetry of distribution | Skew 12.97 for Sales |
| p-value | Probability of such a difference by chance | p < 0.001 for discount effect |
| Correlation vs causation | Association doesn't prove cause | Discounts and losses may both reflect low-margin items |

# Chapter 9 — Project defence and interview preparation

## 9.1 Two-minute presentation
"I analysed four years of retail sales — about $2.3 million across 5,009 orders — using Excel, Python, SQL and an interactive Power BI dashboard. I first inspected and cleaned the data without deleting records, then explored sales, profit, discounts, regions and customers. The business is growing, but its margin is only {p1(F['margin'])}. The biggest finding is that discounts above 20% lose about $135 thousand in total, while the rest of the business earns $422 thousand. Furniture earns only {p1(cat.Margin['Furniture'])} margin, and the Central region has the weakest margin and the heaviest discounting. I validated the numbers between Excel, Python and SQL — 54 automated checks passed — and recommended discount approval rules, Furniture repricing and regional benchmarking. I'm open about the limits: it's a public sample dataset with no cost data, so the findings are associations, not proven causes."

## 9.2 Five-minute presentation (outline)
1. *Context (30 s):* public sample dataset; management questions. 2. *Method (60 s):* tool roles and workflow; cleaning decisions; validation. 3. *Findings (2 min):* KPIs; seasonality/growth; categories; discounts; regions/states; customers. 4. *Recommendations (60 s):* discount rules, Furniture, Central, profit-based reporting, Q4 planning. 5. *Limits and next steps (30 s):* no cost data, association not causation, build/validate Power BI, add cost data.

## 9.3 Skills demonstrated
*Technical:* Excel formulas/pivots; pandas cleaning and EDA; statistics (correlation, t-test, Kruskal–Wallis); forecasting with baselines; SQL (joins, CASE, subqueries, CTE); star-schema modelling; DAX design; cross-tool validation. *Business:* KPI definition, profitability diagnosis, discount policy, regional/segment/customer analysis, evidence-based recommendations, honest limitations.

## 9.4 Interview questions and model answers
""")
QA = [
 ("Why this dataset, and is it real?", "Sample Superstore is a public teaching dataset, so it isn't confidential or necessarily real. It's suitable because it has the structure of real retail data: dates, products, customers, regions, discounts and profit."),
 ("What was your overall objective?", "To act as a data analyst for a retailer: measure performance, find weaknesses and opportunities and recommend actions, using Excel for inspection, Python for analysis, SQL for querying and Power BI for monitoring."),
 ("Why did you use four tools — isn't that redundant?", "Each has a distinct role. Excel for a first look and quick formulas; Python for cleaning, statistics and forecasting; SQL for structured queries and as an independent check; Power BI for management dashboards. Repeating a calculation was done only on purpose, to validate."),
 ("What data-quality problems did you find?", "No missing values, but dates stored as text, postal codes that lost leading zeros (438 rows, and Vermont's kept theirs), 32 product IDs with several names and one possible duplicate line. I fixed formats, standardised names with an audit column and flagged — not deleted — the duplicate."),
 ("Why didn't you delete the duplicate?", "Two identical lines in one order could be a legitimate repeat purchase. I can't prove otherwise, it's worth $281 (0.01% of sales), so I flagged it and documented the decision."),
 ("What does 'distinct orders' mean and why does it matter?", "One order contains several lines. Counting rows gives 9,994; counting distinct Order IDs gives 5,009. Using rows would overstate orders and understate average order value."),
 ("How did you define profit margin?", "Total profit divided by total sales, calculated on group totals. Averaging row margins would give small orders the same weight as large ones. I guard against zero sales."),
 ("What is your most important finding?", f"Discounts above 20% lose money: {F['hi_lines']:,} lines, {p1(F['hi_sales_pct'])} of sales, profit {d0(F['hi_profit'])}, while the remaining lines earn {d0(F['other_profit'])}. Margin falls from {p1(band.Margin['No discount'])} with no discount to {p1(band.Margin['>50%'])} above 50%."),
 ("Can you say discounts cause the losses?", "No. It's a strong association (correlation with margin −0.86, same sign in every region), but the data has no cost or price history. Low-margin or clearance items may simply be discounted more. I'd test it internally, e.g. with an A/B price test or cost data."),
 ("Which category and sub-categories are weak?", f"Furniture: {p1(cat.Margin['Furniture'])} margin versus about 17% for the others. Tables, Bookcases and Supplies lose money overall; Machines are near break-even."),
 ("Which region is weakest and why might that be?", f"Central, margin {p1(reg.Margin['Central'])}. Evidence: highest average discount ({p1(reg.Disc['Central']*100)}) and {p1(F['reg_hi_share']['Central'])} of sales on lines discounted above 20%, versus {p1(F['reg_hi_share']['West'])} in West. Product mix may also matter — Central Furniture is loss-making."),
 ("What did you learn about customers?", f"Customers are loyal ({p1(F['repeat_pct'])} are repeat buyers); the top 20% generate {p1(F['top20_share'])} of sales; {F['neg_customers']} customers are unprofitable, including the top customer by sales."),
 ("How did you validate your results?", f"Excel recalculated with zero errors and matched Python. I wrote 54 automated SQL-vs-Python checks; all pass. One failed initially (302 vs 301 loss-making products) because of floating-point noise at −3.6×10⁻¹⁵; rounding to cents fixed it."),
 ("Why did you use the median and rank-based tests?", "Sales and profit are extremely right-skewed (skew 13 and 7.6), so means are pulled by a few large orders, and t-tests assume near-normality. Medians and Kruskal–Wallis are more robust."),
 ("Explain your forecast and how you evaluated it.", f"Monthly sales; train 2014–2016, test 2017 chronologically. Regression on trend + month dummies. MAPE {fc['Regression (trend + month dummies)']['MAPE']:.1f}% against {fc['Seasonal naive']['MAPE']:.1f}% for the seasonal-naïve baseline and {fc['Naive']['MAPE']:.0f}% for naïve. It beats the baselines, but 12 test points and a ~17% error mean it's only a planning aid."),
 ("Why SQLite?", "It's a lightweight single-file database with standard SQL, no server needed, which makes the project portable and reproducible."),
 ("Explain one SQL query you wrote.", "Q09: CASE WHEN assigns each line to a discount band, GROUP BY aggregates, AVG(profit) gives average profit per line and COUNT(*) the number of lines. It shows profit per line turns negative above 20% discounts."),
 ("Measure versus calculated column in Power BI?", "A measure is calculated on the fly under the current filters and stores nothing; a calculated column is computed per row at refresh and stored. KPIs should be measures."),
 ("Why a star schema?", "A central fact table with dimensions gives clear one-to-many relationships, fast calculations and unambiguous filtering from slicers."),
 ("Describe your Power BI dashboard.", "It has four sections of four pages: Executive Overview (KPI cards, monthly and yearly trends), Sales and Product Performance (category and sub-category sales, loss-making products), Customer and Regional Analysis (segments, regions, top customers) and Profitability and Business Insights (margin by category, discount vs profit scatter, shipping by ship mode, a sub-category insights table). Date, region, category and segment slicers and page navigation are on every page. The model is a cleaned sales table plus a date table, with measures such as Total Sales, Total Profit, Total Orders (distinct), Profit Margin (DIVIDE), Average Discount and Average Shipping Days, and I validated the cards against my Python and SQL results."),
 ("What would you recommend to management?", "Cap discounts at 20% with approval and margin-floor checks; reprice Furniture (Tables, Bookcases); bring Central and the loss-making states up to West-level discipline; report by profit not just sales; plan inventory around the Q4 peak."),
 ("What are the limitations?", "Public sample data, four years, no costs, prices, returns or shipping cost, unknown discount reasons, association not causation, small test set for the forecast."),
 ("What was the biggest challenge?", "Ensuring consistency across tools: criteria such as '>50%' being read as an operator in Excel, and floating-point noise in SQL vs Python. Cross-validation caught both."),
 ("What would you do next with real company data?", "Add product costs and promotion records to test whether discounting causes losses, assess shipping cost, build the live dashboard with refresh, and track margin by discount band monthly."),
 ("How does this project show business knowledge?", "It frames the data as management questions, defines KPIs, separates evidence from hypothesis and turns findings into specific actions with a realistic estimate of impact."),
]
for i, (q, ans) in enumerate(QA, 1): a(f"**Q{i}. {q}**\n\n*Answer:* {ans}\n\n")
a("""## 9.5 Final reminder for the interview
State precisely what you did: Excel workbook with formulas and pivots; executed Python notebook; SQLite database with validated queries; Power BI model, DAX measures and a 16-page interactive dashboard. Be ready to say which numbers you validated in Power BI and how. Honesty about limits (public sample data, no cost data, association not causation) is a strength.
""")
open('documentation/_notes.md', 'w').write(''.join(N)); print(len(''.join(N).split()), 'words')
