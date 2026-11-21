"""Cleaning pipeline for Sample Superstore. Run from project root."""
import pandas as pd, numpy as np

raw = pd.read_csv('data/raw/Sample_Superstore.csv', dtype={'Postal Code': str})
df = raw.copy()

# 1. Dates: text m/d/yyyy -> datetime
df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%Y')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], format='%m/%d/%Y')

# 2. Postal codes: restore leading zeros lost in numeric storage (New England states)
df['Postal Code'] = df['Postal Code'].str.zfill(5)

# 3. Canonical product name per Product ID (32 IDs have >1 name): most frequent, ties -> first seen
canon = (df.groupby('Product ID')['Product Name']
           .agg(lambda s: s.value_counts().index[0]))
df['Product Name Original'] = df['Product Name']
df['Product Name'] = df['Product ID'].map(canon)

# 4. Duplicate flag (identical in every column except Row ID) - kept, flagged
dup_mask = df.drop(columns=['Row ID', 'Product Name Original']).duplicated(keep='first')
df['Possible Duplicate'] = dup_mask.astype(int)

# 5. Feature engineering
df['Order Year'] = df['Order Date'].dt.year
df['Order Quarter'] = df['Order Date'].dt.quarter
df['Order Month'] = df['Order Date'].dt.month
df['Order Month Name'] = df['Order Date'].dt.strftime('%b')
df['Year-Month'] = df['Order Date'].dt.to_period('M').astype(str)
df['Shipping Days'] = (df['Ship Date'] - df['Order Date']).dt.days
df['Profit Margin'] = np.where(df['Sales'] > 0, df['Profit'] / df['Sales'], np.nan)
df['Cost'] = df['Sales'] - df['Profit']
df['Is Loss'] = (df['Profit'] < 0).astype(int)
bins = [-0.001, 0, 0.10, 0.20, 0.30, 0.50, 1.0]
labels = ['No discount', '1-10%', '11-20%', '21-30%', '31-50%', '>50%']
df['Discount Band'] = pd.cut(df['Discount'], bins=bins, labels=labels).astype(str)

df.to_csv('data/processed/cleaned_sales.csv', index=False)
print(df.shape, 'dups flagged:', df['Possible Duplicate'].sum())
print('Sales', round(df.Sales.sum(), 2), 'Profit', round(df.Profit.sum(), 2),
      'Orders', df['Order ID'].nunique())
print(df['Discount Band'].value_counts())
print(df['Product Name'].nunique(), 'canonical product names')
