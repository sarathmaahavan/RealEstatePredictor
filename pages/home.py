import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import plotly.express as px
from datetime import datetime
from models.price_predictor import get_demo_model
from utils.data_processor import DataProcessor
from data.property_data import get_sample_data, get_property_locations
from assets.image_urls import get_property_images


def show():
    """Display the home page with property details input and price prediction"""
    # Get sample data
    data = get_sample_data()
    property_images = get_property_images()
    
    # Hero section with background image and overlay text - exact styling from the reference image
    st.markdown("""
    <div class="hero-section" style="background-image: url('https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1770&q=80');">
        <div class="hero-overlay">
            <h1 class="hero-title">Precise Property Price Prediction Powered by AI</h1>
            <p class="hero-subtitle">Get accurate home value estimates based on advanced machine learning algorithms and comprehensive market data analysis.</p>
            <div>
                <a href="#property-form" class="hero-btn hero-btn-primary">Get Price Estimate</a>
                <a href="#learn-more" class="hero-btn">Learn More</a>
            </div>
        </div>
    </div>
    
    <div class="content-container">
        <h2 id="property-form" style="margin-top: 40px; margin-bottom: 20px;">Find the perfect price for your property</h2>
        <p>Enter property details below to get an accurate price prediction for the Riga, Latvia real estate market.</p>
    """, unsafe_allow_html=True)
    
    # Create a two-column layout for input form
    col1, col2 = st.columns(2)
    
    with col1:
        # Property details inputs
        location = st.selectbox(
            "Location", 
            options=["Riga Center", "Vecriga (Old Town)", "Agenskalns", "Purvciems", "Kengarags", "Jugla", "Imanta", "Ziepniekkalns", "Teika", "Ieala"],
            help="Select the neighborhood in Riga, Latvia"
        )
        
        property_type = st.selectbox(
            "Property Type",
            options=["Single Family Home", "Condo/Apartment", "Townhouse", "Multi-Family", "Luxury Villa"],
            help="Select the type of property"
        )
        
        square_feet = st.number_input(
            "Square Feet",
            min_value=500,
            max_value=10000,
            value=2000,
            step=100,
            help="Enter the total square footage of the property"
        )
        
    with col2:
        bedrooms = st.slider(
            "Number of Bedrooms",
            min_value=1,
            max_value=10,
            value=3,
            help="Select the number of bedrooms"
        )
        
        bathrooms = st.slider(
            "Number of Bathrooms",
            min_value=1,
            max_value=7,
            value=2,
            help="Select the number of bathrooms"
        )
        
        year_built = st.number_input(
            "Year Built",
            min_value=1900,
            max_value=datetime.now().year,
            value=2000,
            step=1,
            help="Enter the year the property was built"
        )
    
    # Additional features (collapsible)
    with st.expander("Additional Features"):
        col3, col4 = st.columns(2)
        
        with col3:
            has_garage = st.checkbox("Garage", value=True)
            has_pool = st.checkbox("Swimming Pool")
            has_garden = st.checkbox("Garden/Yard", value=True)
        
        with col4:
            has_fireplace = st.checkbox("Fireplace")
            is_renovated = st.checkbox("Recently Renovated")
            has_view = st.checkbox("Scenic View")
    
    # Predict button
    if st.button("Predict Price", type="primary"):
        with st.spinner("Calculating property value..."):
            # Collect all inputs into a property dictionary
            property_details = {
                "location": location,
                "property_type": property_type,
                "square_feet": square_feet,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "year_built": year_built,
                "has_garage": has_garage,
                "has_pool": has_pool,
                "has_garden": has_garden,
                "has_fireplace": has_fireplace,
                "is_renovated": is_renovated,
                "has_view": has_view
            }
            
            # Get prediction from model
            predictor = get_demo_model()
            result = predictor.predict(property_details)
            
            # Display prediction result
            display_prediction_result(result, property_details)
            
            # Save this prediction to recent predictions
            if len(st.session_state.recent_predictions) >= 5:
                st.session_state.recent_predictions.pop(0)
            
            st.session_state.recent_predictions.append({
                "property": property_details,
                "prediction": result,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    
    # Display map with property locations
    st.markdown("### Property Locations")
    display_property_map()
    
    # Display a couple of market insights
    st.markdown("### Market Insights")
    display_market_insights(data)
    
    # Close the content container
    st.markdown("</div>", unsafe_allow_html=True)

def display_prediction_result(result, property_details):
    """Display the prediction results with attractive visuals"""
    # Create columns for result display
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display the main prediction
        st.markdown("### Predicted Property Value")
        
        predicted_price = result["predicted_price"]
        lower_bound = result["lower_bound"]
        upper_bound = result["upper_bound"]
        confidence = result["confidence_score"]
        
        # Format prices as strings with commas (using Euros for Latvia)
        predicted_price_str = f"€{predicted_price:,.2f}"
        price_range = f"€{lower_bound:,.2f} - €{upper_bound:,.2f}"
        
        # Display the main price prediction
        st.markdown(f"<h2 style='text-align: center;'>{predicted_price_str}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>Estimated Value Range: {price_range}</p>", unsafe_allow_html=True)
        
        # Create a gauge chart for confidence level using Plotly
        fig = px.bar(
            x=["Confidence"],
            y=[confidence * 100],
            text=[f"{confidence * 100:.0f}%"],
            height=100,
            range_y=[0, 100],
            color=[confidence * 100],
            color_continuous_scale=["red", "yellow", "green"],
        )
        fig.update_layout(margin=dict(t=0, r=0, b=0, l=0))
        st.plotly_chart(fig, use_container_width=True)
        
        # Display a button to save this property
        if st.button("Save This Property"):
            if property_details not in [p["property"] for p in st.session_state.saved_properties]:
                st.session_state.saved_properties.append({
                    "property": property_details.copy(),
                    "prediction": result,
                    "saved_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("Property saved to your dashboard!")
            else:
                st.info("This property is already saved in your dashboard.")
    
    with col2:
        # Display property summary
        st.markdown("### Property Summary")
        property_summary = f"""
        - **Location**: {property_details['location']}
        - **Type**: {property_details['property_type']}
        - **Size**: {property_details['square_feet']} sq ft
        - **Rooms**: {property_details['bedrooms']}b/{property_details['bathrooms']}ba
        - **Year Built**: {property_details['year_built']}
        """
        st.markdown(property_summary)
        
        # Display comparable price per square foot
        price_per_sqft = result["predicted_price"] / property_details["square_feet"]
        st.markdown(f"**Price per sq ft**: €{price_per_sqft:.2f}")

def display_property_map():
    """Display an interactive map with sample property locations in Riga, Latvia"""
    # Get property locations from sample data
    locations = get_property_locations()
    
    # Create a map centered on Riga, Latvia
    riga_center = [56.9496, 24.1052]  # Riga city center coordinates
    
    m = folium.Map(location=riga_center, zoom_start=12, tiles="CartoDB positron")
    
    # Add markers for each property
    for i, (lat, lon) in enumerate(locations):
        # Determine price category (randomly for demo)
        price_category = np.random.choice(["Low", "Fair", "High"])
        
        # Set marker color based on price category
        if price_category == "Low":
            color = "green"
            icon = "home"
        elif price_category == "Fair":
            color = "blue"
            icon = "home"
        else:
            color = "red"
            icon = "home"
            
        # Create popup content
        popup_content = f"""
        <div>
            <h4>Property #{i+1}</h4>
            <p><b>Price:</b> ${np.random.randint(200000, 800000):,}</p>
            <p><b>Category:</b> {price_category} priced</p>
            <p><b>Area:</b> {np.random.randint(1000, 3000)} sq ft</p>
        </div>
        """
        
        # Add marker to map
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_content, max_width=300),
            icon=folium.Icon(color=color, icon=icon, prefix='fa'),
            tooltip=f"Property #{i+1}"
        ).add_to(m)
    
    # Display the map in Streamlit
    folium_static(m)
    
    # Add a legend
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🟢 **Green**: Potentially underpriced")
    with col2:
        st.markdown("🔵 **Blue**: Fair market value")
    with col3:
        st.markdown("🔴 **Red**: Potentially overpriced")

def display_market_insights(data):
    """Display market insights with interactive charts"""
    # Process data for insights
    insights = DataProcessor.generate_market_insights(data)
    
    # Create a two-column layout for insights
    col1, col2 = st.columns(2)
    
    with col1:
        # Price distribution by property type
        st.subheader("Price by Property Type")
        fig = px.box(
            data,
            x="property_type",
            y="price",
            color="property_type",
            title="Price Distribution by Property Type",
            height=400
        )
        fig.update_layout(xaxis_title="Property Type", yaxis_title="Price ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Price vs. Square Feet scatter plot
        st.subheader("Price vs. Size")
        fig = px.scatter(
            data,
            x="square_feet",
            y="price",
            color="bedrooms",
            size="bathrooms",
            hover_name="location",
            title="Price vs. Square Footage",
            height=400
        )
        fig.update_layout(xaxis_title="Square Feet", yaxis_title="Price ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Add some key statistics as metrics
    st.subheader("Market Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Average Price",
            value=f"${insights['avg_price']:,.2f}",
            delta=f"{np.random.randint(-5, 15)}% from last year"
        )
    
    with col2:
        st.metric(
            label="Avg. Price per Sq Ft",
            value=f"${insights['avg_price_per_sqft']:,.2f}",
            delta=f"{np.random.randint(-3, 10)}% from last year"
        )
    
    with col3:
        count_for_sale = len(data)
        st.metric(
            label="Properties For Sale",
            value=f"{count_for_sale}",
            delta=f"{np.random.randint(-20, 30)}% from last month"
        )
