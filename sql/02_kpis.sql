-- Headline KPIs: all rows vs. only the rows the first version kept (no missing value at all).

SELECT
    'all rows'                                   AS scope,
    COUNT(*)                                     AS orders,
    ROUND(SUM(revenue), 2)                       AS revenue_eur,
    ROUND(AVG(revenue), 2)                       AS avg_order_value_eur,
    COUNT(DISTINCT NULLIF(customer_id, 'Unknown')) AS known_customers
FROM fact_sales

UNION ALL

SELECT
    'complete rows only (v1)',
    COUNT(*),
    ROUND(SUM(revenue), 2),
    ROUND(AVG(revenue), 2),
    COUNT(DISTINCT customer_id)
FROM fact_sales
WHERE (recovered IS NULL OR recovered = '') AND numeric_complete = 1;
