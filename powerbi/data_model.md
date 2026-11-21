# Power BI data model (star schema)

**Status:** specification + ready-to-load source files. The `.pbix` itself must be built in Power BI Desktop (see `README_POWERBI.md`).

## Why a star schema?
One central **fact table** (numbers that are summed: sales, profit, quantity) surrounded by **dimension tables** (descriptions used to slice: date, product, customer, geography). Slicers filter a dimension, the filter flows down to the fact table, and every measure recalculates. It is the standard BI design because it is fast, unambiguous and easy to explain.

```
                  Dim_Date (1)                Dim_Product (1)
                       │                           │
                       ▼ Date → Order Date         ▼ Product ID
Dim_Customer (1) ──► Fact_Sales (*) ◄── Dim_Geography (1)
   Customer ID            ▲   Geography ID
                          │ Discount Band
                   Dim_DiscountBand (1)
```

## Tables
| Table | Grain (one row = …) | Rows | Key | Source file |
|---|---|---|---|---|
| **Fact_Sales** | one order line | 9,994 | Row ID | Fact_Sales.csv |
| Dim_Date | one calendar day, 2014-01-01 … 2017-12-31 | 1,461 | Date | Dim_Date.csv |
| Dim_Product | one Product ID | 1,862 | Product ID | Dim_Product.csv |
| Dim_Customer | one customer | 793 | Customer ID | Dim_Customer.csv |
| Dim_Geography | one region/state/city/postal-code combination | 632 | Geography ID | Dim_Geography.csv |
| Dim_DiscountBand | one discount band (provides the correct sort order) | 6 | Discount Band | Dim_DiscountBand.csv |
| _Measures | holds DAX measures only | — | — | blank table |

## Relationships (Model view → drag the key column from the dimension to the fact)
| From (one side) | To (many side) | Cardinality | Filter direction | Active |
|---|---|---|---|---|
| Dim_Date[Date] | Fact_Sales[Order Date] | One-to-many | Single | **Yes** |
| Dim_Date[Date] | Fact_Sales[Ship Date] | One-to-many | Single | No (used with USERELATIONSHIP) |
| Dim_Product[Product ID] | Fact_Sales[Product ID] | One-to-many | Single | Yes |
| Dim_Customer[Customer ID] | Fact_Sales[Customer ID] | One-to-many | Single | Yes |
| Dim_Geography[Geography ID] | Fact_Sales[Geography ID] | One-to-many | Single | Yes |
| Dim_DiscountBand[Discount Band] | Fact_Sales[Discount Band] | One-to-many | Single | Yes |

## Settings
* Mark **Dim_Date** as a date table (Table tools → Mark as date table → column *Date*). Required for time-intelligence DAX.
* Sort **Dim_Date[Month Name]** by *Month Number*; sort **Dim_DiscountBand[Discount Band]** by *Band Order*.
* Hide key/ID columns in the fact table (Report view: hidden) so users only see measures.
* Set summarisation of Sales, Profit, Quantity, Discount to **Don't summarize** (use measures instead).
* Formats: Total Sales/Profit/AOV `$#,##0`; Profit Margin and Average Discount `0.0%`; Average Shipping Days `0.00`.

## Model checks (do these before building pages)
1. Model view shows only one-to-many, single-direction arrows from dimensions to the fact table (no many-to-many, no bi-directional).
2. A card with `Total Sales` shows **$2,297,200.86** (format with 2 decimals once to compare).
3. A table of `Dim_Product[Category]` × `Total Sales` sums to the same total; the categories match `validation_targets.csv`.
4. `Total Orders` = **5,009** (not 9,994).
