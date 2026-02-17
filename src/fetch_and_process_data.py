"""
AAI Dashboard Data Generator
Fetches data from BLS API and generates an Excel file with 3 sheets for the dashboard
Requires: pandas, numpy, requests, openpyxl
"""

import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = 'f3a1929033e4407296889dfa6f1274b0'  #BLS API key
SERIES_IDS = {
    'CPI': 'CUUR0000SA0',           # Consumer Price Index
    'ALL_EMPLOYEES': 'CES0500000003',  # Average Hourly Earnings - All Workers
    'BLUE_COLLAR': 'CES0500000008',    # Average Hourly Earnings - Blue Collar
    'ENTRY_LEVEL': 'CES7072251303'     # Entry Level Food Service Workers
}
START_YEAR = 2006
BASE_DATE = '2006-03'
CURRENT_YEAR = datetime.now().year

# ============================================================================
# BLS DATA FETCHING
# ============================================================================

def fetch_bls_series(series_id, start_year, end_year, api_key):
    """Fetch a single series from BLS API"""
    headers = {'Content-type': 'application/json'}
    data = json.dumps({
        "seriesid": [series_id],
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": api_key
    })
    response = requests.post(
        'https://api.bls.gov/publicAPI/v2/timeseries/data/',
        data=data,
        headers=headers
    )
    return response.json()

def process_bls_series(response, name):
    """Convert BLS API response to DataFrame"""
    if response['status'] != 'REQUEST_SUCCEEDED':
        raise Exception(f"BLS API Error for {name}: {response.get('message', 'Unknown error')}")
    
    df = pd.DataFrame(response['Results']['series'][0]['data'])
    df['year'] = df['year'].astype(int)
    df['month'] = df['period'].str.replace('M', '').astype(int)
    df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df = df.sort_values('date').reset_index(drop=True)
    df = df.rename(columns={'value': name})
    return df[['date', name]]

def fetch_all_series(series_dict, start_year, end_year, api_key):
    """Fetch all BLS series and merge into single DataFrame"""
    print("\nFetching data from BLS API...")
    dfs = []
    for name, series_id in series_dict.items():
        print(f"  {name}...", end=" ")
        # BLS API limits to 20-year spans, so chunk if needed
        chunks = []
        for chunk_start in range(start_year, end_year + 1, 20):
            chunk_end = min(chunk_start + 19, end_year)
            resp = fetch_bls_series(series_id, chunk_start, chunk_end, api_key)
            if resp['status'] == 'REQUEST_SUCCEEDED' and resp['Results']['series'][0]['data']:
                chunks.append(process_bls_series(resp, name))
        if not chunks:
            raise Exception(f"No data returned for {name}")
        combined = pd.concat(chunks, ignore_index=True).drop_duplicates(subset='date').sort_values('date').reset_index(drop=True)
        dfs.append(combined)
        print("✓")
    
    # Merge all series on date
    combined = dfs[0]
    for df in dfs[1:]:
        combined = combined.merge(df, on='date', how='outer')
    
    combined = combined.sort_values('date').reset_index(drop=True)
    combined = combined[combined['date'] >= pd.to_datetime(BASE_DATE)]
    print(f"✓ Fetched {len(combined)} months of data\n")
    return combined
def interpolate_missing_values(df):
    """Interpolate missing CPI values using linear interpolation between adjacent months"""
    print("\nChecking for missing values...")
    
    # Check each series for missing values
    for col in ['CPI', 'ALL_EMPLOYEES', 'BLUE_COLLAR', 'ENTRY_LEVEL']:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            print(f"  {col}: {missing_count} missing values detected")
            
            # Use pandas interpolate with linear method
            # This will use the average of previous and next valid values
            df[col] = df[col].interpolate(method='linear', limit_direction='both')
            
            # Verify interpolation
            remaining_missing = df[col].isna().sum()
            if remaining_missing > 0:
                print(f"    ⚠ Warning: {remaining_missing} values still missing after interpolation")
            else:
                print(f"    ✓ Interpolated successfully")
    
    print("✓ Missing value check complete\n")
    return df
# ============================================================================
# CALCULATIONS
# ============================================================================

def calc_pct_from_base(df, column, base_date):
    """Calculate percentage change from base date"""
    base_val = df[df['date'] == pd.to_datetime(base_date)][column].values[0]
    return ((df[column] / base_val) - 1) * 100

def calc_upskilling(df):
    """Calculate upskilling wage trajectories"""
    C = len(df)
    A = np.arange(len(df))
    entry = df['ENTRY_LEVEL'].ffill()
    
    # Upskilling to Blue Collar
    upskill_blue = ((df['BLUE_COLLAR'] * A) + (entry * (C - A))) / C
    
    # Upskilling to All Workers
    upskill_all = ((df['ALL_EMPLOYEES'] * A) + (entry * (C - A))) / C
    
    return upskill_blue, upskill_all

def create_category_df(df, wage_col):
    """Create category DataFrame with all calculated metrics"""
    cat = pd.DataFrame()
    cat['Year'] = df['date'].dt.year
    cat['Month'] = df['date'].dt.month
    cat['CPI'] = df['CPI']
    cat['Wage'] = df[wage_col]
    
    # Calculate percentage changes from base
    cat['CPI % from base'] = calc_pct_from_base(df, 'CPI', BASE_DATE)
    cat['Wage % from base'] = calc_pct_from_base(df, wage_col, BASE_DATE)
    
    # Calculate Time Price
    tp = cat['CPI'] / cat['Wage']
    cat['Time_Price % from base'] = ((tp / tp.iloc[0]) - 1) * 100
    
    # Calculate Abundance
    ab = cat['Wage'] / cat['CPI']
    cat['Abundance % from base'] = ((ab / ab.iloc[0]) - 1) * 100
    
    return cat

def calc_rolling(cat_df):
    """Calculate 12-month rolling average growth rates"""
    df = cat_df.copy()
    
    # Calculate month-over-month percentage changes
    df['CPI_mom'] = df['CPI'].pct_change(fill_method=None) * 100
    df['Wage_mom'] = df['Wage'].pct_change(fill_method=None) * 100
    
    # Calculate 12-month rolling averages
    df['CPI_12m'] = df['CPI_mom'].rolling(12, min_periods=1).mean()
    df['Wage_12m'] = df['Wage_mom'].rolling(12, min_periods=1).mean()
    
    # Return only the rolling average columns
    return df[['Year', 'Month', 'CPI_12m', 'Wage_12m']].fillna(0).rename(
        columns={'CPI_12m': 'CPI', 'Wage_12m': 'Wage'}
    )

def calc_percentage_changes(df):
    """Calculate percentage changes for different time periods
    
    Uses direct percentage change between two points: (Current / Past) - 1
    Returns None for monthly if data gaps exist (e.g., missing months)
    """
    df = df.reset_index(drop=True)
    
    # Find last VALID (non-NaN) index for critical columns
    valid_indices = df['Abundance % from base'].dropna().index
    if len(valid_indices) == 0:
        return pd.DataFrame()
    
    latest_idx = valid_indices[-1]
    
    changes = []
    for metric in ['CPI', 'Wage', 'Time_Price', 'Abundance']:
        # Determine which raw column to use for calculations
        if metric == 'CPI':
            value_col = 'CPI'
        elif metric == 'Wage':
            value_col = 'Wage'
        elif metric == 'Time_Price':
            # Calculate Time Price on the fly
            tp = df['CPI'] / df['Wage']
        elif metric == 'Abundance':
            # Calculate Abundance on the fly
            ab = df['Wage'] / df['CPI']
        
        pct_col = f"{metric} % from base"
        if pct_col not in df.columns:
            continue
        
        # Get latest VALID value
        valid_data = df[pct_col].dropna()
        if len(valid_data) == 0:
            changes.append({
                'Metric': metric,
                'Last_Month_%': None,
                'Last_Year_%': None,
                'Last_5_Years_%': None,
                'Last_10_Years_%': None,
                'Since_Start_%': None
            })
            continue
        
        latest_idx = valid_data.index[-1]
        
        # Get the raw values for calculations
        if metric == 'Time_Price':
            current_val = (df['CPI'].iloc[latest_idx] / df['Wage'].iloc[latest_idx])
        elif metric == 'Abundance':
            current_val = (df['Wage'].iloc[latest_idx] / df['CPI'].iloc[latest_idx])
        else:
            current_val = df[value_col].iloc[latest_idx]
        
        # Month-over-month: ONLY if previous row is exactly 1 month before
        if latest_idx >= 1:
            prev_idx = latest_idx - 1
            # Check if dates are consecutive months
            curr_date = df.iloc[latest_idx]['Year'] * 12 + df.iloc[latest_idx]['Month']
            prev_date = df.iloc[prev_idx]['Year'] * 12 + df.iloc[prev_idx]['Month']
            
            if curr_date - prev_date == 1:
                if metric == 'Time_Price':
                    prev_val = (df['CPI'].iloc[prev_idx] / df['Wage'].iloc[prev_idx])
                elif metric == 'Abundance':
                    prev_val = (df['Wage'].iloc[prev_idx] / df['CPI'].iloc[prev_idx])
                else:
                    prev_val = df[value_col].iloc[prev_idx]
                
                if not pd.isna(prev_val) and prev_val != 0:
                    mom = ((current_val / prev_val) - 1) * 100
                else:
                    mom = None
            else:
                mom = None  # Gap in data, don't report monthly
        else:
            mom = None
        
        # Year-over-year: find value from 12 months ago
        target_idx = latest_idx - 12
        if target_idx >= 0 and target_idx in df.index:
            if metric == 'Time_Price':
                past_val = (df['CPI'].iloc[target_idx] / df['Wage'].iloc[target_idx])
            elif metric == 'Abundance':
                past_val = (df['Wage'].iloc[target_idx] / df['CPI'].iloc[target_idx])
            else:
                past_val = df[value_col].iloc[target_idx]
            
            if not pd.isna(past_val) and past_val != 0:
                yoy = ((current_val / past_val) - 1) * 100
            else:
                yoy = None
        else:
            yoy = None
        
        # 5 years
        target_idx = latest_idx - 60
        if target_idx >= 0 and target_idx in df.index:
            if metric == 'Time_Price':
                past_val = (df['CPI'].iloc[target_idx] / df['Wage'].iloc[target_idx])
            elif metric == 'Abundance':
                past_val = (df['Wage'].iloc[target_idx] / df['CPI'].iloc[target_idx])
            else:
                past_val = df[value_col].iloc[target_idx]
            
            if not pd.isna(past_val) and past_val != 0:
                five = ((current_val / past_val) - 1) * 100
            else:
                five = None
        else:
            five = None
        
        # 10 years
        target_idx = latest_idx - 120
        if target_idx >= 0 and target_idx in df.index:
            if metric == 'Time_Price':
                past_val = (df['CPI'].iloc[target_idx] / df['Wage'].iloc[target_idx])
            elif metric == 'Abundance':
                past_val = (df['Wage'].iloc[target_idx] / df['CPI'].iloc[target_idx])
            else:
                past_val = df[value_col].iloc[target_idx]
            
            if not pd.isna(past_val) and past_val != 0:
                ten = ((current_val / past_val) - 1) * 100
            else:
                ten = None
        else:
            ten = None
        
        # Since start - keep as % from base (this one stays the same)
        since_start = df[pct_col].iloc[latest_idx]
        
        changes.append({
            'Metric': metric,
            'Last_Month_%': mom,
            'Last_Year_%': yoy,
            'Last_5_Years_%': five,
            'Last_10_Years_%': ten,
            'Since_Start_%': since_start
        })
    
    return pd.DataFrame(changes)

# ============================================================================
# CSV GENERATION FUNCTIONS
# ============================================================================

def generate_kpi_csv(pct_dict, output_file='aai-kpi-data.xlsx'):
    """Generate KPI Excel file
    
    Note: 'monthly' represents the change from the previous available data point,
    which may span more than one month if BLS data is missing (e.g., during shutdowns).
    For example, if October data is missing, 'monthly' will show the Sep→Nov change.
    """
    print("Generating KPI data...")
    print("  Note: 'monthly' = change from last available data point")
    print("        (may be >1 month if BLS data is delayed)")
    
    def get_value(df, metric, period):
        """Helper to get value from percentage changes DataFrame"""
        row = df[df['Metric'] == metric]
        if row.empty or pd.isna(row[period].values[0]):
            return 0.0
        return float(row[period].values[0])
    
    rows = []
    
    view_mapping = [
        ('All_Employees', 'all-workers'),
        ('Blue_Collar', 'blue-collar'),
        ('Upskilling_to_All', 'upskilling-all'),
        ('Upskilling_to_Blue_Collar', 'upskilling-blue')
    ]
    
    for cat, view in view_mapping:
        df = pct_dict[cat]
        
        # Debug: Show what we're working with
        print(f"\n  Processing {view}:")
        print(f"    Metrics available: {df['Metric'].tolist()}")
        
        for metric in ['abundance', 'cpi', 'wage', 'timePrice']:
            # Map to the correct metric name in the DataFrame
            metric_map = {
                'abundance': 'Abundance',
                'cpi': 'CPI',
                'wage': 'Wage',
                'timePrice': 'Time_Price'
            }
            df_metric = metric_map[metric]
            
            monthly = get_value(df, df_metric, 'Last_Month_%')
            yearly = get_value(df, df_metric, 'Last_Year_%')
            long_term = get_value(df, df_metric, 'Since_Start_%') if metric == 'abundance' else None
            
            # Debug output
            if metric in ['abundance', 'cpi', 'timePrice']:
                print(f"    {df_metric}: monthly={monthly:.4f}, yearly={yearly:.2f}")
            
            # Don't round monthly/yearly if they're very small - preserve precision
            # Only round to 2 decimals if > 0.01, otherwise keep more precision
            def smart_round(val):
                if val == 0:
                    return 0.0
                if abs(val) < 0.01:
                    return round(val, 4)  # Keep 4 decimals for tiny values
                return round(val, 2)
            
            rows.append({
                'view': view,
                'metric': metric,
                'monthly': smart_round(monthly),
                'yearly': smart_round(yearly),
                'longTermGrowth': round(long_term, 2) if long_term is not None else ''
            })
    
    kpi_df = pd.DataFrame(rows)
    print(f"  ✓ KPI data prepared ({len(kpi_df)} rows)")
    return kpi_df

def generate_bar_csv(pct_dict, output_file='aai-bar-chart-data.xlsx'):
    """Generate bar chart Excel file"""
    print("Generating bar chart data...")
    
    rows = []
    
    view_mapping = [
        ('All_Employees', 'all-workers'),
        ('Blue_Collar', 'blue-collar'),
        ('Upskilling_to_All', 'upskilling-all'),
        ('Upskilling_to_Blue_Collar', 'upskilling-blue')
    ]
    
    period_mapping = {
        'Last_Month_%': '1-month',
        'Last_Year_%': '1-year',
        'Last_5_Years_%': '5-year',
        'Last_10_Years_%': '10-year',
        'Since_Start_%': 'inception'
    }
    
    for cat, view in view_mapping:
        df = pct_dict[cat]
        lookup = {row['Metric']: row for _, row in df.iterrows()}
        
        for metric in ['Abundance', 'Time Price', 'Wage', 'CPI']:
            # Map display name
            metric_key = metric.replace(' ', '_')
            if metric_key not in lookup:
                continue
            
            row_data = lookup[metric_key]
            
            for period_col, period_name in period_mapping.items():
                value = row_data[period_col]
                if pd.isna(value):
                    value = 0.0
                
                rows.append({
                    'view': view,
                    'period': period_name,
                    'metric': metric,
                    'value': round(float(value), 2)
                })
    
    bar_df = pd.DataFrame(rows)
    print(f"  ✓ Bar chart data prepared ({len(bar_df)} rows)")
    return bar_df

def generate_line_csv(cat_dfs, output_file='aai-line-chart-data.xlsx'):
    """Generate line chart Excel file"""
    print("Generating line chart data...")
    
    rows = []
    
    view_mapping = [
        ('All_Employees', 'all-workers'),
        ('Blue_Collar', 'blue-collar'),
        ('Upskilling_to_All', 'upskilling-all'),
        ('Upskilling_to_Blue_Collar', 'upskilling-blue')
    ]
    
    for cat, view in view_mapping:
        df = cat_dfs[cat]
        
        for _, row in df.iterrows():
            # Skip rows with missing data
            if pd.isna(row['CPI % from base']) or pd.isna(row['Wage % from base']):
                continue
            
            date_str = f"{int(row['Year'])}-{str(int(row['Month'])).zfill(2)}"
            
            rows.append({
                'view': view,
                'date': date_str,
                'CPI': round(float(row['CPI % from base']), 2),
                'Wage': round(float(row['Wage % from base']), 2),
                'Time_Price': round(float(row['Time_Price % from base']), 2),
                'Abundance': round(float(row['Abundance % from base']), 2)
            })
    
    line_df = pd.DataFrame(rows)
    print(f"  ✓ Line chart data prepared ({len(line_df)} rows)")
    return line_df

def calc_rolling_averages(cat_df):
    """Calculate 12-month rolling average of month-over-month percentage changes"""
    df = cat_df.copy()
    
    # Calculate month-over-month percentage changes
    df['CPI_mom'] = df['CPI'].pct_change(fill_method=None) * 100
    df['Wage_mom'] = df['Wage'].pct_change(fill_method=None) * 100
    
    # Calculate 12-month rolling average
    df['CPI_12m'] = df['CPI_mom'].rolling(12, min_periods=1).mean()
    df['Wage_12m'] = df['Wage_mom'].rolling(12, min_periods=1).mean()
    
    return df[['Year', 'Month', 'CPI_12m', 'Wage_12m']].fillna(0)

def generate_rolling_csv(cat_dfs):
    """Generate rolling average CSV file"""
    print("Generating rolling average data...")
    
    rows = []
    
    view_mapping = [
        ('All_Employees', 'all-workers'),
        ('Blue_Collar', 'blue-collar'),
        ('Upskilling_to_All', 'upskilling-all'),
        ('Upskilling_to_Blue_Collar', 'upskilling-blue')
    ]
    
    for cat, view in view_mapping:
        cat_df = cat_dfs[cat]
        rolling = calc_rolling_averages(cat_df)
        
        for _, row in rolling.iterrows():
            date_str = f"{int(row['Year'])}-{str(int(row['Month'])).zfill(2)}"
            
            rows.append({
                'view': view,
                'date': date_str,
                'CPI': round(float(row['CPI_12m']), 2),
                'Wage': round(float(row['Wage_12m']), 2)
            })
    
    rolling_df = pd.DataFrame(rows)
    print(f"  ✓ Rolling average data prepared ({len(rolling_df)} rows)")
    return rolling_df

def generate_rolling_csv(cat_dfs, output_file='aai-rolling-data.xlsx'):
    """Generate rolling average data for the rolling chart"""
    print("Generating rolling average data...")
    
    rows = []
    
    view_mapping = [
        ('All_Employees', 'all-workers'),
        ('Blue_Collar', 'blue-collar'),
        ('Upskilling_to_All', 'upskilling-all'),
        ('Upskilling_to_Blue_Collar', 'upskilling-blue')
    ]
    
    for cat, view in view_mapping:
        cat_df = cat_dfs[cat]
        
        # Calculate rolling averages
        roll_df = calc_rolling(cat_df)
        
        for _, row in roll_df.iterrows():
            date_str = f"{int(row['Year'])}-{str(int(row['Month'])).zfill(2)}"
            
            rows.append({
                'view': view,
                'date': date_str,
                'CPI': round(float(row['CPI']), 2),
                'Wage': round(float(row['Wage']), 2)
            })
    
    rolling_df = pd.DataFrame(rows)
    print(f"  ✓ Rolling average data prepared ({len(rolling_df)} rows)")
    return rolling_df

def create_category_df(df, wage_col):
    """Create category DataFrame with all calculated metrics"""
    cat = pd.DataFrame()
    cat['Year'] = df['date'].dt.year
    cat['Month'] = df['date'].dt.month
    cat['Months_Since_Start'] = range(len(df))  # NEW: Months counter starting at 0
    cat['CPI'] = df['CPI']
    cat['Wage'] = df[wage_col]
    
    # NEW: Add indexed columns (for contributor verification)
    cat['CPI_Index'] = (df['CPI'] / df['CPI'].iloc[0]) * 100
    cat['Wage_Index'] = (df[wage_col] / df[wage_col].iloc[0]) * 100
    
    # Calculate percentage changes from base (keep existing)
    cat['CPI % from base'] = calc_pct_from_base(df, 'CPI', BASE_DATE)
    cat['Wage % from base'] = calc_pct_from_base(df, wage_col, BASE_DATE)
    
    # Calculate Time Price
    tp = cat['CPI'] / cat['Wage']
    cat['Time_Price_Index'] = (tp / tp.iloc[0]) * 100  # NEW: indexed version
    cat['Time_Price % from base'] = ((tp / tp.iloc[0]) - 1) * 100  # existing
    
    # Calculate Abundance
    ab = cat['Wage'] / cat['CPI']
    cat['Abundance_Index'] = (ab / ab.iloc[0]) * 100  # NEW: indexed version (his "AAI" column)
    cat['Abundance % from base'] = ((ab / ab.iloc[0]) - 1) * 100  # existing
    
    return cat
# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    print("=" * 60)
    print("AAI Dashboard Data Generator")
    print("=" * 60)
    
    # Fetch data from BLS
    df = fetch_all_series(SERIES_IDS, START_YEAR, CURRENT_YEAR, API_KEY)

    # Interpolate any missing values
    df = interpolate_missing_values(df)
    
    # Calculate upskilling trajectories
    print("Calculating upskilling trajectories...")
    df['UPSKILL_BC'], df['UPSKILL_ALL'] = calc_upskilling(df)
    print("  ✓ Upskilling calculations complete\n")
    
    # Create category DataFrames
    print("Creating category DataFrames...")
    cat_dfs = {
        'All_Employees': create_category_df(df, 'ALL_EMPLOYEES'),
        'Blue_Collar': create_category_df(df, 'BLUE_COLLAR'),
        'Upskilling_to_All': create_category_df(df, 'UPSKILL_ALL'),
        'Upskilling_to_Blue_Collar': create_category_df(df, 'UPSKILL_BC')
    }
    print("  ✓ Category DataFrames created\n")
    
    # Calculate percentage changes for each category
    print("Calculating percentage changes...")
    pct_dict = {}
    for cat, cat_df in cat_dfs.items():
        pct_dict[cat] = calc_percentage_changes(cat_df)
    print("  ✓ Percentage changes calculated\n")
    
    # Generate data (THIS PART NEEDS TO BE INDENTED - inside main())
    print("Generating data sheets...")
    print("-" * 60)
    kpi_df = generate_kpi_csv(pct_dict)
    bar_df = generate_bar_csv(pct_dict)
    line_df = generate_line_csv(cat_dfs)
    rolling_df = generate_rolling_csv(cat_dfs)
    
    # NEW: Create a detailed data sheet for contributor review
    print("Generating detailed review data...")
    detail_rows = []
    for cat, cat_df in cat_dfs.items():
        for _, row in cat_df.iterrows():
            detail_rows.append({
                'Category': cat,
                'Year': int(row['Year']),
                'Month': int(row['Month']),
                'Months_Since_Start': int(row['Months_Since_Start']),
                'CPI': round(float(row['CPI']), 3),
                'Wage': round(float(row['Wage']), 2),
                'CPI_Index': round(float(row['CPI_Index']), 2),
                'Wage_Index': round(float(row['Wage_Index']), 2),
                'Time_Price_Index': round(float(row['Time_Price_Index']), 2),
                'Abundance_Index': round(float(row['Abundance_Index']), 2),
                'CPI_pct_from_base': round(float(row['CPI % from base']), 2),
                'Wage_pct_from_base': round(float(row['Wage % from base']), 2),
                'Time_Price_pct_from_base': round(float(row['Time_Price % from base']), 2),
                'Abundance_pct_from_base': round(float(row['Abundance % from base']), 2)
            })
    detail_df = pd.DataFrame(detail_rows)
    print(f"  ✓ Detailed review data prepared ({len(detail_df)} rows)")
    print("-" * 60)
    
    # Export to single Excel file with 5 sheets
    output_file = 'aai-dashboard-data.xlsx'
    print(f"\nExporting to {output_file}...")
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        kpi_df.to_excel(writer, sheet_name='KPI Data', index=False)
        bar_df.to_excel(writer, sheet_name='Bar Chart Data', index=False)
        line_df.to_excel(writer, sheet_name='Line Chart Data', index=False)
        rolling_df.to_excel(writer, sheet_name='Rolling Average Data', index=False)
        detail_df.to_excel(writer, sheet_name='Detailed Review', index=False)
    
    print(f"  ✓ Excel file created with 5 sheets")
    print("\n" + "=" * 60)
    print("=" * 60)
    print("\nFile created: aai-dashboard-data.xlsx")
    print("\nSheets:")
    print("  1. KPI Data - KPI card values")
    print("  2. Bar Chart Data - Bar chart values for all time periods")
    print("  3. Line Chart Data - Time series data")
    print("  4. Rolling Average Data - 12-month rolling averages (for rolling chart)")
    print("  5. Detailed Review - Full data with indexed columns for verification")
    print("\nYou can now:")
    print("  - Export sheets 1-4 as CSV for WordPress upload")
    print("  - Use sheet 5 (Detailed Review) to verify calculations match expectations")
    print("  - The 'Abundance_Index' column matches the contributor's 'AAI' column")

    # Get most recent date
    most_recent = df['date'].max()
    month_name = most_recent.strftime('%B')
    year = most_recent.year
    print(f"\nMost recent data:")
    print(f"  {month_name} {year}")

if __name__ == "__main__":
    main()
