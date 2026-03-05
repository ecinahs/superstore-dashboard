import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Testing Dashboard For Me",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling with Mint Green background
st.markdown("""
    <style>
    /* Mint green gradient background */
    .stApp {
        background: linear-gradient(135deg, #e0f7f4 0%, #b8f2e6 50%, #95e1d3 100%);
    }

    .main {
        padding: 0rem 1rem;
    }

    /* Metric cards with white background */
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #b8f2e6 0%, #95e1d3 100%);
    }

    /* Title color */
    h1 {
        color: #0d9488;
        padding-bottom: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    /* Subheader color */
    h2, h3 {
        color: #0f766e;
    }

    /* Chart containers */
    .element-container {
        background-color: white;
        border-radius: 10px;
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
st.title("TESTING DASHBOARD FOR ME")
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

# Product Performance Analysis - 4 Key Charts
st.subheader("🏪 Product Performance Analysis")
st.markdown("##### Key insights into product categories, regions, and profitability")
st.markdown("")

# Row 1: Category and Regional Sales
col1, col2 = st.columns(2)

with col1:
    # Sales by Category
    category_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index().sort_values('Sales', ascending=False)
    fig_category = px.bar(
        category_sales,
        x='Category',
        y='Sales',
        title='💼 Sales by Category',
        labels={'Sales': 'Sales ($)'},
        color='Sales',
        color_continuous_scale='Teal',
        text='Sales'
    )
    fig_category.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig_category.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        margin=dict(t=50, b=50, l=50, r=50)
    )
    st.plotly_chart(fig_category, use_container_width=True)

with col2:
    # Sales by Region
    region_sales = filtered_df.groupby('Region')['Sales'].sum().reset_index().sort_values('Sales', ascending=False)
    fig_region = px.bar(
        region_sales,
        x='Region',
        y='Sales',
        title='🗺️ Sales by Region',
        labels={'Sales': 'Sales ($)'},
        color='Sales',
        color_continuous_scale='Mint',
        text='Sales'
    )
    fig_region.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig_region.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        margin=dict(t=50, b=50, l=50, r=50)
    )
    st.plotly_chart(fig_region, use_container_width=True)

st.markdown("")

# Row 2: Sub-Categories and Top Products
col1, col2 = st.columns(2)

with col1:
    # Top 10 Sub-Categories by Sales
    subcategory_sales = filtered_df.groupby('Sub-Category')['Sales'].sum().reset_index().sort_values('Sales', ascending=False).head(10)
    fig_subcategory = px.bar(
        subcategory_sales,
        y='Sub-Category',
        x='Sales',
        title='📦 Top 10 Sub-Categories by Sales',
        labels={'Sales': 'Sales ($)'},
        orientation='h',
        color='Sales',
        color_continuous_scale='Emrld',
        text='Sales'
    )
    fig_subcategory.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig_subcategory.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        margin=dict(t=50, b=50, l=150, r=50),
        height=500
    )
    st.plotly_chart(fig_subcategory, use_container_width=True)

with col2:
    # Top 10 Most Profitable Products
    product_profit = filtered_df.groupby('Product Name')['Profit'].sum().reset_index().sort_values('Profit', ascending=False).head(10)
    fig_product_profit = px.bar(
        product_profit,
        y='Product Name',
        x='Profit',
        title='💰 Top 10 Most Profitable Products',
        labels={'Profit': 'Profit ($)'},
        orientation='h',
        color='Profit',
        color_continuous_scale='Tealgrn',
        text='Profit'
    )
    fig_product_profit.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig_product_profit.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        margin=dict(t=50, b=50, l=200, r=50),
        height=500
    )
    st.plotly_chart(fig_product_profit, use_container_width=True)

st.markdown("---")

# Row 3: Sales Trends and Customer Segments
st.subheader("📊 Trends & Customer Analysis")
st.markdown("##### Sales performance over time and customer segment insights")
st.markdown("")

col1, col2 = st.columns(2)

with col1:
    # Sales Trend Over Time
    monthly_sales = filtered_df.groupby('Month-Year').agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()

    from plotly.subplots import make_subplots
    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trend.add_trace(
        go.Scatter(x=monthly_sales['Month-Year'], y=monthly_sales['Sales'],
                   name="Sales", line=dict(color='#0d9488', width=3),
                   fill='tozeroy', fillcolor='rgba(13, 148, 136, 0.2)'),
        secondary_y=False
    )
    fig_trend.add_trace(
        go.Scatter(x=monthly_sales['Month-Year'], y=monthly_sales['Profit'],
                   name="Profit", line=dict(color='#f59e0b', width=3)),
        secondary_y=True
    )
    fig_trend.update_xaxes(title_text="Month")
    fig_trend.update_yaxes(title_text="Sales ($)", secondary_y=False)
    fig_trend.update_yaxes(title_text="Profit ($)", secondary_y=True)
    fig_trend.update_layout(
        title='📈 Sales & Profit Trend Over Time',
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col2:
    # Customer Segment Distribution
    segment_data = filtered_df.groupby('Segment').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'count'
    }).reset_index()

    fig_segment = px.pie(
        segment_data,
        values='Sales',
        names='Segment',
        title='👥 Sales Distribution by Customer Segment',
        hole=0.4,
        color_discrete_sequence=['#0d9488', '#14b8a6', '#5eead4']
    )
    fig_segment.update_traces(textposition='inside', textinfo='percent+label')
    fig_segment.update_layout(
        paper_bgcolor='white',
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    st.plotly_chart(fig_segment, use_container_width=True)

st.markdown("---")

# Row 4: Shipping and Profit/Loss Analysis
st.subheader("📦 Shipping & Profitability Analysis")
st.markdown("##### Shipping mode preferences and profit distribution")
st.markdown("")

col1, col2 = st.columns(2)

with col1:
    # Shipping Mode Analysis
    ship_data = filtered_df.groupby('Ship Mode').agg({
        'Order ID': 'count',
        'Sales': 'sum'
    }).reset_index()
    ship_data.columns = ['Ship Mode', 'Number of Orders', 'Total Sales']
    ship_data = ship_data.sort_values('Number of Orders', ascending=False)

    fig_ship = go.Figure()
    fig_ship.add_trace(go.Bar(
        x=ship_data['Ship Mode'],
        y=ship_data['Number of Orders'],
        name='Orders',
        marker_color=['#0d9488', '#14b8a6', '#5eead4', '#99f6e4'],
        text=ship_data['Number of Orders'],
        textposition='outside'
    ))
    fig_ship.update_layout(
        title='📮 Orders by Shipping Mode',
        xaxis_title="Ship Mode",
        yaxis_title="Number of Orders",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        height=400,
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    st.plotly_chart(fig_ship, use_container_width=True)

with col2:
    # Profit vs Loss Distribution
    profit_orders = len(filtered_df[filtered_df['Profit'] > 0])
    loss_orders = len(filtered_df[filtered_df['Profit'] < 0])
    breakeven_orders = len(filtered_df[filtered_df['Profit'] == 0])

    total_profit_amt = filtered_df[filtered_df['Profit'] > 0]['Profit'].sum()
    total_loss_amt = abs(filtered_df[filtered_df['Profit'] < 0]['Profit'].sum())

    profit_loss_data = pd.DataFrame({
        'Category': ['Profitable Orders', 'Loss Orders', 'Break-even'],
        'Count': [profit_orders, loss_orders, breakeven_orders],
        'Amount': [total_profit_amt, total_loss_amt, 0]
    })

    fig_profit_loss = go.Figure(data=[
        go.Bar(
            x=profit_loss_data['Category'],
            y=profit_loss_data['Count'],
            marker_color=['#0d9488', '#ef4444', '#fbbf24'],
            text=profit_loss_data['Count'],
            textposition='outside',
            customdata=profit_loss_data['Amount'],
            hovertemplate='<b>%{x}</b><br>Orders: %{y}<br>Amount: $%{customdata:,.2f}<extra></extra>'
        )
    ])
    fig_profit_loss.update_layout(
        title='💰 Profit vs Loss Distribution',
        yaxis_title="Number of Orders",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    st.plotly_chart(fig_profit_loss, use_container_width=True)

st.markdown("---")

# Row 5: Top States and Discount Analysis
st.subheader("🗺️ Geographic & Discount Insights")
st.markdown("##### State-level performance and discount impact")
st.markdown("")

col1, col2 = st.columns(2)

with col1:
    # Top 10 States by Sales
    state_data = filtered_df.groupby('State').agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    state_data['Profit Margin %'] = (state_data['Profit'] / state_data['Sales'] * 100).round(2)
    top_states = state_data.sort_values('Sales', ascending=False).head(10)

    fig_states = px.bar(
        top_states,
        x='Sales',
        y='State',
        orientation='h',
        color='Profit Margin %',
        color_continuous_scale='RdYlGn',
        title='🏆 Top 10 States by Sales',
        text='Sales'
    )
    fig_states.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig_states.update_layout(
        yaxis={'categoryorder':'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        height=400,
        margin=dict(t=50, b=50, l=100, r=50)
    )
    st.plotly_chart(fig_states, use_container_width=True)

with col2:
    # Discount vs Profit Analysis
    discount_analysis = filtered_df.groupby('Discount').agg({
        'Profit': 'mean',
        'Sales': 'sum',
        'Order ID': 'count'
    }).reset_index()

    fig_discount = px.scatter(
        discount_analysis,
        x='Discount',
        y='Profit',
        size='Order ID',
        color='Sales',
        title='💸 Discount Impact on Average Profit',
        labels={'Discount': 'Discount Rate', 'Profit': 'Average Profit ($)', 'Order ID': 'Order Count'},
        color_continuous_scale='Teal'
    )
    fig_discount.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='white',
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    st.plotly_chart(fig_discount, use_container_width=True)

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
        <p>TESTING DASHBOARD FOR ME | Data Analysis Tool</p>
        <p>Use the filters in the sidebar to explore different segments of your data</p>
    </div>
""", unsafe_allow_html=True)
