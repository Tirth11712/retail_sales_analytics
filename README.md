# Retail Store Sales Analytics

A Python-based end-to-end data analytics project that simulates a realistic retail business dataset, processes it through a structured 4-step analytical pipeline, generates professional visualisations, and produces actionable inventory management recommendations.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [How It Works — The 4-Step Pipeline](#how-it-works--the-4-step-pipeline)
5. [Dataset Details](#dataset-details)
6. [Visualisations Generated](#visualisations-generated)
7. [Outputs & Results](#outputs--results)
8. [Business Use Cases](#business-use-cases)
9. [Setup & Installation](#setup--installation)
10. [How to Run](#how-to-run)
11. [Expected Key Results](#expected-key-results)
12. [Project Workflow Diagram](#project-workflow-diagram)

---

## Project Overview

Retail businesses generate enormous volumes of transactional data every day. Extracting meaningful insights from that data — which products sell best, which regions underperform, when to restock inventory — is critical to profitability and operational efficiency.

This project simulates a full-year (2025) dataset of retail transactions across four regions of India and five product categories. It then runs a complete analytics pipeline to answer real business questions:

- Which regions and product categories drive the most revenue?
- What are the seasonal sales trends throughout the year?
- Which products need urgent restocking before peak demand periods?
- Where is inventory overstocked and capital being unnecessarily tied up?

The project is structured as a **micro analytics project** suitable for learning, portfolio demonstration, or as a template for applying to real retail datasets.

---

## Tech Stack

| Technology | Role |
|---|---|
| **Python 3.9+** | Core programming language |
| **NumPy** | Vectorised numerical computations (revenue, discount calculations, demand logic) |
| **Pandas** | Data loading, cleaning, transformation, groupby aggregations, pivot tables |
| **Matplotlib** | Base charting engine for all six output visualisations |
| **Seaborn** | Statistical chart styling — heatmaps, bar plots, themed grids |
| **CSV (flat file)** | Lightweight input/output data storage — no database required |

No external APIs, no cloud services, no databases. The entire project runs locally with just four standard Python libraries.

---

## Project Structure

```
retail_sales_analytics/
│
├── generate_dataset.py       # Synthetic dataset generator (reproducible, seed 42)
├── retail_analysis.py        # Full 4-step analytics pipeline
├── run_all.py                # One-click runner — executes both scripts in order
├── requirements.txt          # Python dependencies
├── retail_sales.csv          # Generated input data (2,402 rows including dirty records)
│
└── outputs/                  # All generated results land here
    ├── console_output.txt            # Full analysis log saved to file
    ├── stock_recommendations.csv     # Inventory recommendations table
    ├── 01_monthly_trend.png          # Monthly revenue trend by category
    ├── 02_monthly_total.png          # Total monthly revenue + MoM growth
    ├── 03_region_category_heatmap.png  # Region × Category revenue heatmap
    ├── 04_region_month_heatmap.png   # Region × Month seasonality heatmap
    ├── 05_top_products_region_share.png  # Top 10 products + regional pie chart
    └── 06_stock_cover.png            # Inventory cover for best-selling products
```

---

## How It Works — The 4-Step Pipeline

### Step 1 — Sales Record Parsing (`load_and_clean`)

This step ingests the raw CSV and prepares it for analysis. It handles real-world data quality problems that are intentionally injected into the dataset:

- **Duplicate detection & removal** — Identifies and drops duplicate `TransactionID` rows (2 duplicates injected).
- **Missing value imputation** — `UnitsSold` nulls are filled using the **median units sold for that product** (group-aware imputation). `Discount` nulls default to `0.0`.
- **Date feature engineering** — Parses `OrderDate` into a proper datetime, then derives `Month`, `MonthName`, and `Quarter` columns.
- **Revenue computation** — Uses NumPy for vectorised calculation:
  ```
  TotalRevenue = UnitsSold × UnitPrice × (1 − Discount)
  DiscountLoss = UnitsSold × UnitPrice × Discount
  ```

After this step, the dataset is clean, typed correctly, and enriched with derived columns ready for analysis.

---

### Step 2 — Product & Region Aggregation (`aggregate`)

This step summarises the clean data at multiple business dimensions:

- **Overall KPIs** — Total revenue, total units sold, average order value, total revenue lost to discounts.
- **Regional breakdown** — Revenue and market share percentage per region (North, South, East, West).
- **Category performance** — Revenue, units sold, order count, and share percentage across all five categories (Electronics, Clothing, Furniture, Groceries, Home Appliances).
- **Product ranking** — Multi-level groupby on `(Category, Product)` to identify the top 10 best-sellers by revenue.
- **Time-based aggregation** — Monthly revenue broken down by category (for trend charting), and quarterly revenue totals.

All aggregations are done with Pandas `groupby`, `agg`, `pivot_table`, and `pct` rank methods.

---

### Step 3 — Revenue Heatmaps & Trend Charts (`visualize`)

Six publication-quality charts are generated and saved to the `outputs/` folder:

1. **Monthly Revenue Trend by Category** — A multi-line chart showing how each category's revenue moves across all 12 months. Reveals seasonality per category.
2. **Total Monthly Revenue with MoM Growth** — A bar chart of overall monthly revenue with percentage growth annotations above each bar.
3. **Region × Category Heatmap** — A colour-coded grid showing which region drives revenue in which category. Instantly shows cross-segment strengths and gaps.
4. **Region × Month Heatmap** — Seasonal view of how each region performs across all 12 months. Reveals festive-season spikes.
5. **Top 10 Products + Regional Market Share** — A combined figure: a horizontal bar chart of the top 10 revenue-generating products (colour-coded by category) alongside a pie chart of regional market share.
6. **Inventory Cover Chart** — A horizontal bar chart of the 15 best-sellers with the lowest months of stock cover, colour-coded Red/Orange/Green with threshold reference lines.

All charts use Seaborn's `whitegrid` theme and are saved at 150 DPI.

---

### Step 4 — Retail Strategy & Stocking Insights (`stocking_insights`)

This is the most operationally valuable step. It answers the question: *"What should the purchasing team do next week?"*

The logic works as follows:

1. **Current Stock** — The latest `StockOnHand` recorded for each (Region, Product) combination is taken as the current inventory level.
2. **Peak Demand Estimate** — Average monthly units sold during Q4 (October–December, the festive/peak quarter) is used as the forward-looking demand estimate. This is more conservative and realistic than using the annual average.
3. **Months of Cover** — `CurrentStock ÷ AvgMonthlyDemand` gives how many months of stock is available at peak-season demand rates.
4. **Best-Seller Classification** — Products in the top 30% of revenue within their region are flagged as best-sellers. These get priority treatment.
5. **Status Classification**:
   - 🔴 **CRITICAL — Reorder now**: Best-seller with less than 1 month of cover.
   - 🟠 **LOW — Reorder soon**: Best-seller with less than 1.5 months of cover.
   - 🟢 **OVERSTOCK — Run promotion**: Any product with more than 6 months of cover.
   - ✅ **OK**: Everything else.
6. **Reorder Quantity** — Calculated as the units needed to bring stock back to the 1.5-month safety buffer.
7. **Output** — The full inventory table is saved to `outputs/stock_recommendations.csv` for the purchasing team.

---

## Dataset Details

The dataset is synthetically generated by `generate_dataset.py` with `numpy.random.default_rng(seed=42)` for full reproducibility.

| Attribute | Detail |
|---|---|
| **Rows** | 2,402 (2,400 clean transactions + 2 intentional duplicates) |
| **Time Period** | 1 Jan 2025 – 31 Dec 2025 (full calendar year) |
| **Regions** | North (30%), South (22%), East (20%), West (28%) |
| **Categories** | Electronics, Clothing, Furniture, Groceries, Home Appliances |
| **Products** | 20 SKUs (4 per category) with realistic base prices |
| **Seasonality** | Built-in seasonal weights — Oct/Nov festive spike (1.45×/1.40×), Dec year-end sale (1.20×), summer Air Cooler boost |
| **Discounts** | Higher discount probability during festive months (Oct–Nov) |
| **Dirty records** | 3 null `UnitsSold`, 1 null `Discount`, 2 duplicate rows |

The generator is intentionally designed to mirror the kind of messy, real-world data an analyst would receive from a point-of-sale system.

---

## Visualisations Generated

| File | Chart Type | What It Shows |
|---|---|---|
| `01_monthly_trend.png` | Multi-line chart | Revenue per category per month |
| `02_monthly_total.png` | Annotated bar chart | Total monthly revenue + MoM growth % |
| `03_region_category_heatmap.png` | Heatmap | Revenue matrix: Region vs Category |
| `04_region_month_heatmap.png` | Heatmap | Seasonal revenue: Region vs Month |
| `05_top_products_region_share.png` | Bar + Pie (side-by-side) | Top 10 products & regional market share |
| `06_stock_cover.png` | Colour-coded horizontal bar | Inventory cover for 15 lowest-stock best-sellers |

---

## Outputs & Results

After running the project, the `outputs/` folder contains:

- **6 PNG charts** — ready to drop into a report or presentation.
- **`stock_recommendations.csv`** — a structured table with columns: `Region`, `Product`, `CurrentStock`, `AvgMonthlyDemand`, `MonthsOfCover`, `RevenueRank_pct`, `BestSeller`, `ReorderQty`, `Status`. This is a directly actionable deliverable for a supply chain or purchasing team.
- **`console_output.txt`** — complete printed output of the entire analysis run, saved for audit and reproducibility.

---

## Business Use Cases

This project demonstrates analytics workflows applicable to real retail businesses:

- **Sales Performance Reporting** — Monthly and quarterly revenue tracking with growth rates, suitable for executive dashboards.
- **Market Segmentation** — Region and category heatmaps to identify where marketing spend should be focused.
- **Demand Forecasting Proxy** — Using peak-quarter demand as a forward estimate is a common heuristic in retail planning.
- **Inventory Optimisation** — The stock cover analysis directly mirrors what retail ERP systems (like SAP or Oracle Retail) compute internally. The CRITICAL/LOW/OVERSTOCK classification maps directly to reorder point logic.
- **Discount Impact Analysis** — Quantifying revenue lost to discounts helps evaluate promotional ROI.
- **Festive Season Planning** — The seasonal multipliers and Oct–Nov revenue concentration analysis supports pre-festive procurement planning.

---

## Setup & Installation

### Prerequisites

- Python 3.9 or higher
- pip

### Steps

**1. Clone or download the project**
```bash
git clone <repo-url>
cd retail_sales_analytics
```

**2. Create a virtual environment (recommended)**

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Mac / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

The four libraries installed are: `numpy`, `pandas`, `matplotlib`, `seaborn`.

---

## How to Run

### Option A — One-click (recommended)
```bash
python run_all.py
```
This runs `generate_dataset.py` first to create the CSV, then immediately runs `retail_analysis.py` to produce all outputs.

### Option B — Step by step
```bash
python generate_dataset.py   # Creates retail_sales.csv
python retail_analysis.py    # Runs analysis, saves charts and CSV outputs
```

### Output location
All charts, the stock recommendations CSV, and the console log are written to the `outputs/` folder, which is created automatically if it does not exist.

---

## Expected Key Results

| Metric | Value |
|---|---|
| Total Net Revenue | Rs. 6.90 crore (₹68,951,568.60) |
| Strongest Region | North (31.7% market share) |
| Weakest Region | East |
| Top Category | Electronics (47.8% of total revenue) |
| Best-Selling Product | Laptop |
| Peak Month | December |
| Revenue Lost to Discounts | Computed and printed in Step 2 |
| Stock Alerts — CRITICAL | 3 product-region combinations |
| Stock Alerts — LOW | 5 product-region combinations |
| Overstocked SKUs | 28 product-region combinations |

> Results are fully reproducible because the dataset generator uses a fixed random seed (`seed=42`).

---

## Project Workflow Diagram

```
generate_dataset.py
        │
        │  Creates synthetic transactions with
        │  seasonality, regional weights, dirty records
        ▼
  retail_sales.csv  (2,402 rows)
        │
        ▼
retail_analysis.py
        │
        ├─ STEP 1: Load & Clean
        │     • Remove duplicates
        │     • Impute missing values
        │     • Engineer date features
        │     • Compute TotalRevenue & DiscountLoss
        │
        ├─ STEP 2: Aggregate
        │     • KPIs (revenue, units, AOV)
        │     • Region & category breakdowns
        │     • Product rankings
        │     • Monthly & quarterly summaries
        │
        ├─ STEP 3: Visualise
        │     • 6 charts saved to outputs/
        │
        ├─ STEP 4: Stocking Insights
        │     • Compute months of cover
        │     • Classify CRITICAL / LOW / OVERSTOCK / OK
        │     • Generate reorder quantities
        │     • Save stock_recommendations.csv
        │
        └─ BUSINESS SUMMARY
              • 5 key strategic takeaways printed
              • Full log saved to console_output.txt
```

---

## Author Notes

- The project intentionally injects data quality issues (nulls, duplicates) to demonstrate production-grade data cleaning — not just analysis on a pre-cleaned dataset.
- All monetary values are in Indian Rupees (Rs.) and the dataset reflects an Indian retail market context (products, pricing, festive calendar).
- The codebase is structured as four clean functions, each mapping to one analytical module, making it easy to extend or replace individual steps.
