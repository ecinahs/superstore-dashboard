import pandas as pd

# Load raw data
df = pd.read_excel('01_raw_data/Sample - Superstore.xlsx')

print(f'Loaded {len(df)} rows')

# 1. Parse date columns to proper datetime
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')
print('Dates parsed to datetime')

# 2. Fix Postal Code — zero-pad to 5 characters
df['Postal Code'] = df['Postal Code'].astype(str).str.zfill(5)
print(f'Postal codes reformatted (e.g. {df["Postal Code"].iloc[0]})')

# 3. Strip trailing/leading whitespace from Product Name
df['Product Name'] = df['Product Name'].str.strip()
print('Product Name whitespace stripped')

# 4. Round Sales and Profit to 2 decimal places
df['Sales'] = df['Sales'].round(2)
df['Profit'] = df['Profit'].round(2)
print('Sales and Profit rounded to 2 decimal places')

# 5. Flag rows where Ship Date < Order Date (do not drop — preserve data)
df['date_flag'] = df['Ship Date'] < df['Order Date']
flagged = df['date_flag'].sum()
print(f'Flagged {flagged} rows where Ship Date < Order Date (column: date_flag)')

# Save cleaned file
output_path = '02_processed_data/superstore_clean.csv'
df.to_csv(output_path, index=False)
print(f'\nSaved cleaned data to {output_path}')
print(f'Final shape: {df.shape}')
