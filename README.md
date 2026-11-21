# Business Performance Analysis, Sales Forecasting & Business Intelligence Dashboard

End-to-end analytics project on the **Sample Superstore** retail dataset (2014–2017): data inspection in **Excel**, cleaning/EDA/statistics/forecasting in **Python**, business queries in **SQL (SQLite)**, and a **Power BI** model + dashboard specification.

> **Dataset:** Sample Superstore is a **public sample dataset**, not confidential company data.
> **Final report:** `reports/Business_Performance_Project_Report.pdf` (14 pages: SQL queries, Python and R code, forecasting comparison, Power BI dashboard pages, recommendations).
> **Power BI:** `powerbi/Business_Performance_Analysis.pbix`; page images from the Power BI export are in `reports/dashboard_screenshots/`.

## Business problem
A retailer records many transactions but lacks a clear view of sales, profit, products, regions, customers, trends and the effect of discounts. Objective: measure performance, find weaknesses/opportunities and recommend actions.

## Dataset
9,994 order lines × 21 columns · 5,009 orders · 793 customers · 1,862 products · 49 states · 2014-01-03 → 2017-12-30. Details: `documentation/data_dictionary.md`.

## Tools and responsibilities
| Tool | Used for | File |
|---|---|---|
| Excel | inspection, formulas, 6 pivot tables | `excel/initial_data_inspection.xlsx` |
| Python | cleaning, EDA, statistics, forecast, charts | `python/business_analysis.ipynb` |
| SQLite | database + 22 business queries + validation | `sql/superstore.db`, `sql/business_queries.sql` |
| R | statistical tests, regression, forecasting comparison | `r/forecast_and_stats.R` |
| Power BI | Power Query, data model, DAX, 16-page interactive dashboard | `powerbi/Business_Performance_Analysis.pbix` |

## Folder structure
```
data/raw/Sample_Superstore.csv          original (never edited)
data/processed/cleaned_sales.csv        cleaned (9,994 rows x 33 cols)
data/processed/powerbi/*.csv            star schema for Power BI
excel/  python/  sql/  powerbi/  reports/  documentation/
```

## Main findings (validated in Python and SQL)
* Sales **$2,297,201**, profit **$286,397**, margin **12.5%**, 5,009 orders. Sales: 2015 −2.8%, 2016 +29.5%, 2017 +20.4%; Sep+Nov+Dec = 42.9% of sales.
* Discounts above 20%: 1,393 lines, profit **−$135,376**; all other lines +$421,773. Margin 29.5% (no discount) → -119.2% (>50%).
* Furniture margin 2.5% vs ~17% for the other categories; Tables, Bookcases, Supplies lose money.
* Central region margin 7.9% (West 14.9%); 10 loss-making states.
* 299 products and 155 customers have negative total profit.
* Shipping speed is unrelated to margin. Forecast (trend + seasonality) MAPE 17.3% vs 24.5% seasonal-naive on 2017.

## Recommendations
Cap discounts at 20% with approval and margin-floor checks · reprice Furniture (Tables, Bookcases) · bring Central and loss-making states to West-level discount discipline · report profit, not only sales, by product/customer · plan inventory around the Q4 peak. Full detail: `reports/Business_Performance_Project_Report.pdf`.

## Reproduce
```bash
pip install -r requirements.txt
python python/clean_data.py                 # or run python/business_analysis.ipynb
python sql/create_database.py && python sql/run_queries.py   # builds DB, runs queries, 54 validation checks
Rscript r/forecast_and_stats.R               # R statistics and forecast comparison (needs R + forecast package)
python powerbi/prepare_powerbi_data.py      # star-schema CSVs + validation targets
python excel/build_excel.py   # optional: rebuild workbook (pivots added with LibreOffice: excel/add_pivots.py)
```
Power BI: open `powerbi/Business_Performance_Analysis.pbix`; the star-schema CSVs and DAX reference (`powerbi/dax_measures.txt`) are in `powerbi/` and `data/processed/powerbi/`.

## Limitations
Public sample data; 4 years; no cost/price/return/shipping-cost data, so findings are associations, not causes; discount reasons unknown; one possible duplicate kept (0.01% of sales).
