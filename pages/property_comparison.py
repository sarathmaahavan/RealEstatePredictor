import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processor import DataProcessor
from data.property_data import get_sample_data
from models.price_predictor import get_demo_model
from assets.image_urls import get_property_images

def show():
    """Display the property comparison page"""
    st.title("Property Comparison")
    
    # Get sample data and images
    data = get_sample_data()
    property_images = get_property_images()
    
    st.write("Compare multiple properties side-by-side to make an informed decision.")
    
    # Select properties to compare
    st.subheader("Select Properties to Compare")
    
    # Option 1: Choose from saved properties
    if st.session_state.saved_properties:
        st.write("Option 1: Select from your saved properties")
        saved_props = st.session_state.saved_properties
        
        # Format saved properties for selection
        saved_options = [f"{prop['property']['location']} - {prop['property']['property_type']} - {prop['property']['bedrooms']}bd/{prop['property']['bathrooms']}ba - ${prop['prediction']['predicted_price']:,.2f}" for prop in saved_props]
        
        selected_saved = st.multiselect(
            "Your Saved Properties",
            options=saved_options,
            default=saved_options[:min(2, len(saved_options))] if saved_options else None,
            help="Select properties from your saved list to compare"
        )
        
        # Get the index of selected properties
        selected_saved_indices = [saved_options.index(prop) for prop in selected_saved]
        selected_properties = [saved_props[i] for i in selected_saved_indices]
    else:
        st.info("You don't have any saved properties. Go to the Home page to predict prices and save properties.")
        selected_properties = []
    
    # Option 2: Choose from sample listings
    st.write("Option 2: Select from sample property listings")
    
    # Create a more user-friendly way to select sample properties
    col1, col2, col3 = st.columns(3)
    sample_selections = []
    
    # Define some interesting sample properties for comparison
    sample_props = [
        {"name": "Downtown Luxury Condo", "details": {"location": "Downtown", "property_type": "Condo/Apartment", "bedrooms": 2, "bathrooms": 2, "square_feet": 1200, "year_built": 2015, "has_garage": True}},
        {"name": "Suburban Family Home", "details": {"location": "Suburb", "property_type": "Single Family Home", "bedrooms": 4, "bathrooms": 3, "square_feet": 2800, "year_built": 2005, "has_garage": True}},
        {"name": "Urban Townhouse", "details": {"location": "Urban", "property_type": "Townhouse", "bedrooms": 3, "bathrooms": 2.5, "square_feet": 1800, "year_built": 2010, "has_garage": True}},
        {"name": "Coastal Villa", "details": {"location": "Coastal", "property_type": "Luxury Villa", "bedrooms": 5, "bathrooms": 4, "square_feet": 4200, "year_built": 2018, "has_garage": True}},
        {"name": "Mountain Cabin", "details": {"location": "Mountain View", "property_type": "Single Family Home", "bedrooms": 3, "bathrooms": 2, "square_feet": 1700, "year_built": 1995, "has_garage": False}},
        {"name": "Downtown Studio", "details": {"location": "Downtown", "property_type": "Condo/Apartment", "bedrooms": 1, "bathrooms": 1, "square_feet": 650, "year_built": 2012, "has_garage": False}}
    ]
    
    with col1:
        s1 = st.checkbox("Downtown Luxury Condo", value=True)
        s2 = st.checkbox("Suburban Family Home", value=True)
        if s1:
            sample_selections.append(0)
        if s2:
            sample_selections.append(1)
            
    with col2:
        s3 = st.checkbox("Urban Townhouse")
        s4 = st.checkbox("Coastal Villa")
        if s3:
            sample_selections.append(2)
        if s4:
            sample_selections.append(3)
            
    with col3:
        s5 = st.checkbox("Mountain Cabin")
        s6 = st.checkbox("Downtown Studio")
        if s5:
            sample_selections.append(4)
        if s6:
            sample_selections.append(5)
    
    # Get predictions for the sample properties
    predictor = get_demo_model()
    for i in sample_selections:
        prop_details = sample_props[i]["details"]
        prediction = predictor.predict(prop_details)
        selected_properties.append({
            "property": prop_details,
            "prediction": prediction,
            "name": sample_props[i]["name"]
        })
    
    # Perform the comparison if there are selected properties
    if len(selected_properties) >= 2:
        display_property_comparison(selected_properties, property_images)
    elif len(selected_properties) == 1:
        st.warning("Please select at least one more property to compare.")
    else:
        st.info("Please select at least two properties to compare.")

def display_property_comparison(properties, property_images):
    """Display a side-by-side comparison of selected properties"""
    st.markdown("---")
    st.subheader("Property Comparison")
    
    # Determine how many columns we need
    num_properties = len(properties)
    cols = st.columns(num_properties)
    
    # Display property comparison cards
    for i, (col, prop) in enumerate(zip(cols, properties)):
        with col:
            # Display property image
            img_index = i % len(property_images)
            st.image(property_images[img_index], use_column_width=True)
            
            # Property name/title
            if "name" in prop:
                st.markdown(f"### {prop['name']}")
            else:
                st.markdown(f"### Property {i+1}")
            
            # Price prediction
            predicted_price = prop['prediction']['predicted_price']
            st.markdown(f"#### ${predicted_price:,.2f}")
            
            # Property details
            p = prop['property']
            details = f"""
            - **Location**: {p['location']}
            - **Type**: {p['property_type']}
            - **Size**: {p['square_feet']} sq ft
            - **Bedrooms**: {p['bedrooms']}
            - **Bathrooms**: {p['bathrooms']}
            - **Year Built**: {p.get('year_built', 'N/A')}
            - **Price/sqft**: ${predicted_price/p['square_feet']:.2f}
            """
            st.markdown(details)
            
            # Features
            features = []
            if p.get('has_garage', False):
                features.append("Garage")
            if p.get('has_pool', False):
                features.append("Pool")
            if p.get('has_garden', False):
                features.append("Garden")
            if p.get('has_fireplace', False):
                features.append("Fireplace")
            if p.get('is_renovated', False):
                features.append("Renovated")
            if p.get('has_view', False):
                features.append("Scenic View")
                
            if features:
                st.markdown("**Features**: " + ", ".join(features))
    
    # Create visualizations for comparison
    st.markdown("---")
    st.subheader("Visual Comparison")
    
    # Create data for visualizations
    comparison_data = []
    for i, prop in enumerate(properties):
        p = prop['property']
        name = prop.get('name', f"Property {i+1}")
        
        comparison_data.append({
            "Property": name,
            "Price": prop['prediction']['predicted_price'],
            "Square Feet": p['square_feet'],
            "Bedrooms": p['bedrooms'],
            "Bathrooms": p['bathrooms'],
            "Price per Sq Ft": prop['prediction']['predicted_price'] / p['square_feet'],
            "Location": p['location'],
            "Type": p['property_type']
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Create a two-column layout for charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Price comparison bar chart
        fig = px.bar(
            comparison_df,
            x="Property",
            y="Price",
            color="Property",
            title="Price Comparison",
            text_auto='.2s'
        )
        fig.update_layout(xaxis_title="", yaxis_title="Price ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Price per square foot comparison
        fig = px.bar(
            comparison_df,
            x="Property",
            y="Price per Sq Ft",
            color="Property",
            title="Price per Square Foot Comparison",
            text_auto='.2f'
        )
        fig.update_layout(xaxis_title="", yaxis_title="Price per Sq Ft ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Create a radar chart comparing multiple attributes
    st.subheader("Feature Comparison")
    
    # Normalize the data for radar chart
    radar_df = comparison_df.copy()
    features_to_normalize = ["Square Feet", "Price", "Bedrooms", "Bathrooms", "Price per Sq Ft"]
    
    for feature in features_to_normalize:
        max_val = radar_df[feature].max()
        if max_val > 0:  # Avoid division by zero
            radar_df[feature] = radar_df[feature] / max_val
    
    # Create radar chart
    fig = go.Figure()
    
    for i, row in radar_df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row["Square Feet"], row["Bedrooms"], row["Bathrooms"], 
               1 - row["Price"]/radar_df["Price"].max(), 1 - row["Price per Sq Ft"]/radar_df["Price per Sq Ft"].max()],
            theta=["Size", "Bedrooms", "Bathrooms", "Affordability", "Value"],
            fill='toself',
            name=row["Property"]
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Property Feature Comparison"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("Note: In the radar chart, higher values for 'Affordability' and 'Value' indicate lower prices and better value, respectively.")
    
    # Decision helper
    st.markdown("---")
    st.subheader("Decision Helper")
    
    # Calculate some basic comparison metrics
    best_value_idx = comparison_df["Price per Sq Ft"].idxmin()
    best_value_prop = comparison_df.iloc[best_value_idx]["Property"]
    
    most_space_idx = comparison_df["Square Feet"].idxmax()
    most_space_prop = comparison_df.iloc[most_space_idx]["Property"]
    
    newest_idx = max([(i, p['property'].get('year_built', 0)) for i, p in enumerate(properties)], key=lambda x: x[1])[0]
    newest_prop = properties[newest_idx].get('name', f"Property {newest_idx+1}")
    
    # Display insights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Best Value", best_value_prop)
        st.write(f"Lowest price per square foot: ${comparison_df.iloc[best_value_idx]['Price per Sq Ft']:.2f}")
        
    with col2:
        st.metric("Most Space", most_space_prop)
        st.write(f"Largest property: {comparison_df.iloc[most_space_idx]['Square Feet']} sq ft")
        
    with col3:
        st.metric("Newest Property", newest_prop)
        year = properties[newest_idx]['property'].get('year_built', 'N/A')
        st.write(f"Built in: {year}")
