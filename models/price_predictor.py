import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, cross_val_score
import joblib
import os

class PricePredictor:
    def __init__(self):
        """Initialize the price predictor model and prepare it for training/prediction."""
        self.model = None
        self.preprocessor = None
        self.features = None
        self.model_trained = False
        
    def preprocess_data(self, data):
        """
        Preprocess the data by handling categorical and numerical features.
        
        Args:
            data (pandas.DataFrame): The data to preprocess
            
        Returns:
            preprocessor: The fitted column transformer
        """
        categorical_features = [col for col in data.columns if data[col].dtype == 'object']
        numerical_features = [col for col in data.columns if data[col].dtype != 'object' and col != 'price']
        
        # Define preprocessing for numerical and categorical data
        numerical_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numerical_transformer, numerical_features),
                ('cat', categorical_transformer, categorical_features)
            ])
        
        return preprocessor, numerical_features, categorical_features
    
    def train(self, X, y):
        """
        Train the price prediction model.
        
        Args:
            X (pandas.DataFrame): Features
            y (pandas.Series): Target property prices
            
        Returns:
            self: The trained model instance
        """
        # Store feature names for future reference
        self.features = X.columns.tolist()
        
        # Preprocess the data
        self.preprocessor, numerical_features, categorical_features = self.preprocess_data(X)
        
        # Create the pipeline with preprocessing and model
        self.model = Pipeline(steps=[
            ('preprocessor', self.preprocessor),
            ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
        ])
        
        # Train the model
        self.model.fit(X, y)
        self.model_trained = True
        
        return self
    
    def predict(self, features):
        """
        Make price predictions for given property features.
        
        Args:
            features (dict or pandas.DataFrame): Property features
            
        Returns:
            dict: Prediction results including price and confidence interval
        """
        if not self.model_trained:
            raise ValueError("Model not trained. Please train the model first.")
        
        # Convert features to DataFrame if it's a dictionary
        if isinstance(features, dict):
            features_df = pd.DataFrame([features])
        else:
            features_df = features
            
        # Make sure all required features are present
        for feature in self.features:
            if feature not in features_df.columns:
                features_df[feature] = 0  # Default value
        
        # Make prediction
        predicted_price = self.model.predict(features_df)[0]
        
        # Estimate confidence interval (simplified approach)
        # In a real application, you'd use a more sophisticated method
        confidence = 0.10  # 10% of predicted price
        lower_bound = predicted_price * (1 - confidence)
        upper_bound = predicted_price * (1 + confidence)
        
        return {
            "predicted_price": predicted_price,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "confidence_score": 1 - confidence  # Higher is better
        }
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance on test data.
        
        Args:
            X_test (pandas.DataFrame): Test features
            y_test (pandas.Series): Test target values
            
        Returns:
            dict: Evaluation metrics
        """
        if not self.model_trained:
            raise ValueError("Model not trained. Please train the model first.")
        
        # Make predictions
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics
        mse = np.mean((y_test - y_pred) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(y_test - y_pred))
        r2 = 1 - (np.sum((y_test - y_pred) ** 2) / np.sum((y_test - np.mean(y_test)) ** 2))
        
        return {
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
            "r2": r2
        }
    
    def save_model(self, filepath="model.joblib"):
        """Save the trained model to a file."""
        if not self.model_trained:
            raise ValueError("Model not trained. Please train the model first.")
        
        joblib.dump(self.model, filepath)
        
    def load_model(self, filepath="model.joblib"):
        """Load a trained model from a file."""
        if os.path.exists(filepath):
            self.model = joblib.load(filepath)
            self.model_trained = True
        else:
            raise FileNotFoundError(f"Model file {filepath} not found.")

# Quick demo model that can be used for testing
def get_demo_model():
    """
    Create a simple demo model without requiring real training data.
    This is for demonstration purposes only and returns a dummy model.
    
    Returns:
        PricePredictor: A pre-configured predictor model
    """
    # Create a simple model that approximates housing prices based on common factors
    # This is NOT a properly trained model, just for UI demonstration
    predictor = PricePredictor()
    
    # Mock the model with a simple lambda function
    class MockModel:
        def predict(self, X):
            # Get the features we need from X
            try:
                square_feet = X['square_feet'].values[0] if 'square_feet' in X else X[0]
                bedrooms = X['bedrooms'].values[0] if 'bedrooms' in X else X[1]
                bathrooms = X['bathrooms'].values[0] if 'bathrooms' in X else X[2]
                
                # Simple formula: base price + (sq ft * price per sq ft) + bedroom value + bathroom value
                base_price = 150000
                price_per_sqft = 200
                bedroom_value = 25000
                bathroom_value = 15000
                
                # Add some randomness to make it look more realistic
                randomness = np.random.normal(0, 10000)
                
                price = base_price + (square_feet * price_per_sqft) + (bedrooms * bedroom_value) + (bathrooms * bathroom_value) + randomness
                return np.array([max(price, 50000)])  # Ensure the price is at least 50k
            except:
                # Fallback calculation if there's an issue
                return np.array([250000 + np.random.normal(0, 25000)])
    
    predictor.model = MockModel()
    predictor.model_trained = True
    predictor.features = ['square_feet', 'bedrooms', 'bathrooms', 'location', 'property_type', 'year_built']
    
    return predictor
