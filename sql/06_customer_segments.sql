-- Simple RFM-style segmentation of known customers.
-- Recency = days between the last purchase and 31 Dec 2024, frequency = orders, monetary = revenue.
-- Each dimension is split into quartiles with NTILE(4); 4 = best.

WITH c AS (
    SELECT customer_id,
           CAST(julianday('2024-12-31') - julianday(MAX(date_key)) AS INTEGER) AS recency_days,
           COUNT(*)      AS orders,
           SUM(revenue)  AS revenue
    FROM fact_sales
    WHERE customer_id <> 'Unknown'
    GROUP BY customer_id
),
scored AS (
    SELECT *,
           NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score,
           NTILE(4) OVER (ORDER BY orders)            AS f_score,
           NTILE(4) OVER (ORDER BY revenue)           AS m_score
    FROM c
),
segmented AS (
    SELECT *,
           CASE
               WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'Champions'
               WHEN r_score >= 3 AND m_score >= 3                  THEN 'High value, recent'
               WHEN r_score <= 2 AND m_score >= 3                  THEN 'High value, at risk'
               WHEN r_score >= 3                                   THEN 'Recent, low value'
               ELSE 'Low value, inactive'
           END AS segment
    FROM scored
)
SELECT segment,
       COUNT(*)                                             AS customers,
       ROUND(AVG(orders), 2)                                AS avg_orders,
       ROUND(AVG(recency_days), 0)                          AS avg_recency_days,
       ROUND(SUM(revenue), 2)                               AS revenue_eur,
       ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1) AS share_pct
FROM segmented
GROUP BY segment
ORDER BY revenue_eur DESC;
