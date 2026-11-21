"""Creates the star-schema CSV files for Power BI from data/processed/cleaned_sales.csv (run from project root)."""
import pandas as pd, numpy as np
df = pd.read_csv('data/processed/cleaned_sales.csv', dtype={'Postal Code': str}, parse_dates=['Order Date', 'Ship Date'])
out = 'data/processed/powerbi/'
geo = df[['Country', 'Region', 'State', 'City', 'Postal Code']].drop_duplicates().sort_values(['Region', 'State', 'City', 'Postal Code']).reset_index(drop=True)
geo.insert(0, 'Geography ID', np.arange(1, len(geo) + 1)); geo.to_csv(out + 'Dim_Geography.csv', index=False)
cust = df[['Customer ID', 'Customer Name', 'Segment']].drop_duplicates().sort_values('Customer ID'); cust.to_csv(out + 'Dim_Customer.csv', index=False)
prod = df[['Product ID', 'Product Name', 'Category', 'Sub-Category']].drop_duplicates('Product ID').sort_values('Product ID'); prod.to_csv(out + 'Dim_Product.csv', index=False)
dates = pd.DataFrame({'Date': pd.date_range('2014-01-01', '2017-12-31')})
dates['Year'] = dates.Date.dt.year; dates['Quarter'] = 'Q' + dates.Date.dt.quarter.astype(str); dates['Month Number'] = dates.Date.dt.month
dates['Month Name'] = dates.Date.dt.strftime('%b'); dates['Year-Month'] = dates.Date.dt.strftime('%Y-%m'); dates['Month Start'] = dates.Date.dt.to_period('M').dt.to_timestamp()
dates['Weekday'] = dates.Date.dt.strftime('%a'); dates['Weekday Number'] = dates.Date.dt.dayofweek + 1
dates.to_csv(out + 'Dim_Date.csv', index=False, date_format='%Y-%m-%d')
bands = pd.DataFrame({'Discount Band': ['No discount', '1-10%', '11-20%', '21-30%', '31-50%', '>50%'], 'Band Order': range(1, 7)}); bands.to_csv(out + 'Dim_DiscountBand.csv', index=False)
fact = df.merge(geo, on=['Country', 'Region', 'State', 'City', 'Postal Code'])
fact = fact[['Row ID', 'Order ID', 'Order Date', 'Ship Date', 'Ship Mode', 'Customer ID', 'Product ID', 'Geography ID', 'Sales', 'Quantity', 'Discount', 'Profit',
             'Shipping Days', 'Discount Band', 'Is Loss', 'Possible Duplicate']].sort_values('Row ID')
assert len(fact) == len(df) and abs(fact.Sales.sum() - df.Sales.sum()) < 1e-6
fact.to_csv(out + 'Fact_Sales.csv', index=False, date_format='%Y-%m-%d')
print({n: len(x) for n, x in dict(Fact_Sales=fact, Dim_Customer=cust, Dim_Product=prod, Dim_Geography=geo, Dim_Date=dates, Dim_DiscountBand=bands).items()})
# ---- validation targets (what Power BI cards must show under each slicer selection) ----
def kp(d):
    s, p = d.Sales.sum(), d.Profit.sum(); o = d['Order ID'].nunique()
    return dict(Total_Sales=round(s, 2), Total_Profit=round(p, 2), Profit_Margin_pct=round(p / s * 100, 2) if s else 0, Total_Orders=o, Total_Quantity=int(d.Quantity.sum()),
                Average_Order_Value=round(s / o, 2) if o else 0, Average_Discount_pct=round(d.Discount.mean() * 100, 2), Average_Shipping_Days=round(d['Shipping Days'].mean(), 2))
rows = [dict(Slicer_Selection='All data (no filter)', **kp(df))]
for y in [2014, 2015, 2016, 2017]: rows.append(dict(Slicer_Selection=f'Year = {y}', **kp(df[df['Order Year'] == y])))
for r in ['West', 'East', 'Central', 'South']: rows.append(dict(Slicer_Selection=f'Region = {r}', **kp(df[df.Region == r])))
for c in ['Furniture', 'Office Supplies', 'Technology']: rows.append(dict(Slicer_Selection=f'Category = {c}', **kp(df[df.Category == c])))
for s in ['Consumer', 'Corporate', 'Home Office']: rows.append(dict(Slicer_Selection=f'Segment = {s}', **kp(df[df.Segment == s])))
rows.append(dict(Slicer_Selection='Year = 2017 AND Region = Central AND Category = Furniture', **kp(df[(df['Order Year'] == 2017) & (df.Region == 'Central') & (df.Category == 'Furniture')])))
rows.append(dict(Slicer_Selection='Region = West AND Segment = Corporate', **kp(df[(df.Region == 'West') & (df.Segment == 'Corporate')])))
pd.DataFrame(rows).to_csv('powerbi/validation_targets.csv', index=False); print(pd.DataFrame(rows).iloc[[0, 1, 5, 12]].T)
