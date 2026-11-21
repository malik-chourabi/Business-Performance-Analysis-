"""Single source of truth for every number quoted in the report, notes and README (computed from the cleaned data)."""
import pandas as pd, numpy as np, sqlite3
from scipy import stats
from sklearn.linear_model import LinearRegression
d = pd.read_csv('data/processed/cleaned_sales.csv', parse_dates=['Order Date', 'Ship Date'])
F = {}
S, P, O = d.Sales.sum(), d.Profit.sum(), d['Order ID'].nunique()
F.update(sales=S, profit=P, margin=P / S * 100, orders=O, customers=d['Customer ID'].nunique(), qty=int(d.Quantity.sum()), aov=S / O, avg_disc=d.Discount.mean() * 100,
         ship=d['Shipping Days'].mean(), rows=len(d), products=d['Product ID'].nunique(), loss_lines=int(d['Is Loss'].sum()), loss_pct=d['Is Loss'].mean() * 100, loss_total=d.loc[d.Profit < 0, 'Profit'].sum(),
         median_line=d.Sales.median(), median_order=d.groupby('Order ID').Sales.sum().median(), states=d.State.nunique(), cities=d.City.nunique())
def grp(by):
    t = d.groupby(by).agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum'), Orders=('Order ID', 'nunique'), Qty=('Quantity', 'sum'), Disc=('Discount', 'mean'))
    t['Margin'] = t.Profit / t.Sales * 100; t['Share'] = t.Sales / S * 100; return t
F['yr'] = grp('Order Year'); F['cat'] = grp('Category'); F['sub'] = grp('Sub-Category'); F['reg'] = grp('Region'); F['seg'] = grp('Segment'); F['band'] = grp('Discount Band').reindex(['No discount', '1-10%', '11-20%', '21-30%', '31-50%', '>50%'])
F['ship_mode'] = d.groupby('Ship Mode').agg(days=('Shipping Days', 'mean'), lines=('Row ID', 'count'), Sales=('Sales', 'sum'), Profit=('Profit', 'sum')).assign(Margin=lambda x: x.Profit / x.Sales * 100)
F['state'] = grp('State'); F['city'] = grp('City')
pr = grp(['Product ID', 'Product Name']); F['prod'] = pr; F['neg_products'] = int((pr.Profit.round(2) < 0).sum()); F['neg_products_loss'] = pr[pr.Profit.round(2) < 0].Profit.sum()
cu = d.groupby(['Customer ID', 'Customer Name']).agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum'), Orders=('Order ID', 'nunique')).sort_values('Sales', ascending=False); F['cust'] = cu
F['top20_share'] = cu.Sales.head(int(len(cu) * .2)).sum() / cu.Sales.sum() * 100; F['neg_customers'] = int((cu.Profit.round(2) < 0).sum()); F['top20_n'] = int(len(cu) * .2)
oc = d.groupby('Customer ID')['Order ID'].nunique(); F['orders_per_cust'] = oc.mean(); F['repeat_pct'] = (oc > 1).mean() * 100
hi = d[d.Discount > .2]; F.update(hi_lines=len(hi), hi_lines_pct=len(hi) / len(d) * 100, hi_sales=hi.Sales.sum(), hi_sales_pct=hi.Sales.sum() / S * 100, hi_profit=hi.Profit.sum(), other_profit=d[d.Discount <= .2].Profit.sum())
rm = d.assign(hi=np.where(d.Discount > .2, d.Sales, 0)).groupby('Region').agg(h=('hi', 'sum'), s=('Sales', 'sum')); F['reg_hi_share'] = rm.h / rm.s * 100
F['mx'] = d.pivot_table(index='Region', columns='Category', values='Profit', aggfunc='sum')
F['mxm'] = d.pivot_table(index='Region', columns='Category', values='Profit', aggfunc='sum') / d.pivot_table(index='Region', columns='Category', values='Sales', aggfunc='sum') * 100
cm = d[['Sales', 'Quantity', 'Discount', 'Profit', 'Profit Margin', 'Shipping Days']].corr(); F['corr'] = cm
F['spearman_dp'] = d[['Discount', 'Profit']].corr(method='spearman').iloc[0, 1]
a, b = d.loc[d.Discount == 0, 'Profit'], d.loc[d.Discount > 0, 'Profit']; F['mean_nodisc'] = a.mean(); F['mean_disc'] = b.mean(); F['welch_t'], F['welch_p'] = stats.ttest_ind(a, b, equal_var=False)
F['kw'] = {c: stats.kruskal(*[g['Profit Margin'].values for _, g in d.groupby(c)]) for c in ['Category', 'Region', 'Segment']}
F['corr_reg'] = {r: g[['Discount', 'Profit Margin']].corr().iloc[0, 1] for r, g in d.groupby('Region')}
mo = d.groupby('Order Month')[['Sales', 'Profit']].sum(); F['sep_nov_dec'] = mo.loc[[9, 11, 12], 'Sales'].sum() / mo.Sales.sum() * 100; F['jan_feb'] = mo.loc[[1, 2], 'Sales'].sum() / mo.Sales.sum() * 100
ms = d.groupby(d['Order Date'].dt.to_period('M')).Sales.sum(); ms.index = ms.index.to_timestamp()
X = pd.DataFrame({'t': np.arange(len(ms))}, index=ms.index).join(pd.get_dummies(ms.index.month, prefix='m', drop_first=True).set_index(ms.index).astype(int))
tr, te = ms.index < '2017-01-01', ms.index >= '2017-01-01'; pred = pd.Series(LinearRegression().fit(X[tr], ms[tr]).predict(X[te]), index=ms.index[te]); sn = pd.Series(ms[tr].values[-12:], index=ms.index[te]); nv = pd.Series(ms[tr].values[-1], index=ms.index[te])
mt = lambda y, h: dict(MAE=np.mean(abs(y - h)), RMSE=np.sqrt(np.mean((y - h) ** 2)), MAPE=np.mean(abs((y - h) / y)) * 100)
F['fc'] = {'Regression (trend + month dummies)': mt(ms[te], pred), 'Seasonal naive': mt(ms[te], sn), 'Naive': mt(ms[te], nv)}
con = sqlite3.connect('sql/superstore.db'); v = open('sql/validation_report.md').read(); F['sql_checks'] = v.strip().splitlines()[-1]
F['binders_gt50_loss'] = d[(d['Sub-Category'] == 'Binders') & (d['Discount Band'] == '>50%')].Profit.sum()
F['tables_hi'] = d[(d['Sub-Category'] == 'Tables') & (d.Discount > .2)].Profit.sum(); F['tables_nodisc_margin'] = (lambda t: t.Profit.sum() / t.Sales.sum() * 100)(d[(d['Sub-Category'] == 'Tables') & (d.Discount == 0)])
F['furn_central_margin'] = F['mxm'].loc['Central', 'Furniture']; F['loss_states'] = int((F['state'].Profit < 0).sum()); F['loss_states_total'] = F['state'][F['state'].Profit < 0].Profit.sum()
F['dup_sales'] = d[d['Possible Duplicate'] == 1].Sales.sum()
if __name__ == '__main__':
    for k in ['sales', 'profit', 'margin', 'orders', 'aov', 'neg_products', 'neg_products_loss', 'top20_share', 'neg_customers', 'repeat_pct', 'hi_lines', 'hi_sales_pct', 'hi_profit', 'other_profit', 'sep_nov_dec', 'jan_feb', 'furn_central_margin', 'loss_states', 'loss_states_total', 'tables_hi', 'tables_nodisc_margin', 'median_order', 'dup_sales', 'welch_t']: print(k, F[k])
    print(F['fc']); print(F['reg_hi_share']); print(F['sql_checks']); print(F['kw'])
