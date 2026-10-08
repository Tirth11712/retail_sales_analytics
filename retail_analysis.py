"""
Micro Project : Retail Store Sales Analytics
Tools         : Python, NumPy, Pandas, Matplotlib, Seaborn
Modules       : 1. Sales Record Parsing      2. Product & Region Aggregation
                3. Revenue Heatmap & Trends  4. Retail Strategy & Stocking Insights
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

DATA_FILE = "retail_sales.csv"
OUT_DIR = "outputs"
os.makedirs(OUT_DIR, exist_ok=True)
sns.set_theme(style="whitegrid", font_scale=0.95)
pd.set_option("display.width", 120)
pd.set_option("display.float_format", lambda v: f"{v:,.2f}")


class Tee:
    """Send everything printed to both the screen and outputs/console_output.txt."""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)

    def flush(self):
        for s in self.streams:
            s.flush()


def banner(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


# ---------------------------------------------------------------------
# STEP 1 : SALES RECORD PARSING
# ---------------------------------------------------------------------
def load_and_clean(path):
    banner("STEP 1 : SALES RECORD PARSING")
    df = pd.read_csv(path)
    print(f"Raw records loaded        : {len(df)}")
    print(f"Columns                   : {list(df.columns)}")

    dupes = df.duplicated(subset="TransactionID").sum()
    df = df.drop_duplicates(subset="TransactionID")
    print(f"Duplicate rows removed    : {dupes}")

    print(f"Missing values found      : {df.isna().sum().to_dict()}")
    df["UnitsSold"] = df["UnitsSold"].fillna(df.groupby("Product")["UnitsSold"].transform("median"))
    df["Discount"] = df["Discount"].fillna(0.0)

    df["OrderDate"] = pd.to_datetime(df["OrderDate"])
    df["Month"] = df["OrderDate"].dt.month
    df["MonthName"] = df["OrderDate"].dt.strftime("%b")
    df["Quarter"] = "Q" + df["OrderDate"].dt.quarter.astype(str)
    df["UnitsSold"] = df["UnitsSold"].astype(int)

    # Vectorised revenue computation with NumPy
    df["TotalRevenue"] = np.round(df["UnitsSold"] * df["UnitPrice"] * (1 - df["Discount"]), 2)
    df["DiscountLoss"] = np.round(df["UnitsSold"] * df["UnitPrice"] * df["Discount"], 2)

    print(f"Clean records             : {len(df)}")
    print(f"Date range                : {df['OrderDate'].min().date()} to {df['OrderDate'].max().date()}")
    print("\nSample of parsed records:")
    print(df[["TransactionID", "OrderDate", "Region", "Category", "Product",
              "UnitsSold", "Discount", "Quarter", "TotalRevenue"]].head(6).to_string(index=False))
    return df


# ---------------------------------------------------------------------
# STEP 2 : PRODUCT & REGION AGGREGATION
# ---------------------------------------------------------------------
def aggregate(df):
    banner("STEP 2 : PRODUCT & REGION AGGREGATION")
    total = df["TotalRevenue"].sum()
    print(f"Total Revenue             : Rs. {total:,.2f}")
    print(f"Total Units Sold          : {df['UnitsSold'].sum():,}")
    print(f"Average Order Value       : Rs. {df['TotalRevenue'].mean():,.2f}")
    print(f"Revenue lost to discounts : Rs. {df['DiscountLoss'].sum():,.2f}")

    region = df.groupby("Region")["TotalRevenue"].sum().sort_values(ascending=False).to_frame()
    region["MarketShare_%"] = region["TotalRevenue"] / total * 100
    print("\nRegional Revenue & Market Share:")
    print(region.to_string())

    category = df.groupby("Category").agg(Revenue=("TotalRevenue", "sum"),
                                          Units=("UnitsSold", "sum"),
                                          Orders=("TransactionID", "count")).sort_values("Revenue", ascending=False)
    category["Share_%"] = category["Revenue"] / total * 100
    print("\nCategory Performance:")
    print(category.to_string())

    products = df.groupby(["Category", "Product"]).agg(Revenue=("TotalRevenue", "sum"),
                                                        Units=("UnitsSold", "sum")).sort_values("Revenue", ascending=False)
    print("\nTop 10 Best-Selling Products (by revenue):")
    print(products.head(10).to_string())

    monthly_sales = df.groupby([df["OrderDate"].dt.month, "Category"])["TotalRevenue"].sum().unstack()
    monthly_sales.index.name = "Month"
    quarterly = df.groupby("Quarter")["TotalRevenue"].sum()
    print("\nQuarterly Revenue:")
    print(quarterly.to_string())
    return region, category, products, monthly_sales


# ---------------------------------------------------------------------
# STEP 3 : REVENUE HEATMAP & TREND CHARTS
# ---------------------------------------------------------------------
def visualize(df, region, category, products, monthly_sales):
    banner("STEP 3 : REVENUE HEATMAP & TREND CHARTS")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # 3.1 Multi-line monthly trend per category
    fig, ax = plt.subplots(figsize=(10, 5))
    for col in monthly_sales.columns:
        ax.plot(monthly_sales.index, monthly_sales[col] / 1e5, marker="o", linewidth=2, label=col)
    ax.set_xticks(range(1, 13)); ax.set_xticklabels(months)
    ax.set_title("Monthly Revenue Trend by Category (2025)", fontweight="bold")
    ax.set_ylabel("Revenue (Rs. lakh)"); ax.legend(ncol=3, fontsize=8)
    fig.tight_layout(); fig.savefig(f"{OUT_DIR}/01_monthly_trend.png", dpi=150); plt.close(fig)

    # 3.2 Total monthly revenue with month-over-month growth
    total_m = monthly_sales.sum(axis=1)
    growth = total_m.pct_change() * 100
    fig, ax = plt.subplots(figsize=(10, 4.5))
    bars = ax.bar(months, total_m / 1e5, color=sns.color_palette("Blues_d", 12))
    for b, g in zip(bars, growth):
        if not np.isnan(g):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{g:+.0f}%", ha="center", va="bottom", fontsize=8)
    ax.set_title("Total Monthly Revenue with Month-over-Month Growth", fontweight="bold")
    ax.set_ylabel("Revenue (Rs. lakh)")
    fig.tight_layout(); fig.savefig(f"{OUT_DIR}/02_monthly_total.png", dpi=150); plt.close(fig)

    # 3.3 Region x Category heatmap (values in Rs. lakh)
    pivot = df.pivot_table(index="Region", columns="Category", values="TotalRevenue", aggfunc="sum") / 1e5
    fig, ax = plt.subplots(figsize=(9, 4.5))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlOrRd", linewidths=0.5, ax=ax,
                cbar_kws={"label": "Revenue (Rs. lakh)"})
    ax.set_title("Regional Category Sales Heatmap (Rs. lakh)", fontweight="bold")
    fig.tight_layout(); fig.savefig(f"{OUT_DIR}/03_region_category_heatmap.png", dpi=150); plt.close(fig)

    # 3.4 Month x Region heatmap (seasonality)
    pivot2 = df.pivot_table(index="Region", columns="Month", values="TotalRevenue", aggfunc="sum") / 1e5
    pivot2.columns = months
    fig, ax = plt.subplots(figsize=(10, 3.8))
    sns.heatmap(pivot2, annot=True, fmt=".1f", cmap="Blues", linewidths=0.5, ax=ax,
                cbar_kws={"label": "Rs. lakh"})
    ax.set_title("Seasonal Revenue Heatmap: Region x Month (Rs. lakh)", fontweight="bold")
    fig.tight_layout(); fig.savefig(f"{OUT_DIR}/04_region_month_heatmap.png", dpi=150); plt.close(fig)

    # 3.5 Top 10 products & regional market share
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), gridspec_kw={"width_ratios": [1.6, 1]})
    top10 = products.head(10).reset_index()
    sns.barplot(data=top10, y="Product", x=top10["Revenue"] / 1e5, hue="Category", dodge=False, ax=axes[0])
    axes[0].set_xlabel("Revenue (Rs. lakh)"); axes[0].set_ylabel("")
    axes[0].set_title("Top 10 Products by Revenue", fontweight="bold"); axes[0].legend(fontsize=7)
    axes[1].pie(region["TotalRevenue"], labels=region.index, autopct="%1.1f%%", startangle=90,
                colors=sns.color_palette("Set2"), wedgeprops={"edgecolor": "white"})
    axes[1].set_title("Regional Market Share", fontweight="bold")
    fig.tight_layout(); fig.savefig(f"{OUT_DIR}/05_top_products_region_share.png", dpi=150); plt.close(fig)

    for f in sorted(os.listdir(OUT_DIR)):
        if f.endswith(".png") and f[0].isdigit():
            print(f"Chart saved -> {OUT_DIR}/{f}")
    peak = total_m.idxmax()
    print(f"\nPeak month   : {months[peak-1]} (Rs. {total_m.max():,.0f})")
    print(f"Lowest month : {months[total_m.idxmin()-1]} (Rs. {total_m.min():,.0f})")
    return total_m


# ---------------------------------------------------------------------
# STEP 4 : RETAIL STRATEGY & STOCKING INSIGHTS
# ---------------------------------------------------------------------
def stocking_insights(df):
    banner("STEP 4 : RETAIL STRATEGY & STOCKING INSIGHTS")
    # current stock = last recorded StockOnHand of each product at each branch
    last = df.sort_values("OrderDate").groupby(["Region", "Product"]).tail(1)
    stock = last.groupby(["Region", "Product"])["StockOnHand"].sum()

    q4 = df[df["Quarter"] == "Q4"]
    demand = q4.groupby(["Region", "Product"])["UnitsSold"].sum() / 3   # avg monthly units in peak quarter
    revenue = df.groupby(["Region", "Product"])["TotalRevenue"].sum()

    inv = pd.DataFrame({"CurrentStock": stock, "AvgMonthlyDemand": demand, "Revenue": revenue}).dropna()
    inv["MonthsOfCover"] = inv["CurrentStock"] / inv["AvgMonthlyDemand"]
    # best-seller = top 30% revenue within its region
    inv["RevenueRank_pct"] = inv.groupby(level="Region")["Revenue"].rank(pct=True)
    inv["BestSeller"] = inv["RevenueRank_pct"] >= 0.70
    safety = 1.5   # months of stock to hold for best-sellers
    inv["ReorderQty"] = np.ceil(np.maximum(0, safety * inv["AvgMonthlyDemand"] - inv["CurrentStock"])).astype(int)

    def status(r):
        if r.BestSeller and r.MonthsOfCover < 1.0:
            return "CRITICAL - Reorder now"
        if r.BestSeller and r.MonthsOfCover < safety:
            return "LOW - Reorder soon"
        if r.MonthsOfCover > 6:
            return "OVERSTOCK - Run promotion"
        return "OK"
    inv["Status"] = inv.apply(status, axis=1)

    alert = inv[inv["Status"].str.startswith(("CRITICAL", "LOW"))].sort_values("MonthsOfCover")
    print("Replenishment alerts for low-inventory best-sellers:")
    print(alert[["CurrentStock", "AvgMonthlyDemand", "MonthsOfCover", "ReorderQty", "Status"]].to_string())
    over = inv[inv["Status"].str.startswith("OVERSTOCK")]
    print(f"\nOverstocked SKUs (>6 months cover): {len(over)}")
    print(over[["CurrentStock", "AvgMonthlyDemand", "MonthsOfCover"]].head(8).to_string())
    print("\nStock status summary:")
    print(inv["Status"].value_counts().to_string())

    inv.reset_index().to_csv(f"{OUT_DIR}/stock_recommendations.csv", index=False)
    print(f"\nFull table saved -> {OUT_DIR}/stock_recommendations.csv")

    # chart: months of cover for best-sellers
    bs = inv[inv["BestSeller"]].sort_values("MonthsOfCover").head(15).reset_index()
    bs["Label"] = bs["Product"] + " (" + bs["Region"] + ")"
    colors = ["#d62728" if m < 1 else "#ff7f0e" if m < safety else "#2ca02c" for m in bs["MonthsOfCover"]]
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.barh(bs["Label"], bs["MonthsOfCover"], color=colors)
    ax.axvline(1.0, color="#d62728", ls="--", lw=1, label="Critical (1 month)")
    ax.axvline(safety, color="#ff7f0e", ls="--", lw=1, label=f"Safety stock ({safety} months)")
    ax.invert_yaxis(); ax.set_xlabel("Months of stock cover at peak-season demand")
    ax.set_title("Inventory Cover of Best-Selling Products (lowest 15)", fontweight="bold"); ax.legend()
    fig.tight_layout(); fig.savefig(f"{OUT_DIR}/06_stock_cover.png", dpi=150); plt.close(fig)
    print(f"Chart saved -> {OUT_DIR}/06_stock_cover.png")
    return inv, alert


def business_summary(df, region, category, products, total_m, alert):
    banner("BUSINESS INSIGHTS SUMMARY")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    top_p = products.index[0][1]
    festive = total_m.loc[[10, 11]].sum() / total_m.sum() * 100
    lines = [
        f"1. {region.index[0]} is the strongest region ({region['MarketShare_%'].iloc[0]:.1f}% share); "
        f"{region.index[-1]} is the weakest ({region['MarketShare_%'].iloc[-1]:.1f}%).",
        f"2. {category.index[0]} generates the most revenue ({category['Share_%'].iloc[0]:.1f}% of total).",
        f"3. Best-selling product overall: {top_p} (Rs. {products['Revenue'].iloc[0]:,.0f}).",
        f"4. Peak month is {months[total_m.idxmax()-1]}; Oct+Nov festive season = {festive:.1f}% of annual revenue.",
        f"5. {len(alert)} best-seller/branch combinations need replenishment before the next peak.",
    ]
    for l in lines:
        print(l)


def main():
    if not os.path.exists(DATA_FILE):
        sys.exit(f"'{DATA_FILE}' not found. Run:  python generate_dataset.py  first.")
    data = load_and_clean(DATA_FILE)
    reg, cat, prod, monthly = aggregate(data)
    tot = visualize(data, reg, cat, prod, monthly)
    inventory, alerts = stocking_insights(data)
    business_summary(data, reg, cat, prod, tot, alerts)
    print("\nAnalysis complete.")


if __name__ == "__main__":
    # Mirror console output into outputs/console_output.txt
    log = open(f"{OUT_DIR}/console_output.txt", "w", encoding="utf-8")
    original_stdout = sys.stdout
    sys.stdout = Tee(original_stdout, log)
    try:
        main()
    finally:
        sys.stdout = original_stdout
        log.close()
