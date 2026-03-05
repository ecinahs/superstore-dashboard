import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv(r'c:\Users\zsr3s\data-analysis\01_raw_data\Sample - Superstore.csv', encoding='latin-1')

print("=" * 80)
print("SUPERSTORE DATA ANALYSIS")
print("=" * 80)

# Basic dataset information
print("\n1. DATASET OVERVIEW")
print("-" * 80)
print(f"Total number of records: {len(df):,}")
print(f"Total number of columns: {len(df.columns)}")
print(f"Date range: {df['Order Date'].min()} to {df['Order Date'].max()}")
print(f"\nColumn names:\n{', '.join(df.columns.tolist())}")

# Check for missing values
print("\n2. DATA QUALITY CHECK")
print("-" * 80)
missing_values = df.isnull().sum()
if missing_values.sum() > 0:
    print("Missing values found:")
    print(missing_values[missing_values > 0])
else:
    print("No missing values found - data quality is good!")

# Summary statistics for numerical columns
print("\n3. FINANCIAL SUMMARY STATISTICS")
print("-" * 80)
print(df[['Sales', 'Quantity', 'Discount', 'Profit']].describe())

# Total metrics
print("\n4. KEY BUSINESS METRICS")
print("-" * 80)
print(f"Total Sales: ${df['Sales'].sum():,.2f}")
print(f"Total Profit: ${df['Profit'].sum():,.2f}")
print(f"Overall Profit Margin: {(df['Profit'].sum() / df['Sales'].sum() * 100):.2f}%")
print(f"Total Quantity Sold: {df['Quantity'].sum():,} units")
print(f"Average Order Value: ${df['Sales'].mean():,.2f}")
print(f"Number of Unique Customers: {df['Customer ID'].nunique():,}")
print(f"Number of Unique Orders: {df['Order ID'].nunique():,}")

# Sales by Category
print("\n5. SALES BY CATEGORY")
print("-" * 80)
category_sales = df.groupby('Category').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Order ID': 'count'
}).round(2)
category_sales.columns = ['Total Sales', 'Total Profit', 'Number of Orders']
category_sales['Profit Margin %'] = (category_sales['Total Profit'] / category_sales['Total Sales'] * 100).round(2)
category_sales = category_sales.sort_values('Total Sales', ascending=False)
print(category_sales)

# Sales by Region
print("\n6. SALES BY REGION")
print("-" * 80)
region_sales = df.groupby('Region').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Order ID': 'count'
}).round(2)
region_sales.columns = ['Total Sales', 'Total Profit', 'Number of Orders']
region_sales['Profit Margin %'] = (region_sales['Total Profit'] / region_sales['Total Sales'] * 100).round(2)
region_sales = region_sales.sort_values('Total Sales', ascending=False)
print(region_sales)

# Sales by Customer Segment
print("\n7. SALES BY CUSTOMER SEGMENT")
print("-" * 80)
segment_sales = df.groupby('Segment').agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Order ID': 'count'
}).round(2)
segment_sales.columns = ['Total Sales', 'Total Profit', 'Number of Orders']
segment_sales['Profit Margin %'] = (segment_sales['Total Profit'] / segment_sales['Total Sales'] * 100).round(2)
segment_sales = segment_sales.sort_values('Total Sales', ascending=False)
print(segment_sales)

# Top 10 Sub-Categories by Sales
print("\n8. TOP 10 SUB-CATEGORIES BY SALES")
print("-" * 80)
top_subcategories = df.groupby('Sub-Category').agg({
    'Sales': 'sum',
    'Profit': 'sum'
}).round(2)
top_subcategories.columns = ['Total Sales', 'Total Profit']
top_subcategories['Profit Margin %'] = (top_subcategories['Total Profit'] / top_subcategories['Total Sales'] * 100).round(2)
top_subcategories = top_subcategories.sort_values('Total Sales', ascending=False).head(10)
print(top_subcategories)

# Top 10 States by Sales
print("\n9. TOP 10 STATES BY SALES")
print("-" * 80)
top_states = df.groupby('State').agg({
    'Sales': 'sum',
    'Profit': 'sum'
}).round(2)
top_states.columns = ['Total Sales', 'Total Profit']
top_states = top_states.sort_values('Total Sales', ascending=False).head(10)
print(top_states)

# Ship Mode Analysis
print("\n10. SHIPPING MODE ANALYSIS")
print("-" * 80)
ship_mode = df.groupby('Ship Mode').agg({
    'Order ID': 'count',
    'Sales': 'sum'
}).round(2)
ship_mode.columns = ['Number of Orders', 'Total Sales']
ship_mode['% of Total Orders'] = (ship_mode['Number of Orders'] / ship_mode['Number of Orders'].sum() * 100).round(2)
ship_mode = ship_mode.sort_values('Number of Orders', ascending=False)
print(ship_mode)

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
