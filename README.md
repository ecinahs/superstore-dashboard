# Superstore Sales Dashboard

An interactive dashboard for analyzing Superstore sales data with real-time filtering and beautiful visualizations.

## Features

- **Interactive Filters**: Filter by date range, category, region, customer segment, and shipping mode
- **Key Metrics**: Real-time KPIs including total sales, profit, orders, customers, and items sold
- **Visualizations**:
  - Sales and profit trends over time
  - Category and regional performance
  - Sub-category analysis
  - Customer segment distribution
  - Profit analysis by category and product
  - Discount impact analysis
  - Shipping mode performance
  - Geographic performance by state
  - Detailed transaction data table

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Dashboard

1. Navigate to the project directory:
```bash
cd c:\Users\zsr3s\data-analysis
```

2. Run the Streamlit app:
```bash
streamlit run dashboard.py
```

3. The dashboard will automatically open in your default web browser at `http://localhost:8501`

## Usage

- Use the **sidebar filters** on the left to filter data by:
  - Date range
  - Category (Furniture, Office Supplies, Technology)
  - Region (Central, East, South, West)
  - Customer Segment (Consumer, Corporate, Home Office)
  - Ship Mode

- **Key metrics** are displayed at the top showing totals and averages

- Scroll down to explore various **interactive visualizations**

- Use the **search box** at the bottom to find specific products or customers

- **Hover** over charts for detailed information

- **Click and drag** on charts to zoom in on specific areas

## Files

- `dashboard.py` - Main Streamlit dashboard application
- `requirements.txt` - Python dependencies
- `01_raw_data/Sample - Superstore.csv` - Source data file
- `03_notebooks/Superstore_Analysis.ipynb` - Jupyter notebook with detailed analysis

## Deployment

Want to share your dashboard online? Check out the **[PUBLISHING_GUIDE.md](PUBLISHING_GUIDE.md)** for detailed instructions on deploying to:

- 🌟 **Streamlit Community Cloud** (Recommended - FREE)
- ☁️ **Heroku**
- 🚀 **Other cloud platforms** (Render, Railway, etc.)
- 🏠 **Local network sharing**

### Quick Deploy to Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your repository
4. Deploy with one click!

## Tips

- Try different filter combinations to uncover insights
- Look for trends in the time series charts
- Compare performance across categories and regions
- Identify top-performing and loss-making products
- Analyze the impact of discounts on profitability

## Data Analysis

A comprehensive Python analysis script is available at `basic_analysis.py` which provides:
- Dataset overview and data quality checks
- Financial summary statistics
- Sales breakdown by category, region, and customer segment
- Top performing sub-categories and states
- Shipping mode analysis

Run it with:
```bash
python basic_analysis.py
```

## License

This project uses the Sample Superstore dataset for educational and demonstration purposes.

## Screenshots

The dashboard features:
- 🎨 Beautiful mint green theme
- 📊 10+ interactive visualizations
- 🔍 Advanced filtering capabilities
- 📱 Responsive design
- 💾 Data export functionality
