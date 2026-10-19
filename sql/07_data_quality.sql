-- Data quality checks.

-- 1) Does each product always carry the same category?
--    In a clean master-data setup this returns 1 category per product.
SELECT p.product_name,
       COUNT(DISTINCT f.category_label)                   AS distinct_categories,
       GROUP_CONCAT(DISTINCT f.category_label)            AS categories_seen
FROM fact_sales f
JOIN dim_product p ON p.product_key = f.product_key
WHERE f.category_label <> 'Unknown'
GROUP BY p.product_name
ORDER BY distinct_categories DESC, p.product_name;

-- 2) How widely does the unit price of the same product vary?
SELECT p.product_name,
       ROUND(MIN(f.unit_price), 2) AS min_price_eur,
       ROUND(MAX(f.unit_price), 2) AS max_price_eur,
       ROUND(AVG(f.unit_price), 2) AS avg_price_eur
FROM fact_sales f
JOIN dim_product p ON p.product_key = f.product_key
WHERE f.unit_price IS NOT NULL
GROUP BY p.product_name
ORDER BY p.product_name;

-- 3) What was recovered, and what is still missing?
SELECT 'rows'                                   AS item, COUNT(*) AS n FROM fact_sales
UNION ALL SELECT 'recovered quantity',          COUNT(*) FROM fact_sales WHERE recovered LIKE '%quantity%'
UNION ALL SELECT 'recovered unit_price',        COUNT(*) FROM fact_sales WHERE recovered LIKE '%unit_price%'
UNION ALL SELECT 'recovered discount_percent',  COUNT(*) FROM fact_sales WHERE recovered LIKE '%discount_percent%'
UNION ALL SELECT 'numbers still missing',       COUNT(*) FROM fact_sales WHERE numeric_complete = 0
UNION ALL SELECT 'customer Unknown',            COUNT(*) FROM fact_sales WHERE customer_id = 'Unknown'
UNION ALL SELECT 'payment Unknown',             COUNT(*) FROM fact_sales WHERE payment_method = 'Unknown'
UNION ALL SELECT 'category Unknown',            COUNT(*) FROM fact_sales WHERE category_label = 'Unknown';
