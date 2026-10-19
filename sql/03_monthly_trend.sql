-- Monthly revenue with month-over-month change and running total (window functions).

WITH monthly AS (
    SELECT d.month_label,
           COUNT(*)            AS orders,
           SUM(f.revenue)      AS revenue
    FROM fact_sales f
    JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY d.month_label
)
SELECT
    month_label,
    orders,
    ROUND(revenue, 2)                                                    AS revenue_eur,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month_label))
          / LAG(revenue) OVER (ORDER BY month_label), 1)                 AS mom_change_pct,
    ROUND(SUM(revenue) OVER (ORDER BY month_label), 2)                   AS running_total_eur,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 1)                     AS share_of_year_pct
FROM monthly
ORDER BY month_label;
