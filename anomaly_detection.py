"""
🔍 FEATURE 1 & 2: Water Quality Monitoring - Anomaly Detection
- Uses Isolation Forest for unsupervised anomaly detection
- Detects unusual water quality sensor readings
- Provides anomaly scores and risk alerts
- Free & Open Source (sklearn, pandas, numpy)
"""

import joblib
import pandas as pd
import numpy as np
import json
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class WaterQualityAnomalyDetector:
    """
    Detects anomalies in water quality data using Isolation Forest
    """
    
    def __init__(self, contamination=0.05):
        """
        Initialize the anomaly detector
        
        Args:
            contamination (float): Expected proportion of anomalies (5% by default)
        """
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def train(self, data):
        """
        Train the anomaly detection model on historical water quality data
        
        Args:
            data (DataFrame): Historical water quality measurements
        """
        if isinstance(data, dict):
            data = pd.DataFrame([data])
        
        # Scale the data
        data_scaled = self.scaler.fit_transform(data)
        
        # Train Isolation Forest
        self.model.fit(data_scaled)
        self.is_trained = True
        print("✅ Anomaly detector trained successfully!")
        return self
    
    def detect_anomaly(self, sample):
        """
        Detect if a water quality sample is anomalous
        
        Args:
            sample (dict/DataFrame): Water quality readings
            
        Returns:
            dict: {is_anomaly, anomaly_score, risk_level}
        """
        if not self.is_trained:
            raise ValueError("❌ Model must be trained first!")
        
        if isinstance(sample, dict):
            sample = pd.DataFrame([sample])
        
        # Scale the sample
        sample_scaled = self.scaler.transform(sample)
        
        # Get anomaly score (-1 = anomaly, 1 = normal)
        prediction = self.model.predict(sample_scaled)[0]
        anomaly_score = self.model.score_samples(sample_scaled)[0]
        
        # Normalize anomaly score to 0-100 range (0=normal, 100=severe anomaly)
        normalized_score = (1 - (anomaly_score / self.model.score_samples(sample_scaled).min())) * 100
        normalized_score = max(0, min(100, normalized_score))
        
        # Determine risk level
        if prediction == -1:  # Anomaly detected
            is_anomaly = True
            if normalized_score > 80:
                risk_level = "CRITICAL - Immediate Action Required"
            elif normalized_score > 60:
                risk_level = "HIGH - Urgent Investigation Needed"
            else:
                risk_level = "MEDIUM - Monitor Closely"
        else:
            is_anomaly = False
            risk_level = "NORMAL - Within Expected Range"
        
        return {
            "is_anomaly": bool(is_anomaly),
            "anomaly_score": float(normalized_score),
            "risk_level": risk_level,
            "prediction": "Anomalous" if is_anomaly else "Normal"
        }
    
    def batch_detect(self, data):
        """
        Detect anomalies in multiple samples
        
        Args:
            data (DataFrame): Multiple water quality measurements
            
        Returns:
            DataFrame: Original data with anomaly flags and scores
        """
        if not self.is_trained:
            raise ValueError("❌ Model must be trained first!")
        
        if isinstance(data, list):
            data = pd.DataFrame(data)
        
        # Scale the data
        data_scaled = self.scaler.transform(data)
        
        # Get predictions and scores
        predictions = self.model.predict(data_scaled)
        scores = self.model.score_samples(data_scaled)
        
        # Normalize scores
        normalized_scores = (1 - (scores / scores.min())) * 100
        normalized_scores = np.clip(normalized_scores, 0, 100)
        
        # Add to dataframe
        data['is_anomaly'] = predictions == -1
        data['anomaly_score'] = normalized_scores
        data['risk_level'] = data['is_anomaly'].apply(
            lambda x: "Anomalous" if x else "Normal"
        )
        
        return data
    
    def save_model(self, filepath):
        """Save the trained model"""
        joblib.dump({'model': self.model, 'scaler': self.scaler}, filepath)
        print(f"✅ Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load a previously trained model"""
        loaded = joblib.load(filepath)
        self.model = loaded['model']
        self.scaler = loaded['scaler']
        self.is_trained = True
        print(f"✅ Model loaded from {filepath}")
        return self


# Example usage
if __name__ == "__main__":
    # Sample historical water quality data
    historical_data = pd.DataFrame({
        'ph': [7.2, 7.3, 7.1, 7.4, 7.0, 8.5],  # 8.5 is unusual
        'turbidity_ntu': [5, 6, 4, 5, 6, 25],  # 25 is unusual
        'do_mg_l': [6, 6.5, 6.2, 6.3, 6.1, 2],  # 2 is unusual
        'bod_mg_l': [3, 3.5, 3.2, 3.1, 3.3, 15],  # 15 is unusual
    })
    
    # Initialize and train detector
    detector = WaterQualityAnomalyDetector(contamination=0.1)
    detector.train(historical_data)
    
    # Test with normal sample
    normal_sample = {'ph': 7.2, 'turbidity_ntu': 5, 'do_mg_l': 6, 'bod_mg_l': 3}
    print("\n🔍 Testing Normal Sample:")
    print(detector.detect_anomaly(normal_sample))
    
    # Test with anomalous sample
    anomalous_sample = {'ph': 9.0, 'turbidity_ntu': 50, 'do_mg_l': 1, 'bod_mg_l': 20}
    print("\n⚠️ Testing Anomalous Sample:")
    print(detector.detect_anomaly(anomalous_sample))
    
    # Batch detection
    print("\n📊 Batch Detection:")
    results = detector.batch_detect(historical_data)
    print(results)