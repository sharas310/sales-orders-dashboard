-- Star schema for the sales data (SQLite).
-- One fact table with one row per transaction, five small dimension tables.

DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_store;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_payment;

CREATE TABLE dim_store (
    store_id      TEXT PRIMARY KEY
);

CREATE TABLE dim_product (
    product_key   INTEGER PRIMARY KEY,
    product_name  TEXT NOT NULL UNIQUE
);

CREATE TABLE dim_customer (
    customer_id   TEXT PRIMARY KEY          -- 'Unknown' when missing in the source
);

CREATE TABLE dim_payment (
    payment_method TEXT PRIMARY KEY         -- 'Unknown' when missing in the source
);

CREATE TABLE dim_date (
    date_key      TEXT PRIMARY KEY,         -- YYYY-MM-DD
    year          INTEGER NOT NULL,
    month         INTEGER NOT NULL,
    month_label   TEXT NOT NULL,            -- YYYY-MM
    quarter       INTEGER NOT NULL,
    weekday       INTEGER NOT NULL          -- 0 = Sunday ... 6 = Saturday (SQLite %w)
);

CREATE TABLE fact_sales (
    row_id            INTEGER PRIMARY KEY,
    date_key          TEXT    NOT NULL REFERENCES dim_date(date_key),
    store_id          TEXT    NOT NULL REFERENCES dim_store(store_id),
    product_key       INTEGER NOT NULL REFERENCES dim_product(product_key),
    customer_id       TEXT    NOT NULL REFERENCES dim_customer(customer_id),
    payment_method    TEXT    NOT NULL REFERENCES dim_payment(payment_method),
    category_label    TEXT    NOT NULL,     -- as recorded; see 07_data_quality.sql before using it
    quantity          INTEGER,              -- NULL only where it could not be recovered
    unit_price        REAL,
    discount_percent  REAL,
    revenue           REAL    NOT NULL,     -- never missing in the source
    numeric_complete  INTEGER NOT NULL,     -- 1 = quantity, price and discount all known
    recovered         TEXT                  -- fields filled in by src/clean_sales.py
);

CREATE INDEX ix_fact_date    ON fact_sales(date_key);
CREATE INDEX ix_fact_product ON fact_sales(product_key);
CREATE INDEX ix_fact_store   ON fact_sales(store_id);
