import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
from utils.data_processor import DataProcessor
from data.property_data import get_sample_data, get_property_locations
from assets.image_urls import get_dashboard_images

def show():
    """Display the market trends page with visualizations and insights"""
    st.title("Real Estate Market Trends")
    
    # Get sample data
    data = get_sample_data()
    dashboard_images = get_dashboard_images()
    
    # Display a dashboard header image
    st.image(dashboard_images[0], use_column_width=True)
    
    st.write("Explore current real estate market trends, price distributions, and property insights.")
    
    # Create filter options
    st.sidebar.subheader("Filter Options")
    
    # Location filter
    locations = ["All"] + sorted(data["location"].unique().tolist())
    selected_location = st.sidebar.selectbox("Location", locations, index=0)
    
    # Property type filter
    property_types = ["All"] + sorted(data["property_type"].unique().tolist())
    selected_property_type = st.sidebar.selectbox("Property Type", property_types, index=0)
    
    # Price range filter
    min_price = int(data["price"].min())
    max_price = int(data["price"].max())
    price_range = st.sidebar.slider(
        "Price Range ($)",
        min_value=min_price,
        max_value=max_price,
        value=(min_price, max_price),
        step=10000
    )
    
    # Apply filters
    filtered_data = data.copy()
    
    if selected_location != "All":
        filtered_data = filtered_data[filtered_data["location"] == selected_location]
        
    if selected_property_type != "All":
        filtered_data = filtered_data[filtered_data["property_type"] == selected_property_type]
        
    filtered_data = filtered_data[(filtered_data["price"] >= price_range[0]) & 
                                  (filtered_data["price"] <= price_range[1])]
    
    # Display market overview metrics
    st.subheader("Market Overview")
    
    avg_price = filtered_data["price"].mean()
    median_price = filtered_data["price"].median()
    properties_count = len(filtered_data)
    avg_sqft_price = filtered_data["price"].sum() / filtered_data["square_feet"].sum()
    
    # Create metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Average Price",
            value=f"${avg_price:,.0f}",
            delta=f"{np.random.randint(-5, 6)}%"
        )
    
    with col2:
        st.metric(
            label="Median Price",
            value=f"${median_price:,.0f}",
            delta=f"{np.random.randint(-4, 7)}%"
        )
    
    with col3:
        st.metric(
            label="Avg. Price/Sq Ft",
            value=f"${avg_sqft_price:.2f}",
            delta=f"{np.random.randint(-3, 8)}%"
        )
    
    with col4:
        st.metric(
            label="Properties Available",
            value=f"{properties_count}",
            delta=f"{np.random.randint(-20, 21)}"
        )
    
    # Display price distribution
    st.subheader("Price Distribution")
    
    # Create histogram with KDE
    fig = px.histogram(
        filtered_data,
        x="price",
        nbins=30,
        marginal="box",
        color="property_type" if selected_property_type == "All" else None,
        title="Property Price Distribution",
        opacity=0.7,
        hover_data=["location", "bedrooms", "bathrooms", "square_feet"]
    )
    fig.update_layout(xaxis_title="Price ($)", yaxis_title="Number of Properties")
    st.plotly_chart(fig, use_container_width=True)
    
    # Create a two-column layout for additional charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Create a scatterplot of price vs. square feet
        st.subheader("Price vs. Property Size")
        fig = px.scatter(
            filtered_data,
            x="square_feet",
            y="price",
            color="location" if selected_location == "All" else "property_type",
            size="bedrooms",
            hover_name="location",
            hover_data=["property_type", "bathrooms", "year_built"],
            title="Price vs. Square Footage",
            trendline="ols" if len(filtered_data) > 2 else None
        )
        fig.update_layout(xaxis_title="Square Feet", yaxis_title="Price ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Create a bar chart of average price by location
        st.subheader("Average Price by Location")
        location_avg = filtered_data.groupby("location")["price"].mean().reset_index()
        location_avg = location_avg.sort_values("price", ascending=False)
        
        fig = px.bar(
            location_avg,
            x="location",
            y="price",
            color="location",
            title="Average Price by Location",
            text_auto='.2s'
        )
        fig.update_layout(xaxis_title="Location", yaxis_title="Average Price ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Display price trends over time (simulated data)
    st.subheader("Price Trends Over Time")
    
    # Generate simulated price trend data
    today = datetime.now()
    dates = [(today - timedelta(days=30*i)).strftime("%Y-%m") for i in range(12, 0, -1)]
    
    trend_data = []
    for loc in data["location"].unique():
        base_price = data[data["location"] == loc]["price"].mean()
        for i, date in enumerate(dates):
            # Create a realistic trend with seasonal variations and a general trend
            month = int(date.split("-")[1])
            seasonal_factor = 1.0 + 0.03 * np.sin((month - 1) * np.pi / 6)  # Seasonal variation
            trend_factor = 1.0 + 0.005 * i  # General upward trend
            random_factor = np.random.normal(1.0, 0.02)  # Random noise
            
            price = base_price * seasonal_factor * trend_factor * random_factor
            
            trend_data.append({
                "Date": date,
                "Location": loc,
                "Average Price": price
            })
    
    trend_df = pd.DataFrame(trend_data)
    
    # Create line chart for price trends
    fig = px.line(
        trend_df,
        x="Date",
        y="Average Price",
        color="Location",
        title="12-Month Price Trend by Location",
        markers=True
    )
    fig.update_layout(xaxis_title="Month", yaxis_title="Average Price ($)")
    st.plotly_chart(fig, use_container_width=True)
    
    # Display a heatmap of property prices by location
    st.subheader("Property Price Heatmap")
    
    # Get property locations
    locations = get_property_locations()
    
    # Create a map centered on the average lat/lon
    avg_lat = sum(loc[0] for loc in locations) / len(locations)
    avg_lon = sum(loc[1] for loc in locations) / len(locations)
    
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12, tiles="CartoDB positron")
    
    # Add a heatmap layer
    from folium.plugins import HeatMap
    
    # Generate some random property values for the heatmap
    property_values = []
    for i, (lat, lon) in enumerate(locations):
        # Get a random price within the filtered range
        price = np.random.uniform(price_range[0], price_range[1])
        # Normalize the price for the heatmap (0-1 range)
        normalized_price = (price - price_range[0]) / (price_range[1] - price_range[0])
        property_values.append([lat, lon, normalized_price])
    
    # Add the heatmap layer
    HeatMap(property_values, radius=15, blur=10, gradient={0.4: 'blue', 0.65: 'lime', 0.8: 'yellow', 1: 'red'}).add_to(m)
    
    # Display the map
    folium_static(m)
    st.markdown("*The heatmap shows concentration of property values - red areas indicate higher prices.*")
    
    # Insights section
    st.subheader("Market Insights")
    
    # Generate some insights based on the data
    insights = [
        f"The average property price in {selected_location if selected_location != 'All' else 'all areas'} is ${avg_price:,.2f}.",
        f"Properties in {filtered_data.groupby('location')['price'].mean().idxmax()} have the highest average price.",
        f"{filtered_data.groupby('property_type')['price'].mean().idxmax()} properties tend to be the most expensive type.",
        f"The average price per square foot is ${avg_sqft_price:.2f}.",
        f"There are currently {properties_count} properties available that match your filters."
    ]
    
    # Display insights in an expandable section
    with st.expander("View Market Insights", expanded=True):
        for insight in insights:
            st.markdown(f"- {insight}")
        
        # Add a fake trend prediction
        trend_direction = np.random.choice(["rising", "stable", "falling"])
        trend_percentage = np.random.randint(1, 6)
        
        if trend_direction == "rising":
            st.markdown(f"- Market prediction: Prices are expected to **increase by {trend_percentage}%** in the next quarter.")
        elif trend_direction == "stable":
            st.markdown(f"- Market prediction: Prices are expected to remain **stable** in the next quarter.")
        else:
            st.markdown(f"- Market prediction: Prices are expected to **decrease by {trend_percentage}%** in the next quarter.")
