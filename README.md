# American Abundance Index

A comprehensive measure of economic wellbeing that tracks how purchasing power changes over time by comparing wage growth to consumer price inflation.

**Live Dashboard:** 

**Maintained by:** [Human Progress](https://www.humanprogress.org/) at the Cato Institute

---

## What is the American Abundance Index?

The American Abundance Index (AAI) uses the Time Price methodology developed by economists Gale Pooley and Marian Tupy to measure changes in economic abundance. 
Rather than simply tracking inflation or wages in isolation, the AAI shows how much more (or less) purchasing power American workers have gained over time.

### Key Features

- **Multiple Worker Categories:** Tracks abundance for all private-sector workers, blue-collar workers, and upskilling scenarios
- **Time Price Methodology:** Measures how many hours of work are required to purchase a constant basket of goods
- **Historical Perspective:** Data from March 2006 to present
- **Monthly Updates:** Automatically updated with latest Bureau of Labor Statistics data

---

## Methodology

The AAI is calculated by comparing the Consumer Price Index (CPI) to average hourly earnings for different worker categories:
```
AAI = (Hourly Earnings Index / CPI) × 100
```

An AAI above 0 indicates workers can afford more than the baseline year; below 0 indicates less purchasing power.

### Worker Categories

1. **All Private-Sector Workers:** Average hourly earnings for all private sector employees
2. **Blue-Collar Workers:** Production and nonsupervisory employees in goods-producing industries
3. **Upskilling Scenarios:** Models career progression from entry-level to higher-wage work over time

### Upskilling Models

We model workers who transition from entry-level positions to higher-paying roles over their career:

- **Upskilling to All Private-Sector Jobs:** Gradual transition from entry-level wages to average all private-sector wages
- **Upskilling to Blue-Collar Jobs:** Gradual transition from entry-level wages to blue-collar wages

These scenarios demonstrate how career development and skill acquisition affect purchasing power over a worker's lifetime.

---

## Data Sources

All data comes from the U.S. Bureau of Labor Statistics (BLS) via their public API:

- **Consumer Price Index:** Series ID `CUUR0000SA0`
- **All Private-Sector Workers Hourly Earnings:** Series ID `CES0500000003`
- **Blue-Collar Hourly Earnings:** Series ID `CES0600000008`
- **Entry-Level Food Service Hourly Earnings:** Series ID `CES7072251303`

---

## Repository Structure
```
├── data/
│   └── processed/          # Latest processed data in Excel format
├── src/                    # Python pipeline scripts
│   ├── fetch_and_process_data.py
│   └── README.md
├── docs/                   # Detailed documentation
│   ├── methodology.md
│   ├── data-dictionary.md
│   └── setup-guide.md
└── examples/               # Simple visualization examples
    ├── visualization_example.html
    └── README.md
```

---

## Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Running the Pipeline

1. Get a free BLS API key at https://data.bls.gov/registrationEngine/
2. Add your key to `src/fetch_and_process_data.py` (line 14)
3. Run the script:
```bash
python src/fetch_and_process_data.py
```

This will fetch the latest BLS data and generate `aai-dashboard-data.xlsx` with 5 sheets:
- KPI Data
- Bar Chart Data
- Line Chart Data
- Rolling Average Data
- Detailed Review

See `docs/setup-guide.md` for detailed installation instructions.

---

## Using the Data

The processed data is available in `data/processed/` in Excel format with multiple sheets. Each sheet contains data organized for specific visualization purposes.

See `docs/data-dictionary.md` for detailed column descriptions.

### Creating Visualizations

The `examples/` folder contains a simple D3.js visualization showing how to load and display the AAI data. This serves as a starting point for creating your own charts and dashboards.

---

## Citation

If you use this data or methodology in your research or publications, please cite:
```
Human Progress. (2026). American Abundance Index. Cato Institute. 
Retrieved from https://github.com/YOUR_USERNAME/american-abundance-index
```

For the underlying Time Price methodology, please cite:
```
Tupy, M. L., & Pooley, G. (2022). Superabundance: The Story of Population Growth, 
Innovation, and Human Flourishing on an Infinitely Bountiful Planet. 
Cato Institute.
```

---

## Contributing

We welcome contributions! Please feel free to:

- Report issues or bugs
- Suggest improvements to the methodology
- Submit pull requests with enhancements

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This means you are free to use, modify, and distribute this code and data, provided you include the original copyright notice and license.

---

## Contact

For questions or feedback:
- **Website:** https://www.humanprogress.org
- **Email:** Contact via GitHub Issues
- **Issues:** Use GitHub Issues for bug reports and feature requests

---

## Acknowledgments

This project builds on the Time Price methodology developed by Gale Pooley and Marian Tupy. Special thanks to all contributors at the Cato Institute's Center for Global Liberty & Prosperity.

---

**Last Updated:** January 30, 2025
