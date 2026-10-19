"""
Load data/sales_clean.csv into a SQLite star schema, run every query in sql/
and export the tables Power BI needs.

Run from the repository root (after src/clean_sales.py):
    python src/build_db.py

Creates:
    data/sales.db              SQLite database (open it with DB Browser for SQLite or DBeaver)
    sql/results/*.csv          output of each analysis query
    powerbi/*.csv              fact and dimension tables for Power BI
"""
import re
import sqlite3
from pathlib import Path

import pandas as pd

CLEAN = Path("data/sales_clean.csv")
DB = Path("data/sales.db")
SQL = Path("sql")
RESULTS = SQL / "results"
PBI = Path("powerbi")


def split_statements(text: str) -> list[str]:
    no_comments = re.sub(r"--[^\n]*", "", text)
    return [s.strip() for s in no_comments.split(";") if s.strip()]


def main():
    df = pd.read_csv(CLEAN, parse_dates=["transaction_date"])
    df["date_key"] = df["transaction_date"].dt.strftime("%Y-%m-%d")
    df["recovered"] = df["recovered"].fillna("")

    DB.unlink(missing_ok=True)
    con = sqlite3.connect(DB)
    con.executescript((SQL / "01_schema.sql").read_text(encoding="utf-8"))

    products = pd.DataFrame({"product_name": sorted(df["product_name"].unique())})
    products["product_key"] = range(1, len(products) + 1)
    df = df.merge(products, on="product_name")

    dates = pd.DataFrame({"d": pd.date_range(df["transaction_date"].min(), df["transaction_date"].max())})
    dim_date = pd.DataFrame({
        "date_key": dates["d"].dt.strftime("%Y-%m-%d"),
        "year": dates["d"].dt.year,
        "month": dates["d"].dt.month,
        "month_label": dates["d"].dt.strftime("%Y-%m"),
        "quarter": dates["d"].dt.quarter,
        "weekday": (dates["d"].dt.dayofweek + 1) % 7,  # same convention as SQLite %w
    })

    tables = {
        "dim_store": pd.DataFrame({"store_id": sorted(df["store_id"].unique())}),
        "dim_product": products[["product_key", "product_name"]],
        "dim_customer": pd.DataFrame({"customer_id": sorted(df["customer_id"].unique())}),
        "dim_payment": pd.DataFrame({"payment_method": sorted(df["payment_method"].unique())}),
        "dim_date": dim_date,
        "fact_sales": df.rename(columns={"category": "category_label"})[
            ["row_id", "date_key", "store_id", "product_key", "customer_id", "payment_method",
             "category_label", "quantity", "unit_price", "discount_percent", "revenue",
             "numeric_complete", "recovered"]].assign(
                quantity=lambda x: x["quantity"].astype("Int64"),
                numeric_complete=lambda x: x["numeric_complete"].astype(int)),
    }
    for name, t in tables.items():
        t.to_sql(name, con, if_exists="append", index=False)
    con.commit()
    print(f"✓ {DB}: " + ", ".join(f"{k} {len(v)}" for k, v in tables.items()))

    RESULTS.mkdir(parents=True, exist_ok=True)
    for f in sorted(SQL.glob("0*.sql")):
        if f.name.startswith("01_"):
            continue
        for i, stmt in enumerate(split_statements(f.read_text(encoding="utf-8")), 1):
            res = pd.read_sql_query(stmt, con)
            suffix = f"_{i}" if len(split_statements(f.read_text(encoding="utf-8"))) > 1 else ""
            out = RESULTS / f"{f.stem}{suffix}.csv"
            res.to_csv(out, index=False)
            print(f"\n── {f.name}{suffix} ──")
            print(res.head(25).to_string(index=False))

    PBI.mkdir(exist_ok=True)
    for name, t in tables.items():
        t.to_csv(PBI / f"{name}.csv", index=False)
    print(f"\n✓ Power BI tables in {PBI}/")
    con.close()


if __name__ == "__main__":
    main()
