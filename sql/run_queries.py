"""Executes every query in business_queries.sql, writes sql/query_results.md, validates vs pandas (sql/validation_report.md)."""
import sqlite3, re, pandas as pd, numpy as np
con = sqlite3.connect('sql/superstore.db')
txt = open('sql/business_queries.sql').read()
blocks = re.split(r'\n(?=-- Q\d\d)', txt)[1:]
out = ['# SQL query results (executed on sql/superstore.db)\n']
res = {}
for b in blocks:
    head = b.splitlines()[0]; qid = head[3:6]
    sql = '\n'.join(l for l in b.splitlines() if not l.strip().startswith('--')).strip()
    df = pd.read_sql_query(sql, con); res[qid] = df
    out.append(f'\n## {head[3:]}\n\n```sql\n{b.strip()}\n```\n\n**Result** ({len(df)} rows)\n\n{df.to_markdown(index=False, floatfmt=',.2f')}\n')
open('sql/query_results.md', 'w').write('\n'.join(out))
py = pd.read_csv('data/processed/cleaned_sales.csv')
checks = []
def chk(name, sql_v, py_v, tol=0.01): checks.append((name, sql_v, py_v, 'PASS' if abs(float(sql_v) - float(py_v)) <= tol else 'FAIL'))
q = res['Q02'].iloc[0]
chk('Total sales', q.total_sales, py.Sales.sum()); chk('Total profit', q.total_profit, py.Profit.sum())
chk('Profit margin %', q.profit_margin_pct, py.Profit.sum()/py.Sales.sum()*100)
chk('Distinct orders', q.distinct_orders, py['Order ID'].nunique(), 0); chk('Distinct customers', q.distinct_customers, py['Customer ID'].nunique(), 0)
chk('Total quantity', q.total_quantity, py.Quantity.sum(), 0); chk('Average order value', q.avg_order_value, py.Sales.sum()/py['Order ID'].nunique())
chk('Average shipping days', q.avg_shipping_days, py['Shipping Days'].mean()); chk('Average discount', q.avg_discount, py.Discount.mean(), 0.0001)
for _, r in res['Q03'].iterrows():
    chk(f'Category sales: {r.category}', r.sales, py[py.Category==r.category].Sales.sum()); chk(f'Category profit: {r.category}', r.profit, py[py.Category==r.category].Profit.sum())
for _, r in res['Q05'].iterrows():
    chk(f'Region profit: {r.region}', r.profit, py[py.Region==r.region].Profit.sum()); chk(f'Region sales: {r.region}', r.sales, py[py.Region==r.region].Sales.sum())
for _, r in res['Q06'].iterrows():
    chk(f'Segment sales: {r.segment}', r.sales, py[py.Segment==r.segment].Sales.sum()); chk(f'Segment orders: {r.segment}', r.orders, py[py.Segment==r.segment]['Order ID'].nunique(), 0)
q8 = res['Q08'].iloc[0]; pp = py.groupby('Product ID').Profit.sum()
chk('Loss-making products (by Product ID)', q8.loss_making_products, (pp.round(2)<0).sum(), 0); chk('Profit lost on loss-making products', q8.profit_lost_on_them, pp[pp.round(2)<0].sum())
for _, r in res['Q09'].iterrows():
    band = {'1. No discount':'No discount','2. 1-10%':'1-10%','3. 11-20%':'11-20%','4. 21-30%':'21-30%','5. 31-50%':'31-50%','6. >50%':'>50%'}[r.discount_band]
    chk(f'Discount band profit: {band}', r.total_profit, py[py['Discount Band']==band].Profit.sum()); chk(f'Discount band lines: {band}', r.order_lines, (py['Discount Band']==band).sum(), 0)
for _, r_ in res['Q23'].iterrows():
    g = r_.discount_group[2:]; g = {'No Discount': 'No Discount', 'Low (>0-20%)': 'Low (>0-20%)', 'Medium (>20-40%)': 'Medium (>20-40%)', 'High (>40%)': 'High (>40%)'}[g]
    chk(f'Discount group profit: {g}', r_.profit, py[py['Discount Group'] == g].Profit.sum()); chk(f'Discount group lines: {g}', r_.lines, (py['Discount Group'] == g).sum(), 0)
chk('Months in monthly query', len(res['Q11']), py['Year-Month'].nunique(), 0)
chk('Sum of monthly sales', res['Q11'].sales.sum(), py.Sales.sum(), 0.05)
for _, r in res['Q12'].iterrows(): chk(f'Year {int(r.order_year)} sales', r.sales, py[py['Order Year']==r.order_year].Sales.sum())
tc = py.groupby('Customer ID').Sales.sum().sort_values(ascending=False)
chk('Top customer sales', res['Q13'].iloc[0].sales, tc.iloc[0]); chk('10th customer sales', res['Q13'].iloc[9].sales, tc.iloc[9])
chk('Loss-making states', len(res['Q14']), (py.groupby('State').Profit.sum()<0).sum(), 0)
chk('Customers with loss', res['Q19'].iloc[0,0], (py.groupby('Customer ID').Profit.sum()<0).sum(), 0)
chk('Order_lines vs flat sales diff', res['Q22'].iloc[0].sales_difference, 0, 0.0001)
v = pd.DataFrame(checks, columns=['Check', 'SQL', 'Python', 'Result'])
open('sql/validation_report.md', 'w').write('# SQL vs Python validation\n\n' + v.to_markdown(index=False, floatfmt=',.2f') + f'\n\n**{(v.Result=="PASS").sum()} of {len(v)} checks passed.**\n')
print(f'{(v.Result=="PASS").sum()}/{len(v)} PASS'); print(v[v.Result=='FAIL'])
