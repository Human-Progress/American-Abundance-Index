# Data Dictionary

This document describes all columns in the processed AAI dataset.

---

## File Format

- **Filename:** `aai_data_YYYY-MM-DD.xlsx`
- **Format:** Multi-sheet Excel file
- **Encoding:** UTF-8
- **Date Format:** YYYY-MM

---

## Excel Sheet Overview

The data file contains 5 sheets:

1. **KPI Data** - Summary metrics for dashboard cards
2. **Bar Chart Data** - Period-over-period percentage changes
3. **Line Chart Data** - Complete time series
4. **Rolling Average Data** - 12-month rolling averages
5. **Detailed Review** - Full dataset with all calculations

---

## Sheet 1: KPI Data

Summary metrics showing current month and year-over-year changes.

### Columns

| Column | Type | Description | Example Values |
|--------|------|-------------|----------------|
| `view` | String | Worker category identifier | all-workers, blue-collar, upskilling-all, upskilling-blue |
| `metric` | String | Metric name | abundance, cpi, wage, timePrice |
| `monthly` | Float | Last month percentage change | 0.45, -0.23 |
| `yearly` | Float | Last year percentage change | 6.68, 4.75 |
| `longTermGrowth` | Float | Since-start change (abundance only) | 12.51 |

### Notes

- `monthly` represents change from the most recent previous data point (may span >1 month if BLS data is delayed)
- `yearly` represents 12-month change
- `longTermGrowth` only populated for abundance metric
- All percentage values are stored as numbers (e.g., 5.5 means 5.5%)

---

## Sheet 2: Bar Chart Data

Percentage changes across different time periods for bar chart visualization.

### Columns

| Column | Type | Description | Example Values |
|--------|------|-------------|----------------|
| `view` | String | Worker category identifier | all-workers, blue-collar, upskilling-all, upskilling-blue |
| `period` | String | Time period | 1-month, 1-year, 5-year, 10-year, inception |
| `metric` | String | Metric name | Abundance, Time Price, Wage, CPI |
| `value` | Float | Percentage change for the period | 12.51, -11.07, 45.30 |

### Period Definitions

- **1-month:** Change from previous month (if consecutive data available)
- **1-year:** Change over last 12 months
- **5-year:** Change over last 60 months
- **10-year:** Change over last 120 months
- **inception:** Change since March 2006 (base date)

### Notes

- Each view × period × metric combination has one row
- Total rows: 4 views × 5 periods × 4 metrics = 80 rows
- Metric names include spaces (e.g., "Time Price" not "timePrice")

---

## Sheet 3: Line Chart Data

Complete time series of percentage changes from base date (March 2006).

### Columns

| Column | Type | Description | Example Values |
|--------|------|-------------|----------------|
| `view` | String | Worker category identifier | all-workers, blue-collar, upskilling-all, upskilling-blue |
| `date` | String | Month in YYYY-MM format | 2024-01, 2024-12 |
| `CPI` | Float | CPI % change from base | 60.15, 62.30 |
| `Wage` | Float | Wage % change from base | 75.50, 78.20 |
| `Time_Price` | Float | Time Price % change from base | -11.07, -9.50 |
| `Abundance` | Float | Abundance % change from base | 12.51, 10.80 |

### Notes

- Base date (2006-03) has all metrics at 0.00%
- Covers March 2006 through most recent BLS release
- Each view has ~225+ rows depending on current date
- Missing months appear as gaps (no interpolation)

---

## Sheet 4: Rolling Average Data

12-month rolling average growth rates for smoothed trend visualization.

### Columns

| Column | Type | Description | Example Values |
|--------|------|-------------|----------------|
| `view` | String | Worker category identifier | all-workers, blue-collar, upskilling-all, upskilling-blue |
| `date` | String | Month in YYYY-MM format | 2024-01, 2024-12 |
| `CPI` | Float | 12-month rolling average CPI growth (%) | 3.5, 4.2 |
| `Wage` | Float | 12-month rolling average wage growth (%) | 5.2, 6.1 |

### Calculation Method

For each month:
1. Calculate month-over-month percentage change: `(current / previous - 1) × 100`
2. Apply 12-month rolling average
3. Result shows annualized growth rate trend

### Notes

- First 11 months use available data (fewer than 12 months)
- Smooths out monthly volatility
- Useful for identifying long-term trends

---

## Sheet 5: Detailed Review

Comprehensive dataset with all raw values, indices, and intermediate calculations.

### Columns

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| `Category` | String | Worker category name | All_Employees, Blue_Collar, etc. |
| `Year` | Integer | Calendar year | 2024 |
| `Month` | Integer | Month number (1-12) | 1 = January |
| `Months_Since_Start` | Integer | Counter from March 2006 | 0, 1, 2, ... |
| `CPI` | Float | Raw CPI value | 310.33 |
| `Wage` | Float | Raw hourly earnings value ($) | 34.69 |
| `CPI_Index` | Float | CPI indexed to base = 100 | 151.2 |
| `Wage_Index` | Float | Wage indexed to base = 100 | 143.7 |
| `Time_Price_Index` | Float | Time Price index (base = 100) | 105.2 |
| `Abundance_Index` | Float | Abundance index (base = 100) | 95.0 |
| `CPI_pct_from_base` | Float | CPI % change from base | 51.2 |
| `Wage_pct_from_base` | Float | Wage % change from base | 43.7 |
| `Time_Price_pct_from_base` | Float | Time Price % change from base | 5.2 |
| `Abundance_pct_from_base` | Float | Abundance % change from base | -5.0 |

### Key Relationships

**Index Values:**
- Base month (2006-03): All indices = 100.0
- Formula: `Index = (Current Value / Base Value) × 100`

**Percentage from Base:**
- Base month (2006-03): All percentages = 0.0%
- Formula: `% from base = Index - 100`

**Time Price vs. Abundance:**
- Time Price Index = `(CPI_Index / Wage_Index) × 100`
- Abundance Index = `(Wage_Index / CPI_Index) × 100`
- They are inverses: When Time Price falls, Abundance rises

### Use Cases

- **Verification:** Compare `Abundance_Index` to contributor's AAI column
- **Auditing:** Check calculation steps
- **Research:** Access raw BLS values
- **Debugging:** Identify data issues or anomalies

---

## Worker Category Definitions

### all-workers
- **Full Name:** All Private-Sector Workers
- **BLS Series:** CES0500000003
- **Description:** Average hourly earnings for all employees in private sector (excludes government)

### blue-collar
- **Full Name:** Blue-Collar Workers
- **BLS Series:** CES0600000008
- **Description:** Production and nonsupervisory employees in goods-producing industries

### upskilling-all
- **Full Name:** Workers Upskilling to All Private-Sector Jobs
- **Calculation:** Linear interpolation from entry-level food service wages to all private-sector wages
- **Starting Point:** Entry-level food service (BLS CES7072251303)
- **Ending Point:** All private-sector workers (BLS CES0500000003)

### upskilling-blue
- **Full Name:** Workers Upskilling to Blue-Collar Jobs
- **Calculation:** Linear interpolation from entry-level food service wages to blue-collar wages
- **Starting Point:** Entry-level food service (BLS CES7072251303)
- **Ending Point:** Blue-collar workers (BLS CES0600000008)

---

## Data Quality Indicators

### Missing Data

- **Representation:** Gaps in time series (no rows for missing months)
- **Common Causes:** BLS delays, government shutdowns, data revisions
- **Handling:** No interpolation; missing months remain as gaps

### Data Revisions

- BLS occasionally revises historical data
- Revisions are incorporated when pipeline re-runs
- Compare files across dates to track changes

### Validation Checks

Each data release is validated for:
- Positive CPI and wage values
- Reasonable month-over-month changes (<10%)
- Index consistency (base month = 100)
- No duplicate dates within a view

---

## Example Rows

### KPI Data Example
```
view: all-workers
metric: abundance
monthly: 0.45
yearly: 6.68
longTermGrowth: 12.51
```

### Bar Chart Data Example
```
view: all-workers
period: 1-year
metric: Abundance
value: 1.84
```

### Line Chart Data Example
```
view: all-workers
date: 2024-01
CPI: 60.15
Wage: 75.50
Time_Price: -11.07
Abundance: 12.51
```

### Rolling Average Data Example
```
view: all-workers
date: 2024-01
CPI: 3.5
Wage: 5.2
```

### Detailed Review Example
```
Category: All_Employees
Year: 2024
Month: 1
Months_Since_Start: 214
CPI: 310.33
Wage: 34.69
CPI_Index: 151.2
Wage_Index: 143.7
Time_Price_Index: 105.2
Abundance_Index: 95.0
CPI_pct_from_base: 51.2
Wage_pct_from_base: 43.7
Time_Price_pct_from_base: 5.2
Abundance_pct_from_base: -5.0
```

---

## Common Calculations

### Converting Index to Percentage
```python
percentage_from_base = index_value - 100
```

Example: Index of 112.5 = +12.5% from base

### Converting Percentage to Index
```python
index_value = percentage_from_base + 100
```

Example: +12.5% from base = Index of 112.5

### Calculating Time Price from Abundance
```python
time_price_index = 10000 / abundance_index
```

Example: Abundance Index of 95.0 → Time Price Index of 105.26

---

## Data Types and Precision

- **Integers:** Year, Month, Months_Since_Start
- **Floats (2 decimals):** All percentage values, indices
- **Floats (3 decimals):** Raw CPI values
- **Floats (2 decimals):** Raw wage values
- **Strings:** view, metric, period, Category, date

---

## Change Log

Document updates to data structure:

| Date | Change | Impact |
|------|--------|--------|
| 2025-30-27 | Initial data dictionary | - |

---

## Questions?

For questions about data definitions or calculations:
- See `docs/methodology.md` for calculation details
- See `src/README.md` for code documentation
- Open an issue on GitHub for clarification
```
