import pandas as pd
import numpy as np
import hashlib
import re
from datetime import timedelta, datetime

# Clean price string to float
def clean_price(price_str):
    if pd.isna(price_str):
        return np.nan
    price_str = str(price_str).replace('₹', '').replace(',', '').strip()
    try:
        return float(price_str)
    except:
        return np.nan

# Extract specs from features column
def extract_specs(features):
    specs = {}
    features = str(features).lower()

    ram_match = re.search(r'(\d+)\s*gb\s*ram', features)
    specs['ram_gb'] = int(ram_match.group(1)) if ram_match else None

    storage_match = re.search(r'(?:internal storage|storage|rom)\s*(\d+)\s*gb', features)
    specs['storage_gb'] = int(storage_match.group(1)) if storage_match else None

    battery_match = re.search(r'(\d+)\s*mah', features)
    specs['battery_mah'] = int(battery_match.group(1)) if battery_match else None

    display_match = re.search(r'display size\s*[:\-]?\s*(\d+\.?\d*)\s*(cm|inch|in)?', features)
    if display_match:
        size = float(display_match.group(1))
        unit = display_match.group(2)
        if unit and 'cm' in unit:
            size_inch = round(size / 2.54, 2)
        else:
            size_inch = round(size, 2)
        specs['display_inch'] = size_inch
    else:
        specs['display_inch'] = None

    proc_brand_match = re.search(r'processor brand\s*[:\-]?\s*([a-z0-9\s]+)', features)
    specs['processor_brand'] = proc_brand_match.group(1).strip() if proc_brand_match else None

    proc_type_match = re.search(r'processor type\s*[:\-]?\s*([a-z0-9\s]+)', features)
    specs['processor_type'] = proc_type_match.group(1).strip() if proc_type_match else None

    return specs

# Create product ID by hashing title
def create_product_id(title):
    return hashlib.md5(title.encode('utf-8')).hexdigest()[:10]

# Vary price ±5%
def vary_price(base_price):
    if pd.isna(base_price):
        return np.nan
    variation = base_price * np.random.uniform(-0.05, 0.05)
    return round(base_price + variation, 2)

# Vary rating ±0.2 between 1 and 5
def vary_rating(base_rating):
    if pd.isna(base_rating):
        return np.nan
    variation = np.random.uniform(-0.2, 0.2)
    new_rating = base_rating + variation
    return round(min(max(new_rating, 1), 5), 2)

# Vary reviews ±10%
def vary_reviews(base_reviews):
    if pd.isna(base_reviews):
        return 0
    variation = base_reviews * np.random.uniform(-0.1, 0.1)
    return max(int(base_reviews + variation), 0)

# Convert availability to binary
def availability_binary(status):
    if isinstance(status, str) and 'in stock' in status.lower():
        return 1
    return 0

# Simulate event and impact
def simulate_event(day_idx, event_days):
    if day_idx in event_days:
        return 1, np.random.uniform(1.1, 1.5)
    else:
        return 0, 1.0

# Safely parse rating, treat empty strings as NaN
def safe_float(val):
    try:
        f = float(val)
        if f < 1 or f > 5:
            return np.nan
        return f
    except:
        # simulate random rating for missing
        return round(np.random.uniform(3, 4.5), 2)


# Simulate time series
def simulate_time_series(df, days=60):
    rows = []
    start_date = datetime.now() - timedelta(days=days)
    
    # Pre-select event days globally to keep consistency
    event_days = np.random.choice(range(days), size=5, replace=False)
    
    for _, row in df.iterrows():
        specs = extract_specs(row['features'])
        product_id = create_product_id(row['title'])
        base_price = clean_price(row['price'])
        base_rating = safe_float(row['rating'])
        
        try:
            base_reviews = int(row['reviews'])
        except:
            # If reviews is empty or invalid, simulate a base review count
            base_reviews = np.random.randint(10, 100)
        
        avail_bin = availability_binary(row['availability'])
        category = row['category']

        for day in range(days):
            date = start_date + timedelta(days=day)
            price = vary_price(base_price)
            rating = vary_rating(base_rating)
            reviews = vary_reviews(base_reviews)
            availability = avail_bin
            competitor_price = round(price * np.random.uniform(0.9, 1.1), 2)
            promotion_flag = int(np.random.rand() < 0.1)  # 10% chance of promotion
            estimated_demand = reviews * availability
            cost_price = round(price * np.random.uniform(0.6, 0.85), 2)
            profit_margin = round(price - cost_price, 2)
            event, event_impact = simulate_event(day, event_days)
            ad_spend = round(np.random.uniform(0, 200), 2)

            rows.append({
                'date': date.strftime('%Y-%m-%d'),
                'product_id': product_id,
                'title': row['title'],
                'category': category,
                'price': price,
                'rating': rating,
                'reviews': reviews,
                'availability': availability,
                'competitor_price': competitor_price,
                'promotion_flag': promotion_flag,
                'estimated_demand': estimated_demand,
                'cost_price': cost_price,
                'profit_margin': profit_margin,
                'event': event,
                'event_impact': round(event_impact, 2),
                'ad_spend': ad_spend,
                'ram_gb': specs['ram_gb'],
                'storage_gb': specs['storage_gb'],
                'battery_mah': specs['battery_mah'],
                'display_inch': specs['display_inch'],
                'processor_brand': specs['processor_brand'],
                'processor_type': specs['processor_type'],
            })

    df_expanded = pd.DataFrame(rows)

    # Calculate market share per date & category
    # Calculate market share as percentage
    df_expanded['total_demand'] = df_expanded.groupby(['date', 'category'])['estimated_demand'].transform('sum')
    df_expanded['market_share'] = df_expanded.apply(
        lambda x: round((x['estimated_demand'] / x['total_demand']) * 100, 2) if x['total_demand'] > 0 else 0, axis=1
    )
    df_expanded.drop(columns=['total_demand'], inplace=True)

    return df_expanded 


# Load your scraped CSV file - update path accordingly
df = pd.read_csv('C:\\Amaz\\flipkart_scraped_data.csv')

# Run simulation for 60 days
df_simulated = simulate_time_series(df, days=60)

# Save output CSV
df_simulated.to_csv('C:\\Amaz\\flipkart_products_timeseries.csv', index=False)

print("✅ Simulation complete. Output saved to flipkart_products_timeseries.csv")

