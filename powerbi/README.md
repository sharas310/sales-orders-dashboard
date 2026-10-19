# Power BI report: build guide

The CSV files in this folder are a ready star schema, exported by `src/build_db.py`.
Building the report takes about 30–45 minutes in Power BI Desktop (free, Windows).

## 1. Load the data

*Home → Get data → Text/CSV*, load all six files:

| File | Role |
|---|---|
| `fact_sales.csv` | one row per transaction (3,000) |
| `dim_date.csv` | calendar 2024 |
| `dim_product.csv` | 20 products |
| `dim_store.csv` | 5 stores |
| `dim_customer.csv` | 931 customers + "Unknown" |
| `dim_payment.csv` | 5 methods + "Unknown" |

In Power Query, check the types: `date_key` as **Text** in both tables, then add a column
`date = Date.FromText([date_key])` to `dim_date` (type Date). `revenue`, `unit_price` and
`discount_percent` are Decimal numbers, `quantity` is Whole number.

## 2. Model

*Model view*, create these relationships (many-to-one, single direction, from fact to dimension):

```
fact_sales[date_key]       → dim_date[date_key]
fact_sales[product_key]    → dim_product[product_key]
fact_sales[store_id]       → dim_store[store_id]
fact_sales[customer_id]    → dim_customer[customer_id]
fact_sales[payment_method] → dim_payment[payment_method]
```

Mark `dim_date` as date table (*Table tools → Mark as date table → date*).
Hide the key columns in the fact table so report users only see dimensions.

## 3. Measures

Paste the measures from [`measures.dax`](measures.dax) into `fact_sales`.

## 4. Report pages

**Page 1 · Overview**
- KPI cards: Revenue, Orders, Avg Order Value, Known Customers
- Card: *Revenue hidden by dropna %* (≈ 40 %), titled "Revenue missed by the first version"
- Column chart: Revenue by `dim_date[month_label]`, tooltip with *Revenue MoM %*
- Slicers: store, payment method

**Page 2 · Products & stores**
- Bar chart: Revenue by product, sorted, with a constant line at 5 % share
- Matrix: store × month, Revenue, conditional formatting (background colour scale)
- Table: store, Orders, Revenue, Avg Order Value, Avg Discount %

**Page 3 · Data quality**
- Card: *Recovered Rows*
- Table from `sql/results/07_data_quality_1.csv`: each product appears with 5 different categories
- Short text box: why the category field is not used for analysis

## 5. Export for the portfolio

Save as `powerbi/sales_report.pbix` and add a screenshot of each page to `images/powerbi_*.png`.
Then link the screenshots in the main README.
