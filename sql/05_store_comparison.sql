-- Store comparison: revenue, share, average order value, average discount and
-- each store's best month.

WITH store_month AS (
    SELECT f.store_id, d.month_label, SUM(f.revenue) AS revenue
    FROM fact_sales f
    JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY f.store_id, d.month_label
),
best_month AS (
    SELECT store_id, month_label, revenue,
           ROW_NUMBER() OVER (PARTITION BY store_id ORDER BY revenue DESC) AS rn
    FROM store_month
)
SELECT
    f.store_id,
    COUNT(*)                                              AS orders,
    ROUND(SUM(f.revenue), 2)                              AS revenue_eur,
    ROUND(100.0 * SUM(f.revenue) / (SELECT SUM(revenue) FROM fact_sales), 1) AS share_pct,
    ROUND(AVG(f.revenue), 2)                              AS avg_order_value_eur,
    ROUND(AVG(f.discount_percent), 1)                     AS avg_discount_pct,
    b.month_label                                         AS best_month,
    ROUND(b.revenue, 2)                                   AS best_month_revenue_eur
FROM fact_sales f
JOIN best_month b ON b.store_id = f.store_id AND b.rn = 1
GROUP BY f.store_id, b.month_label, b.revenue
ORDER BY revenue_eur DESC;
