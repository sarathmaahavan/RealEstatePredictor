import streamlit as st
import os
import sys

# Add the current directory to the path so that python can find the modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Direct imports from the modules
import pages.home
import pages.property_comparison
import pages.market_trends
import pages.dashboard

# Page configuration
st.set_page_config(
    page_title="Real Estate Price Predictor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if "saved_properties" not in st.session_state:
    st.session_state.saved_properties = []
if "recent_predictions" not in st.session_state:
    st.session_state.recent_predictions = []
if "user_preferences" not in st.session_state:
    st.session_state.user_preferences = {"notify_price_drop": False, "notify_market_change": False}

# Navigation setup
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Property Comparison", "Market Trends", "Dashboard"]
)

# Render the selected page
if page == "Home":
    pages.home.show()
elif page == "Property Comparison":
    pages.property_comparison.show()
elif page == "Market Trends":
    pages.market_trends.show()
elif page == "Dashboard":
    pages.dashboard.show()

# Footer
st.sidebar.markdown("---")
st.sidebar.info("© 2023 Real Estate Price Predictor")
