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
    page_title="PropValue - Real Estate Price Predictor",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match the design in the image
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        font-weight: 600;
    }
    .stButton button {
        background-color: #1E90FF;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    /* Header styling */
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: white;
        padding: 1rem 2rem;
        border-bottom: 1px solid #eee;
        margin-bottom: 1rem;
    }
    .logo {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E90FF;
    }
    .nav-links {
        display: flex;
        gap: 2rem;
    }
    .nav-links a {
        text-decoration: none;
        color: #333;
        font-weight: 500;
    }
    .sign-in-btn {
        background-color: #1E90FF;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Custom header to match the image
st.markdown("""
<div class="header">
    <div class="logo">PropValue</div>
    <div class="nav-links">
        <a href="#">Home</a>
        <a href="#">Predictions</a>
        <a href="#">Market Trends</a>
        <a href="#">About</a>
    </div>
    <button class="sign-in-btn">Sign In</button>
</div>
""", unsafe_allow_html=True)

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
