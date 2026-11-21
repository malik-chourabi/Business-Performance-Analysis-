# Power BI — build guide (what you must do in Power BI Desktop)

> **Status.** The finished dashboard is `Business_Performance_Analysis.pbix` in this folder. This guide remains the reference for how the model, measures and pages are built and what values to expect; page-by-page contents of the delivered file are in Appendix B of the final report. Images named `*_PREVIEW.png` are Python-drawn layout previews, not Power BI screenshots.

## Step 0 — Prepare
1. Install Power BI Desktop (free, Microsoft Store). 2. Copy the folder `data/processed/powerbi/` to your computer.

## Step 1 — Load data with Power Query (Phase 5)
1. Home → **Transform data** → Manage Parameters → New: `DataFolder` (Text) = `C:\...\data\processed\powerbi\` (trailing backslash).
2. For each query in `power_query_steps.m`: New Source → Blank Query → Advanced Editor → paste → rename the query (Fact_Sales, Dim_Date, Dim_Product, Dim_Customer, Dim_Geography, Dim_DiscountBand).
3. Check **View → Column quality**: 0 errors / 0 empty everywhere; row counts 9,994 / 1,461 / 1,862 / 793 / 632 / 6.
4. Close & Apply.

## Step 2 — Model (Phase 5)
Follow `data_model.md`: create the 5 active relationships + the inactive Ship Date relationship, mark Dim_Date as date table, set sort-by columns, hide keys.
Import `theme.json` (View → Themes → Browse for themes).

## Step 3 — Measures (Phase 6)
Home → Enter Data → empty table named `_Measures`. Select it → New measure → paste each measure from `dax_measures.txt` (one at a time). Check them against `validation_targets.csv`.

## Step 4 — Pages (Phase 7)
Canvas 16:9 (1280×720). Background `#F4F6F8`; white cards with a thin border. Page title top-left (bold 18 pt navy). **Slicers on every page, synced** (View → Sync slicers): Year (Dim_Date[Year], tile/button style), Region, Category, Segment (dropdown). Add a page-navigation strip using 4 buttons (Insert → Buttons → Navigator → Page navigator).

### Page 1 — Executive Overview
Question: *How is the business doing overall?*
| Visual | Type | Fields | Notes |
|---|---|---|---|
| 5 KPI cards | Card (or New card) | Total Sales, Total Profit, Profit Margin, Total Orders, Total Quantity | + small text card `Headline Insight` |
| Sales & profit trend | Line chart | X: Dim_Date[Year-Month]; Y: Total Sales, Total Profit; | Add `Sales 3M Rolling Avg` as a dashed line |
| Sales by category | Clustered bar | Y: Dim_Product[Category]; X: Total Sales; tooltip Profit Margin | |
| Sales by region | Filled map or bar | Dim_Geography[Region]; Total Sales; tooltip Profit Margin | |
| YoY card | Card | Sales YoY % | Works when one Year is selected |
**Expected (no filter):** $2,297,201 sales · $286,397 profit · 12.5 % margin · 5,009 orders · 37,873 units. Year view: 2014 $484K → 2015 $471K → 2016 $609K → 2017 $733K. Seasonality: Sep, Nov, Dec = 43 % of annual sales.

### Page 2 — Sales and Product Performance
Question: *Which products make or lose money?*
| Visual | Type | Fields |
|---|---|---|
| Category × sub-category | Clustered bar / treemap | Sub-Category; Total Sales; colour by Profit Margin |
| Sub-category profit | Bar, conditional colour (red < 0) | Sub-Category; Total Profit |
| Top 10 products | Table / bar with **Top N filter** (top 10 by Total Profit) | Product Name, Total Sales, Total Profit, Profit Margin |
| Bottom 10 products | Same, Top N → Bottom 10 by Total Profit | |
| Loss-making products | Card | Loss-Making Products (expect **299** with no filter) |
| Scatter | Scatter | X: Total Sales; Y: Profit Margin; Details: Sub-Category; size: Quantity |
**Expected:** loss-making sub-categories = Tables (−$17,725), Bookcases (−$3,473), Supplies (−$1,189). Best product: Canon imageCLASS 2200 Advanced Copier, $25,200 profit. Worst: Cubify CubeX 3D Printer Double Head Print, −$8,880.

### Page 3 — Customer and Regional Analysis
Question: *Who buys, where, and how profitably?*
| Visual | Type | Fields |
|---|---|---|
| Segment comparison | Clustered column | Segment; Total Sales, Total Profit; tooltip Profit Margin, Average Order Value |
| Segment share | Donut | Segment; Sales Share % |
| Region sales vs profit | Clustered bar | Region; Total Sales, Total Profit |
| State map | Filled map (state) | Dim_Geography[State]; colour by Profit Margin (diverging red–green, centre 0) |
| Top 10 customers | Table (Top N by Total Sales) | Customer Name, Segment, Total Sales, Total Profit, Total Orders, Customer Sales Share % |
| State ranking | Bar (bottom 10 by profit) | State; Total Profit |
**Expected:** Consumer 50.6 % of sales (margin 11.5 %), Corporate 30.7 % (13.0 %), Home Office 18.7 % (14.0 %). Regions by profit: West $108K, East $92K, South $47K, Central $40K (margin 7.9 %). 10 loss-making states; Texas −$25.7K. Top customer Sean Miller $25,043 sales but −$1,981 profit. 155 of 793 customers have negative total profit.

### Page 4 — Profitability and Business Insights
Question: *What drives weak profitability?*
| Visual | Type | Fields |
|---|---|---|
| Discount band profit | Column (sort by Band Order) | Dim_DiscountBand[Discount Band]; Total Profit; Profit Margin as line |
| Discount vs margin scatter | Scatter | Details: Sub-Category; X: Average Discount; Y: Profit Margin |
| Region × category margin | Matrix with conditional colour | Rows Region; Columns Category; Values Profit Margin |
| Shipping | Clustered column | Ship Mode; Average Shipping Days; secondary: Profit Margin |
| Loss KPIs | Cards | Loss-Making Lines %, Total Losses, Share of Sales Discounted > 20 % |
| Insight text box | Text box | Static text with the 3–4 key findings (copy from the report) |
**Expected:** margin by band — none 29.5 %, 1–10 % 16.6 %, 11–20 % 11.6 %, 21–30 % −10.1 %, 31–50 % −24.8 %, >50 % −119.2 %. Lines discounted >20 %: 1,393 lines, 15.8 % of sales, **−$135,376 profit**. Loss-making lines 18.7 %. Ship modes average 0.04 / 2.18 / 3.24 / 5.01 days; margin shows no relationship with speed.

## Step 5 — Interactivity & testing (Phase 7)
* Slicers synced across pages; cross-filtering on (default); drill-through page optional (Product → profit detail).
* Test: select each row of `validation_targets.csv` with the slicers and confirm the cards equal the table values (Total Sales, Profit, Margin, Orders, Quantity, AOV, Avg Discount, Avg Ship Days). Tick off in your notes.
* Save as `business_performance_dashboard.pbix`; export each page: File → Export → PDF, and take screenshots into `reports/dashboard_screenshots/`.
