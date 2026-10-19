"""
Clean the raw sales file without throwing away 40% of it.

The first version of this project dropped every row with any missing value
(1,809 of 3,000 rows kept). This script keeps all rows and recovers what can be
recovered exactly:

* revenue is never missing and always equals
      quantity × unit_price × (1 − discount_percent / 100)   (to the cent)
  so when one of quantity, unit_price or discount_percent is missing it can be
  solved from the other two;
* when two of them are missing, the known constraints are used:
  quantity is a whole number 1-99 and discount is one of 0, 5, 10, 15, 20, 25 %.
  A value is filled in only if exactly one combination fits; otherwise it stays empty;
* category, customer_id and payment_method cannot be derived from other columns,
  so missing values become "Unknown" (the row still counts for revenue).

Every recovered field is listed in the column `recovered`, so nothing is hidden.

Run from the repository root:
    python src/clean_sales.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("data/store_dataset_3000_rows.csv")
OUT = Path("data/sales_clean.csv")
DISCOUNTS = [0, 5, 10, 15, 20, 25]
CENT = 0.0051  # revenue is rounded to cents


def revenue(q, p, d):
    return q * p * (1 - d / 100)


def solve_row(r):
    """Return (quantity, unit_price, discount_percent, recovered_fields) for one row."""
    q, p, d, rev = r["quantity"], r["unit_price"], r["discount_percent"], r["revenue"]
    known = {"quantity": pd.notna(q), "unit_price": pd.notna(p), "discount_percent": pd.notna(d)}
    rec = []

    if all(known.values()):
        return q, p, d, rec

    if not known["quantity"] and known["unit_price"] and known["discount_percent"]:
        qq = round(rev / (p * (1 - d / 100)))
        if 1 <= qq <= 99 and abs(revenue(qq, p, d) - rev) <= CENT:
            q = float(qq); rec.append("quantity")

    elif not known["unit_price"] and known["quantity"] and known["discount_percent"]:
        pp = round(rev / (q * (1 - d / 100)), 2)
        if abs(revenue(q, pp, d) - rev) <= CENT:
            p = pp; rec.append("unit_price")

    elif not known["discount_percent"] and known["quantity"] and known["unit_price"]:
        fits = [x for x in DISCOUNTS if abs(revenue(q, p, x) - rev) <= CENT]
        if len(fits) == 1:
            d = float(fits[0]); rec.append("discount_percent")

    elif not known["quantity"] and not known["discount_percent"] and known["unit_price"]:
        fits = []
        for x in DISCOUNTS:
            qq = round(rev / (p * (1 - x / 100)))
            if 1 <= qq <= 99 and abs(revenue(qq, p, x) - rev) <= CENT:
                fits.append((qq, x))
        if len(fits) == 1:
            q, d = float(fits[0][0]), float(fits[0][1]); rec += ["quantity", "discount_percent"]

    elif not known["unit_price"] and not known["discount_percent"] and known["quantity"]:
        fits = []
        for x in DISCOUNTS:
            pp = round(rev / (q * (1 - x / 100)), 2)
            if 0 < pp and abs(revenue(q, pp, x) - rev) <= CENT:
                fits.append((pp, x))
        if len(fits) == 1:
            p, d = fits[0][0], float(fits[0][1]); rec += ["unit_price", "discount_percent"]

    # quantity + unit_price both missing: infinitely many solutions -> left empty
    return q, p, d, rec


def main():
    raw = pd.read_csv(RAW)
    df = raw.copy()
    df["row_id"] = np.arange(1, len(df) + 1)
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    solved = df.apply(solve_row, axis=1, result_type="expand")
    solved.columns = ["quantity", "unit_price", "discount_percent", "rec"]
    df[["quantity", "unit_price", "discount_percent"]] = solved[["quantity", "unit_price", "discount_percent"]]
    rec_lists = solved["rec"]

    for col in ("category", "customer_id", "payment_method"):
        was_missing = df[col].isna()
        df[col] = df[col].fillna("Unknown")
        rec_lists = [r + ([f"{col}=Unknown"] if m else []) for r, m in zip(rec_lists, was_missing)]
    df["recovered"] = [";".join(r) for r in rec_lists]
    df["numeric_complete"] = df[["quantity", "unit_price", "discount_percent"]].notna().all(axis=1)

    # sanity check: every complete row still reproduces its revenue
    c = df[df["numeric_complete"]]
    err = (revenue(c["quantity"], c["unit_price"], c["discount_percent"]) - c["revenue"]).abs().max()
    assert err <= CENT, f"revenue check failed ({err})"

    cols = ["row_id", "store_id", "product_id", "product_name", "category", "quantity", "unit_price",
            "discount_percent", "customer_id", "transaction_date", "payment_method", "revenue",
            "numeric_complete", "recovered"]
    df[cols].to_csv(OUT, index=False)

    # report
    before = raw.dropna()
    n_num_missing = raw[["quantity", "unit_price", "discount_percent"]].isna().any(axis=1).sum()
    n_num_fixed = (~raw[["quantity", "unit_price", "discount_percent"]].notna().all(axis=1)
                   & df["numeric_complete"]).sum()
    print(f"Rows: {len(raw)}  |  complete in raw file: {len(before)} ({len(before) / len(raw):.1%})")
    print(f"Rows with a missing number: {n_num_missing}, recovered exactly: {n_num_fixed}, "
          f"left empty (ambiguous): {n_num_missing - n_num_fixed}")
    print(f"Revenue, complete rows only: €{before['revenue'].sum():,.2f}")
    print(f"Revenue, all rows:           €{df['revenue'].sum():,.2f}")
    print(f"Orders: {len(before)} -> {len(df)}  |  AOV: €{before['revenue'].mean():,.2f} -> €{df['revenue'].mean():,.2f}")
    print(f"✓ {OUT}")


if __name__ == "__main__":
    main()
