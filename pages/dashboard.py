import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from data.property_data import get_sample_data
from assets.image_urls import get_dashboard_images, get_property_images

def show():
    """Display the user dashboard with saved properties and preferences"""
    st.title("Your Real Estate Dashboard")
    
    # Get sample data and images
    dashboard_images = get_dashboard_images()
    property_images = get_property_images()
    
    # Display a dashboard header image
    st.image(dashboard_images[1], use_column_width=True)
    
    # Check if there are any saved properties
    if not st.session_state.saved_properties and not st.session_state.recent_predictions:
        st.warning("You haven't saved any properties or made any predictions yet.")
        st.write("Go to the Home page to predict property prices and save properties of interest.")
        return
    
    # Create tabs for different dashboard sections
    tab1, tab2, tab3 = st.tabs(["Saved Properties", "Recent Predictions", "Preferences"])
    
    with tab1:
        display_saved_properties(property_images)
    
    with tab2:
        display_recent_predictions()
    
    with tab3:
        display_user_preferences()

def display_saved_properties(property_images):
    """Display the user's saved properties"""
    if not st.session_state.saved_properties:
        st.info("You haven't saved any properties yet.")
        st.write("When you find a property you like, click the 'Save This Property' button on the prediction page.")
        return
    
    st.subheader("Your Saved Properties")
    
    # Create a button to clear all saved properties
    if st.button("Clear All Saved Properties"):
        st.session_state.saved_properties = []
        st.success("All saved properties have been cleared.")
        st.rerun()
    
    # Display saved properties in a grid
    saved_props = st.session_state.saved_properties
    
    # Display properties in rows of 2
    for i in range(0, len(saved_props), 2):
        cols = st.columns(2)
        
        for j in range(2):
            if i + j < len(saved_props):
                prop = saved_props[i + j]
                p = prop["property"]
                pred = prop["prediction"]
                
                with cols[j]:
                    # Create a card-like display
                    with st.container():
                        # Property image
                        img_index = (i + j) % len(property_images)
                        st.image(property_images[img_index], use_column_width=True)
                        
                        # Property details
                        st.markdown(f"### {p['location']} {p['property_type']}")
                        st.markdown(f"**Predicted Price:** ${pred['predicted_price']:,.2f}")
                        st.markdown(f"**Features:** {p['bedrooms']}bd/{p['bathrooms']}ba, {p['square_feet']} sq ft")
                        
                        if 'year_built' in p:
                            st.markdown(f"**Year Built:** {p['year_built']}")
                        
                        # Additional features
                        features = []
                        if p.get('has_garage', False):
                            features.append("Garage")
                        if p.get('has_pool', False):
                            features.append("Pool")
                        if p.get('has_garden', False):
                            features.append("Garden/Yard")
                        if p.get('has_fireplace', False):
                            features.append("Fireplace")
                        if p.get('is_renovated', False):
                            features.append("Renovated")
                        if p.get('has_view', False):
                            features.append("Scenic View")
                            
                        if features:
                            st.markdown("**Amenities:** " + ", ".join(features))
                        
                        st.markdown(f"**Saved on:** {prop.get('saved_on', 'N/A')}")
                        
                        # Add a delete button
                        if st.button(f"Remove Property {i+j+1}"):
                            st.session_state.saved_properties.pop(i + j)
                            st.success(f"Property removed from saved list.")
                            st.rerun()
    
    # Show price range of saved properties
    if len(saved_props) > 1:
        st.subheader("Price Comparison of Saved Properties")
        
        # Create a DataFrame for visualization
        comparison_data = []
        for i, prop in enumerate(saved_props):
            p = prop["property"]
            comparison_data.append({
                "Property": f"{p['location']} {p['property_type']}",
                "Price": prop["prediction"]["predicted_price"],
                "Square Feet": p["square_feet"],
                "Price per Sq Ft": prop["prediction"]["predicted_price"] / p["square_feet"]
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Create a bar chart comparing prices
        fig = px.bar(
            comparison_df,
            x="Property",
            y="Price",
            color="Price per Sq Ft",
            title="Saved Properties Price Comparison",
            text_auto='.2s',
            color_continuous_scale="Viridis"
        )
        fig.update_layout(xaxis_title="", yaxis_title="Price ($)")
        st.plotly_chart(fig, use_container_width=True)

def display_recent_predictions():
    """Display the user's recent property predictions"""
    if not st.session_state.recent_predictions:
        st.info("You haven't made any property predictions yet.")
        st.write("Go to the Home page to predict property prices.")
        return
    
    st.subheader("Your Recent Predictions")
    
    # Create a button to clear recent predictions
    if st.button("Clear Recent Predictions"):
        st.session_state.recent_predictions = []
        st.success("Recent predictions have been cleared.")
        st.rerun()
    
    # Convert recent predictions to DataFrame for display
    predictions = []
    for pred in st.session_state.recent_predictions:
        p = pred["property"]
        predictions.append({
            "Location": p["location"],
            "Type": p["property_type"],
            "Bedrooms": p["bedrooms"],
            "Bathrooms": p["bathrooms"],
            "Square Feet": p["square_feet"],
            "Predicted Price": f"${pred['prediction']['predicted_price']:,.2f}",
            "Price Range": f"${pred['prediction']['lower_bound']:,.2f} - ${pred['prediction']['upper_bound']:,.2f}",
            "Timestamp": pred["timestamp"]
        })
    
    # Reverse the order to show newest first
    predictions.reverse()
    
    # Display as a table
    st.dataframe(pd.DataFrame(predictions), use_container_width=True)
    
    # Create a line chart showing prediction history
    if len(predictions) > 1:
        st.subheader("Your Prediction History")
        
        # Extract data for chart
        history_data = []
        for i, pred in enumerate(reversed(st.session_state.recent_predictions)):
            history_data.append({
                "Index": i + 1,
                "Predicted Price": pred["prediction"]["predicted_price"],
                "Property": f"{pred['property']['location']} {pred['property']['property_type']}"
            })
        
        history_df = pd.DataFrame(history_data)
        
        # Create a line chart
        fig = px.line(
            history_df,
            x="Index",
            y="Predicted Price",
            markers=True,
            text="Property",
            hover_data=["Property"],
            title="Your Prediction History"
        )
        fig.update_layout(xaxis_title="Prediction Number", yaxis_title="Predicted Price ($)")
        st.plotly_chart(fig, use_container_width=True)

def display_user_preferences():
    """Display and update user preferences"""
    st.subheader("Your Preferences")
    
    st.write("Customize your dashboard and notification preferences.")
    
    # Notification preferences
    st.markdown("### Notification Settings")
    
    notify_price_drop = st.checkbox(
        "Notify me about price drops in saved areas",
        value=st.session_state.user_preferences.get("notify_price_drop", False)
    )
    
    notify_market_change = st.checkbox(
        "Notify me about significant market changes",
        value=st.session_state.user_preferences.get("notify_market_change", False)
    )
    
    notify_frequency = st.radio(
        "Notification frequency",
        options=["Daily", "Weekly", "Monthly"],
        index=1  # Default to weekly
    )
    
    # Save button
    if st.button("Save Preferences"):
        st.session_state.user_preferences.update({
            "notify_price_drop": notify_price_drop,
            "notify_market_change": notify_market_change,
            "notify_frequency": notify_frequency
        })
        st.success("Preferences saved successfully!")
    
    # Display current search criteria
    st.markdown("### Default Search Criteria")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_location = st.selectbox(
            "Default Location",
            options=["Downtown", "Suburb", "Urban", "Rural", "Coastal", "Mountain View"],
            index=0
        )
        
        default_min_price = st.number_input(
            "Default Minimum Price ($)",
            min_value=0,
            max_value=10000000,
            value=200000,
            step=50000
        )
        
        default_min_beds = st.slider(
            "Default Minimum Bedrooms",
            min_value=1,
            max_value=7,
            value=2
        )
    
    with col2:
        default_property_type = st.selectbox(
            "Default Property Type",
            options=["Any", "Single Family Home", "Condo/Apartment", "Townhouse", "Multi-Family", "Luxury Villa"],
            index=0
        )
        
        default_max_price = st.number_input(
            "Default Maximum Price ($)",
            min_value=0,
            max_value=10000000,
            value=800000,
            step=50000
        )
        
        default_min_baths = st.slider(
            "Default Minimum Bathrooms",
            min_value=1,
            max_value=6,
            value=2
        )
    
    if st.button("Save Search Criteria"):
        st.session_state.user_preferences.update({
            "default_location": default_location,
            "default_property_type": default_property_type,
            "default_min_price": default_min_price,
            "default_max_price": default_max_price,
            "default_min_beds": default_min_beds,
            "default_min_baths": default_min_baths
        })
        st.success("Search criteria saved successfully!")
        
    # Account section (simulated)
    st.markdown("### Account Information")
    st.info("This is a demo application. In a real application, this section would contain user account details and preferences.")
    
    # Display a feedback form
    st.markdown("### Feedback")
    st.write("We'd love to hear your thoughts on how we can improve!")
    
    feedback = st.text_area("Your feedback", "")
    
    if st.button("Submit Feedback"):
        if feedback.strip():
            st.success("Thank you for your feedback! We'll use it to improve our service.")
        else:
            st.error("Please enter your feedback before submitting.")
