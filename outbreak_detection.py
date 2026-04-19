"""
🦠 FEATURE 1: Early Disease Warning - Outbreak Detection
- Time-series analysis for outbreak signals
- Statistical trend detection
- Early warning alerts based on health data patterns
- Free & Open Source (pandas, numpy, scipy)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
import json

class OutbreakDetector:
    """
    Detects early signs of water-borne disease outbreaks
    using statistical and time-series analysis
    """
    
    def __init__(self, baseline_period_days=30):
        """
        Initialize outbreak detector
        
        Args:
            baseline_period_days (int): Days to use for establishing baseline
        """
        self.baseline_period = baseline_period_days
        self.baseline_stats = {}
        self.alert_threshold = 2.0  # Z-score threshold
        
    def calculate_baseline(self, health_data):
        """
        Calculate baseline statistics from historical health data
        
        Args:
            health_data (list/DataFrame): Historical health records
            {date, disease_cases, water_quality_score, region}
            
        Returns:
            dict: Baseline statistics
        """
        if isinstance(health_data, list):
            health_data = pd.DataFrame(health_data)
        
        health_data['date'] = pd.to_datetime(health_data['date'])
        
        # Group by region if available
        regions = health_data['region'].unique() if 'region' in health_data.columns else ['all']
        
        for region in regions:
            if region != 'all':
                region_data = health_data[health_data['region'] == region]
            else:
                region_data = health_data
            
            cases = region_data['disease_cases'].values
            
            self.baseline_stats[region] = {
                'mean': np.mean(cases),
                'std': np.std(cases),
                'median': np.median(cases),
                'percentile_75': np.percentile(cases, 75),
                'percentile_95': np.percentile(cases, 95)
            }
        
        print(f"✅ Baseline calculated for {len(self.baseline_stats)} region(s)")
        return self.baseline_stats
    
    def detect_outbreak(self, current_cases, region='all'):
        """
        Detect potential outbreak in current data
        
        Args:
            current_cases (int/float): Current number of disease cases
            region (str): Geographic region
            
        Returns:
            dict: Outbreak detection results
        """
        if region not in self.baseline_stats:
            return {"error": f"Region '{region}' not in baseline. Please calculate baseline first."}
        
        baseline = self.baseline_stats[region]
        
        # Calculate Z-score
        if baseline['std'] == 0:
            z_score = 0
        else:
            z_score = (current_cases - baseline['mean']) / baseline['std']
        
        # Determine outbreak probability
        if z_score > self.alert_threshold * 2:
            status = "CRITICAL"
            outbreak_probability = min(95, 50 + z_score * 10)
            recommendation = "IMMEDIATE PUBLIC HEALTH ALERT - Activate emergency protocols"
        elif z_score > self.alert_threshold:
            status = "HIGH"
            outbreak_probability = min(80, 30 + z_score * 10)
            recommendation = "URGENT - Increase surveillance and prepare response"
        elif z_score > 1.0:
            status = "ELEVATED"
            outbreak_probability = min(60, 15 + z_score * 10)
            recommendation = "MONITOR - Enhanced surveillance recommended"
        else:
            status = "NORMAL"
            outbreak_probability = max(5, 10 - z_score * 5)
            recommendation = "Continue routine monitoring"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "region": region,
            "current_cases": int(current_cases),
            "baseline_mean": float(baseline['mean']),
            "baseline_std": float(baseline['std']),
            "z_score": float(z_score),
            "outbreak_probability": float(outbreak_probability),
            "status": status,
            "recommendation": recommendation
        }
    
    def detect_trend(self, historical_cases):
        """
        Detect rising/falling trend in disease cases
        
        Args:
            historical_cases (list): List of case counts over time
            
        Returns:
            dict: Trend analysis results
        """
        if len(historical_cases) < 3:
            return {"error": "Need at least 3 data points for trend analysis"}
        
        cases = np.array(historical_cases)
        x = np.arange(len(cases))
        
        # Linear regression to detect trend
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, cases)
        
        # Calculate percent change
        percent_change = ((cases[-1] - cases[0]) / (cases[0] + 1)) * 100
        
        if slope > 0 and p_value < 0.05:
            trend = "RISING (Statistically Significant)"
            alert_level = "HIGH" if slope > np.std(cases) / len(cases) else "MEDIUM"
        elif slope < 0 and p_value < 0.05:
            trend = "FALLING (Statistically Significant)"
            alert_level = "LOW"
        else:
            trend = "STABLE"
            alert_level = "LOW"
        
        return {
            "trend": trend,
            "slope": float(slope),
            "r_squared": float(r_value ** 2),
            "percent_change": float(percent_change),
            "p_value": float(p_value),
            "alert_level": alert_level,
            "interpretation": f"Cases changing by {slope:.2f} per day ({percent_change:.1f}% total change)"
        }


# Example usage
if __name__ == "__main__":
    # Sample historical health data
    base_date = datetime.now() - timedelta(days=30)
    historical_health = []
    
    for i in range(30):
        historical_health.append({
            'date': base_date + timedelta(days=i),
            'disease_cases': np.random.normal(50, 10),
            'water_quality_score': np.random.uniform(60, 90),
            'region': 'Region_A'
        })
    
    # Initialize and calculate baseline
    detector = OutbreakDetector(baseline_period_days=30)
    detector.calculate_baseline(historical_health)
    
    # Test outbreak detection
    print("\n🦠 Normal Case Load:")
    print(json.dumps(detector.detect_outbreak(52, 'Region_A'), indent=2))
    
    print("\n⚠️ Elevated Case Load:")
    print(json.dumps(detector.detect_outbreak(95, 'Region_A'), indent=2))
    
    print("\n🚨 Critical Case Load:")
    print(json.dumps(detector.detect_outbreak(150, 'Region_A'), indent=2))
    
    # Test trend detection
    print("\n📈 Trend Analysis:")
    recent_cases = [45, 50, 55, 65, 80, 100, 120]
    print(json.dumps(detector.detect_trend(recent_cases), indent=2))