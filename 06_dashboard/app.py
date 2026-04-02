import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Superstore Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Dark theme CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #1e1e2e; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #2a2a3e; }
    .metric-card {
        background-color: #2a2a3e;
        border-radius: 10px;
        padding: 16px 20px;
        border-left: 4px solid #4ecdc4;
        margin-bottom: 8px;
    }
    .metric-card h3 { margin: 0; font-size: 13px; color: #888; }
    .metric-card p  { margin: 4px 0 0; font-size: 26px; font-weight: 700; color: #e0e0e0; }
    .metric-card small { font-size: 12px; color: #4ecdc4; }
    h1, h2, h3 { color: #e0e0e0 !important; }
    .stMarkdown hr { border-color: #3a3a4e; }
</style>
""", unsafe_allow_html=True)

COLORS = {
    'bg': '#1e1e2e', 'panel': '#2a2a3e',
    'teal': '#4ecdc4', 'coral': '#ff6b6b',
    'yellow': '#ffd93d', 'purple': '#a29bfe',
    'green': '#6bcb77', 'white': '#e0e0e0', 'grey': '#555'
}
PALETTE = [COLORS['teal'], COLORS['coral'], COLORS['yellow'], COLORS['purple'], COLORS['green']]

PLOTLY_LAYOUT = dict(
    paper_bgcolor=COLORS['bg'], plot_bgcolor=COLORS['panel'],
    font_color=COLORS['white'], font_family='Arial',
    legend=dict(bgcolor=COLORS['panel'], bordercolor=COLORS['grey']),
    xaxis=dict(gridcolor='#3a3a4e', zerolinecolor=COLORS['grey']),
    yaxis=dict(gridcolor='#3a3a4e', zerolinecolor=COLORS['grey']),
    margin=dict(t=50, b=40, l=40, r=20)
)

# ── Load data ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("01_raw_data/Sample - Superstore.csv", encoding='latin1')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date']  = pd.to_datetime(df['Ship Date'])
    df['Year']       = df['Order Date'].dt.year
    df['Month']      = df['Order Date'].dt.to_period('M').astype(str)
    df['Disc_Bin']   = pd.cut(df['Discount'],
                               bins=[-0.01, 0, 0.2, 0.4, 0.6, 0.8],
                               labels=['0%', '1–20%', '21–40%', '41–60%', '61–80%'])
    return df

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────────
st.sidebar.title("🔍 Filters")
years     = sorted(df['Year'].unique())
regions   = sorted(df['Region'].unique())
segments  = sorted(df['Segment'].unique())
cats      = sorted(df['Category'].unique())

sel_years    = st.sidebar.multiselect("Year",     years,    default=years)
sel_regions  = st.sidebar.multiselect("Region",   regions,  default=regions)
sel_segments = st.sidebar.multiselect("Segment",  segments, default=segments)
sel_cats     = st.sidebar.multiselect("Category", cats,     default=cats)

mask = (
    df['Year'].isin(sel_years) &
    df['Region'].isin(sel_regions) &
    df['Segment'].isin(sel_segments) &
    df['Category'].isin(sel_cats)
)
fdf = df[mask]

# ── Header ────────────────────────────────────────────────────────
st.title("📊 Superstore Sales Dashboard")
st.markdown("Interactive analytics across sales, profit, discounts, and geography.")
st.markdown("---")

# ── KPI cards ─────────────────────────────────────────────────────
total_sales   = fdf['Sales'].sum()
total_profit  = fdf['Profit'].sum()
total_orders  = fdf['Order ID'].nunique()
avg_margin    = total_profit / total_sales * 100 if total_sales else 0
total_qty     = fdf['Quantity'].sum()

c1, c2, c3, c4, c5 = st.columns(5)
def kpi(col, label, value, note=""):
    col.markdown(f"""
    <div class="metric-card">
        <h3>{label}</h3>
        <p>{value}</p>
        <small>{note}</small>
    </div>""", unsafe_allow_html=True)

kpi(c1, "Total Sales",   f"${total_sales:,.0f}",  f"{len(fdf):,} rows")
kpi(c2, "Total Profit",  f"${total_profit:,.0f}", f"{avg_margin:.1f}% margin")
kpi(c3, "Orders",        f"{total_orders:,}",     "unique order IDs")
kpi(c4, "Units Sold",    f"{total_qty:,}",        "total quantity")
kpi(c5, "Avg Order Value", f"${total_sales/total_orders:,.0f}" if total_orders else "$0", "per order")

st.markdown("---")

# ── Row 1: Category margin | Discount impact ─────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Insight 1 — Profit Margin by Category")
    cat_df = fdf.groupby('Category').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
    cat_df['Margin%'] = (cat_df['Profit'] / cat_df['Sales'] * 100).round(1)
    cat_df = cat_df.sort_values('Margin%')

    fig = go.Figure(go.Bar(
        x=cat_df['Margin%'], y=cat_df['Category'], orientation='h',
        marker_color=[COLORS['coral'], COLORS['teal'], COLORS['green']],
        text=[f"{v}%" for v in cat_df['Margin%']], textposition='outside'
    ))
    fig.update_layout(title="Profit Margin % by Category", xaxis_title="Margin (%)", **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Insight 2 — Discount Destroys Profit")
    disc_df = fdf.groupby('Disc_Bin')['Profit'].mean().reset_index()
    disc_df.columns = ['Discount Range', 'Avg Profit']
    disc_df['color'] = disc_df['Avg Profit'].apply(lambda v: COLORS['green'] if v >= 0 else COLORS['coral'])

    fig = go.Figure(go.Bar(
        x=disc_df['Discount Range'], y=disc_df['Avg Profit'],
        marker_color=disc_df['color'],
        text=[f"${v:.0f}" for v in disc_df['Avg Profit']], textposition='outside'
    ))
    fig.add_hline(y=0, line_color=COLORS['white'], line_width=1)
    fig.update_layout(title="Avg Profit per Order by Discount Band", yaxis_title="Avg Profit ($)", **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Sub-category | Region ─────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Insight 3 — Sub-Category Profit")
    sub_df = fdf.groupby('Sub-Category')['Profit'].sum().reset_index().sort_values('Profit')
    sub_df['color'] = sub_df['Profit'].apply(lambda v: COLORS['coral'] if v < 0 else COLORS['teal'])

    fig = go.Figure(go.Bar(
        x=sub_df['Profit'], y=sub_df['Sub-Category'], orientation='h',
        marker_color=sub_df['color'],
        text=[f"${v:,.0f}" for v in sub_df['Profit']], textposition='outside'
    ))
    fig.add_vline(x=0, line_color=COLORS['white'], line_width=1)
    fig.update_layout(title="Total Profit by Sub-Category", xaxis_title="Profit ($)",
                      height=500, **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Insight 4 — Region Performance")
    reg_df = fdf.groupby('Region').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
    reg_df['Margin%'] = (reg_df['Profit'] / reg_df['Sales'] * 100).round(1)
    reg_df = reg_df.sort_values('Margin%', ascending=False)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        name='Sales', x=reg_df['Region'], y=reg_df['Sales'],
        marker_color=COLORS['teal'],
        text=[f"${v/1000:.0f}K" for v in reg_df['Sales']], textposition='outside'
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        name='Margin %', x=reg_df['Region'], y=reg_df['Margin%'],
        mode='lines+markers+text', line_color=COLORS['yellow'],
        marker_size=10, text=[f"{v}%" for v in reg_df['Margin%']],
        textposition='top center'
    ), secondary_y=True)
    fig.update_layout(title="Sales & Profit Margin by Region",
                      height=500, **PLOTLY_LAYOUT)
    fig.update_yaxes(title_text="Sales ($)", secondary_y=False,
                     gridcolor='#3a3a4e', color=COLORS['white'])
    fig.update_yaxes(title_text="Margin (%)", secondary_y=True,
                     gridcolor='#3a3a4e', color=COLORS['white'])
    st.plotly_chart(fig, use_container_width=True)

# ── Row 3: YoY growth | Monthly trend ────────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("Insight 5 — Year-over-Year Growth")
    yoy = fdf.groupby('Year').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
    yoy['Sales_Growth%']  = yoy['Sales'].pct_change().mul(100).round(1)
    yoy['Profit_Growth%'] = yoy['Profit'].pct_change().mul(100).round(1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=yoy['Year'], y=yoy['Sales_Growth%'], name='Sales Growth %',
        mode='lines+markers+text', line_color=COLORS['teal'],
        marker_size=10, text=[f"{v}%" if pd.notna(v) else "" for v in yoy['Sales_Growth%']],
        textposition='top center'
    ))
    fig.add_trace(go.Scatter(
        x=yoy['Year'], y=yoy['Profit_Growth%'], name='Profit Growth %',
        mode='lines+markers+text', line_color=COLORS['yellow'],
        marker_size=10, text=[f"{v}%" if pd.notna(v) else "" for v in yoy['Profit_Growth%']],
        textposition='bottom center'
    ))
    fig.add_hline(y=0, line_color=COLORS['grey'], line_dash='dash')
    fig.update_layout(title="Year-over-Year Sales & Profit Growth",
                      xaxis_title="Year", yaxis_title="Growth (%)", **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

with col6:
    st.subheader("Bonus — Monthly Sales Trend")
    monthly = fdf.groupby('Month').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly['Month'], y=monthly['Sales'], name='Sales',
        mode='lines', line=dict(color=COLORS['teal'], width=2), fill='tozeroy',
        fillcolor='rgba(78,205,196,0.15)'
    ))
    fig.add_trace(go.Scatter(
        x=monthly['Month'], y=monthly['Profit'], name='Profit',
        mode='lines', line=dict(color=COLORS['yellow'], width=2)
    ))
    fig.update_layout(title="Monthly Sales & Profit Over Time",
                      xaxis_title="Month", yaxis_title="Amount ($)",
                      xaxis_tickangle=-45, **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 4: Segment breakdown | State map ─────────────────────────
col7, col8 = st.columns(2)

with col7:
    st.subheader("Segment Performance")
    seg_df = fdf.groupby('Segment').agg(
        Sales=('Sales','sum'), Profit=('Profit','sum'), Orders=('Order ID','nunique')
    ).reset_index()
    seg_df['Margin%'] = (seg_df['Profit'] / seg_df['Sales'] * 100).round(1)

    fig = px.bar(seg_df, x='Segment', y=['Sales', 'Profit'],
                 barmode='group', color_discrete_sequence=[COLORS['teal'], COLORS['coral']])
    fig.update_layout(title="Sales vs Profit by Segment",
                      yaxis_title="Amount ($)", **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

with col8:
    st.subheader("Profit by State")
    state_df = fdf.groupby('State')['Profit'].sum().reset_index()

    fig = px.choropleth(
        state_df, locations='State', locationmode='USA-states',
        color='Profit', scope='usa',
        color_continuous_scale=['#ff6b6b', '#1e1e2e', '#4ecdc4'],
        color_continuous_midpoint=0,
        labels={'Profit': 'Profit ($)'}
    )
    fig.update_layout(title="Profit by State", geo_bgcolor=COLORS['bg'],
                      **PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

# ── Raw data explorer ─────────────────────────────────────────────
st.markdown("---")
with st.expander("🔎 Explore Raw Data"):
    st.dataframe(
        fdf[['Order Date','Category','Sub-Category','Region','Segment',
             'Sales','Quantity','Discount','Profit']].sort_values('Order Date', ascending=False),
        use_container_width=True, height=300
    )
    st.caption(f"{len(fdf):,} rows shown based on current filters.")
