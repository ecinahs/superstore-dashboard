import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / '02_processed_data' / 'superstore_clean.csv'

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Superstore Dashboard",
    page_icon="🛒",
    layout="wide",
)

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(
        DATA_PATH,
        parse_dates=['Order Date', 'Ship Date']
    )
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.to_period('M').astype(str)
    df['Discount Band'] = pd.cut(
        df['Discount'],
        bins=[-0.01, 0, 0.2, 0.4, 0.8],
        labels=['No Discount', 'Low (1–20%)', 'Mid (21–40%)', 'High (41–80%)']
    )
    return df

df = load_data()

# ── Sidebar filters ──────────────────────────────────────────────────────────
st.sidebar.header("Filters")

years = sorted(df['Year'].unique())
selected_years = st.sidebar.multiselect("Year", years, default=years)

regions = sorted(df['Region'].unique())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

segments = sorted(df['Segment'].unique())
selected_segments = st.sidebar.multiselect("Segment", segments, default=segments)

categories = sorted(df['Category'].unique())
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)

mask = (
    df['Year'].isin(selected_years) &
    df['Region'].isin(selected_regions) &
    df['Segment'].isin(selected_segments) &
    df['Category'].isin(selected_categories)
)
filtered = df[mask]

# ── Header ───────────────────────────────────────────────────────────────────
st.title("Superstore Sales Dashboard")
st.caption(f"Showing {len(filtered):,} of {len(df):,} orders · {filtered['Order Date'].min().date()} → {filtered['Order Date'].max().date()}")

# ── KPI cards ────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

total_sales   = filtered['Sales'].sum()
total_profit  = filtered['Profit'].sum()
margin        = total_profit / total_sales * 100 if total_sales else 0
total_orders  = filtered['Order ID'].nunique()
total_customers = filtered['Customer ID'].nunique()

k1.metric("Total Sales",     f"${total_sales:,.0f}")
k2.metric("Total Profit",    f"${total_profit:,.0f}")
k3.metric("Profit Margin",   f"{margin:.1f}%")
k4.metric("Orders",          f"{total_orders:,}")
k5.metric("Customers",       f"{total_customers:,}")

st.divider()

# ── Row 1: Trend + Category ──────────────────────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Sales & Profit Trend")
    yr = filtered.groupby('Year').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=yr['Year'], y=yr['Sales'], name='Sales', marker_color='#4C72B0', opacity=0.8), secondary_y=False)
    fig.add_trace(go.Scatter(x=yr['Year'], y=yr['Profit'], name='Profit', mode='lines+markers', line=dict(color='#2CA02C', width=3)), secondary_y=True)
    fig.update_yaxes(tickprefix='$', tickformat=',.0f', secondary_y=False)
    fig.update_yaxes(tickprefix='$', tickformat=',.0f', secondary_y=True)
    fig.update_layout(height=350, legend=dict(orientation='h', y=1.1), margin=dict(t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Sales by Category")
    cat = filtered.groupby('Category').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
    cat['Margin%'] = (cat['Profit'] / cat['Sales'] * 100).round(1)
    fig = px.bar(
        cat.sort_values('Sales'),
        x='Sales', y='Category', orientation='h',
        color='Margin%',
        color_continuous_scale=['#DD4444', '#f5c842', '#2CA02C'],
        text=cat['Margin%'].apply(lambda x: f'{x}% margin'),
        height=350,
    )
    fig.update_traces(textposition='inside')
    fig.update_layout(margin=dict(t=10, b=0), coloraxis_colorbar=dict(title='Margin %'))
    fig.update_xaxes(tickprefix='$', tickformat=',.0f')
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Sub-category + Discount impact ────────────────────────────────────
col3, col4 = st.columns([3, 2])

with col3:
    st.subheader("Profit by Sub-Category")
    sub = filtered.groupby('Sub-Category')['Profit'].sum().reset_index().sort_values('Profit')
    sub['Color'] = sub['Profit'].apply(lambda x: '#DD4444' if x < 0 else '#2CA02C')
    fig = px.bar(
        sub, x='Profit', y='Sub-Category', orientation='h',
        color='Color', color_discrete_map='identity',
        height=420,
    )
    fig.update_layout(showlegend=False, margin=dict(t=10, b=0))
    fig.update_xaxes(tickprefix='$', tickformat=',.0f')
    fig.add_vline(x=0, line_color='black', line_width=1)
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Discount Impact on Profit")
    disc = filtered.groupby('Discount Band', observed=True)['Profit'].mean().reset_index()
    disc['Color'] = disc['Profit'].apply(lambda x: '#DD4444' if x < 0 else '#2CA02C')
    fig = px.bar(
        disc, x='Discount Band', y='Profit',
        color='Color', color_discrete_map='identity',
        text=disc['Profit'].apply(lambda x: f'${x:.0f}'),
        height=420,
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False, margin=dict(t=10, b=0))
    fig.update_yaxes(tickprefix='$', tickformat=',.0f', title='Avg Profit per Order')
    fig.add_hline(y=0, line_color='black', line_width=1)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 3: Region + Segment ───────────────────────────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("Performance by Region")
    reg = filtered.groupby('Region').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
    reg['Margin%'] = (reg['Profit'] / reg['Sales'] * 100).round(1)
    fig = px.scatter(
        reg, x='Sales', y='Profit', size='Sales', color='Region',
        text='Region', hover_data={'Margin%': True},
        height=320,
    )
    fig.update_traces(textposition='top center')
    fig.update_layout(margin=dict(t=10, b=0), showlegend=False)
    fig.update_xaxes(tickprefix='$', tickformat=',.0f')
    fig.update_yaxes(tickprefix='$', tickformat=',.0f')
    st.plotly_chart(fig, use_container_width=True)

with col6:
    st.subheader("Sales by Customer Segment")
    seg = filtered.groupby('Segment').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
    seg['Margin%'] = (seg['Profit'] / seg['Sales'] * 100).round(1)
    fig = px.pie(
        seg, values='Sales', names='Segment',
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2,
        height=320,
    )
    fig.update_traces(textinfo='label+percent', textposition='outside')
    fig.update_layout(margin=dict(t=10, b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 4: Top states + Top customers ────────────────────────────────────────
col7, col8 = st.columns(2)

with col7:
    st.subheader("Top 10 States by Sales")
    states = filtered.groupby('State')['Sales'].sum().reset_index().sort_values('Sales', ascending=False).head(10)
    fig = px.bar(
        states.sort_values('Sales'), x='Sales', y='State', orientation='h',
        color='Sales', color_continuous_scale='Blues',
        height=360,
    )
    fig.update_layout(margin=dict(t=10, b=0), coloraxis_showscale=False)
    fig.update_xaxes(tickprefix='$', tickformat=',.0f')
    st.plotly_chart(fig, use_container_width=True)

with col8:
    st.subheader("Top 10 Customers by Sales")
    customers = filtered.groupby('Customer Name').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
    customers = customers.sort_values('Sales', ascending=False).head(10)
    customers['Margin%'] = (customers['Profit'] / customers['Sales'] * 100).round(1)
    fig = px.bar(
        customers.sort_values('Sales'), x='Sales', y='Customer Name', orientation='h',
        color='Margin%',
        color_continuous_scale=['#DD4444', '#f5c842', '#2CA02C'],
        height=360,
    )
    fig.update_layout(margin=dict(t=10, b=0))
    fig.update_xaxes(tickprefix='$', tickformat=',.0f')
    st.plotly_chart(fig, use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Data source: Sample - Superstore.xlsx · Cleaned & analysed with Python/Pandas")
