"""
Streamlit E-commerce Sales Dashboard (CSV export version)
- Simulated dataset
- Date range & category filters
- KPIs: Total Revenue, Total Units Sold
- Plotly charts: sales over time, top products, sales by region
- Table of filtered data
- Download filtered CSV only (no PDF)

Requirements: streamlit, pandas, plotly
Install: pip install streamlit pandas plotly
Run: streamlit run streamlit_sales_dashboard.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import plotly.express as px

# -----------------------------
# Branding
# -----------------------------
AUTHOR_NAME = "Balogun Segun"
PORTFOLIO_LINK = "https://segs101.github.io/My-Portfolio/"

# -----------------------------
# Helpers: Data generation
# -----------------------------
@st.cache_data
def generate_dummy_data(months=9, seed=42):
    np.random.seed(seed)
    start_date = datetime.today() - timedelta(days=30 * months)
    dates = pd.date_range(start=start_date, periods=months * 30)

    products = [
        "Classic Tee","Sport Sneakers","Wireless Headset","Smartwatch","Backpack","Running Shorts","Sunglasses","Water Bottle","Phone Case","Bluetooth Speaker"
    ]

    categories = {
        "Apparel": ["Classic Tee", "Running Shorts"],
        "Footwear": ["Sport Sneakers"],
        "Electronics": ["Wireless Headset", "Smartwatch", "Bluetooth Speaker"],
        "Accessories": ["Backpack", "Sunglasses", "Water Bottle", "Phone Case"],
    }

    regions = ["North", "South", "East", "West"]

    rows = []
    for date in dates:
        daily_tx = np.random.poisson(lam=8)
        for _ in range(daily_tx):
            product = np.random.choice(products)
            category = [k for k, v in categories.items() if product in v][0]
            units = max(1, int(np.random.poisson(2)))
            price = {
                "Classic Tee": 15,"Sport Sneakers": 75,"Wireless Headset": 45,"Smartwatch": 95,"Backpack": 40,
                "Running Shorts": 20,"Sunglasses": 25,"Water Bottle": 10,"Phone Case": 12,"Bluetooth Speaker": 55
            }[product]
            trend = 1 + ((date - dates[0]).days / (len(dates) * 30)) * 0.2
            revenue = round(units * price * np.random.uniform(0.8, 1.2) * trend, 2)
            region = np.random.choice(regions, p=[0.3, 0.25, 0.2, 0.25])
            rows.append([date.date(), product, category, units, revenue, region])

    df = pd.DataFrame(rows, columns=["Date", "Product", "Category", "Units Sold", "Revenue", "Region"])
    return df

# -----------------------------
# Streamlit App
# -----------------------------
def main():
    st.set_page_config(page_title="E-commerce Sales Dashboard", layout="wide")

    df = generate_dummy_data(months=9)
    df["Date"] = pd.to_datetime(df["Date"])

    st.sidebar.header("Filters")
    min_date = df["Date"].min()
    max_date = df["Date"].max()
    date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    categories = ["All"] + sorted(df["Category"].unique().tolist())
    category = st.sidebar.selectbox("Category", categories)

    region_opts = ["All"] + sorted(df["Region"].unique().tolist())
    region = st.sidebar.selectbox("Region", region_opts)

    start_dt, end_dt = date_range
    mask = (df["Date"].dt.date >= start_dt) & (df["Date"].dt.date <= end_dt)
    if category != "All":
        mask &= (df["Category"] == category)
    if region != "All":
        mask &= (df["Region"] == region)

    df_filtered = df.loc[mask].copy()

    st.title("E-commerce Sales Dashboard")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    total_revenue = df_filtered["Revenue"].sum()
    total_units = df_filtered["Units Sold"].sum()
    avg_order_value = (total_revenue / (len(df_filtered) if len(df_filtered) else 1))

    col1.metric("Total Revenue (USD)", f"₦{total_revenue:,.2f}")
    col2.metric("Total Units Sold", f"{int(total_units):,}")
    col3.metric("Avg Revenue / Row", f"₦{avg_order_value:,.2f}")

    st.subheader("Visualizations")
    chart_col1, chart_col2 = st.columns((2, 1))

    sales_time = df_filtered.groupby(pd.Grouper(key="Date", freq="W"))["Revenue"].sum().reset_index()
    if sales_time.empty:
        st.warning("No data in selected range / filters. Try expanding the date range.")
        return

    fig_time = px.line(sales_time, x="Date", y="Revenue", title="Sales Over Time", markers=True)
    chart_col1.plotly_chart(fig_time, use_container_width=True)

    top_products = df_filtered.groupby("Product")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=False).head(10)
    fig_top = px.bar(top_products, x="Revenue", y="Product", orientation='h', title="Top Products by Revenue")
    chart_col2.plotly_chart(fig_top, use_container_width=True)

    st.subheader("Regional Performance")
    region_summary = df_filtered.groupby("Region")["Revenue"].sum().reset_index()
    fig_region = px.pie(region_summary, values="Revenue", names="Region", title="Revenue by Region")
    st.plotly_chart(fig_region, use_container_width=True)

    st.subheader("Filtered Data")
    st.dataframe(df_filtered.reset_index(drop=True))

    csv_bytes = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download CSV of filtered data", data=csv_bytes, file_name="filtered_sales.csv", mime="text/csv")

    st.markdown("---")
    st.markdown(f"Built by **{AUTHOR_NAME}** — [Portfolio]({PORTFOLIO_LINK})")

if __name__ == "__main__":
    main()
 