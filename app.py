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
    initial_sidebar_state="collapsed"
)

# Custom CSS to match the design in the image
st.markdown("""
<style>
    /* Hide sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Main content styling */
    .main .block-container {
        padding-top: 0 !important;
        max-width: 100% !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    
    .stApp {
        background-color: white;
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
    
    /* Header styling */
    .header-container {
        max-width: 100%;
        padding: 0;
        margin: 0;
    }
    
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: white;
        padding: 1rem 4rem;
        border-bottom: 1px solid #eee;
        margin-bottom: 0;
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
    
    .active-nav-link {
        color: #1E90FF !important;
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
    
    /* Content container for proper spacing */
    .content-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    /* Hero section */
    .hero-section {
        position: relative;
        width: 100%;
        height: 600px;
        background-size: cover;
        background-position: center;
        color: white;
        margin-bottom: 2rem;
    }
    
    .hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.5));
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 0 4rem;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        max-width: 800px;
        text-shadow: 0px 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        margin-bottom: 2rem;
        max-width: 700px;
        text-shadow: 0px 1px 3px rgba(0,0,0,0.3);
    }
    
    .hero-btn {
        background-color: white;
        color: #333;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        font-weight: 600;
        display: inline-block;
        cursor: pointer;
        text-decoration: none;
        margin-right: 1rem;
        transition: all 0.2s ease;
    }
    
    .hero-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .hero-btn-primary {
        background-color: #1E90FF;
        color: white;
    }
    
    .hero-btn-primary:hover {
        background-color: #0070e0;
    }
</style>
""", unsafe_allow_html=True)

# Create session state for active page if it doesn't exist
if "active_page" not in st.session_state:
    st.session_state.active_page = "Home"

# Define page selection function
def set_page(page_name):
    st.session_state.active_page = page_name
    st.rerun() # Using st.rerun() instead of experimental_rerun

# Custom header to match the image
home_class = "active-nav-link" if st.session_state.active_page == "Home" else ""
predictions_class = "active-nav-link" if st.session_state.active_page == "Predictions" else ""
market_trends_class = "active-nav-link" if st.session_state.active_page == "Market Trends" else ""
about_class = "active-nav-link" if st.session_state.active_page == "About" else ""

# Create the HTML for the header with navigation
header_html = f"""
<div class="header">
    <div class="logo">PropValue</div>
    <div class="nav-links">
        <a href="#" class="{home_class}" onclick="handleNavClick('Home'); return false;">Home</a>
        <a href="#" class="{predictions_class}" onclick="handleNavClick('Predictions'); return false;">Predictions</a>
        <a href="#" class="{market_trends_class}" onclick="handleNavClick('Market Trends'); return false;">Market Trends</a>
        <a href="#" class="{about_class}" onclick="handleNavClick('About'); return false;">About</a>
    </div>
    <button class="sign-in-btn">Sign In</button>
</div>
"""

# Add JavaScript separately (not inside the f-string)
js_code = """
<script>
function handleNavClick(page) {
    // For debugging
    console.log("Navigation clicked: " + page);
    
    // Try to set the value using a form submit approach instead
    const form = document.querySelector('form');
    if (form) {
        const input = form.querySelector('input');
        if (input) {
            input.value = page;
            form.submit();
        }
    }
}
</script>
"""

# Combine the HTML and JavaScript
full_header = header_html + js_code

st.markdown(full_header, unsafe_allow_html=True)

# Get click events from the navigation
nav_placeholder = st.empty()
nav_clicked = nav_placeholder.text_input("", key="nav_input", label_visibility="collapsed")

if nav_clicked and nav_clicked != st.session_state.active_page:
    set_page(nav_clicked)

# Initialize session state variables if they don't exist
if "saved_properties" not in st.session_state:
    st.session_state.saved_properties = []
if "recent_predictions" not in st.session_state:
    st.session_state.recent_predictions = []
if "user_preferences" not in st.session_state:
    st.session_state.user_preferences = {"notify_price_drop": False, "notify_market_change": False}

# Render the selected page based on navigation
page = st.session_state.active_page

if page == "Home":
    pages.home.show()
elif page == "Predictions":
    pages.property_comparison.show()
elif page == "Market Trends":
    pages.market_trends.show()
elif page == "About":
    pages.dashboard.show()

# Footer
st.markdown("<div style='text-align: center; margin-top: 50px; color: #666; font-size: 0.8rem;'>© 2023 PropValue - Real Estate Price Predictor</div>", unsafe_allow_html=True)
