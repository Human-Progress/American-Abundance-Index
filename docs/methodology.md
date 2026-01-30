# American Abundance Index: Detailed Methodology

## Overview

The American Abundance Index (AAI) measures economic wellbeing by tracking purchasing power over time. It builds on the Time Price framework, which answers the question: "How many hours must a worker labor to afford a basket of goods?"

---

## Theoretical Foundation

### The Time Price Concept

Traditional economic measures often look at inflation (CPI) or wages in isolation. The Time Price methodology, pioneered by Gale Pooley and Marian Tupy, integrates both by measuring the hours of work required to purchase goods and services.

**Formula:**
```
Time Price = Price of Goods / Hourly Wage
```

When wages grow faster than prices, time prices fall—meaning workers can afford more with less labor.

### From Time Price to Abundance Index

The AAI inverts this relationship to create an intuitive index where:
- Higher values = Greater abundance
- 0 = Baseline year purchasing power
- Values above 0 = More purchasing power than baseline
- Values below 0 = Less purchasing power than baseline

**AAI Formula:**
```
AAI = (Hourly Earnings Index / Consumer Price Index)
```

---

## Data Collection

### Bureau of Labor Statistics (BLS) API

We query three primary data series from the BLS:

1. **CPI-U (Consumer Price Index - Urban Consumers)**
   - Series ID: `CUUR0000SA0`
   - Measures average change in prices paid by urban consumers
   - Seasonally adjusted
   - Base period: 1982-84 = 100

2. **Average Hourly Earnings - All Private Employees**
   - Series ID: `CES0500000003`
   - Total private sector
   - Current dollars
   - Seasonally adjusted

3. **Average Hourly Earnings - Production Workers**
   - Series ID: `CES0600000008`
   - Goods-producing industries
   - Production and nonsupervisory employees
   - Current dollars
   - Seasonally adjusted

4. **Average Hourly Earnings - Entry-Level Food Service**
   - Series ID: `CES7072251303`
   - Used for upskilling trajectory calculations
   - Current dollars
   - Seasonally adjusted

### Data Frequency and Updates

- **Frequency:** Monthly
- **Lag:** BLS data typically available 2-3 weeks after month end
- **Update Schedule:** Pipeline runs monthly after BLS releases

---

## Index Calculation

### Step 1: Normalize to Base Year

We normalize both CPI and hourly earnings to a common base year (March 2006, set to 100):
```python
normalized_value = (current_value / base_year_value)
```

### Step 2: Calculate AAI

For each worker category and time period:
```python
AAI = (Hourly_Earnings_Index / CPI)
```

### Step 3: Calculate Time Price
```python
Time_Price = (CPI / Hourly_Earnings_Index)
```

### Step 4: Upskilling Scenarios

Upskilling models simulate career progression from entry-level to higher-wage positions.

**Linear Interpolation Method:**

For a worker starting at entry-level wages and transitioning to target wages:
```python
def calculate_upskilling(entry_wage, target_wage, months_elapsed, total_months):
    if months_elapsed >= total_months:
        return target_wage
    
    progress_ratio = months_elapsed / total_months
    wage_differential = target_wage - entry_wage
    
    return entry_wage + (wage_differential × progress_ratio)
```

**Example:**
- Month 0: Worker earns entry-level food service wage
- Month 113 (halfway through period): Worker earns average of entry-level and target wage
- Month 226+: Worker earns target wage (all private-sector or blue-collar)

We model two upskilling scenarios:
- **Upskilling to All Private-Sector Jobs:** Transition from entry-level to average all private-sector wages
- **Upskilling to Blue-Collar Jobs:** Transition from entry-level to blue-collar wages

---

## Validation and Quality Control

### Data Integrity Checks

1. **Missing Data:** Flag any gaps in monthly data
2. **Outliers:** Identify values that deviate significantly from trend
3. **Consistency:** Verify that BLS series IDs haven't changed
4. **Logical Bounds:** Ensure AAI values are positive and reasonable

### Cross-Validation

We compare our calculated indices against:
- Published BLS inflation calculators
- Real wage growth statistics from other sources
- Historical economic indicators

---

## Limitations and Assumptions

### Assumptions

1. **Representative Wages:** BLS average hourly earnings represent typical worker experience
2. **CPI Basket:** Urban consumer price index reflects actual consumption patterns
3. **Linear Transitions:** Upskilling follows smooth, linear wage progression
4. **No Selection Bias:** Workers who upskill are representative of the category

### Known Limitations

1. **Aggregation:** National averages mask regional and demographic variation
2. **Benefits:** Index only captures wages, not total compensation (health insurance, retirement, etc.)
3. **Quality Changes:** CPI attempts to adjust for quality but may not fully capture improvements
4. **Composition Effects:** Changes in workforce composition can affect average wages
5. **Missing Data:** In rare cases when BLS data are missing (for example, inflation data for October 2025), the script does not interpolate values and instead leaves gaps in the time series

---

## Use Cases

### Academic Research
- Measuring long-term economic wellbeing trends
- Comparing purchasing power across decades
- Analyzing the impact of policy changes

### Policy Analysis
- Evaluating real wage growth
- Understanding economic mobility
- Assessing standard of living changes

### Public Communication
- Making economic data accessible
- Illustrating abundance vs. scarcity narratives
- Contextualizing current economic conditions

---

## References

Pooley, G., & Tupy, M. L. (2022). *Superabundance: The Story of Population Growth, Innovation, and Human Flourishing on an Infinitely Bountiful Planet*. Cato Institute.

Bureau of Labor Statistics. (n.d.). *CPI Home*. U.S. Department of Labor. https://www.bls.gov/cpi/

Bureau of Labor Statistics. (n.d.). *Current Employment Statistics*. U.S. Department of Labor. https://www.bls.gov/ces/
```
