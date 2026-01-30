# Visualization Examples

This directory contains simple examples demonstrating how to load and visualize the American Abundance Index data.

---

## Files

- **visualization_example.html** - Interactive D3.js line chart example

---

## visualization_example.html

A standalone HTML file that demonstrates:

- Loading data from the Excel file using SheetJS
- Creating an interactive D3.js line chart
- Displaying Abundance Index over time for all private-sector workers
- Adding tooltips and hover interactions

### Features

- **Self-contained:** No external dependencies beyond CDN libraries
- **Well-commented:** Code explains each step
- **Interactive:** Hover to see values, zoom and pan
- **Responsive:** Works on desktop and mobile

### How to Use

1. Download `aai_data_YYYY-MM-DD.xlsx` from `data/processed/`
2. Place it in the same directory as `visualization_example.html`
3. Open `visualization_example.html` in a web browser

**Note:** For local file access, you may need to run a simple HTTP server:
```bash
# Python 3
python -m http.server 8000

# Then visit: http://localhost:8000/visualization_example.html
```

### Customization

The example is designed to be easily modified:

- **Change metric:** Modify the code to show CPI, Wage, or Time Price instead of Abundance
- **Change view:** Modify to show blue-collar or upskilling data
- **Change colors:** Update color schemes
- **Add multiple lines:** Display multiple metrics on one chart

---

## Creating Your Own Visualizations

### Data Structure

The Excel file contains multiple sheets. For line charts, use the "Line Chart Data" sheet:
```javascript
// After loading with SheetJS
const workbook = XLSX.read(data, {type: 'array'});
const lineData = XLSX.utils.sheet_to_json(
    workbook.Sheets['Line Chart Data']
);

// Filter for your desired view
const allWorkersData = lineData.filter(d => d.view === 'all-workers');
```

### Available Views

- `all-workers` - All private-sector workers
- `blue-collar` - Blue-collar workers
- `upskilling-all` - Workers upskilling to all private-sector jobs
- `upskilling-blue` - Workers upskilling to blue-collar jobs

### Available Metrics

- `Abundance` - Abundance index (% from base)
- `Time_Price` - Time price (% from base)
- `Wage` - Average hourly earnings (% from base)
- `CPI` - Consumer Price Index (% from base)

---

## Other Visualization Ideas

### Bar Chart Example

Show period-over-period changes using "Bar Chart Data" sheet:
```javascript
const barData = XLSX.utils.sheet_to_json(
    workbook.Sheets['Bar Chart Data']
);

// Filter for 1-year changes, all workers
const yearlyChanges = barData.filter(d => 
    d.view === 'all-workers' && 
    d.period === '1-year'
);

// Create D3 bar chart with yearlyChanges
```

### KPI Dashboard

Create summary cards using "KPI Data" sheet:
```javascript
const kpiData = XLSX.utils.sheet_to_json(
    workbook.Sheets['KPI Data']
);

// Get monthly abundance change for all workers
const abundanceMonthly = kpiData.find(d => 
    d.view === 'all-workers' && 
    d.metric === 'abundance'
).monthly;

// Display in a card: `${abundanceMonthly}%`
```

### Rolling Average Chart

Show smoothed trends using "Rolling Average Data" sheet:
```javascript
const rollingData = XLSX.utils.sheet_to_json(
    workbook.Sheets['Rolling Average Data']
);

// Create area chart showing wage growth vs CPI growth
```

---

## Libraries Used

The example uses these CDN-hosted libraries:

- **D3.js v7:** Visualization framework
  - https://cdn.jsdelivr.net/npm/d3@7
  
- **SheetJS (xlsx):** Excel file parsing
  - https://cdn.sheetjs.com/xlsx-latest/package/dist/xlsx.full.min.js

No installation required - libraries load from CDN when you open the HTML file.

---

## Browser Compatibility

Tested and working in:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Note:** Internet Explorer is not supported (use a modern browser).

---

## Troubleshooting

### Chart Doesn't Appear

1. **Check console for errors:** Press F12 to open developer tools
2. **Verify file path:** Ensure Excel file is in same directory
3. **Check file name:** Update the filename in the HTML if different
4. **Run local server:** Some browsers block local file access

### Data Doesn't Load

1. **Verify Excel file format:** Must be `.xlsx` (not `.xls` or `.csv`)
2. **Check sheet names:** Must match exactly ("Line Chart Data")
3. **Verify data structure:** Open file to confirm columns match expected format

### Styling Issues

1. **CSS not loading:** Check that `<style>` block is present in `<head>`
2. **Chart too small:** Adjust `width` and `height` variables in JavaScript
3. **Labels cut off:** Increase margin values in D3 setup

---

## Next Steps

- Review `docs/data-dictionary.md` to understand all available columns
- See `docs/methodology.md` for calculation details
- Explore the full dashboard at https://humanprogress.org/american-abundance-index
- Create your own custom visualizations using this example as a starting point

---

## Contributing Examples

Have a great visualization idea? We welcome contributions!

1. Fork the repository
2. Add your example with clear comments
3. Update this README with description
4. Submit a pull request
```
