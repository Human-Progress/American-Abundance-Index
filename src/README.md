# Source Code Documentation

This directory contains the Python pipeline for fetching BLS data and generating the American Abundance Index dataset.

---

## Files

- **fetch_and_process_data.py** - Main data pipeline script

---

## Overview

The pipeline performs the following operations:

1. **Data Fetching:** Retrieves time series data from the BLS API
2. **Data Processing:** Calculates indices, percentage changes, and upskilling trajectories
3. **Data Export:** Generates a multi-sheet Excel file for visualization

---

## Script Structure

### Configuration (Lines 11-19)
```python
API_KEY = 'your_key_here'  # BLS API key (REQUIRED)
SERIES_IDS = {
    'CPI': 'CUUR0000SA0',
    'ALL_EMPLOYEES': 'CES0500000003',
    'BLUE_COLLAR': 'CES0500000008',
    'ENTRY_LEVEL': 'CES7072251303'
}
START_YEAR = 2006
BASE_DATE = '2006-03'
```

**Important:** You must add your BLS API key before running. Get one at: https://data.bls.gov/registrationEngine/

### Main Functions

#### BLS Data Fetching
```python
fetch_bls_series(series_id, start_year, end_year, api_key)
```
Fetches a single time series from the BLS API.

**Parameters:**
- `series_id` (str): BLS series identifier
- `start_year` (int): Starting year for data
- `end_year` (int): Ending year for data
- `api_key` (str): Your BLS API key

**Returns:** JSON response from BLS API

---
```python
process_bls_series(response, name)
```
Converts BLS JSON response to a pandas DataFrame.

**Parameters:**
- `response` (dict): BLS API JSON response
- `name` (str): Column name for the series

**Returns:** DataFrame with columns `['date', name]`

---
```python
fetch_all_series(series_dict, start_year, end_year, api_key)
```
Fetches and merges all required BLS series.

**Parameters:**
- `series_dict` (dict): Dictionary mapping names to series IDs
- `start_year` (int): Starting year
- `end_year` (int): Ending year
- `api_key` (str): BLS API key

**Returns:** DataFrame with all series merged on date

---

#### Calculations
```python
calc_pct_from_base(df, column, base_date)
```
Calculates percentage change from a base date.

**Formula:** `((current / base) - 1) × 100`

**Parameters:**
- `df` (DataFrame): Data containing the column
- `column` (str): Column name to calculate percentage for
- `base_date` (str): Base date in 'YYYY-MM' format

**Returns:** Series of percentage changes

---
```python
calc_upskilling(df)
```
Calculates upskilling wage trajectories using linear interpolation.

**Formula:** 
```
Upskilled Wage = (Target Wage × Months) + (Entry Wage × (Total Months - Months)) / Total Months
```

**Parameters:**
- `df` (DataFrame): Data containing wage columns

**Returns:** Tuple of (upskill_to_blue_collar, upskill_to_all_workers)

**Methodology:**
- Starts at entry-level food service wages
- Gradually transitions to target wage over career
- Models realistic career progression

---
```python
create_category_df(df, wage_col)
```
Creates a comprehensive category DataFrame with all metrics.

**Columns Created:**
- `Year`, `Month`: Temporal identifiers
- `Months_Since_Start`: Counter from base date
- `CPI`, `Wage`: Raw values
- `CPI_Index`, `Wage_Index`: Indexed values (base = 100)
- `CPI % from base`, `Wage % from base`: Percentage changes
- `Time_Price_Index`, `Time_Price % from base`: Time price metrics
- `Abundance_Index`, `Abundance % from base`: Abundance metrics

**Parameters:**
- `df` (DataFrame): Raw BLS data
- `wage_col` (str): Column name for wage series

**Returns:** DataFrame with all calculated metrics

---
```python
calc_percentage_changes(df)
```
Calculates percentage changes for different time periods.

**Time Periods:**
- Last Month (if consecutive data available)
- Last Year (12 months)
- Last 5 Years (60 months)
- Last 10 Years (120 months)
- Since Start (from base date)

**Method:** Direct percentage change between two points: `(Current / Past) - 1`

**Note:** Returns `None` for monthly changes if data gaps exist (e.g., missing months during government shutdowns)

**Parameters:**
- `df` (DataFrame): Category DataFrame with metrics

**Returns:** DataFrame with percentage changes for each metric

---
```python
calc_rolling(cat_df)
```
Calculates 12-month rolling average growth rates.

**Process:**
1. Calculate month-over-month percentage changes
2. Apply 12-month rolling average
3. Fill initial months with 0

**Parameters:**
- `cat_df` (DataFrame): Category DataFrame

**Returns:** DataFrame with rolling average columns

---

#### Data Export Functions
```python
generate_kpi_csv(pct_dict)
```
Generates KPI data for dashboard cards.

**Output Columns:**
- `view`: Worker category (all-workers, blue-collar, etc.)
- `metric`: Metric name (abundance, cpi, wage, timePrice)
- `monthly`: Last month change (%)
- `yearly`: Last year change (%)
- `longTermGrowth`: Since-start change (%) - abundance only

---
```python
generate_bar_csv(pct_dict)
```
Generates bar chart data for all time periods.

**Output Columns:**
- `view`: Worker category
- `period`: Time period (1-month, 1-year, 5-year, 10-year, inception)
- `metric`: Metric name (Abundance, Time Price, Wage, CPI)
- `value`: Percentage change

---
```python
generate_line_csv(cat_dfs)
```
Generates time series data for line charts.

**Output Columns:**
- `view`: Worker category
- `date`: YYYY-MM format
- `CPI`, `Wage`, `Time_Price`, `Abundance`: Percentage from base

---
```python
generate_rolling_csv(cat_dfs)
```
Generates rolling average data for rolling chart.

**Output Columns:**
- `view`: Worker category
- `date`: YYYY-MM format
- `CPI`, `Wage`: 12-month rolling average growth rates

---

## Running the Script

### Basic Usage
```bash
python fetch_and_process_data.py
```

### Prerequisites

1. Python 3.8+
2. Required packages (install via `pip install -r requirements.txt`):
   - pandas
   - numpy
   - requests
   - openpyxl
3. BLS API key (free registration at https://data.bls.gov/registrationEngine/)

### Output

Creates `aai-dashboard-data.xlsx` with 5 sheets:

1. **KPI Data** - Dashboard card values
2. **Bar Chart Data** - Period-over-period comparisons
3. **Line Chart Data** - Full time series
4. **Rolling Average Data** - 12-month rolling averages
5. **Detailed Review** - Complete dataset for verification

---

## Customization

### Adding New Worker Categories

To add a new worker category:

1. Add the BLS series to `SERIES_IDS`:
```python
   SERIES_IDS = {
       'CPI': 'CUUR0000SA0',
       'NEW_CATEGORY': 'CES1234567890'  # Your series ID
   }
```

2. Update the category DataFrame creation in `main()`:
```python
   cat_dfs['New_Category'] = create_category_df(df, 'NEW_CATEGORY')
```

3. Add view mapping in CSV generation functions:
```python
   view_mapping = [
       ('All_Employees', 'all-workers'),
       ('New_Category', 'new-workers')
   ]
```

### Changing Calculation Methods

The script uses two main calculation approaches:

1. **Index-based:** For Time Price and Abundance
```python
   index = (current_value / base_value) * 100
```

2. **Direct percentage change:** For period comparisons
```python
   pct_change = ((current / past) - 1) * 100
```

To modify, edit the relevant functions in the Calculations section.

---

## Data Quality Notes

### Missing Data Handling

- **Interpolation:** Not used - missing months remain as gaps
- **Monthly Changes:** Only calculated if consecutive months exist
- **Impact:** Monthly KPI may be `None` if BLS data is delayed

### Known Issues

1. **October 2025 CPI:** BLS occasionally delays releases
   - Script handles gracefully by returning `None` for that month
   - Does not interpolate or estimate missing values

2. **Series Updates:** BLS occasionally revises historical data
   - Re-running the script captures revisions automatically
   - Compare "Detailed Review" sheet across runs to track changes

---

## Error Handling

### Common Errors

**API Key Issues:**
```
BLS API Error: Invalid API Key
```
Solution: Verify API key is correct and active

**Rate Limiting:**
```
Rate limit exceeded
```
Solution: Wait before retrying (500 requests/day limit)

**Data Gaps:**
```
Warning: Missing data for month YYYY-MM
```
Solution: This is normal - BLS may delay releases. Monthly change will be `None`.

---

## Performance

- **API Calls:** 4 requests (one per series)
- **Execution Time:** ~10-15 seconds with good internet
- **Memory Usage:** ~50-100 MB
- **Output Size:** ~2-3 MB Excel file

---

## Testing

### Verify Output

After running, check:

1. **Row counts match expected:**
   - KPI Data: 16 rows (4 metrics × 4 views)
   - Bar Chart Data: 80 rows (4 metrics × 4 views × 5 periods)
   - Line/Rolling Data: ~900 rows (depends on months of data)

2. **Abundance Index matches contributor expectations:**
   - Open "Detailed Review" sheet
   - Compare `Abundance_Index` column to expected values
   - Base month (2006-03) should equal 100.00

3. **No negative CPI or wages:**
   - All raw CPI and wage values should be positive

---

## Contributing

To contribute improvements:

1. Fork the repository
2. Create a feature branch
3. Test thoroughly with your BLS API key
4. Submit a pull request with:
   - Description of changes
   - Test results
   - Any new dependencies

---

## Additional Resources

- **BLS API Documentation:** https://www.bls.gov/developers/
- **Time Price Methodology:** Tupy & Pooley, "Superabundance" (2022)
- **Pandas Documentation:** https://pandas.pydata.org/docs/
```
