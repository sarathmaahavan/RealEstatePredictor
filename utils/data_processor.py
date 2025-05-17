import pandas as pd
import numpy as np
import re
from datetime import datetime

class DataProcessor:
    """Utility class for processing real estate data"""
    
    @staticmethod
    def clean_property_data(df):
        """
        Clean and process property data.
        
        Args:
            df (pandas.DataFrame): Raw property data
            
        Returns:
            pandas.DataFrame: Cleaned property data
        """
        # Make a copy to avoid modifying the original
        data = df.copy()
        
        # Handle missing values
        for col in data.columns:
            if data[col].dtype == 'object':
                data[col].fillna('Unknown', inplace=True)
            else:
                data[col].fillna(data[col].median(), inplace=True)
        
        # Convert price to numeric
        if 'price' in data.columns and data['price'].dtype == 'object':
            data['price'] = data['price'].apply(lambda x: DataProcessor._extract_price(x))
            
        # Convert square feet to numeric
        if 'square_feet' in data.columns and data['square_feet'].dtype == 'object':
            data['square_feet'] = data['square_feet'].apply(lambda x: DataProcessor._extract_numeric(x))
            
        # Convert bedrooms and bathrooms to numeric
        for col in ['bedrooms', 'bathrooms']:
            if col in data.columns and data[col].dtype == 'object':
                data[col] = data[col].apply(lambda x: DataProcessor._extract_numeric(x))
                
        # Convert year_built to numeric
        if 'year_built' in data.columns:
            data['year_built'] = pd.to_numeric(data['year_built'], errors='coerce')
            current_year = datetime.now().year
            data.loc[data['year_built'] > current_year, 'year_built'] = np.nan
            data['year_built'].fillna(data['year_built'].median(), inplace=True)
            
        return data
    
    @staticmethod
    def _extract_price(price_str):
        """Extract numeric price from string"""
        if pd.isna(price_str):
            return np.nan
            
        if isinstance(price_str, (int, float)):
            return price_str
            
        # Remove any non-numeric characters except decimal point
        price_numeric = re.sub(r'[^\d.]', '', str(price_str))
        try:
            return float(price_numeric)
        except ValueError:
            return np.nan
    
    @staticmethod
    def _extract_numeric(value):
        """Extract numeric value from string"""
        if pd.isna(value):
            return np.nan
            
        if isinstance(value, (int, float)):
            return value
            
        # Extract numbers from string
        numbers = re.findall(r'\d+\.?\d*', str(value))
        if numbers:
            return float(numbers[0])
        return np.nan
    
    @staticmethod
    def generate_market_insights(data):
        """
        Generate market insights from property data.
        
        Args:
            data (pandas.DataFrame): Property data
            
        Returns:
            dict: Dictionary of market insights
        """
        if len(data) == 0:
            return {
                "avg_price": 0,
                "price_range": (0, 0),
                "avg_price_per_sqft": 0,
                "popular_locations": [],
                "property_type_distribution": {},
                "price_trends": []
            }
            
        # Calculate basic statistics
        avg_price = data['price'].mean()
        min_price = data['price'].min()
        max_price = data['price'].max()
        
        # Price per square foot
        if 'square_feet' in data.columns:
            data['price_per_sqft'] = data['price'] / data['square_feet']
            avg_price_per_sqft = data['price_per_sqft'].mean()
        else:
            avg_price_per_sqft = 0
        
        # Popular locations
        if 'location' in data.columns:
            location_counts = data['location'].value_counts().head(5)
            popular_locations = location_counts.index.tolist()
        else:
            popular_locations = []
            
        # Property type distribution
        if 'property_type' in data.columns:
            property_type_dist = data['property_type'].value_counts().to_dict()
        else:
            property_type_dist = {}
            
        # Price trends (simplified, in a real app you'd use time series data)
        price_trends = []
        if 'date_listed' in data.columns and 'price' in data.columns:
            data['date_listed'] = pd.to_datetime(data['date_listed'])
            data = data.sort_values('date_listed')
            
            # Group by month and calculate average price
            monthly_prices = data.groupby(pd.Grouper(key='date_listed', freq='M'))['price'].mean().reset_index()
            price_trends = monthly_prices.to_dict('records')
        
        return {
            "avg_price": avg_price,
            "price_range": (min_price, max_price),
            "avg_price_per_sqft": avg_price_per_sqft,
            "popular_locations": popular_locations,
            "property_type_distribution": property_type_dist,
            "price_trends": price_trends
        }
    
    @staticmethod
    def filter_properties(data, filters):
        """
        Filter properties based on user criteria.
        
        Args:
            data (pandas.DataFrame): Property data
            filters (dict): Filter criteria
            
        Returns:
            pandas.DataFrame: Filtered property data
        """
        filtered_data = data.copy()
        
        # Apply filters
        if 'min_price' in filters and filters['min_price'] is not None:
            filtered_data = filtered_data[filtered_data['price'] >= filters['min_price']]
            
        if 'max_price' in filters and filters['max_price'] is not None:
            filtered_data = filtered_data[filtered_data['price'] <= filters['max_price']]
            
        if 'min_bedrooms' in filters and filters['min_bedrooms'] is not None:
            filtered_data = filtered_data[filtered_data['bedrooms'] >= filters['min_bedrooms']]
            
        if 'min_bathrooms' in filters and filters['min_bathrooms'] is not None:
            filtered_data = filtered_data[filtered_data['bathrooms'] >= filters['min_bathrooms']]
            
        if 'min_square_feet' in filters and filters['min_square_feet'] is not None:
            filtered_data = filtered_data[filtered_data['square_feet'] >= filters['min_square_feet']]
            
        if 'location' in filters and filters['location'] is not None and filters['location'] != 'All':
            filtered_data = filtered_data[filtered_data['location'] == filters['location']]
            
        if 'property_type' in filters and filters['property_type'] is not None and filters['property_type'] != 'All':
            filtered_data = filtered_data[filtered_data['property_type'] == filters['property_type']]
            
        return filtered_data
    
    @staticmethod
    def get_similar_properties(data, reference_property, n=3):
        """
        Find similar properties to a reference property.
        
        Args:
            data (pandas.DataFrame): Property data
            reference_property (dict): Reference property to compare against
            n (int): Number of similar properties to return
            
        Returns:
            pandas.DataFrame: Similar properties
        """
        # Create a copy of the data
        df = data.copy()
        
        # Define feature weights
        weights = {
            'price': 0.4,
            'square_feet': 0.3,
            'bedrooms': 0.15,
            'bathrooms': 0.15
        }
        
        # Calculate similarity score (lower is more similar)
        for feature, weight in weights.items():
            if feature in df.columns and feature in reference_property:
                ref_value = reference_property[feature]
                df[f'{feature}_diff'] = abs(df[feature] - ref_value) / df[feature].max()
                df[f'{feature}_score'] = df[f'{feature}_diff'] * weight
        
        # Sum all feature scores to get total similarity score
        score_columns = [col for col in df.columns if col.endswith('_score')]
        df['similarity_score'] = df[score_columns].sum(axis=1)
        
        # Filter out the reference property if it exists in the dataset
        if 'id' in reference_property and 'id' in df.columns:
            df = df[df['id'] != reference_property['id']]
        
        # Return the n most similar properties
        similar_properties = df.sort_values('similarity_score').head(n)
        return similar_properties.drop([col for col in similar_properties.columns if col.endswith('_diff') or col.endswith('_score')], axis=1)
