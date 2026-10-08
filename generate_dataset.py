"""generate_dataset.py - Creates retail_sales.csv (synthetic, realistic retail transactions)."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 2400
regions = ["North", "South", "East", "West"]
region_w = [0.30, 0.22, 0.20, 0.28]
catalog = {
    "Electronics": {"Smartphone": 18000, "Laptop": 52000, "Headphones": 2500, "Smart Watch": 8500},
    "Clothing":    {"Jeans": 1800, "T-Shirt": 600, "Jacket": 3200, "Saree": 2600},
    "Furniture":   {"Office Chair": 7500, "Study Table": 9800, "Bookshelf": 5400, "Sofa": 32000},
    "Groceries":   {"Rice 10kg": 650, "Cooking Oil 5L": 780, "Tea 1kg": 520, "Dry Fruits": 1200},
    "Home Appliances": {"Mixer Grinder": 3400, "Microwave": 9200, "Air Cooler": 8800, "Iron": 1300},
}
# seasonal multipliers per month (festive Oct-Nov, summer for coolers, year-end sale Dec)
season = {1:0.85,2:0.80,3:0.90,4:1.00,5:1.10,6:0.95,7:0.85,8:0.95,9:1.05,10:1.45,11:1.40,12:1.20}
dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
w = np.array([season[d.month] for d in dates]); w = w / w.sum()

rows = []
for i in range(N):
    d = dates[rng.choice(len(dates), p=w)]
    region = rng.choice(regions, p=region_w)
    cat = rng.choice(list(catalog), p=[0.24, 0.26, 0.14, 0.22, 0.14])
    prod = rng.choice(list(catalog[cat]))
    base = catalog[cat][prod]
    if prod == "Air Cooler" and d.month in (4, 5, 6):
        units = int(rng.integers(3, 12))
    elif cat == "Groceries":
        units = int(rng.integers(5, 30))
    elif cat == "Clothing":
        units = int(rng.integers(2, 15))
    else:
        units = int(rng.integers(1, 6))
    price = round(base * rng.uniform(0.92, 1.08), 2)
    disc = rng.choice([0.0, 0.02, 0.05, 0.10, 0.15, 0.20],
                      p=[0.30, 0.15, 0.25, 0.18, 0.08, 0.04] if d.month not in (10, 11) else [0.10, 0.10, 0.20, 0.30, 0.20, 0.10])
    stock = int(rng.integers(5, 120))
    rows.append([f"TRX-{i+1:04d}", d.date(), region, cat, prod, price, units, disc, stock])

df = pd.DataFrame(rows, columns=["TransactionID", "OrderDate", "Region", "Category", "Product",
                                 "UnitPrice", "UnitsSold", "Discount", "StockOnHand"])
df = df.sort_values("OrderDate").reset_index(drop=True)
df["TransactionID"] = [f"TRX-{i+1:04d}" for i in range(len(df))]
# inject a few dirty records to demonstrate cleaning
df.loc[[15, 340, 901], "UnitsSold"] = np.nan
df.loc[[77], "Discount"] = np.nan
df = pd.concat([df, df.iloc[[100, 200]]], ignore_index=True)  # duplicates
df.to_csv("retail_sales.csv", index=False)
print(f"retail_sales.csv created with {len(df)} rows")
