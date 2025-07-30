import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import pandas as pd
import joblib
import os
import json
from datetime import datetime

class AutoencoderModel:
    def __init__(self, input_dim=10, encoding_dim=5, model_path=None):
        """
        Initialize the Autoencoder model for anomaly detection
        
        Args:
            input_dim (int): Dimension of input features
            encoding_dim (int): Dimension of the encoded representation
            model_path (str): Path to load a pre-trained model
        """
        self.input_dim = input_dim
        self.encoding_dim = encoding_dim
        self.model_path = model_path
        self.scaler = MinMaxScaler()
        self.threshold = None
        
        if model_path and os.path.exists(model_path):
            self.model = load_model(model_path)
            # Load scaler and threshold if available
            scaler_path = os.path.join(os.path.dirname(model_path), 'scaler.pkl')
            threshold_path = os.path.join(os.path.dirname(model_path), 'threshold.json')
            
            if os.path.exists(scaler_path):
                self.scaler = joblib.load(scaler_path)
            
            if os.path.exists(threshold_path):
                with open(threshold_path, 'r') as f:
                    self.threshold = json.load(f)['threshold']
        else:
            self.model = self._build_model()
    
    def _build_model(self):
        """
        Build the autoencoder architecture
        
        Returns:
            Model: Compiled Keras autoencoder model
        """
        # Input layer
        input_layer = Input(shape=(self.input_dim,))
        
        # Encoder
        encoded = Dense(8, activation='relu')(input_layer)
        encoded = Dropout(0.2)(encoded)
        encoded = Dense(self.encoding_dim, activation='relu')(encoded)
        
        # Decoder
        decoded = Dense(8, activation='relu')(encoded)
        decoded = Dropout(0.2)(decoded)
        decoded = Dense(self.input_dim, activation='sigmoid')(decoded)
        
        # Autoencoder model
        autoencoder = Model(input_layer, decoded)
        
        # Compile the model
        autoencoder.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mean_squared_error'
        )
        
        return autoencoder
    
    def preprocess_data(self, X):
        """
        Preprocess the input data
        
        Args:
            X (array-like): Input features
            
        Returns:
            array: Scaled features
        """
        # Convert to numpy array if it's a DataFrame
        if isinstance(X, pd.DataFrame):
            X = X.values
        
        # Fit the scaler if it hasn't been fit yet
        if not hasattr(self.scaler, 'data_min_'):
            return self.scaler.fit_transform(X)
        
        return self.scaler.transform(X)
    
    def train(self, X, epochs=50, batch_size=32, validation_split=0.2, save_path=None):
        """
        Train the autoencoder model
        
        Args:
            X (array-like): Training data
            epochs (int): Number of training epochs
            batch_size (int): Batch size for training
            validation_split (float): Fraction of data to use for validation
            save_path (str): Path to save the trained model
            
        Returns:
            history: Training history
        """
        # Preprocess the data
        X_scaled = self.preprocess_data(X)
        
        # Split into train and validation sets
        X_train, X_val = train_test_split(X_scaled, test_size=validation_split, random_state=42)
        
        # Train the model
        history = self.model.fit(
            X_train, X_train,  # Autoencoder tries to reconstruct the input
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, X_val),
            verbose=1
        )
        
        # Calculate reconstruction error on validation set
        val_predictions = self.model.predict(X_val)
        val_mse = np.mean(np.power(X_val - val_predictions, 2), axis=1)
        
        # Set threshold as mean + 2*std of validation reconstruction error
        self.threshold = float(np.mean(val_mse) + 2 * np.std(val_mse))
        
        # Save the model if a path is provided
        if save_path:
            self._save_model(save_path)
        
        return history
    
    def _save_model(self, save_path):
        """
        Save the model, scaler, and threshold
        
        Args:
            save_path (str): Path to save the model
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Save the model
        self.model.save(save_path)
        
        # Save the scaler
        scaler_path = os.path.join(os.path.dirname(save_path), 'scaler.pkl')
        joblib.dump(self.scaler, scaler_path)
        
        # Save the threshold
        threshold_path = os.path.join(os.path.dirname(save_path), 'threshold.json')
        with open(threshold_path, 'w') as f:
            json.dump({'threshold': self.threshold, 'timestamp': datetime.now().isoformat()}, f)
    
    def predict(self, X):
        """
        Make predictions and return reconstruction error
        
        Args:
            X (array-like): Input features
            
        Returns:
            tuple: (reconstruction_error, is_anomaly)
        """
        # Preprocess the data
        X_scaled = self.preprocess_data(X)
        
        # Make predictions
        predictions = self.model.predict(X_scaled)
        
        # Calculate reconstruction error (MSE)
        reconstruction_error = np.mean(np.power(X_scaled - predictions, 2), axis=1)
        
        # Determine if it's an anomaly
        is_anomaly = reconstruction_error > self.threshold if self.threshold else None
        
        return reconstruction_error, is_anomaly
    
    def get_threshold(self):
        """
        Get the current anomaly threshold
        
        Returns:
            float: Anomaly threshold
        """
        return self.threshold
    
    def set_threshold(self, threshold):
        """
        Set a custom anomaly threshold
        
        Args:
            threshold (float): New threshold value
        """
        self.threshold = threshold

# Example usage for generating synthetic data and training
def generate_synthetic_data(n_samples=1000, n_features=10):
    """
    Generate synthetic data for demonstration
    
    Args:
        n_samples (int): Number of samples to generate
        n_features (int): Number of features
        
    Returns:
        DataFrame: Synthetic data
    """
    # Generate normal behavior data
    normal_data = np.random.normal(0.5, 0.1, size=(int(n_samples * 0.9), n_features))
    
    # Generate anomalous behavior data
    anomalous_data = np.random.normal(0.2, 0.3, size=(int(n_samples * 0.1), n_features))
    
    # Combine the data
    data = np.vstack([normal_data, anomalous_data])
    
    # Create feature names
    feature_names = [f'feature_{i}' for i in range(n_features)]
    
    # Create a DataFrame
    df = pd.DataFrame(data, columns=feature_names)
    
    # Add labels for evaluation (not used in training)
    labels = np.zeros(n_samples)
    labels[int(n_samples * 0.9):] = 1  # Anomalies are labeled as 1
    df['is_anomaly'] = labels
    
    return df

def main():
    """
    Main function to demonstrate the autoencoder model
    """
    # Generate synthetic data
    print("Generating synthetic data...")
    data = generate_synthetic_data(n_samples=1000, n_features=10)
    
    # Split features and labels
    X = data.drop('is_anomaly', axis=1)
    y_true = data['is_anomaly']
    
    # Initialize the model
    print("Initializing autoencoder model...")
    model = AutoencoderModel(input_dim=X.shape[1], encoding_dim=5)
    
    # Train the model
    print("Training the model...")
    history = model.train(
        X, 
        epochs=20, 
        batch_size=32, 
        save_path='models/autoencoder_model.h5'
    )
    
    # Make predictions
    print("Making predictions...")
    reconstruction_error, is_anomaly = model.predict(X)
    
    # Evaluate the model
    from sklearn.metrics import classification_report, confusion_matrix
    
    print("\nModel Evaluation:")
    print(classification_report(y_true, is_anomaly))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_true, is_anomaly))
    
    print(f"\nAnomaly Threshold: {model.get_threshold():.6f}")
    
    # Example of detecting an anomaly in new data
    print("\nTesting with new data...")
    new_normal = np.random.normal(0.5, 0.1, size=(1, X.shape[1]))
    new_anomaly = np.random.normal(0.2, 0.3, size=(1, X.shape[1]))
    
    error_normal, is_anomaly_normal = model.predict(new_normal)
    error_anomaly, is_anomaly_anomaly = model.predict(new_anomaly)
    
    print(f"Normal sample - Reconstruction Error: {error_normal[0]:.6f}, Is Anomaly: {is_anomaly_normal[0]}")
    print(f"Anomaly sample - Reconstruction Error: {error_anomaly[0]:.6f}, Is Anomaly: {is_anomaly_anomaly[0]}")

if __name__ == "__main__":
    main()