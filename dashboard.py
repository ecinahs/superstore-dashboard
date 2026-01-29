import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Superstore Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1f77b4;
        padding-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data with caching
@st.cache_data
def load_data():
    df = pd.read_csv('01_raw_data/Sample - Superstore.csv', encoding='latin-1')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['Quarter'] = df['Order Date'].dt.quarter
    df['Month-Year'] = df['Order Date'].dt.to_period('M').astype(str)
    return df

# Load the data
df = load_data()

# Title and description
st.title("📊 Superstore Sales Dashboard")
st.markdown("### Interactive analysis of sales, profit, and customer behavior")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Date range filter
min_date = df['Order Date'].min().date()
max_date = df['Order Date'].max().date()
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Category filter
categories = ['All'] + sorted(df['Category'].unique().tolist())
selected_category = st.sidebar.selectbox("Select Category", categories)

# Region filter
regions = ['All'] + sorted(df['Region'].unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", regions)

# Segment filter
segments = ['All'] + sorted(df['Segment'].unique().tolist())
selected_segment = st.sidebar.selectbox("Select Customer Segment", segments)

# Ship Mode filter
ship_modes = ['All'] + sorted(df['Ship Mode'].unique().tolist())
selected_ship_mode = st.sidebar.selectbox("Select Ship Mode", ship_modes)

# Apply filters
filtered_df = df.copy()

# Date filter
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df['Order Date'].dt.date >= start_date) &
        (filtered_df['Order Date'].dt.date <= end_date)
    ]

# Category filter
if selected_category != 'All':
    filtered_df = filtered_df[filtered_df['Category'] == selected_category]

# Region filter
if selected_region != 'All':
    filtered_df = filtered_df[filtered_df['Region'] == selected_region]

# Segment filter
if selected_segment != 'All':
    filtered_df = filtered_df[filtered_df['Segment'] == selected_segment]

# Ship Mode filter
if selected_ship_mode != 'All':
    filtered_df = filtered_df[filtered_df['Ship Mode'] == selected_ship_mode]

# Check if data is available after filtering
if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters. Please adjust your selection.")
    st.stop()

# Key Metrics Row
st.markdown("---")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_sales = filtered_df['Sales'].sum()
    st.metric(
        label="💰 Total Sales",
        value=f"${total_sales:,.0f}",
        delta=f"{len(filtered_df)} transactions"
    )

with col2:
    total_profit = filtered_df['Profit'].sum()
    profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
    st.metric(
        label="📈 Total Profit",
        value=f"${total_profit:,.0f}",
        delta=f"{profit_margin:.2f}% margin"
    )

with col3:
    total_orders = filtered_df['Order ID'].nunique()
    avg_order_value = filtered_df.groupby('Order ID')['Sales'].sum().mean()
    st.metric(
        label="🛒 Total Orders",
        value=f"{total_orders:,}",
        delta=f"${avg_order_value:.2f} avg"
    )

with col4:
    total_customers = filtered_df['Customer ID'].nunique()
    avg_customer_value = total_sales / total_customers if total_customers > 0 else 0
    st.metric(
        label="👥 Total Customers",
        value=f"{total_customers:,}",
        delta=f"${avg_customer_value:.2f} avg"
    )

with col5:
    total_quantity = filtered_df['Quantity'].sum()
    avg_discount = filtered_df['Discount'].mean() * 100
    st.metric(
        label="📦 Items Sold",
        value=f"{total_quantity:,}",
        delta=f"{avg_discount:.1f}% avg discount"
    )

st.markdown("---")

# Row 1: Sales and Profit Trends
st.subheader("📊 Sales & Profit Trends Over Time")
col1, col2 = st.columns(2)

with col1:
    # Monthly sales trend
    monthly_sales = filtered_df.groupby('Month-Year')['Sales'].sum().reset_index()
    fig_sales_trend = px.line(
        monthly_sales,
        x='Month-Year',
        y='Sales',
        title='Monthly Sales Trend',
        labels={'Sales': 'Sales ($)', 'Month-Year': 'Month'},
        markers=True
    )
    fig_sales_trend.update_layout(
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_sales_trend, use_container_width=True)

with col2:
    # Monthly profit trend
    monthly_profit = filtered_df.groupby('Month-Year')['Profit'].sum().reset_index()
    fig_profit_trend = px.line(
        monthly_profit,
        x='Month-Year',
        y='Profit',
        title='Monthly Profit Trend',
        labels={'Profit': 'Profit ($)', 'Month-Year': 'Month'},
        markers=True,
        color_discrete_sequence=['#2ecc71']
    )
    fig_profit_trend.update_layout(
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig_profit_trend, use_container_width=True)

st.markdown("---")

# Row 2: Category and Regional Analysis
st.subheader("🏪 Category & Regional Performance")
col1, col2 = st.columns(2)

with col1:
    # Sales by Category
    category_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index().sort_values('Sales', ascending=False)
    fig_category = px.bar(
        category_sales,
        x='Category',
        y='Sales',
        title='Sales by Category',
        labels={'Sales': 'Sales ($)'},
        color='Sales',
        color_continuous_scale='Blues'
    )
    fig_category.update_layout(showlegend=False)
    st.plotly_chart(fig_category, use_container_width=True)

with col2:
    # Sales by Region
    region_sales = filtered_df.groupby('Region')['Sales'].sum().reset_index().sort_values('Sales', ascending=False)
    fig_region = px.bar(
        region_sales,
        x='Region',
        y='Sales',
        title='Sales by Region',
        labels={'Sales': 'Sales ($)'},
        color='Sales',
        color_continuous_scale='Greens'
    )
    fig_region.update_layout(showlegend=False)
    st.plotly_chart(fig_region, use_container_width=True)

st.markdown("---")

# Row 3: Sub-Category and Segment Analysis
st.subheader("📦 Sub-Category & Customer Segment Analysis")
col1, col2 = st.columns(2)

with col1:
    # Top 10 Sub-Categories by Sales
    subcategory_sales = filtered_df.groupby('Sub-Category')['Sales'].sum().reset_index().sort_values('Sales', ascending=False).head(10)
    fig_subcategory = px.bar(
        subcategory_sales,
        y='Sub-Category',
        x='Sales',
        title='Top 10 Sub-Categories by Sales',
        labels={'Sales': 'Sales ($)'},
        orientation='h',
        color='Sales',
        color_continuous_scale='Oranges'
    )
    fig_subcategory.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_subcategory, use_container_width=True)

with col2:
    # Segment Distribution
    segment_data = filtered_df.groupby('Segment').agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()

    fig_segment = px.pie(
        segment_data,
        values='Sales',
        names='Segment',
        title='Sales Distribution by Customer Segment',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_segment.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_segment, use_container_width=True)

st.markdown("---")

# Row 4: Profit Analysis
st.subheader("💰 Profit Analysis")
col1, col2 = st.columns(2)

with col1:
    # Profit by Category
    category_profit = filtered_df.groupby('Category').agg({
        'Profit': 'sum',
        'Sales': 'sum'
    }).reset_index()
    category_profit['Profit Margin %'] = (category_profit['Profit'] / category_profit['Sales'] * 100).round(2)

    fig_profit_category = px.bar(
        category_profit,
        x='Category',
        y='Profit',
        title='Profit by Category',
        labels={'Profit': 'Profit ($)'},
        color='Profit Margin %',
        color_continuous_scale='RdYlGn',
        text='Profit Margin %'
    )
    fig_profit_category.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig_profit_category, use_container_width=True)

with col2:
    # Top 10 Most Profitable Products
    product_profit = filtered_df.groupby('Product Name')['Profit'].sum().reset_index().sort_values('Profit', ascending=False).head(10)
    fig_product_profit = px.bar(
        product_profit,
        y='Product Name',
        x='Profit',
        title='Top 10 Most Profitable Products',
        labels={'Profit': 'Profit ($)'},
        orientation='h',
        color='Profit',
        color_continuous_scale='Greens'
    )
    fig_product_profit.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_product_profit, use_container_width=True)

st.markdown("---")

# Row 5: Discount Analysis and Shipping
st.subheader("🎯 Discount Impact & Shipping Analysis")
col1, col2 = st.columns(2)

with col1:
    # Discount vs Profit scatter
    sample_df = filtered_df.sample(min(1000, len(filtered_df)))  # Sample for performance
    fig_discount = px.scatter(
        sample_df,
        x='Discount',
        y='Profit',
        title='Discount vs Profit Relationship',
        labels={'Discount': 'Discount Rate', 'Profit': 'Profit ($)'},
        color='Category',
        opacity=0.6,
        trendline='ols'
    )
    fig_discount.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_discount, use_container_width=True)

with col2:
    # Shipping Mode Analysis
    ship_mode_data = filtered_df.groupby('Ship Mode').agg({
        'Sales': 'sum',
        'Order ID': 'nunique'
    }).reset_index()
    ship_mode_data.columns = ['Ship Mode', 'Sales', 'Orders']

    fig_ship = px.bar(
        ship_mode_data,
        x='Ship Mode',
        y='Orders',
        title='Orders by Shipping Mode',
        labels={'Orders': 'Number of Orders'},
        color='Sales',
        color_continuous_scale='Purples',
        text='Orders'
    )
    fig_ship.update_traces(textposition='outside')
    st.plotly_chart(fig_ship, use_container_width=True)

st.markdown("---")

# Row 6: Geographic Analysis
st.subheader("🗺️ Geographic Performance")
col1, col2 = st.columns([2, 1])

with col1:
    # Top 15 States by Sales
    state_sales = filtered_df.groupby('State').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique'
    }).reset_index().sort_values('Sales', ascending=False).head(15)
    state_sales.columns = ['State', 'Sales', 'Profit', 'Orders']

    fig_states = px.bar(
        state_sales,
        y='State',
        x='Sales',
        title='Top 15 States by Sales',
        labels={'Sales': 'Sales ($)'},
        orientation='h',
        color='Profit',
        color_continuous_scale='Viridis'
    )
    fig_states.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig_states, use_container_width=True)

with col2:
    # Regional Summary Table
    st.markdown("#### Regional Summary")
    regional_summary = filtered_df.groupby('Region').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique'
    }).round(2)
    regional_summary.columns = ['Sales ($)', 'Profit ($)', 'Orders']
    regional_summary['Profit Margin %'] = (regional_summary['Profit ($)'] / regional_summary['Sales ($)'] * 100).round(2)
    st.dataframe(regional_summary, use_container_width=True)

st.markdown("---")

# Row 7: Detailed Data Table
st.subheader("📋 Detailed Transaction Data")

# Add search and sort options
col1, col2 = st.columns([3, 1])
with col1:
    search_term = st.text_input("🔍 Search products or customers", "")
with col2:
    num_rows = st.selectbox("Rows to display", [10, 25, 50, 100], index=1)

# Filter data based on search
display_df = filtered_df.copy()
if search_term:
    display_df = display_df[
        display_df['Product Name'].str.contains(search_term, case=False, na=False) |
        display_df['Customer Name'].str.contains(search_term, case=False, na=False)
    ]

# Select columns to display
display_columns = [
    'Order Date', 'Customer Name', 'Segment', 'Region', 'Category',
    'Sub-Category', 'Product Name', 'Sales', 'Quantity', 'Discount', 'Profit'
]

# Display the table
st.dataframe(
    display_df[display_columns].head(num_rows).style.format({
        'Sales': '${:,.2f}',
        'Profit': '${:,.2f}',
        'Discount': '{:.1%}'
    }),
    use_container_width=True,
    height=400
)

st.markdown(f"Showing {min(num_rows, len(display_df))} of {len(display_df)} records")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>📊 Superstore Sales Dashboard | Data Analysis Tool</p>
        <p>Use the filters in the sidebar to explore different segments of your data</p>
    </div>
""", unsafe_allow_html=True)
