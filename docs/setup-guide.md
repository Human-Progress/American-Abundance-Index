# Setup Guide

This guide walks you through installing and running the American Abundance Index data pipeline.

---

## System Requirements

- **Python:** 3.8 or higher
- **Operating System:** Windows, macOS, or Linux
- **Internet Connection:** Required for BLS API access

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/american-abundance-index.git
cd american-abundance-index
```

**Note:** Replace `YOUR_USERNAME` with your actual GitHub username or organization name.

### 2. Create a Virtual Environment (Recommended)

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `pandas` - Data manipulation
- `numpy` - Numerical calculations
- `requests` - API calls
- `openpyxl` - Excel file handling

---

## Getting a BLS API Key

The pipeline requires a Bureau of Labor Statistics API key to fetch data.

### Steps to Register:

1. Go to https://data.bls.gov/registrationEngine/
2. Fill out the registration form with your email
3. Check your email for the API key (usually arrives within minutes)
4. Keep this key secure - you'll need it in the next step

### API Key Limits:

- **Free tier:** 500 requests per day, 25 requests at a time
- **Sufficient for:** Monthly updates of the AAI (uses ~4 requests)

---

## Configuration

### Add Your API Key

Open `src/fetch_and_process_data.py` and locate line 14:
```python
API_KEY = 'your_bls_api_key_here'  # Replace with your BLS API key
```

Replace the placeholder with your actual BLS API key:
```python
API_KEY = 'abc123def456ghi789'  # Your actual key
```

**Important:** Never commit your API key to version control. The `.gitignore` file helps prevent this, but always double-check before pushing changes.

---

## Running the Pipeline

### Basic Usage

From the repository root directory:
```bash
python src/fetch_and_process_data.py
```

### What Happens:

1. **Fetches data** from BLS API for four series:
   - Consumer Price Index (CPI)
   - All Private-Sector Workers hourly earnings
   - Blue-Collar Workers hourly earnings
   - Entry-Level Food Service hourly earnings

2. **Calculates metrics:**
   - Percentage changes from base date (March 2006)
   - Time Price indices
   - Abundance indices
   - Upskilling trajectories
   - Rolling averages

3. **Generates output:** Creates `aai-dashboard-data.xlsx` with 5 sheets:
   - **KPI Data:** Summary metrics for dashboard cards
   - **Bar Chart Data:** Period-over-period changes
   - **Line Chart Data:** Time series for all metrics
   - **Rolling Average Data:** 12-month rolling averages
   - **Detailed Review:** Full dataset with all calculations

### Expected Output:
```
============================================================
AAI Dashboard Data Generator
============================================================

Fetching data from BLS API...
  CPI... ✓
  ALL_EMPLOYEES... ✓
  BLUE_COLLAR... ✓
  ENTRY_LEVEL... ✓
✓ Fetched 226 months of data

Calculating upskilling trajectories...
  ✓ Upskilling calculations complete

Creating category DataFrames...
  ✓ Category DataFrames created

Calculating percentage changes...
  ✓ Percentage changes calculated

Generating data sheets...
------------------------------------------------------------
Generating KPI data...
  Note: 'monthly' = change from last available data point
        (may be >1 month if BLS data is delayed)

  Processing all-workers:
    Metrics available: ['Abundance', 'CPI', 'Wage', 'Time_Price']
    Abundance: monthly=0.0004, yearly=1.84
    CPI: monthly=0.41, yearly=4.75
    Time_Price: monthly=0.01, yearly=-1.81

  ✓ KPI data prepared (16 rows)
Generating bar chart data...
  ✓ Bar chart data prepared (80 rows)
Generating line chart data...
  ✓ Line chart data prepared (904 rows)
Generating rolling average data...
  ✓ Rolling average data prepared (904 rows)
Generating detailed review data...
  ✓ Detailed review data prepared (904 rows)
------------------------------------------------------------

Exporting to aai-dashboard-data.xlsx...
  ✓ Excel file created with 5 sheets

============================================================
============================================================

File created: aai-dashboard-data.xlsx

Sheets:
  1. KPI Data - KPI card values
  2. Bar Chart Data - Bar chart values for all time periods
  3. Line Chart Data - Time series data
  4. Rolling Average Data - 12-month rolling averages
  5. Detailed Review - Full data with indexed columns

You can now:
  - Use sheets 1-4 for dashboard visualizations
  - Use sheet 5 (Detailed Review) to verify calculations
  - The 'Abundance_Index' column matches contributor expectations
```

---

## Updating the Data

### Monthly Updates

Run the pipeline after BLS releases new data (typically mid-month):
```bash
python src/fetch_and_process_data.py
```

The script automatically fetches all available data from March 2006 to present.

### Moving Output Files

After generation, move the Excel file to the data folder:

**macOS/Linux:**
```bash
mv aai-dashboard-data.xlsx data/processed/aai_data_$(date +%Y-%m-%d).xlsx
```

**Windows (PowerShell):**
```powershell
Move-Item aai-dashboard-data.xlsx data/processed/aai_data_$(Get-Date -Format yyyy-MM-dd).xlsx
```

**Or manually:**
1. Rename `aai-dashboard-data.xlsx` to include the date (e.g., `aai_data_2025-01-27.xlsx`)
2. Move it to `data/processed/`

---

## Troubleshooting

### API Key Errors

**Error:** `BLS API Error: Invalid API Key`

**Solution:** 
- Verify your API key is correct
- Check that you've registered at https://data.bls.gov/registrationEngine/
- Ensure your key hasn't expired (BLS keys are valid for 1 year)

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'pandas'`

**Solution:**
```bash
pip install -r requirements.txt
```

If still failing, try upgrading pip:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Connection Errors

**Error:** `Connection timeout` or `Failed to reach BLS API`

**Solution:**
- Check your internet connection
- BLS API may be temporarily down - try again later
- Check BLS status at https://www.bls.gov/

### Rate Limiting

**Error:** `Rate limit exceeded`

**Solution:**
- Free tier allows 500 requests/day
- Wait and try again later
- The AAI pipeline uses only ~4 requests, so this is rare

### Missing Data Warnings

**Warning:** `Missing data for month YYYY-MM`

**Solution:**
- This is normal - BLS occasionally delays releases
- Script does not interpolate missing values
- Missing months will appear as gaps in time series
- Re-run pipeline when BLS publishes the data

---

## Advanced Configuration

### Changing the Base Year

To change the baseline from March 2006:

1. Open `src/fetch_and_process_data.py`
2. Modify line 18:
```python
   BASE_DATE = '2006-03'  # Change to your desired base date
```
3. Ensure your `START_YEAR` includes this date

**Note:** Changing the base date will affect all index calculations.

### Changing the Date Range

To fetch data from a different starting year:

1. Open `src/fetch_and_process_data.py`
2. Modify line 17:
```python
   START_YEAR = 2006  # Change to your desired starting year
```

**Note:** The AAI methodology requires continuous data from the base date forward. Changing these values may affect index calculations.

### Adding New BLS Series

To track additional worker categories:

1. Find the BLS series ID at https://data.bls.gov/
2. Add to `SERIES_IDS` dictionary (lines 12-16):
```python
   SERIES_IDS = {
       'CPI': 'CUUR0000SA0',
       'NEW_CATEGORY': 'CES1234567890'  # Your series ID
   }
```
3. Update `main()` function to process the new series

See `src/README.md` for detailed customization instructions.

---

## Verifying Results

### Using the Detailed Review Sheet

The "Detailed Review" sheet contains all calculations for verification:

1. Open `aai-dashboard-data.xlsx`
2. Navigate to the "Detailed Review" sheet
3. Key columns for verification:
   - `Abundance_Index`: Should match expected values (base month = 100.0)
   - `CPI_Index`, `Wage_Index`: Indexed values (base = 100)
   - `*_pct_from_base`: Percentage changes from baseline

### Cross-Checking with BLS

You can verify raw data against BLS directly:

- **CPI:** https://data.bls.gov/timeseries/CUUR0000SA0
- **All Workers:** https://data.bls.gov/timeseries/CES0500000003
- **Blue Collar:** https://data.bls.gov/timeseries/CES0600000008
- **Entry Level:** https://data.bls.gov/timeseries/CES7072251303

### Expected Values Check

For March 2006 (base month):
- All indices should equal **100.00**
- All "% from base" values should equal **0.00%**

For most recent month:
- CPI Index should be ~150-160 (as of 2025)
- Wage indices vary by category
- All values should be positive

---

## Performance Optimization

### Reducing API Calls

The script is already optimized to minimize API calls:
- Fetches entire date range in single requests
- Uses batch processing where possible
- Only 4 API calls total per run

### Faster Execution

For faster processing on large datasets:

1. **Use SSD storage** for faster file I/O
2. **Increase available RAM** (script uses ~50-100 MB)
3. **Faster internet connection** reduces API fetch time

Typical execution time: **10-15 seconds** with good internet

---

## Data Quality Checks

After running the pipeline, verify:

### Row Counts
- **KPI Data:** 16 rows (4 metrics × 4 views)
- **Bar Chart Data:** 80 rows (4 metrics × 4 views × 5 periods)
- **Line Chart Data:** ~900 rows (depends on months available)
- **Rolling Average Data:** ~900 rows (same as line chart)
- **Detailed Review:** ~900 rows (same as line chart)

### Value Ranges
- **CPI:** Should be positive, typically 200-350
- **Wages:** Should be positive, typically $15-40/hour
- **Indices:** Should be positive, base month = 100
- **Percentages:** Reasonable ranges (not ±500%)

### Data Integrity
- No duplicate dates within a view
- Dates are sequential (allowing for gaps)
- Base month values are correct

---

## Next Steps

- **Explore the data:** Open the generated Excel file and review each sheet
- **Create visualizations:** See `examples/visualization_example.html` for a D3.js demo
- **Read methodology:** See `docs/methodology.md` for calculation details
- **Understand the data:** See `docs/data-dictionary.md` for column definitions

---

## Getting Help

If you encounter issues:

1. Check this guide's Troubleshooting section
2. Review `src/README.md` for code-specific documentation
3. Verify your Python version: `python --version` (must be 3.8+)
4. Check installed packages: `pip list`
5. Open an issue on GitHub with:
   - Error message (full traceback)
   - Steps to reproduce
   - Python version and operating system
   - Output of `pip list`

---

## Additional Resources

- **BLS API Documentation:** https://www.bls.gov/developers/
- **BLS Data Finder:** https://data.bls.gov/
- **Python Documentation:** https://docs.python.org/3/
- **Pandas Documentation:** https://pandas.pydata.org/docs/
- **Time Price Methodology:** Tupy & Pooley, "Superabundance" (2022)
```
