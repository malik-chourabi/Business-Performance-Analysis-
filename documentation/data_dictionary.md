# Data dictionary — Sample Superstore

**Source:** "Sample - Superstore" retail dataset (Tableau sample data, widely redistributed on public sites). **It is a public sample dataset for learning, not confidential data from a real company.** Original file: `data/raw/Sample_Superstore.csv` (9,994 rows × 21 columns, orders placed 2014-01-03 to 2017-12-30, United States). Currency is not stated; USD is assumed.

## 1. Original variables (21)
| # | Variable | Type | Role | Meaning | Notes |
|---|---|---|---|---|---|
| 1 | Row ID | integer | Identifier | Sequential line number, 1…9,994 | Unique |
| 2 | Order ID | text | Identifier | Order reference (5,009 distinct) | One order has 1–14 lines → count with DISTINCT |
| 3 | Order Date | date (text `m/d/yyyy` in CSV) | Date | Date the order was placed | Converted to date |
| 4 | Ship Date | date (text) | Date | Date the order shipped | Never before Order Date |
| 5 | Ship Mode | categorical (4) | Dimension | Standard Class, Second Class, First Class, Same Day | |
| 6 | Customer ID | text | Identifier | 793 customers | One name and one segment per ID |
| 7 | Customer Name | text | Identifier | Full name | |
| 8 | Segment | categorical (3) | Dimension | Consumer, Corporate, Home Office | |
| 9 | Country | categorical (1) | Dimension | Always "United States" | No analytical value |
| 10 | City | categorical (531) | Dimension | Delivery city | |
| 11 | State | categorical (49) | Dimension | Delivery state (incl. District of Columbia) | |
| 12 | Postal Code | text (stored as number in CSV) | Geographic code | ZIP code | Leading zero lost for 438 rows (CT, MA, ME, NH, NJ, RI); Vermont keeps it → inconsistent |
| 13 | Region | categorical (4) | Dimension | West, East, Central, South | Each state belongs to one region |
| 14 | Product ID | text | Identifier | 1,862 products | 32 IDs carry more than one name |
| 15 | Category | categorical (3) | Dimension | Furniture, Office Supplies, Technology | |
| 16 | Sub-Category | categorical (17) | Dimension | e.g. Chairs, Binders, Phones | One per Product ID |
| 17 | Product Name | text | Identifier | Product description | |
| 18 | Sales | numeric (USD) | Measure | Revenue of the line **after** discount | > 0 for all rows |
| 19 | Quantity | integer | Measure | Units sold (1–14) | |
| 20 | Discount | numeric 0–0.8 | Measure | Discount rate applied | 12 distinct levels |
| 21 | Profit | numeric (USD) | Measure | Profit of the line; negative = loss | 1,871 lines negative |

## 2. Variables added during cleaning/feature engineering (12)
| Variable | Definition | Purpose |
|---|---|---|
| Product Name Original | Product Name as found in the file | Audit trail (129 rows standardised) |
| Product Name | Most frequent name for the Product ID | One name per product |
| Possible Duplicate | 1 for a line identical to an earlier one except Row ID (1 row) | Flag, not deletion |
| Order Year / Order Quarter / Order Month | from Order Date | Trends, seasonality |
| Order Month Name | `Jan`…`Dec` | Labels |
| Year-Month | `YYYY-MM` | Monthly series |
| Shipping Days | Ship Date − Order Date (0–7) | Delivery performance |
| Profit Margin | Profit ÷ Sales (blank if Sales = 0; never occurs) | Profitability independent of size |
| Cost | Sales − Profit | Implied cost base |
| Is Loss | 1 if Profit < 0 | Loss tracking |
| Discount Band | No discount, 1-10%, 11-20%, 21-30%, 31-50%, >50% | Discount comparison |

`data/processed/cleaned_sales.csv` = 9,994 rows × 33 columns (21 original + 12 added).

## 3. KPI definitions (identical in Excel, Python, SQL and DAX)
| KPI | Definition |
|---|---|
| Total Sales / Profit / Quantity | Sum of the column |
| Total Orders | **Distinct** Order IDs (5,009) — not rows |
| Profit Margin | Total Profit ÷ Total Sales (ratio of totals) |
| Average Order Value | Total Sales ÷ Total Orders |
| Average Discount | Simple average of Discount over order lines |
| Average Shipping Days | Average of Shipping Days over order lines |
| Loss-making product | Product ID whose total profit, rounded to cents, is below 0 |

## 4. Limitations
1. Public sample data, not a real company; patterns may be synthetic.
2. Only four years (2014–2017), no later years; no current-day relevance.
3. No cost, price list, returns, inventory, marketing spend or shipping-cost columns → cannot separate "discounted because low-margin" from "low-margin because discounted"; cannot assess shipping profitability.
4. Discounts are recorded per line, with no reason (promotion, clearance, negotiation).
5. Currency and units are not documented.
6. Customer identity is one ID per person; no demographics → limited customer analytics.
7. One possible duplicate line cannot be verified; it is immaterial (0.01 % of sales).
8. Findings show **association**, not causation.
