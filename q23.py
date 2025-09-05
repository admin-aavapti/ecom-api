import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from prophet import Prophet
from prophet.plot import plot_plotly
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
import numpy as np

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('C:\\Amaz\\flipkart_products_timeseries.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filter Products")
category = st.sidebar.selectbox("Category", df['category'].unique())
price_range = st.sidebar.slider("Price Range", float(df['price'].min()), float(df['price'].max()), (float(df['price'].min()), float(df['price'].max())))

filtered_df = df[(df['category'] == category) & 
                 (df['price'] >= price_range[0]) & 
                 (df['price'] <= price_range[1])]

# Main Title
st.title("Dashboard")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["Overview", "Forecast", "Prediction", "Market Share", "Price vs Profit", "All Forecasts", "Optimizer", "Positioning"])

# ------------------ TAB 1: OVERVIEW ------------------
with tab1:
    st.subheader("Overview Metrics")

    col1, col2, col3 = st.columns(3)
    col1.metric("Average Price", f"₹{filtered_df['price'].mean():,.0f}")
    col2.metric("Average Rating", f"{filtered_df['rating'].mean():.2f}")
    col3.metric("Average Profit Margin", f"₹{filtered_df['profit_margin'].mean():.0f}")

    top_products = filtered_df.groupby('title')['market_share'].mean().sort_values(ascending=False).head(5)
    st.write("Top 5 Products by Avg Market Share")

# Compute average market share only on filtered data
    top_products_df = filtered_df.groupby('title')['market_share'].mean().reset_index()
    top_products_df = top_products_df.sort_values(by='market_share', ascending=False).head(5)

# Format for better display
    top_products_df['market_share (%)'] = top_products_df['market_share'].round(2)
    top_products_df.drop(columns=['market_share'], inplace=True)

    st.dataframe(top_products_df.reset_index(drop=True))


    fig = px.line(filtered_df, x='date', y='price', color='title', title="Price Trend Over Time")
    st.plotly_chart(fig, use_container_width=True)

# ------------------ TAB 2: PROPHET FORECAST ------------------
with tab2:
    st.subheader("Price Forecast")
    selected_product = st.selectbox("Select Product", filtered_df['title'].unique(), key="forecast_product")

    product_df = filtered_df[filtered_df['title'] == selected_product][['date', 'price']].rename(columns={'date': 'ds', 'price': 'y'})
    model = Prophet()
    model.fit(product_df)

    future = model.make_future_dataframe(periods=15)
    forecast = model.predict(future)

    fig1 = plot_plotly(model, forecast)
    st.plotly_chart(fig1)

# ------------------ TAB 3: LSTM PRICE PREDICTION ------------------
with tab3:
    st.subheader("Price Prediction")

    lstm_df = filtered_df[filtered_df['title'] == selected_product].sort_values('date')[['date', 'price']]
    lstm_df.set_index('date', inplace=True)

    scaler = MinMaxScaler()
    scaled_prices = scaler.fit_transform(lstm_df[['price']])

    sequence_length = 10
    X, y = [], []
    for i in range(len(scaled_prices) - sequence_length):
        X.append(scaled_prices[i:i+sequence_length])
        y.append(scaled_prices[i+sequence_length])

    X, y = np.array(X), np.array(y)

    model = Sequential()
    model.add(LSTM(50, return_sequences=False, input_shape=(X.shape[1], X.shape[2])))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X, y, epochs=10, batch_size=16, verbose=0)

    pred = model.predict(X)
    predicted_prices = scaler.inverse_transform(pred)

    pred_dates = lstm_df.index[sequence_length:]
    df_pred = pd.DataFrame({'date': pred_dates, 'actual': lstm_df['price'].values[sequence_length:], 'predicted': predicted_prices.flatten()})
    
    fig2 = px.line(df_pred, x='date', y=['actual', 'predicted'], title="LSTM Price Prediction")
    st.plotly_chart(fig2)

# ------------------ TAB 4: MARKET SHARE ------------------
with tab4:
    st.subheader("Market Share Trend")

    share_df = filtered_df.groupby(['date', 'title'])['market_share'].mean().reset_index()
    fig3 = px.line(share_df, x='date', y='market_share', color='title', title="Market Share Over Time")
    st.plotly_chart(fig3)

# ------------------ TAB 5: PRICE vs PROFIT ------------------
with tab5:
    st.subheader("Price vs Profit Margin")

    fig4 = px.scatter(filtered_df, x='price', y='profit_margin', color='title',
                      size='estimated_demand', hover_data=['rating', 'ad_spend'],
                      title="Profit vs. Price (Size: Demand)")
    st.plotly_chart(fig4)

# ------------------ TAB 6: FORECAST ALL PRODUCTS ------------------
with tab6:
    st.subheader("Future Price Forecasts for All Products")

    # Get unique products with titles
    all_products = filtered_df[['product_id', 'title']].drop_duplicates().set_index('product_id')

    fig_all = go.Figure()

    for pid, row in all_products.iterrows():
        product_title = row['title']
        product_data = filtered_df[filtered_df['product_id'] == pid][['date', 'price']].rename(columns={'date': 'ds', 'price': 'y'})
        product_data['ds'] = pd.to_datetime(product_data['ds'])

        model = Prophet(daily_seasonality=True)
        model.fit(product_data)

        future = model.make_future_dataframe(periods=15)
        forecast = model.predict(future)

        forecasted = forecast.tail(15)
        fig_all.add_trace(go.Scatter(
            x=forecasted['ds'],
            y=forecasted['yhat'],
            mode='lines',
            name=product_title  
        ))

    fig_all.update_layout(
        title="15-Day Future Price Forecasts for All Products",
        xaxis_title="Date",
        yaxis_title="Price",
        legend_title="Products",
        height=600
    )

    st.plotly_chart(fig_all, use_container_width=True)

with tab7:
    st.subheader("Simulated Pricing Optimizer")

    # Select a product
    sim_product = st.selectbox("Select Product", filtered_df['title'].unique(), key="simulator_product")

    # Get latest data for that product
    latest_df = filtered_df[filtered_df['title'] == sim_product].sort_values('date', ascending=False).iloc[0]

    base_price = latest_df['price']
    base_demand = latest_df['estimated_demand']
    cost_price = latest_df['cost_price']
    elasticity = 1.2  # You can make this dynamic

    st.markdown(f"**Current Price:** ₹{base_price} | **Cost Price:** ₹{cost_price} | **Base Demand:** {int(base_demand)}")

    # Simulated price slider
    new_price = st.slider("Set New Price", min_value=round(cost_price + 1, 2), max_value=round(base_price * 1.5, 2), value=round(base_price, 2), step=1.0)

    # Apply demand elasticity rule
    simulated_demand = base_demand * (base_price / new_price) ** elasticity
    simulated_profit_margin = new_price - cost_price
    simulated_total_profit = simulated_demand * simulated_profit_margin

    col1, col2, col3 = st.columns(3)
    col1.metric("Simulated Demand", f"{int(simulated_demand)} units")
    col2.metric("Profit per Unit", f"₹{simulated_profit_margin:.2f}")
    col3.metric("Total Profit", f"₹{simulated_total_profit:,.0f}")

    # Visualization
    prices = np.linspace(cost_price + 1, base_price * 1.5, 50)
    demands = base_demand * (base_price / prices) ** elasticity
    margins = prices - cost_price
    profits = demands * margins

    fig5 = px.line(x=prices, y=profits, labels={'x': 'Price', 'y': 'Total Profit'}, title="Profit vs. Price Simulation")
    fig5.add_vline(x=new_price, line_dash='dash', line_color='green', annotation_text="Your Selected Price")
    st.plotly_chart(fig5, use_container_width=True)

with tab8:
    st.subheader("📌 Product Market Positioning")

    # Average values per product
    positioning_df = filtered_df.groupby('title').agg({
        'price': 'mean',
        'profit_margin': 'mean',
        'market_share': 'mean'
    }).reset_index()

    fig6 = px.scatter(positioning_df, 
                     x='price', y='profit_margin', 
                     size='market_share', 
                     color='title',
                     hover_name='title',
                     title="Market Positioning: Price vs Profit (Bubble Size = Market Share)",
                     labels={"price": "Avg Price", "profit_margin": "Avg Profit Margin"})

    st.plotly_chart(fig6, use_container_width=True)
