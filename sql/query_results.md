# SQL query results (executed on sql/superstore.db)


## Q01 | Database structure: list tables and row counts (verification)

```sql
-- Q01 | Database structure: list tables and row counts (verification)
-- Purpose: confirm the import loaded every row.
SELECT 'sales_clean' AS table_name, COUNT(*) AS row_count FROM sales_clean
UNION ALL SELECT 'order_lines', COUNT(*) FROM order_lines
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL SELECT 'dim_geography', COUNT(*) FROM dim_geography;
```

**Result** (6 rows)

| table_name    |   row_count |
|:--------------|------------:|
| sales_clean   |        9994 |
| order_lines   |        9994 |
| orders        |        5009 |
| dim_customer  |         793 |
| dim_product   |        1862 |
| dim_geography |         632 |


## Q02 | What is the total revenue, profit, margin and order volume?

```sql
-- Q02 | What is the total revenue, profit, margin and order volume?
-- Purpose: headline KPIs; the numbers every other query is checked against.
SELECT ROUND(SUM(sales), 2)                         AS total_sales,
       ROUND(SUM(profit), 2)                        AS total_profit,
       ROUND(SUM(profit) * 100.0 / SUM(sales), 2)   AS profit_margin_pct,
       COUNT(DISTINCT order_id)                     AS distinct_orders,
       COUNT(DISTINCT customer_id)                  AS distinct_customers,
       SUM(quantity)                                AS total_quantity,
       ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS avg_order_value,
       ROUND(AVG(discount), 4)                      AS avg_discount,
       ROUND(AVG(shipping_days), 2)                 AS avg_shipping_days
FROM sales_clean;
```

**Result** (1 rows)

|   total_sales |   total_profit |   profit_margin_pct |   distinct_orders |   distinct_customers |   total_quantity |   avg_order_value |   avg_discount |   avg_shipping_days |
|--------------:|---------------:|--------------------:|------------------:|---------------------:|-----------------:|------------------:|---------------:|--------------------:|
|  2,297,200.86 |     286,397.02 |               12.47 |          5,009.00 |               793.00 |        37,873.00 |            458.61 |           0.16 |                3.96 |


## Q03 | Which product category generates the highest revenue, and the highest profit?

```sql
-- Q03 | Which product category generates the highest revenue, and the highest profit?
-- Purpose: category contribution and margin. ORDER BY sales DESC puts the revenue leader first.
SELECT category,
       ROUND(SUM(sales), 2) AS sales,
       ROUND(SUM(profit), 2) AS profit,
       ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS margin_pct,
       COUNT(DISTINCT order_id) AS orders
FROM sales_clean GROUP BY category ORDER BY sales DESC;
```

**Result** (3 rows)

| category        |      sales |     profit |   margin_pct |   orders |
|:----------------|-----------:|-----------:|-------------:|---------:|
| Technology      | 836,154.03 | 145,454.95 |        17.40 |     1544 |
| Furniture       | 741,999.80 |  18,451.27 |         2.49 |     1764 |
| Office Supplies | 719,047.03 | 122,490.80 |        17.04 |     3742 |


## Q04 | Sub-category profitability (loss-making sub-categories show negative profit)

```sql
-- Q04 | Sub-category profitability (loss-making sub-categories show negative profit)
SELECT category, sub_category,
       ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS profit,
       ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS margin_pct,
       ROUND(AVG(discount), 3) AS avg_discount
FROM sales_clean GROUP BY category, sub_category ORDER BY profit ASC;
```

**Result** (17 rows)

| category        | sub_category   |      sales |     profit |   margin_pct |   avg_discount |
|:----------------|:---------------|-----------:|-----------:|-------------:|---------------:|
| Furniture       | Tables         | 206,965.53 | -17,725.48 |        -8.56 |           0.26 |
| Furniture       | Bookcases      | 114,880.00 |  -3,472.56 |        -3.02 |           0.21 |
| Office Supplies | Supplies       |  46,673.54 |  -1,189.10 |        -2.55 |           0.08 |
| Office Supplies | Fasteners      |   3,024.28 |     949.52 |        31.40 |           0.08 |
| Technology      | Machines       | 189,238.63 |   3,384.76 |         1.79 |           0.31 |
| Office Supplies | Labels         |  12,486.31 |   5,546.25 |        44.42 |           0.07 |
| Office Supplies | Art            |  27,118.79 |   6,527.79 |        24.07 |           0.07 |
| Office Supplies | Envelopes      |  16,476.40 |   6,964.18 |        42.27 |           0.08 |
| Furniture       | Furnishings    |  91,705.16 |  13,059.14 |        14.24 |           0.14 |
| Office Supplies | Appliances     | 107,532.16 |  18,138.01 |        16.87 |           0.17 |
| Office Supplies | Storage        | 223,843.61 |  21,278.83 |         9.51 |           0.07 |
| Furniture       | Chairs         | 328,449.10 |  26,590.17 |         8.10 |           0.17 |
| Office Supplies | Binders        | 203,412.73 |  30,221.76 |        14.86 |           0.37 |
| Office Supplies | Paper          |  78,479.21 |  34,053.57 |        43.39 |           0.07 |
| Technology      | Accessories    | 167,380.32 |  41,936.64 |        25.05 |           0.08 |
| Technology      | Phones         | 330,007.05 |  44,515.73 |        13.49 |           0.15 |
| Technology      | Copiers        | 149,528.03 |  55,617.82 |        37.20 |           0.16 |


## Q05 | Which region is the most profitable?

```sql
-- Q05 | Which region is the most profitable?
SELECT region,
       ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS profit,
       ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS margin_pct,
       ROUND(AVG(discount), 3) AS avg_discount,
       COUNT(DISTINCT order_id) AS orders
FROM sales_clean GROUP BY region ORDER BY profit DESC;
```

**Result** (4 rows)

| region   |      sales |     profit |   margin_pct |   avg_discount |   orders |
|:---------|-----------:|-----------:|-------------:|---------------:|---------:|
| West     | 725,457.82 | 108,418.45 |        14.94 |           0.11 |     1611 |
| East     | 678,781.24 |  91,522.78 |        13.48 |           0.14 |     1401 |
| South    | 391,721.91 |  46,749.43 |        11.93 |           0.15 |      822 |
| Central  | 501,239.89 |  39,706.36 |         7.92 |           0.24 |     1175 |


## Q06 | Which customer segment contributes most to sales? (share of total via a subquery)

```sql
-- Q06 | Which customer segment contributes most to sales? (share of total via a subquery)
SELECT segment,
       ROUND(SUM(sales), 2) AS sales,
       ROUND(SUM(sales) * 100.0 / (SELECT SUM(sales) FROM sales_clean), 2) AS sales_share_pct,
       ROUND(SUM(profit), 2) AS profit,
       ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS margin_pct,
       COUNT(DISTINCT customer_id) AS customers,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS avg_order_value
FROM sales_clean GROUP BY segment ORDER BY sales DESC;
```

**Result** (3 rows)

| segment     |        sales |   sales_share_pct |     profit |   margin_pct |   customers |   orders |   avg_order_value |
|:------------|-------------:|------------------:|-----------:|-------------:|------------:|---------:|------------------:|
| Consumer    | 1,161,401.34 |             50.56 | 134,119.21 |        11.55 |         409 |     2586 |            449.11 |
| Corporate   |   706,146.37 |             30.74 |  91,979.13 |        13.03 |         236 |     1514 |            466.41 |
| Home Office |   429,653.15 |             18.70 |  60,298.68 |        14.03 |         148 |      909 |            472.67 |


## Q07 | Which products generate losses? (total profit < 0) — HAVING filters AFTER aggregation

```sql
-- Q07 | Which products generate losses? (total profit < 0) — HAVING filters AFTER aggregation
SELECT product_id, product_name, category, sub_category,
       ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS profit,
       ROUND(AVG(discount), 3) AS avg_discount
FROM sales_clean GROUP BY product_id, product_name, category, sub_category
HAVING ROUND(SUM(profit), 2) < 0 ORDER BY profit ASC LIMIT 15;   -- ROUND avoids floating-point noise (e.g. -3.6e-15)
```

**Result** (15 rows)

| product_id      | product_name                                                                 | category        | sub_category   |     sales |    profit |   avg_discount |
|:----------------|:-----------------------------------------------------------------------------|:----------------|:---------------|----------:|----------:|---------------:|
| TEC-MA-10000418 | Cubify CubeX 3D Printer Double Head Print                                    | Technology      | Machines       | 11,099.96 | -8,879.97 |           0.53 |
| TEC-MA-10000822 | Lexmark MX611dhe Monochrome Laser Printer                                    | Technology      | Machines       | 16,829.90 | -4,589.97 |           0.40 |
| TEC-MA-10004125 | Cubify CubeX 3D Printer Triple Head Print                                    | Technology      | Machines       |  7,999.98 | -3,839.99 |           0.50 |
| FUR-TA-10000198 | Chromcraft Bull-Nose Wood Oval Conference Tables & Bases                     | Furniture       | Tables         |  9,917.64 | -2,876.12 |           0.28 |
| FUR-TA-10001889 | Bush Advantage Collection Racetrack Conference Table                         | Furniture       | Tables         |  9,544.73 | -1,934.40 |           0.35 |
| OFF-BI-10004995 | GBC DocuBind P400 Electric Binding System                                    | Office Supplies | Binders        | 17,965.07 | -1,878.17 |           0.45 |
| TEC-MA-10002412 | Cisco TelePresence System EX90 Videoconferencing Unit                        | Technology      | Machines       | 22,638.48 | -1,811.08 |           0.50 |
| OFF-SU-10002881 | Martin Yale Chadless Opener Electric Letter Opener                           | Office Supplies | Supplies       | 16,656.20 | -1,299.18 |           0.10 |
| FUR-TA-10001950 | Balt Solid Wood Round Tables                                                 | Furniture       | Tables         |  6,518.75 | -1,201.06 |           0.20 |
| FUR-TA-10004289 | BoxOffice By Design Rectangular and Half-Moon Meeting Room Tables            | Furniture       | Tables         |  1,706.25 | -1,148.44 |           0.48 |
| FUR-TA-10004154 | Riverside Furniture Oval Coffee Table, Oval End Table, End Table with Drawer | Furniture       | Tables         |  4,446.18 | -1,147.40 |           0.30 |
| TEC-MA-10002210 | Epson TM-T88V Direct Thermal Printer - Monochrome - Desktop                  | Technology      | Machines       |  1,212.70 | -1,057.23 |           0.55 |
| FUR-CH-10003312 | Hon 2090 �Pillow Soft� Series Mid Back Swivel/Tilt Chairs                    | Furniture       | Chairs         |  5,282.42 |   -989.05 |           0.22 |
| FUR-BO-10001972 | O'Sullivan 4-Shelf Bookcase in Odessa Pine                                   | Furniture       | Bookcases      |  2,740.20 |   -975.10 |           0.42 |
| FUR-TA-10004256 | Bretford �Just In Time� Height-Adjustable Multi-Task Work Tables             | Furniture       | Tables         |  5,634.90 |   -964.19 |           0.23 |


## Q08 | How many products lose money, and how much? (CASE WHEN inside a subquery)

```sql
-- Q08 | How many products lose money, and how much? (CASE WHEN inside a subquery)
SELECT COUNT(*) AS products_total,
       SUM(CASE WHEN ROUND(p, 2) < 0 THEN 1 ELSE 0 END) AS loss_making_products,
       ROUND(SUM(CASE WHEN ROUND(p, 2) < 0 THEN p ELSE 0 END), 2) AS profit_lost_on_them
FROM (SELECT product_id, SUM(profit) AS p FROM sales_clean GROUP BY product_id);
```

**Result** (1 rows)

|   products_total |   loss_making_products |   profit_lost_on_them |
|-----------------:|-----------------------:|----------------------:|
|         1,862.00 |                 299.00 |            -76,721.13 |


## Q09 | Which discount levels are associated with lower average profit?

```sql
-- Q09 | Which discount levels are associated with lower average profit?
-- CASE WHEN builds the discount bands; association only, not proof of cause.
SELECT CASE WHEN discount = 0 THEN '1. No discount'
            WHEN discount <= 0.10 THEN '2. 1-10%'
            WHEN discount <= 0.20 THEN '3. 11-20%'
            WHEN discount <= 0.30 THEN '4. 21-30%'
            WHEN discount <= 0.50 THEN '5. 31-50%'
            ELSE '6. >50%' END AS discount_band,
       COUNT(*) AS order_lines,
       ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS total_profit,
       ROUND(AVG(profit), 2) AS avg_profit_per_line,
       ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS margin_pct,
       ROUND(100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_lines_loss_making
FROM sales_clean GROUP BY discount_band ORDER BY discount_band;
```

**Result** (6 rows)

| discount_band   |   order_lines |        sales |   total_profit |   avg_profit_per_line |   margin_pct |   pct_lines_loss_making |
|:----------------|--------------:|-------------:|---------------:|----------------------:|-------------:|------------------------:|
| 1. No discount  |          4798 | 1,087,908.47 |     320,987.60 |                 66.90 |        29.51 |                    0.00 |
| 2. 1-10%        |            94 |    54,369.35 |       9,029.18 |                 96.06 |        16.61 |                    4.30 |
| 3. 11-20%       |          3709 |   792,152.89 |      91,756.30 |                 24.74 |        11.58 |                   14.00 |
| 4. 21-30%       |           227 |   103,226.65 |     -10,369.28 |                -45.68 |       -10.05 |                   91.60 |
| 5. 31-50%       |           310 |   195,314.76 |     -48,447.73 |               -156.28 |       -24.80 |                   91.60 |
| 6. >50%         |           856 |    64,228.74 |     -76,559.05 |                -89.44 |      -119.20 |                  100.00 |


## Q10 | Average profit by exact discount level

```sql
-- Q10 | Average profit by exact discount level
SELECT discount, COUNT(*) AS order_lines, ROUND(AVG(profit), 2) AS avg_profit, ROUND(SUM(profit), 2) AS total_profit
FROM sales_clean GROUP BY discount ORDER BY discount;
```

**Result** (12 rows)

|   discount |   order_lines |   avg_profit |   total_profit |
|-----------:|--------------:|-------------:|---------------:|
|       0.00 |      4,798.00 |        66.90 |     320,987.60 |
|       0.10 |         94.00 |        96.06 |       9,029.18 |
|       0.15 |         52.00 |        27.29 |       1,418.99 |
|       0.20 |      3,657.00 |        24.70 |      90,337.31 |
|       0.30 |        227.00 |       -45.68 |     -10,369.28 |
|       0.32 |         27.00 |       -88.56 |      -2,391.14 |
|       0.40 |        206.00 |      -111.93 |     -23,057.05 |
|       0.45 |         11.00 |      -226.65 |      -2,493.11 |
|       0.50 |         66.00 |      -310.70 |     -20,506.43 |
|       0.60 |        138.00 |       -43.08 |      -5,944.66 |
|       0.70 |        418.00 |       -95.87 |     -40,075.36 |
|       0.80 |        300.00 |      -101.80 |     -30,539.04 |


## Q11 | Monthly sales totals (all 48 months)

```sql
-- Q11 | Monthly sales totals (all 48 months)
SELECT year_month, ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS profit, COUNT(DISTINCT order_id) AS orders
FROM sales_clean GROUP BY year_month ORDER BY year_month;
```

**Result** (48 rows)

| year_month   |      sales |    profit |   orders |
|:-------------|-----------:|----------:|---------:|
| 2014-01      |  14,236.90 |  2,450.19 |       32 |
| 2014-02      |   4,519.89 |    862.31 |       28 |
| 2014-03      |  55,691.01 |    498.73 |       71 |
| 2014-04      |  28,295.35 |  3,488.84 |       66 |
| 2014-05      |  23,648.29 |  2,738.71 |       69 |
| 2014-06      |  34,595.13 |  4,976.52 |       66 |
| 2014-07      |  33,946.39 |   -841.48 |       65 |
| 2014-08      |  27,909.47 |  5,318.10 |       72 |
| 2014-09      |  81,777.35 |  8,328.10 |      130 |
| 2014-10      |  31,453.39 |  3,448.26 |       78 |
| 2014-11      |  78,628.72 |  9,292.13 |      151 |
| 2014-12      |  69,545.62 |  8,983.57 |      141 |
| 2015-01      |  18,174.08 | -3,281.01 |       29 |
| 2015-02      |  11,951.41 |  2,813.85 |       36 |
| 2015-03      |  38,726.25 |  9,732.10 |       79 |
| 2015-04      |  34,195.21 |  4,187.50 |       72 |
| 2015-05      |  30,131.69 |  4,667.87 |       74 |
| 2015-06      |  24,797.29 |  3,335.56 |       68 |
| 2015-07      |  28,765.33 |  3,288.65 |       66 |
| 2015-08      |  36,898.33 |  5,355.81 |       68 |
| 2015-09      |  64,595.92 |  8,209.16 |      140 |
| 2015-10      |  31,404.92 |  2,817.37 |       87 |
| 2015-11      |  75,972.56 | 12,474.79 |      158 |
| 2015-12      |  74,919.52 |  8,016.97 |      161 |
| 2016-01      |  18,542.49 |  2,824.82 |       48 |
| 2016-02      |  22,978.82 |  5,004.58 |       45 |
| 2016-03      |  51,715.88 |  3,611.97 |       86 |
| 2016-04      |  38,750.04 |  2,977.81 |       89 |
| 2016-05      |  56,987.73 |  8,662.15 |      108 |
| 2016-06      |  40,344.53 |  4,750.38 |       97 |
| 2016-07      |  39,261.96 |  4,432.88 |       96 |
| 2016-08      |  31,115.37 |  2,062.07 |       90 |
| 2016-09      |  73,410.02 |  9,328.66 |      192 |
| 2016-10      |  59,687.75 | 16,243.14 |      105 |
| 2016-11      |  79,411.97 |  4,011.41 |      183 |
| 2016-12      |  96,999.04 | 17,885.31 |      176 |
| 2017-01      |  43,971.37 |  7,140.44 |       69 |
| 2017-02      |  20,301.13 |  1,613.87 |       53 |
| 2017-03      |  58,872.35 | 14,751.89 |      118 |
| 2017-04      |  36,521.54 |    933.29 |      116 |
| 2017-05      |  44,261.11 |  6,342.58 |      118 |
| 2017-06      |  52,981.73 |  8,223.34 |      133 |
| 2017-07      |  45,264.42 |  6,952.62 |      111 |
| 2017-08      |  63,120.89 |  9,040.96 |      111 |
| 2017-09      |  87,866.65 | 10,991.56 |      226 |
| 2017-10      |  77,776.92 |  9,275.28 |      147 |
| 2017-11      | 118,447.82 |  9,690.10 |      261 |
| 2017-12      |  83,829.32 |  8,483.35 |      224 |


## Q12 | Yearly sales, profit and growth (self-join of yearly totals)

```sql
-- Q12 | Yearly sales, profit and growth (self-join of yearly totals)
WITH y AS (SELECT order_year, SUM(sales) AS sales, SUM(profit) AS profit FROM sales_clean GROUP BY order_year)
SELECT cur.order_year, ROUND(cur.sales, 2) AS sales, ROUND(cur.profit, 2) AS profit,
       ROUND(cur.profit * 100.0 / cur.sales, 2) AS margin_pct,
       ROUND((cur.sales - prev.sales) * 100.0 / prev.sales, 2) AS sales_growth_pct
FROM y cur LEFT JOIN y prev ON prev.order_year = cur.order_year - 1 ORDER BY cur.order_year;
```

**Result** (4 rows)

|   order_year |      sales |    profit |   margin_pct |   sales_growth_pct |
|-------------:|-----------:|----------:|-------------:|-------------------:|
|     2,014.00 | 484,247.50 | 49,543.97 |        10.23 |             nan    |
|     2,015.00 | 470,532.51 | 61,618.60 |        13.10 |              -2.83 |
|     2,016.00 | 609,205.60 | 81,795.17 |        13.43 |              29.47 |
|     2,017.00 | 733,215.26 | 93,439.27 |        12.74 |              20.36 |


## Q13 | Which customers generate the highest sales? (top 10, using JOIN to the customer dimension)

```sql
-- Q13 | Which customers generate the highest sales? (top 10, using JOIN to the customer dimension)
SELECT c.customer_id, c.customer_name, c.segment,
       ROUND(SUM(l.sales), 2) AS sales, ROUND(SUM(l.profit), 2) AS profit,
       COUNT(DISTINCT l.order_id) AS orders
FROM order_lines l
JOIN orders o ON o.order_id = l.order_id
JOIN dim_customer c ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name, c.segment ORDER BY sales DESC LIMIT 10;
```

**Result** (10 rows)

| customer_id   | customer_name      | segment     |     sales |    profit |   orders |
|:--------------|:-------------------|:------------|----------:|----------:|---------:|
| SM-20320      | Sean Miller        | Home Office | 25,043.05 | -1,980.74 |        5 |
| TC-20980      | Tamara Chand       | Corporate   | 19,052.22 |  8,981.32 |        5 |
| RB-19360      | Raymond Buch       | Consumer    | 15,117.34 |  6,976.10 |        6 |
| TA-21385      | Tom Ashbrook       | Home Office | 14,595.62 |  4,703.79 |        4 |
| AB-10105      | Adrian Barton      | Consumer    | 14,473.57 |  5,444.81 |       10 |
| KL-16645      | Ken Lonsdale       | Consumer    | 14,175.23 |    806.85 |       12 |
| SC-20095      | Sanjit Chand       | Consumer    | 14,142.33 |  5,757.41 |        9 |
| HL-15040      | Hunter Lopez       | Consumer    | 12,873.30 |  5,622.43 |        6 |
| SE-20110      | Sanjit Engle       | Consumer    | 12,209.44 |  2,650.68 |       11 |
| CC-12370      | Christopher Conant | Consumer    | 12,129.07 |  2,177.05 |        5 |


## Q14 | Loss-making states (JOIN order_lines -> orders -> dim_geography)

```sql
-- Q14 | Loss-making states (JOIN order_lines -> orders -> dim_geography)
SELECT g.state, g.region, ROUND(SUM(l.sales), 2) AS sales, ROUND(SUM(l.profit), 2) AS profit,
       ROUND(SUM(l.profit) * 100.0 / SUM(l.sales), 2) AS margin_pct, ROUND(AVG(l.discount), 3) AS avg_discount
FROM order_lines l JOIN orders o ON o.order_id = l.order_id JOIN dim_geography g ON g.geo_id = o.geo_id
GROUP BY g.state, g.region HAVING SUM(l.profit) < 0 ORDER BY profit ASC;
```

**Result** (10 rows)

| state          | region   |      sales |     profit |   margin_pct |   avg_discount |
|:---------------|:---------|-----------:|-----------:|-------------:|---------------:|
| Texas          | Central  | 170,188.05 | -25,729.36 |       -15.12 |           0.37 |
| Ohio           | East     |  78,258.14 | -16,971.38 |       -21.69 |           0.33 |
| Pennsylvania   | East     | 116,511.91 | -15,559.96 |       -13.35 |           0.33 |
| Illinois       | Central  |  80,166.10 | -12,607.89 |       -15.73 |           0.39 |
| North Carolina | South    |  55,603.16 |  -7,490.91 |       -13.47 |           0.28 |
| Colorado       | West     |  32,108.12 |  -6,527.86 |       -20.33 |           0.32 |
| Tennessee      | South    |  30,661.87 |  -5,341.69 |       -17.42 |           0.29 |
| Arizona        | West     |  35,282.00 |  -3,427.92 |        -9.72 |           0.30 |
| Florida        | South    |  89,473.71 |  -3,399.30 |        -3.80 |           0.30 |
| Oregon         | West     |  17,431.15 |  -1,190.47 |        -6.83 |           0.29 |


## Q15 | Region x Category profit matrix (CASE WHEN pivot)

```sql
-- Q15 | Region x Category profit matrix (CASE WHEN pivot)
SELECT region,
       ROUND(SUM(CASE WHEN category = 'Furniture' THEN profit ELSE 0 END), 0) AS furniture_profit,
       ROUND(SUM(CASE WHEN category = 'Office Supplies' THEN profit ELSE 0 END), 0) AS office_supplies_profit,
       ROUND(SUM(CASE WHEN category = 'Technology' THEN profit ELSE 0 END), 0) AS technology_profit
FROM sales_clean GROUP BY region ORDER BY region;
```

**Result** (4 rows)

| region   |   furniture_profit |   office_supplies_profit |   technology_profit |
|:---------|-------------------:|-------------------------:|--------------------:|
| Central  |          -2,871.00 |                 8,880.00 |           33,697.00 |
| East     |           3,046.00 |                41,015.00 |           47,462.00 |
| South    |           6,771.00 |                19,986.00 |           19,992.00 |
| West     |          11,505.00 |                52,610.00 |           44,304.00 |


## Q16 | Share of each region's sales made on lines discounted above 20%

```sql
-- Q16 | Share of each region's sales made on lines discounted above 20%
SELECT region,
       ROUND(100.0 * SUM(CASE WHEN discount > 0.20 THEN sales ELSE 0 END) / SUM(sales), 1) AS pct_sales_discount_over_20
FROM sales_clean GROUP BY region ORDER BY pct_sales_discount_over_20 DESC;
```

**Result** (4 rows)

| region   |   pct_sales_discount_over_20 |
|:---------|-----------------------------:|
| Central  |                        25.80 |
| East     |                        21.50 |
| South    |                        18.10 |
| West     |                         2.40 |


## Q17 | Shipping performance by ship mode

```sql
-- Q17 | Shipping performance by ship mode
SELECT ship_mode, COUNT(*) AS order_lines, ROUND(AVG(shipping_days), 2) AS avg_days,
       MIN(shipping_days) AS min_days, MAX(shipping_days) AS max_days,
       ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS margin_pct
FROM sales_clean GROUP BY ship_mode ORDER BY avg_days;
```

**Result** (4 rows)

| ship_mode      |   order_lines |   avg_days |   min_days |   max_days |   margin_pct |
|:---------------|--------------:|-----------:|-----------:|-----------:|-------------:|
| Same Day       |           543 |       0.04 |          0 |          1 |        12.38 |
| First Class    |          1538 |       2.18 |          1 |          4 |        13.93 |
| Second Class   |          1945 |       3.24 |          1 |          5 |        12.51 |
| Standard Class |          5968 |       5.01 |          3 |          7 |        12.08 |


## Q18 | Investigate specific transactions: largest single-line losses (WHERE + ORDER BY)

```sql
-- Q18 | Investigate specific transactions: largest single-line losses (WHERE + ORDER BY)
SELECT order_id, product_name, region, sales, discount, profit
FROM sales_clean WHERE profit < 0 ORDER BY profit ASC LIMIT 10;
```

**Result** (10 rows)

| order_id       | product_name                                                                | region   |     sales |   discount |    profit |
|:---------------|:----------------------------------------------------------------------------|:---------|----------:|-----------:|----------:|
| CA-2016-108196 | Cubify CubeX 3D Printer Double Head Print                                   | East     |  4,499.98 |       0.70 | -6,599.98 |
| US-2017-168116 | Cubify CubeX 3D Printer Triple Head Print                                   | South    |  7,999.98 |       0.50 | -3,839.99 |
| CA-2014-169019 | GBC DocuBind P400 Electric Binding System                                   | Central  |  2,177.58 |       0.80 | -3,701.89 |
| CA-2017-134845 | Lexmark MX611dhe Monochrome Laser Printer                                   | West     |  2,549.99 |       0.70 | -3,399.98 |
| US-2017-122714 | Ibico EPK-21 Electric Binding System                                        | Central  |  1,889.99 |       0.80 | -2,929.48 |
| CA-2015-147830 | Cubify CubeX 3D Printer Double Head Print                                   | East     |  1,799.99 |       0.70 | -2,639.99 |
| CA-2017-131254 | Fellowes PB500 Electric Punch Plastic Comb Binding Machine with Manual Bind | Central  |  1,525.19 |       0.80 | -2,287.78 |
| CA-2015-116638 | Chromcraft Bull-Nose Wood Oval Conference Tables & Bases                    | South    |  4,297.64 |       0.40 | -1,862.31 |
| CA-2016-130946 | GBC DocuBind P400 Electric Binding System                                   | Central  |  1,088.79 |       0.80 | -1,850.95 |
| CA-2014-145317 | Cisco TelePresence System EX90 Videoconferencing Unit                       | South    | 22,638.48 |       0.50 | -1,811.08 |


## Q19 | Customers with negative total profit, and the biggest top-sales customer with a loss

```sql
-- Q19 | Customers with negative total profit, and the biggest top-sales customer with a loss
SELECT COUNT(*) AS customers_with_loss
FROM (SELECT customer_id FROM sales_clean GROUP BY customer_id HAVING SUM(profit) < 0);
```

**Result** (1 rows)

|   customers_with_loss |
|----------------------:|
|                   155 |


## Q20 | Binders: profitable overall, but where do the losses sit? (filter + CASE WHEN)

```sql
-- Q20 | Binders: profitable overall, but where do the losses sit? (filter + CASE WHEN)
SELECT discount_band, COUNT(*) AS lines, ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS profit
FROM sales_clean WHERE sub_category = 'Binders' GROUP BY discount_band ORDER BY profit;
```

**Result** (3 rows)

| discount_band   |   lines |     sales |     profit |
|:----------------|--------:|----------:|-----------:|
| >50%            |     613 | 36,140.61 | -38,510.50 |
| 11-20%          |     573 | 85,442.64 |  29,417.81 |
| No discount     |     337 | 81,829.48 |  39,314.45 |


## Q21 | Data-quality check: the one possible duplicate pair (kept and flagged)

```sql
-- Q21 | Data-quality check: the one possible duplicate pair (kept and flagged)
SELECT row_id, order_id, product_id, sales, quantity, discount, profit, possible_duplicate
FROM sales_clean
WHERE order_id = 'US-2014-150119' AND product_id = 'FUR-CH-10002965';
```

**Result** (2 rows)

|   row_id | order_id       | product_id      |   sales |   quantity |   discount |   profit |   possible_duplicate |
|---------:|:---------------|:----------------|--------:|-----------:|-----------:|---------:|---------------------:|
|     3406 | US-2014-150119 | FUR-CH-10002965 |  281.37 |          2 |       0.30 |   -12.06 |                    0 |
|     3407 | US-2014-150119 | FUR-CH-10002965 |  281.37 |          2 |       0.30 |   -12.06 |                    1 |


## Q22 | Integrity check: line totals in order_lines equal the flat table (should return 0 difference)

```sql
-- Q22 | Integrity check: line totals in order_lines equal the flat table (should return 0 difference)
SELECT ROUND((SELECT SUM(sales) FROM order_lines) - (SELECT SUM(sales) FROM sales_clean), 6) AS sales_difference,
       ROUND((SELECT SUM(profit) FROM order_lines) - (SELECT SUM(profit) FROM sales_clean), 6) AS profit_difference;
```

**Result** (1 rows)

|   sales_difference |   profit_difference |
|-------------------:|--------------------:|
|               0.00 |                0.00 |


## Q23 | Discount groups used in the report (4 bands): No discount, Low (>0-20%), Medium (>20-40%), High (>40%)

```sql
-- Q23 | Discount groups used in the report (4 bands): No discount, Low (>0-20%), Medium (>20-40%), High (>40%)
-- Purpose: shows that lines discounted by more than 20% lose money on average; ">20%" means strictly greater than 0.20.
SELECT CASE WHEN discount = 0   THEN '1 No Discount'
            WHEN discount <= 0.2 THEN '2 Low (>0-20%)'
            WHEN discount <= 0.4 THEN '3 Medium (>20-40%)'
            ELSE '4 High (>40%)' END AS discount_group,
       COUNT(*) AS lines, ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS profit,
       ROUND(AVG(profit), 2) AS avg_profit_per_line,
       ROUND(SUM(profit) * 100.0 / SUM(sales), 1) AS margin_pct,
       ROUND(100.0 * SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_lines_loss
FROM sales_clean GROUP BY discount_group ORDER BY discount_group;
```

**Result** (4 rows)

| discount_group     |   lines |        sales |     profit |   avg_profit_per_line |   margin_pct |   pct_lines_loss |
|:-------------------|--------:|-------------:|-----------:|----------------------:|-------------:|-----------------:|
| 1 No Discount      |    4798 | 1,087,908.47 | 320,987.60 |                 66.90 |        29.50 |             0.00 |
| 2 Low (>0-20%)     |    3803 |   846,522.24 | 100,785.47 |                 26.50 |        11.90 |            13.80 |
| 3 Medium (>20-40%) |     460 |   234,137.90 | -35,817.47 |                -77.86 |       -15.30 |            90.20 |
| 4 High (>40%)      |     933 |   128,632.25 | -99,558.59 |               -106.71 |       -77.40 |           100.00 |
