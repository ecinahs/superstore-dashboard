import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

df = pd.read_csv('02_processed_data/superstore_clean.csv', parse_dates=['Order Date', 'Ship Date'])
df['Year'] = df['Order Date'].dt.year

# Style
sns.set_theme(style='whitegrid', palette='muted')
plt.rcParams.update({'figure.dpi': 150, 'font.size': 10})

BLUE   = '#4C72B0'
RED    = '#DD4444'
GREEN  = '#2CA02C'
COLORS = [GREEN if v >= 0 else RED for v in [1]]  # used per chart

# ── 1. Yearly Sales & Profit Trend ──────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(8, 4))
yr = df.groupby('Year').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum'))
ax1.bar(yr.index, yr['Sales'], color=BLUE, alpha=0.7, label='Sales')
ax1.set_ylabel('Sales ($)', color=BLUE)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e3:.0f}K'))
ax2 = ax1.twinx()
ax2.plot(yr.index, yr['Profit'], color=GREEN, marker='o', linewidth=2, label='Profit')
ax2.set_ylabel('Profit ($)', color=GREEN)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e3:.0f}K'))
ax1.set_title('Yearly Sales & Profit Trend', fontweight='bold')
lines = [plt.Rectangle((0,0),1,1, color=BLUE, alpha=0.7), plt.Line2D([0],[0], color=GREEN, marker='o')]
ax1.legend(lines, ['Sales', 'Profit'], loc='upper left')
plt.tight_layout()
plt.savefig('05_outputs/figures/01_yearly_trend.png')
plt.close()
print('Saved: 01_yearly_trend.png')

# ── 2. Sales & Profit Margin by Category ────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
cat = df.groupby('Category').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum'))
cat['Margin%'] = (cat['Profit'] / cat['Sales'] * 100).round(1)
cat = cat.sort_values('Sales', ascending=True)

axes[0].barh(cat.index, cat['Sales'], color=BLUE, alpha=0.8)
axes[0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e3:.0f}K'))
axes[0].set_title('Sales by Category', fontweight='bold')

bar_colors = [GREEN if v >= 0 else RED for v in cat['Margin%']]
axes[1].barh(cat.index, cat['Margin%'], color=bar_colors, alpha=0.85)
axes[1].axvline(0, color='black', linewidth=0.8)
axes[1].set_xlabel('Profit Margin (%)')
axes[1].set_title('Profit Margin by Category', fontweight='bold')

plt.tight_layout()
plt.savefig('05_outputs/figures/02_category_performance.png')
plt.close()
print('Saved: 02_category_performance.png')

# ── 3. Sub-Category Profit (all) ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 6))
sub = df.groupby('Sub-Category')['Profit'].sum().sort_values()
colors = [RED if v < 0 else GREEN for v in sub]
ax.barh(sub.index, sub.values, color=colors, alpha=0.85)
ax.axvline(0, color='black', linewidth=0.8)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e3:.0f}K'))
ax.set_title('Profit by Sub-Category', fontweight='bold')
ax.set_xlabel('Total Profit ($)')
plt.tight_layout()
plt.savefig('05_outputs/figures/03_subcategory_profit.png')
plt.close()
print('Saved: 03_subcategory_profit.png')

# ── 4. Discount Impact on Profit ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
df['Discount Band'] = pd.cut(
    df['Discount'],
    bins=[-0.01, 0, 0.2, 0.4, 0.8],
    labels=['No discount', 'Low\n(1–20%)', 'Mid\n(21–40%)', 'High\n(41–80%)']
)
disc = df.groupby('Discount Band', observed=True)['Profit'].mean()
bar_colors = [GREEN if v >= 0 else RED for v in disc]
bars = ax.bar(disc.index, disc.values, color=bar_colors, alpha=0.85, edgecolor='white')
ax.axhline(0, color='black', linewidth=0.8)
ax.set_ylabel('Avg Profit per Order ($)')
ax.set_title('Discount Level vs Average Profit', fontweight='bold')
for bar, val in zip(bars, disc.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (2 if val >= 0 else -8),
            f'${val:.0f}', ha='center', fontsize=9)
plt.tight_layout()
plt.savefig('05_outputs/figures/04_discount_impact.png')
plt.close()
print('Saved: 04_discount_impact.png')

# ── 5. Profit by Region ──────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
reg = df.groupby('Region').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum'))
reg['Margin%'] = (reg['Profit'] / reg['Sales'] * 100).round(1)
reg = reg.sort_values('Profit', ascending=True)
ax.barh(reg.index, reg['Profit'], color=BLUE, alpha=0.8)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e3:.0f}K'))
ax.set_title('Total Profit by Region', fontweight='bold')
for i, (val, margin) in enumerate(zip(reg['Profit'], reg['Margin%'])):
    ax.text(val + 500, i, f'  {margin}% margin', va='center', fontsize=9)
plt.tight_layout()
plt.savefig('05_outputs/figures/05_region_profit.png')
plt.close()
print('Saved: 05_region_profit.png')

# ── 6. Top 10 States by Sales ────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
states = df.groupby('State')['Sales'].sum().sort_values(ascending=False).head(10)
ax.bar(states.index, states.values, color=BLUE, alpha=0.8)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e3:.0f}K'))
ax.set_title('Top 10 States by Sales', fontweight='bold')
ax.set_ylabel('Total Sales ($)')
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig('05_outputs/figures/06_top_states.png')
plt.close()
print('Saved: 06_top_states.png')

# ── 7. Segment Performance ───────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
seg = df.groupby('Segment').agg(Sales=('Sales', 'sum'), Profit=('Profit', 'sum'))
seg['Margin%'] = (seg['Profit'] / seg['Sales'] * 100).round(1)
x = range(len(seg))
width = 0.35
bars1 = ax.bar([i - width/2 for i in x], seg['Sales'], width, label='Sales', color=BLUE, alpha=0.8)
bars2 = ax.bar([i + width/2 for i in x], seg['Profit'], width, label='Profit', color=GREEN, alpha=0.8)
ax.set_xticks(list(x))
ax.set_xticklabels(seg.index)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1e3:.0f}K'))
ax.set_title('Sales & Profit by Customer Segment', fontweight='bold')
ax.legend()
for i, margin in enumerate(seg['Margin%']):
    ax.text(i, seg['Sales'].iloc[i] + 5000, f'{margin}%', ha='center', fontsize=9, color='gray')
plt.tight_layout()
plt.savefig('05_outputs/figures/07_segment_performance.png')
plt.close()
print('Saved: 07_segment_performance.png')

print('\nAll charts saved to 05_outputs/figures/')
