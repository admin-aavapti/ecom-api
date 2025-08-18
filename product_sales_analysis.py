import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# STEP 1: Load Product Data 

print("🔄 Loading product data...")
df = pd.read_csv("flipkart_products_all_categories.csv")

# STEP 2: Simulate 6 Months of Daily Sales

print("🎲 Simulating daily sales for last 6 months...")

days = 180
date_range = [datetime.today() - timedelta(days=i) for i in range(days)]

sales_data = []
for _, row in df.iterrows():
    for date in date_range:
        fake_sales = np.random.poisson(lam=2)  # avg 2 per day
        sales_data.append({
            "date": date,
            "category": row["category"],
            "title": row["title"],
            "sales": fake_sales,
            "price": row["price"]
        })

sales_df = pd.DataFrame(sales_data)
sales_df['date'] = pd.to_datetime(sales_df['date'])

# STEP 3: Add Weekly & Monthly Periods 

sales_df['week'] = sales_df['date'].dt.to_period('W').apply(lambda r: r.start_time)
sales_df['month'] = sales_df['date'].dt.to_period('M').astype(str)

# STEP 4: Add Festival Names 

festival_dict = {
    "2025-01-01": "New Year",
    "2025-01-14": "Makar Sankranti",
    "2025-01-26": "Republic Day",
    "2025-03-17": "Maha Shivratri",
    "2025-03-29": "Holi",
    "2025-04-10": "Ram Navami",
    "2025-04-14": "Ambedkar Jayanti",
    "2025-04-18": "Good Friday",
    "2025-05-01": "Labour Day",
    "2025-05-22": "Buddha Purnima",
    "2025-06-06": "Eid-ul-Fitr",
    "2025-08-15": "Independence Day",
    "2025-08-19": "Raksha Bandhan",
    "2025-08-29": "Janmashtami",
    "2025-10-02": "Gandhi Jayanti",
    "2025-10-20": "Diwali",
    "2025-10-22": "Bhai Dooj",
    "2025-11-02": "Chhath Puja",
    "2025-12-25": "Christmas"
}

sales_df['date_str'] = sales_df['date'].dt.strftime('%Y-%m-%d')
sales_df['is_festival'] = sales_df['date_str'].isin(festival_dict)
sales_df['festival_name'] = sales_df['date_str'].map(festival_dict)

# ------------------ STEP 5: Daily Top-Selling Products ------------------

print("\n📅 Top-Selling Products Per Day (Sample 5 Days):\n")
daily_top = (
    sales_df.groupby(['date', 'title'])['sales']
    .sum()
    .reset_index()
    .sort_values(['date', 'sales'], ascending=[True, False])
)

for date in daily_top['date'].unique()[:5]:  # First 5 days only
    top3 = daily_top[daily_top['date'] == date].head(3)
    print(f"🗓️ {date.date()}")
    print(top3[['title', 'sales']])
    print("-" * 40)

# ------------------ STEP 6: Weekly Top-Selling Products ------------------

print("\n📆 Top-Selling Products Per Week (Sample 5 Weeks):\n")
weekly_top = (
    sales_df.groupby(['week', 'title'])['sales']
    .sum()
    .reset_index()
    .sort_values(['week', 'sales'], ascending=[True, False])
)

for week in weekly_top['week'].unique()[:5]:
    top3 = weekly_top[weekly_top['week'] == week].head(3)
    print(f"📆 Week of: {week.date()}")
    print(top3[['title', 'sales']])
    print("-" * 40)

# ------------------ STEP 7: Monthly Top-Selling Products ------------------

print("\n📅 Top-Selling Products Per Month:\n")
monthly_top = (
    sales_df.groupby(['month', 'title'])['sales']
    .sum()
    .reset_index()
    .sort_values(['month', 'sales'], ascending=[True, False])
)

for month in monthly_top['month'].unique():
    top3 = monthly_top[monthly_top['month'] == month].head(3)
    print(f"📅 Month: {month}")
    print(top3[['title', 'sales']])
    print("-" * 40)

# ------------------ STEP 8: Total Top Products in 6 Months ------------------

print("\n📈 Top 10 Best-Selling Products in the Last 6 Months:\n")
yearly_top = (
    sales_df.groupby('title')['sales']
    .sum()
    .reset_index()
    .sort_values('sales', ascending=False)
    .head(10)
)
print(yearly_top[['title', 'sales']])

# ------------------ STEP 9: Festival-Specific Top Products ------------------

print("\n🎉 Top-Selling Products During Festivals (with Festival Names):\n")
festival_sales = sales_df[sales_df['is_festival']]

festival_top = (
    festival_sales.groupby(['festival_name', 'category', 'title'])['sales']
    .sum()
    .reset_index()
    .sort_values(['festival_name', 'category', 'sales'], ascending=[True, True, False])
)

for fest in festival_top['festival_name'].dropna().unique():
    print(f"\n🎊 Festival: {fest}")
    fest_data = festival_top[festival_top['festival_name'] == fest]
    for category in fest_data['category'].unique():
        top3 = fest_data[fest_data['category'] == category].head(3)
        print(f"📁 Category: {category}")
        print(top3[['title', 'sales']])
        print("-" * 30)

# ------------------ STEP 10: Save CSVs ------------------

print("\n💾 Saving CSV files...")
sales_df.to_csv("product_sales_simulated.csv", index=False)
yearly_top.to_csv("top_products_last_6_months.csv", index=False)
monthly_top.to_csv("monthly_top_products.csv", index=False)

print("\n✅ Done! All reports generated and saved.")
