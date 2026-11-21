# Methodology

## Workflow and tool responsibilities
| Phase | Tool | Responsibility (no analysis is repeated in a second tool except as validation) | Output |
|---|---|---|---|
| 1 | — | Dataset understanding, business questions, objectives | `documentation/` |
| 2 | **Excel** | Import, structure and quality inspection, sort/filter, basic formulas (SUM, AVERAGE, COUNTIF(S), SUMIFS, IF), pivot tables, preliminary descriptives | `excel/initial_data_inspection.xlsx` |
| 3 | **Python** (pandas, NumPy, Matplotlib, SciPy, scikit-learn) | Cleaning, feature engineering, EDA, statistics, forecast, charts, export | `python/business_analysis.ipynb`, `data/processed/cleaned_sales.csv` |
| 4 | **SQLite / SQL** | Database design, business queries, validation of key figures against Python | `sql/superstore.db`, `sql/business_queries.sql` |
| 5–7 | **Power BI** | Power Query, star schema, DAX, four-page interactive dashboard | `powerbi/Business_Performance_Analysis.pbix` (built in Power BI Desktop) + data, DAX reference and build guide |
| 8–9 | — | Interpretation, recommendations, report, notes, README | `reports/`, `documentation/` |

## Data flow
`Sample_Superstore.csv` (raw, never edited) → Excel inspection (read-only use) → Python cleaning → `cleaned_sales.csv` → (a) SQLite database; (b) star-schema CSVs → Power BI.

## Cleaning principles
1. Preserve the raw file. 2. Delete nothing without proof (0 rows deleted; 1 possible duplicate flagged). 3. Fix formats (dates, postal codes). 4. Standardise only where the key is unambiguous (product name per Product ID). 5. Reconcile after cleaning (rows and totals equal the raw file). 6. Document every decision.

## Analytical principles
* KPI definitions are fixed once (see data dictionary) and reused everywhere.
* Margins are computed on totals, not averaged across rows.
* Skewed variables (Sales, Profit) → medians and rank-based tests alongside means.
* Time-ordered data are split chronologically for forecasting; models are compared with naïve baselines and evaluated on held-out data only.
* Correlation and group differences are described as associations; causal language is avoided.

## Validation
* Excel formulas ↔ Python: totals and every grouped table agree (Excel recalculated with 0 formula errors).
* SQL ↔ Python: 54 automated checks, all passed (`sql/validation_report.md`).
* Power BI ↔ Python: `powerbi/validation_targets.csv` lists the expected card values for 17 slicer selections; to be ticked off by the author against the finished `.pbix` (Appendix B, Table B5 of the final report).
