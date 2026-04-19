"""
📊 FEATURE 5: Public Health Dashboard Backend
- Generates real-time risk scores and metrics
- Prepares API endpoints for dashboard frontend
- Aggregates all ML model outputs
- Free & Open Source (Flask, pandas, numpy)
"""

from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class HealthDashboardBackend:
    """
    Central backend for generating dashboard data
    """
    
    def __init__(self):
        self.risk_cache = {}
        self.last_update = None
        
    def calculate_regional_risk_score(self, regions_data):
        """
        Calculate composite risk score for each region
        
        Args:
            regions_data (list): Regional health/water data
            
        Returns:
            dict: Risk scores by region
        """
        risk_scores = {}
        
        for region in regions_data:
            scores = []
            
            # Water quality component (0-100)
            if 'water_quality' in region:
                scores.append(min(100, (1 - region['water_quality']/100) * 100))
            
            # Disease cases component (0-100)
            if 'disease_cases' in region and 'baseline_cases' in region:
                case_ratio = region['disease_cases'] / (region['baseline_cases'] + 1)
                scores.append(min(100, case_ratio * 50))
            
            # Population vulnerability (0-100)
            if 'sanitation_coverage' in region:
                scores.append((100 - region['sanitation_coverage']))
            
            # Calculate weighted average
            if scores:
                risk_score = np.mean(scores)
            else:
                risk_score = 50
            
            # Determine risk level
            if risk_score > 75:
                risk_level = "CRITICAL"
                color = "red"
            elif risk_score > 50:
                risk_level = "HIGH"
                color = "orange"
            elif risk_score > 25:
                risk_level = "MODERATE"
                color = "yellow"
            else:
                risk_level = "LOW"
                color = "green"
            
            risk_scores[region['name']] = {
                'risk_score': float(risk_score),
                'risk_level': risk_level,
                'color': color,
                'components': {
                    'water_quality': region.get('water_quality', 'N/A'),
                    'disease_cases': int(region.get('disease_cases', 0)),
                    'sanitation_coverage': region.get('sanitation_coverage', 'N/A')
                }
            }
        
        return risk_scores
    
    def get_trend_data(self, historical_data, days=30):
        """
        Generate trend data for dashboard graphs
        
        Args:
            historical_data (DataFrame): Time-series data
            days (int): Number of days to include
            
        Returns:
            dict: Trend data formatted for charts
        """
        historical_data = pd.DataFrame(historical_data)
        historical_data['date'] = pd.to_datetime(historical_data['date'])
        
        recent = historical_data[historical_data['date'] >= datetime.now() - timedelta(days=days)]
        recent = recent.sort_values('date')
        
        return {
            'dates': recent['date'].astype(str).tolist(),
            'disease_cases': recent['disease_cases'].tolist() if 'disease_cases' in recent.columns else [],
            'water_quality_score': recent['water_quality_score'].tolist() if 'water_quality_score' in recent.columns else [],
            'sanitation_coverage': recent['sanitation_coverage'].tolist() if 'sanitation_coverage' in recent.columns else []
        }
    
    def get_alerts(self, risk_scores, thresholds={'critical': 75, 'high': 50}):
        """
        Generate active alerts for dashboard
        
        Args:
            risk_scores (dict): Regional risk scores
            thresholds (dict): Alert thresholds
            
        Returns:
            list: List of active alerts
        """
        alerts = []
        
        for region, data in risk_scores.items():
            score = data['risk_score']
            
            if score > thresholds['critical']:
                alerts.append({
                    'id': f"alert_{region}_critical_{datetime.now().timestamp()}",
                    'type': 'CRITICAL',
                    'region': region,
                    'message': f"🚨 CRITICAL: {region} requires immediate health intervention",
                    'severity': 3,
                    'timestamp': datetime.now().isoformat()
                })
            elif score > thresholds['high']:
                alerts.append({
                    'id': f"alert_{region}_high_{datetime.now().timestamp()}",
                    'type': 'HIGH',
                    'region': region,
                    'message': f"⚠️ HIGH: {region} shows elevated disease risk",
                    'severity': 2,
                    'timestamp': datetime.now().isoformat()
                })
        
        return sorted(alerts, key=lambda x: x['severity'], reverse=True)
    
    def get_summary_statistics(self, all_regions_data):
        """
        Calculate summary stats for dashboard header
        
        Args:
            all_regions_data (list): All regional data
            
        Returns:
            dict: Summary statistics
        """
        total_cases = sum(r.get('disease_cases', 0) for r in all_regions_data)
        avg_water_quality = np.mean([r.get('water_quality', 50) for r in all_regions_data])
        critical_regions = sum(1 for r in all_regions_data if r.get('disease_cases', 0) > 100)
        
        return {
            'total_disease_cases': int(total_cases),
            'average_water_quality': float(avg_water_quality),
            'regions_at_risk': critical_regions,
            'last_updated': datetime.now().isoformat(),
            'data_freshness': 'Real-time'
        }
    
    def generate_full_dashboard_json(self, regions_data, historical_data):
        """
        Generate complete dashboard JSON data
        
        Args:
            regions_data (list): Current regional data
            historical_data (DataFrame): Historical trend data
            
        Returns:
            dict: Complete dashboard data
        """
        risk_scores = self.calculate_regional_risk_score(regions_data)
        alerts = self.get_alerts(risk_scores)
        trends = self.get_trend_data(historical_data)
        summary = self.get_summary_statistics(regions_data)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'regional_risk_scores': risk_scores,
            'active_alerts': alerts,
            'trend_data': trends,
            'map_data': {
                'regions': [
                    {
                        'name': region,
                        'risk_level': data['risk_level'],
                        'risk_score': data['risk_score'],
                        'color': data['color']
                    }
                    for region, data in risk_scores.items()
                ]
            }
        }


# Flask API Setup
def create_dashboard_api():
    """Create Flask API for dashboard"""
    app = Flask(__name__)
    backend = HealthDashboardBackend()
    
    @app.route('/api/dashboard', methods=['GET'])
    def get_dashboard():
        """Get complete dashboard data"""
        # In production, fetch from database
        sample_regions = [
            {'name': 'Region_A', 'disease_cases': 85, 'baseline_cases': 50, 'water_quality': 65, 'sanitation_coverage': 70},
            {'name': 'Region_B', 'disease_cases': 45, 'baseline_cases': 50, 'water_quality': 80, 'sanitation_coverage': 85},
            {'name': 'Region_C', 'disease_cases': 150, 'baseline_cases': 50, 'water_quality': 40, 'sanitation_coverage': 50}
        ]
        
        sample_history = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=30),
            'disease_cases': np.random.normal(70, 20, 30),
            'water_quality_score': np.random.normal(70, 10, 30),
            'sanitation_coverage': np.random.normal(75, 5, 30)
        })
        
        dashboard_data = backend.generate_full_dashboard_json(sample_regions, sample_history)
        return jsonify(dashboard_data)
    
    @app.route('/api/alerts', methods=['GET'])
    def get_alerts():
        """Get current alerts"""
        # In production, fetch from database
        sample_regions = [
            {'name': 'Region_A', 'disease_cases': 85, 'baseline_cases': 50, 'water_quality': 65, 'sanitation_coverage': 70},
            {'name': 'Region_C', 'disease_cases': 150, 'baseline_cases': 50, 'water_quality': 40, 'sanitation_coverage': 50}
        ]
        
        risk_scores = backend.calculate_regional_risk_score(sample_regions)
        alerts = backend.get_alerts(risk_scores)
        
        return jsonify({'alerts': alerts})
    
    @app.route('/api/regions/<region_name>', methods=['GET'])
    def get_region_detail(region_name):
        """Get detailed data for specific region"""
        return jsonify({'region': region_name, 'data': 'Details here'})
    
    return app


# Example usage
if __name__ == "__main__":
    backend = HealthDashboardBackend()
    
    # Sample data
    regions = [
        {'name': 'Region_A', 'disease_cases': 85, 'baseline_cases': 50, 'water_quality': 65, 'sanitation_coverage': 70},
        {'name': 'Region_B', 'disease_cases': 45, 'baseline_cases': 50, 'water_quality': 80, 'sanitation_coverage': 85},
        {'name': 'Region_C', 'disease_cases': 150, 'baseline_cases': 50, 'water_quality': 40, 'sanitation_coverage': 50}
    ]
    
    history = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=30),
        'disease_cases': np.random.normal(70, 20, 30),
        'water_quality_score': np.random.normal(70, 10, 30),
        'sanitation_coverage': np.random.normal(75, 5, 30)
    })
    
    print("\n📊 Dashboard Data:")
    dashboard = backend.generate_full_dashboard_json(regions, history)
    print(json.dumps(dashboard, indent=2, default=str))