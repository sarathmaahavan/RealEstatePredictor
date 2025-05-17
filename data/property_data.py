import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def get_sample_data():
    """
    Generate sample property data for demonstration.
    
    Returns:
        pandas.DataFrame: A dataframe containing sample property data
    """
    # Set seed for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    # Define sample data parameters
    n_properties = 100
    locations = ["Riga Center", "Vecriga (Old Town)", "Agenskalns", "Purvciems", "Kengarags", "Jugla", "Imanta", "Ziepniekkalns", "Teika", "Ieala"]
    property_types = ["Single Family Home", "Condo/Apartment", "Townhouse", "Multi-Family", "Luxury Villa"]
    
    # Generate sample data
    data = {
        "id": list(range(1, n_properties + 1)),
        "location": [random.choice(locations) for _ in range(n_properties)],
        "property_type": [random.choice(property_types) for _ in range(n_properties)],
        "bedrooms": [random.randint(1, 6) for _ in range(n_properties)],
        "bathrooms": [round(random.uniform(1, 4), 1) for _ in range(n_properties)],
        "square_feet": [random.randint(600, 5000) for _ in range(n_properties)],
        "year_built": [random.randint(1950, 2023) for _ in range(n_properties)],
        "has_garage": [random.choice([True, False, True]) for _ in range(n_properties)],
        "has_pool": [random.choice([True, False, False, False, False]) for _ in range(n_properties)],
        "has_garden": [random.choice([True, False, True, True]) for _ in range(n_properties)],
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Generate prices based on property characteristics
    # Base price factors for Riga neighborhoods
    location_factors = {
        "Riga Center": 1.6,
        "Vecriga (Old Town)": 1.8,
        "Agenskalns": 1.2,
        "Purvciems": 1.0,
        "Kengarags": 0.9,
        "Jugla": 1.0,
        "Imanta": 1.1,
        "Ziepniekkalns": 0.95,
        "Teika": 1.3,
        "Ieala": 1.5  # New premium neighborhood
    }
    
    property_type_factors = {
        "Single Family Home": 1.2,
        "Condo/Apartment": 1.0,
        "Townhouse": 1.1,
        "Multi-Family": 1.3,
        "Luxury Villa": 2.0
    }
    
    # Calculate price based on property characteristics
    df["price"] = df.apply(
        lambda row: (
            200000 +  # Base price
            (row["square_feet"] * 150) +  # Price per square foot
            (row["bedrooms"] * 20000) +  # Value per bedroom
            (row["bathrooms"] * 15000) +  # Value per bathroom
            ((2023 - row["year_built"]) * -500) +  # Age depreciation
            (50000 if row["has_garage"] else 0) +  # Garage premium
            (80000 if row["has_pool"] else 0) +  # Pool premium
            (30000 if row["has_garden"] else 0)  # Garden premium
        ) * location_factors[row["location"]] * property_type_factors[row["property_type"]] * np.random.normal(1, 0.1),  # Add random noise
        axis=1
    )
    
    # Round and ensure minimum price
    df["price"] = df["price"].apply(lambda x: max(round(x, -3), 100000))
    
    # Add date listed (within the last 60 days)
    today = datetime.now()
    df["date_listed"] = [today - timedelta(days=random.randint(1, 60)) for _ in range(n_properties)]
    
    return df

def get_property_locations():
    """
    Generate sample property locations for map visualizations.
    
    Returns:
        list: A list of (latitude, longitude) tuples for sample properties
    """
    # Center points for Riga neighborhoods (approximate values)
    location_centers = {
        "Riga Center": (56.9496, 24.1052),
        "Vecriga (Old Town)": (56.9476, 24.1087),
        "Agenskalns": (56.9354, 24.0751),
        "Purvciems": (56.9561, 24.1968),
        "Kengarags": (56.9137, 24.1674),
        "Jugla": (56.9859, 24.2461),
        "Imanta": (56.9559, 24.0040),
        "Ziepniekkalns": (56.8990, 24.0876),
        "Teika": (56.9772, 24.1914),
        "Ieala": (56.9600, 24.1300)  # New neighborhood coordinates
    }
    
    # Generate 20 random property locations
    locations = []
    for _ in range(20):
        # Choose a random location type
        loc_type = random.choice(list(location_centers.keys()))
        
        # Get the center coordinates for that location
        center_lat, center_lon = location_centers[loc_type]
        
        # Add some random offset (about 0.02 degrees, which is roughly 1-2 miles)
        lat = center_lat + random.uniform(-0.02, 0.02)
        lon = center_lon + random.uniform(-0.02, 0.02)
        
        locations.append((lat, lon))
    
    return locations
