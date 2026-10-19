-- Pareto view of products: rank, share and cumulative share of revenue.

WITH by_product AS (
    SELECT p.product_name,
           COUNT(*)        AS orders,
           SUM(f.revenue)  AS revenue
    FROM fact_sales f
    JOIN dim_product p ON p.product_key = f.product_key
    GROUP BY p.product_name
)
SELECT
    RANK() OVER (ORDER BY revenue DESC)                                        AS rank,
    product_name,
    orders,
    ROUND(revenue, 2)                                                          AS revenue_eur,
    ROUND(100.0 * revenue / SUM(revenue) OVER (), 1)                           AS share_pct,
    ROUND(100.0 * SUM(revenue) OVER (ORDER BY revenue DESC
                                     ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
          / SUM(revenue) OVER (), 1)                                           AS cumulative_share_pct
FROM by_product
ORDER BY revenue DESC;
