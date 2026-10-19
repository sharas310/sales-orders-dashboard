"""
Charts for the README, drawn from the query results in sql/results/.

Run from the repository root (after src/build_db.py):
    python src/charts.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

R = Path("sql/results")
OUT = Path("images")
BLUE, GREY, INK, MUTED, SURFACE = "#2a78d6", "#b9b8b1", "#0b0b0b", "#52514e", "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": MUTED,
    "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 10,
})


def eur_m(x, _=None):
    return f"€{x / 1e6:.1f}M"


def monthly():
    """Revenue per month: complete rows only (v1) vs. all rows (v2)."""
    raw = pd.read_csv("data/sales_clean.csv", parse_dates=["transaction_date"])
    raw["month"] = raw["transaction_date"].dt.strftime("%b")
    v1_mask = raw["recovered"].isna() & raw["numeric_complete"]
    order = pd.date_range("2024-01-01", periods=12, freq="MS").strftime("%b")
    v1 = raw[v1_mask].groupby("month")["revenue"].sum().reindex(order)
    v2 = raw.groupby("month")["revenue"].sum().reindex(order)

    fig, ax = plt.subplots(figsize=(9, 4.2))
    x = range(12)
    ax.bar([i - 0.2 for i in x], v1, 0.38, color=GREY, label="v1: complete rows only (1,809)")
    ax.bar([i + 0.2 for i in x], v2, 0.38, color=BLUE, label="v2: all rows (3,000)")
    ax.set_xticks(list(x), order)
    ax.yaxis.set_major_formatter(eur_m)
    ax.grid(axis="y", color="#e6e5e0", lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title("Monthly revenue: dropping incomplete rows hid 40% of it", loc="left", fontsize=12)
    ax.legend(frameon=False, loc="upper left", ncol=2)
    ax.set_ylim(0, v2.max() * 1.2)
    fig.tight_layout()
    fig.savefig(OUT / "monthly_revenue_v1_vs_v2.png", dpi=150)


def products():
    p = pd.read_csv(R / "04_pareto_products.csv").sort_values("share_pct")
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.barh(p["product_name"], p["share_pct"], color=BLUE, height=0.7)
    ax.axvline(5, color=MUTED, lw=1, ls="--", zorder=0)
    ax.text(5.05, -0.9, "equal share (5%)", color=MUTED, fontsize=9)
    for y, v in enumerate(p["share_pct"]):
        ax.text(v - 0.08, y, f"{v:.1f}%", va="center", ha="right", fontsize=8, color="white")
    ax.set_xlabel("Share of revenue, %")
    ax.set_xlim(0, p["share_pct"].max() * 1.15)
    ax.set_title("Revenue by product: no Pareto effect, top 5 = 28.5%", loc="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "products_share.png", dpi=150)


def segments():
    s = pd.read_csv(R / "06_customer_segments.csv").sort_values("share_pct")
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    ax.barh(s["segment"], s["share_pct"], color=BLUE, height=0.6)
    for y, (v, c) in enumerate(zip(s["share_pct"], s["customers"])):
        ax.text(v + 0.6, y, f"{v:.1f}% of revenue · {c} customers", va="center", fontsize=9, color=MUTED)
    ax.set_xlim(0, s["share_pct"].max() * 1.7)
    ax.set_xlabel("Share of revenue, %")
    ax.set_title("RFM segments: a quarter of customers bring 45% of revenue", loc="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "customer_segments.png", dpi=150)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    monthly()
    products()
    segments()
    print("✓ images/monthly_revenue_v1_vs_v2.png, images/products_share.png, images/customer_segments.png")
