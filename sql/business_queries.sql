-- =====================================================================
-- Business queries — Sample Superstore (SQLite)
-- Database: sql/superstore.db
-- Tables: sales_clean (flat), dim_customer, dim_product, dim_geography, orders, order_lines
-- IMPORTANT: unique orders are counted with COUNT(DISTINCT order_id) — one order has many rows.
-- Profit margin = SUM(profit) / SUM(sales) (ratio of totals, not average of row margins).
-- =====================================================================

-- Q01 | Database structure: list tables and row counts (verification)
-- Purpose: confirm the import loaded every row.
SELECT 'sales_clean' AS table_name, COUNT(*) AS row_count FROM sales_clean
UNION ALL SELECT 'order_lines', COUNT(*) FROM order_lines
UNION ALL SELECT 'orders', COUNT(*) FROM orders
UNION ALL SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL SELECT 'dim_geography', COUNT(*) FROM dim_geography;

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

-- Q03 | Which product category generates the highest revenue, and the highest profit?
-- Purpose: category contribution and margin. ORDER BY sales DESC puts the revenue leader first.
SELECT category,
       ROUND(SUM(sales), 2) AS sales,
       ROUND(SUM(profit), 2) AS profit,
       ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS margin_pct,
       COUNT(DISTINCT order_id) AS orders
FROM sales_clean GROUP BY category ORDER BY sales DESC;

-- Q04 | Sub-category profitability (loss-making sub-categories show negative profit)
SELECT category, sub_category,
       ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS profit,
       ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS margin_pct,
       ROUND(AVG(discount), 3) AS avg_discount
FROM sales_clean GROUP BY category, sub_category ORDER BY profit ASC;

-- Q05 | Which region is the most profitable?
SELECT region,
       ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS profit,
       ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS margin_pct,
       ROUND(AVG(discount), 3) AS avg_discount,
       COUNT(DISTINCT order_id) AS orders
FROM sales_clean GROUP BY region ORDER BY profit DESC;

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

-- Q07 | Which products generate losses? (total profit < 0) — HAVING filters AFTER aggregation
SELECT product_id, product_name, category, sub_category,
       ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS profit,
       ROUND(AVG(discount), 3) AS avg_discount
FROM sales_clean GROUP BY product_id, product_name, category, sub_category
HAVING ROUND(SUM(profit), 2) < 0 ORDER BY profit ASC LIMIT 15;   -- ROUND avoids floating-point noise (e.g. -3.6e-15)

-- Q08 | How many products lose money, and how much? (CASE WHEN inside a subquery)
SELECT COUNT(*) AS products_total,
       SUM(CASE WHEN ROUND(p, 2) < 0 THEN 1 ELSE 0 END) AS loss_making_products,
       ROUND(SUM(CASE WHEN ROUND(p, 2) < 0 THEN p ELSE 0 END), 2) AS profit_lost_on_them
FROM (SELECT product_id, SUM(profit) AS p FROM sales_clean GROUP BY product_id);

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

-- Q10 | Average profit by exact discount level
SELECT discount, COUNT(*) AS order_lines, ROUND(AVG(profit), 2) AS avg_profit, ROUND(SUM(profit), 2) AS total_profit
FROM sales_clean GROUP BY discount ORDER BY discount;

-- Q11 | Monthly sales totals (all 48 months)
SELECT year_month, ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS profit, COUNT(DISTINCT order_id) AS orders
FROM sales_clean GROUP BY year_month ORDER BY year_month;

-- Q12 | Yearly sales, profit and growth (self-join of yearly totals)
WITH y AS (SELECT order_year, SUM(sales) AS sales, SUM(profit) AS profit FROM sales_clean GROUP BY order_year)
SELECT cur.order_year, ROUND(cur.sales, 2) AS sales, ROUND(cur.profit, 2) AS profit,
       ROUND(cur.profit * 100.0 / cur.sales, 2) AS margin_pct,
       ROUND((cur.sales - prev.sales) * 100.0 / prev.sales, 2) AS sales_growth_pct
FROM y cur LEFT JOIN y prev ON prev.order_year = cur.order_year - 1 ORDER BY cur.order_year;

-- Q13 | Which customers generate the highest sales? (top 10, using JOIN to the customer dimension)
SELECT c.customer_id, c.customer_name, c.segment,
       ROUND(SUM(l.sales), 2) AS sales, ROUND(SUM(l.profit), 2) AS profit,
       COUNT(DISTINCT l.order_id) AS orders
FROM order_lines l
JOIN orders o ON o.order_id = l.order_id
JOIN dim_customer c ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name, c.segment ORDER BY sales DESC LIMIT 10;

-- Q14 | Loss-making states (JOIN order_lines -> orders -> dim_geography)
SELECT g.state, g.region, ROUND(SUM(l.sales), 2) AS sales, ROUND(SUM(l.profit), 2) AS profit,
       ROUND(SUM(l.profit) * 100.0 / SUM(l.sales), 2) AS margin_pct, ROUND(AVG(l.discount), 3) AS avg_discount
FROM order_lines l JOIN orders o ON o.order_id = l.order_id JOIN dim_geography g ON g.geo_id = o.geo_id
GROUP BY g.state, g.region HAVING SUM(l.profit) < 0 ORDER BY profit ASC;

-- Q15 | Region x Category profit matrix (CASE WHEN pivot)
SELECT region,
       ROUND(SUM(CASE WHEN category = 'Furniture' THEN profit ELSE 0 END), 0) AS furniture_profit,
       ROUND(SUM(CASE WHEN category = 'Office Supplies' THEN profit ELSE 0 END), 0) AS office_supplies_profit,
       ROUND(SUM(CASE WHEN category = 'Technology' THEN profit ELSE 0 END), 0) AS technology_profit
FROM sales_clean GROUP BY region ORDER BY region;

-- Q16 | Share of each region's sales made on lines discounted above 20%
SELECT region,
       ROUND(100.0 * SUM(CASE WHEN discount > 0.20 THEN sales ELSE 0 END) / SUM(sales), 1) AS pct_sales_discount_over_20
FROM sales_clean GROUP BY region ORDER BY pct_sales_discount_over_20 DESC;

-- Q17 | Shipping performance by ship mode
SELECT ship_mode, COUNT(*) AS order_lines, ROUND(AVG(shipping_days), 2) AS avg_days,
       MIN(shipping_days) AS min_days, MAX(shipping_days) AS max_days,
       ROUND(SUM(profit) * 100.0 / SUM(sales), 2) AS margin_pct
FROM sales_clean GROUP BY ship_mode ORDER BY avg_days;

-- Q18 | Investigate specific transactions: largest single-line losses (WHERE + ORDER BY)
SELECT order_id, product_name, region, sales, discount, profit
FROM sales_clean WHERE profit < 0 ORDER BY profit ASC LIMIT 10;

-- Q19 | Customers with negative total profit, and the biggest top-sales customer with a loss
SELECT COUNT(*) AS customers_with_loss
FROM (SELECT customer_id FROM sales_clean GROUP BY customer_id HAVING SUM(profit) < 0);

-- Q20 | Binders: profitable overall, but where do the losses sit? (filter + CASE WHEN)
SELECT discount_band, COUNT(*) AS lines, ROUND(SUM(sales), 2) AS sales, ROUND(SUM(profit), 2) AS profit
FROM sales_clean WHERE sub_category = 'Binders' GROUP BY discount_band ORDER BY profit;

-- Q21 | Data-quality check: the one possible duplicate pair (kept and flagged)
SELECT row_id, order_id, product_id, sales, quantity, discount, profit, possible_duplicate
FROM sales_clean
WHERE order_id = 'US-2014-150119' AND product_id = 'FUR-CH-10002965';

-- Q22 | Integrity check: line totals in order_lines equal the flat table (should return 0 difference)
SELECT ROUND((SELECT SUM(sales) FROM order_lines) - (SELECT SUM(sales) FROM sales_clean), 6) AS sales_difference,
       ROUND((SELECT SUM(profit) FROM order_lines) - (SELECT SUM(profit) FROM sales_clean), 6) AS profit_difference;

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
