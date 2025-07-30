import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
import os
import json
from datetime import datetime

class TrustScoreModel:
    def __init__(self, model_path=None):
        """
        Initialize the Random Forest model for trust scoring
        
        Args:
            model_path (str): Path to load a pre-trained model
        """
        self.model_path = model_path
        
        if model_path and os.path.exists(model_path):
            self.model = joblib.load(model_path)
        else:
            self.model = None
            
        # Define feature columns
        self.numeric_features = [
            'session_duration', 'request_count', 'avg_time_between_requests',
            'bytes_transferred', 'failed_login_attempts', 'time_since_last_login'
        ]
        
        self.categorical_features = [
            'user_role', 'device_type', 'connection_type', 'browser',
            'operating_system', 'time_of_day', 'day_of_week', 'location_category'
        ]
    
    def _build_pipeline(self):
        """
        Build the preprocessing and model pipeline
        
        Returns:
            Pipeline: Scikit-learn pipeline with preprocessing and model
        """
        # Preprocessing for numerical features
        numeric_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        
        # Preprocessing for categorical features
        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        # Combine preprocessing steps
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numeric_features),
                ('cat', categorical_transformer, self.categorical_features)
            ])
        
        # Create the full pipeline with the Random Forest model
        pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(random_state=42))
        ])
        
        return pipeline
    
    def train(self, X, y, param_grid=None, cv=5, save_path=None):
        """
        Train the Random Forest model with hyperparameter tuning
        
        Args:
            X (DataFrame): Training features
            y (Series): Target labels (1 for trusted, 0 for untrusted)
            param_grid (dict): Hyperparameters to search
            cv (int): Number of cross-validation folds
            save_path (str): Path to save the trained model
            
        Returns:
            self: Trained model instance
        """
        # Build the pipeline
        pipeline = self._build_pipeline()
        
        # Default parameter grid if none provided
        if param_grid is None:
            param_grid = {
                'classifier__n_estimators': [100, 200],
                'classifier__max_depth': [None, 10, 20],
                'classifier__min_samples_split': [2, 5],
                'classifier__min_samples_leaf': [1, 2]
            }
        
        # Perform grid search with cross-validation
        grid_search = GridSearchCV(
            pipeline, param_grid, cv=cv, scoring='roc_auc', n_jobs=-1, verbose=1
        )
        
        # Train the model
        grid_search.fit(X, y)
        
        # Get the best model
        self.model = grid_search.best_estimator_
        
        # Print best parameters
        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best ROC AUC score: {grid_search.best_score_:.4f}")
        
        # Save the model if a path is provided
        if save_path:
            self._save_model(save_path)
        
        return self
    
    def _save_model(self, save_path):
        """
        Save the trained model
        
        Args:
            save_path (str): Path to save the model
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save the model
        joblib.dump(self.model, save_path)
        
        # Save metadata
        metadata_path = os.path.join(os.path.dirname(save_path), 'model_metadata.json')
        metadata = {
            'model_type': 'RandomForestClassifier',
            'numeric_features': self.numeric_features,
            'categorical_features': self.categorical_features,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def predict(self, X):
        """
        Make binary predictions (trusted or untrusted)
        
        Args:
            X (DataFrame): Input features
            
        Returns:
            array: Binary predictions (1 for trusted, 0 for untrusted)
        """
        if self.model is None:
            raise ValueError("Model has not been trained or loaded yet")
        
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """
        Predict probability of being trusted
        
        Args:
            X (DataFrame): Input features
            
        Returns:
            array: Probability of being trusted (class 1)
        """
        if self.model is None:
            raise ValueError("Model has not been trained or loaded yet")
        
        # Return probability of the positive class (trusted)
        return self.model.predict_proba(X)[:, 1]
    
    def compute_trust_score(self, X):
        """
        Compute trust score (probability of being trusted)
        
        Args:
            X (DataFrame): Input features
            
        Returns:
            float or array: Trust score(s) between 0 and 1
        """
        return self.predict_proba(X)
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate the model on test data
        
        Args:
            X_test (DataFrame): Test features
            y_test (Series): Test labels
            
        Returns:
            dict: Evaluation metrics
        """
        if self.model is None:
            raise ValueError("Model has not been trained or loaded yet")
        
        # Make predictions
        y_pred = self.predict(X_test)
        y_prob = self.predict_proba(X_test)
        
        # Calculate metrics
        report = classification_report(y_test, y_pred, output_dict=True)
        cm = confusion_matrix(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        
        # Return evaluation results
        return {
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'roc_auc': auc
        }

# Example usage for generating synthetic data and training
def generate_synthetic_data(n_samples=1000):
    """
    Generate synthetic data for demonstration
    
    Args:
        n_samples (int): Number of samples to generate
        
    Returns:
        tuple: (X, y) - features and labels
    """
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Create a DataFrame with features
    data = pd.DataFrame()
    
    # Numeric features
    data['session_duration'] = np.random.exponential(scale=30, size=n_samples)  # minutes
    data['request_count'] = np.random.poisson(lam=20, size=n_samples)
    data['avg_time_between_requests'] = np.random.exponential(scale=2, size=n_samples)  # seconds
    data['bytes_transferred'] = np.random.lognormal(mean=10, sigma=1, size=n_samples)
    data['failed_login_attempts'] = np.random.poisson(lam=0.2, size=n_samples)
    data['time_since_last_login'] = np.random.exponential(scale=24, size=n_samples)  # hours
    
    # Categorical features
    data['user_role'] = np.random.choice(['admin', 'doctor', 'nurse', 'patient'], size=n_samples, p=[0.1, 0.3, 0.3, 0.3])
    data['device_type'] = np.random.choice(['desktop', 'laptop', 'tablet', 'mobile'], size=n_samples)
    data['connection_type'] = np.random.choice(['wifi', 'ethernet', 'cellular', 'vpn'], size=n_samples)
    data['browser'] = np.random.choice(['chrome', 'firefox', 'safari', 'edge', 'other'], size=n_samples)
    data['operating_system'] = np.random.choice(['windows', 'macos', 'linux', 'ios', 'android'], size=n_samples)
    data['time_of_day'] = np.random.choice(['morning', 'afternoon', 'evening', 'night'], size=n_samples)
    data['day_of_week'] = np.random.choice(['weekday', 'weekend'], size=n_samples)
    data['location_category'] = np.random.choice(['home', 'office', 'hospital', 'unknown'], size=n_samples)
    
    # Generate labels based on rules (for demonstration)
    # These rules simulate patterns that might indicate untrusted behavior
    
    # Initialize all as trusted
    labels = np.ones(n_samples)
    
    # Rule 1: High failed login attempts
    labels[data['failed_login_attempts'] > 2] = 0
    
    # Rule 2: Very short sessions with many requests
    labels[(data['session_duration'] < 5) & (data['request_count'] > 30)] = 0
    
    # Rule 3: Unusual time and location
    labels[(data['time_of_day'] == 'night') & (data['location_category'] == 'unknown')] = 0
    
    # Rule 4: Unusual device for role
    labels[(data['user_role'] == 'admin') & (data['device_type'] == 'mobile')] = 0
    
    # Add some randomness
    random_indices = np.random.choice(n_samples, size=int(n_samples * 0.05), replace=False)
    labels[random_indices] = 1 - labels[random_indices]  # Flip labels for these indices
    
    return data, labels

def main():
    """
    Main function to demonstrate the trust score model
    """
    # Generate synthetic data
    print("Generating synthetic data...")
    X, y = generate_synthetic_data(n_samples=1000)
    
    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize the model
    print("Initializing trust score model...")
    model = TrustScoreModel()
    
    # Define a smaller parameter grid for demonstration
    param_grid = {
        'classifier__n_estimators': [100],
        'classifier__max_depth': [10, None],
        'classifier__min_samples_split': [2]
    }
    
    # Train the model
    print("Training the model...")
    model.train(
        X_train, 
        y_train, 
        param_grid=param_grid,
        cv=3,  # Smaller CV for demonstration
        save_path='models/trust_score_model.joblib'
    )
    
    # Evaluate the model
    print("\nEvaluating the model...")
    evaluation = model.evaluate(X_test, y_test)
    
    print(f"\nClassification Report:")
    for class_name, metrics in evaluation['classification_report'].items():
        if class_name in ['0', '1']:
            print(f"Class {class_name}:")
            for metric_name, value in metrics.items():
                print(f"  {metric_name}: {value:.4f}")
    
    print(f"\nROC AUC Score: {evaluation['roc_auc']:.4f}")
    
    # Example of computing trust score for new data
    print("\nComputing trust scores for sample data...")
    
    # Create sample data points
    sample_trusted = X_test.iloc[0].copy()  # Start with a real example
    sample_untrusted = X_test.iloc[0].copy()  # Start with the same example but modify it
    
    # Modify the untrusted sample to have suspicious characteristics
    sample_untrusted['failed_login_attempts'] = 3
    sample_untrusted['time_of_day'] = 'night'
    sample_untrusted['location_category'] = 'unknown'
    
    # Compute trust scores
    trusted_score = model.compute_trust_score(pd.DataFrame([sample_trusted]))[0]
    untrusted_score = model.compute_trust_score(pd.DataFrame([sample_untrusted]))[0]
    
    print(f"Trust score for trusted sample: {trusted_score:.4f}")
    print(f"Trust score for untrusted sample: {untrusted_score:.4f}")

if __name__ == "__main__":
    main()