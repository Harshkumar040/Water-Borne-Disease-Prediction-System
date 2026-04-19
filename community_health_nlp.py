"""
👥 FEATURE 3: Community Health Reporting - NLP Analysis
- Extract insights from citizen health reports using NLP
- Cluster similar health complaints
- Identify unusual symptom patterns
- Free & Open Source (spaCy, scikit-learn, pandas)
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
import json
import re
from collections import Counter

class CommunityHealthAnalyzer:
    """
    Analyzes citizen health reports to identify patterns
    """
    
    def __init__(self):
        self.symptom_keywords = {
            'diarrhea': ['diarrhea', 'loose motions', 'loose stool', 'bm', 'loose stools'],
            'cholera': ['cholera', 'rice water stool', 'severe diarrhea'],
            'typhoid': ['typhoid', 'fever', 'headache', 'body pain'],
            'dysentery': ['dysentery', 'bloody stool', 'blood in stool', 'red stool'],
            'hepatitis': ['hepatitis', 'jaundice', 'yellow', 'liver'],
            'skin_infection': ['skin', 'rash', 'infection', 'itching'],
            'respiratory': ['cough', 'cold', 'fever', 'respiratory']
        }
        self.vectorizer = None
        self.reports_data = None
    
    def extract_symptoms(self, report_text):
        """
        Extract disease symptoms from citizen report
        
        Args:
            report_text (str): Free text health report
            
        Returns:
            dict: Extracted symptoms and severity
        """
        text = report_text.lower()
        detected_symptoms = []
        
        for disease, keywords in self.symptom_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    detected_symptoms.append(disease)
                    break
        
        # Estimate severity based on keywords
        severity_keywords = {
            'critical': ['severe', 'critical', 'urgent', 'emergency', 'hospitalized'],
            'high': ['serious', 'very', 'extreme'],
            'medium': ['moderate', 'significant'],
            'low': ['mild', 'slight']
        }
        
        severity = 'unknown'
        for sev_level, keywords in severity_keywords.items():
            if any(keyword in text for keyword in keywords):
                severity = sev_level
                break
        
        return {
            'symptoms': list(set(detected_symptoms)),
            'severity': severity,
            'symptom_count': len(set(detected_symptoms))
        }
    
    def analyze_reports(self, reports):
        """
        Analyze batch of health reports
        
        Args:
            reports (list): List of citizen health reports
                           [{date, location, report_text, user_id}, ...]
            
        Returns:
            dict: Analysis results
        """
        if isinstance(reports, list):
            self.reports_data = pd.DataFrame(reports)
        else:
            self.reports_data = reports
        
        # Extract symptoms
        symptoms_extracted = []
        for report in self.reports_data['report_text']:
            symptoms_extracted.append(self.extract_symptoms(report))
        
        self.reports_data['extracted_symptoms'] = [s['symptoms'] for s in symptoms_extracted]
        self.reports_data['severity'] = [s['severity'] for s in symptoms_extracted]
        
        # Count symptom frequencies
        all_symptoms = []
        for symptoms in self.reports_data['extracted_symptoms']:
            all_symptoms.extend(symptoms)
        
        symptom_counts = Counter(all_symptoms)
        
        return {
            'total_reports': len(self.reports_data),
            'reports_with_symptoms': (self.reports_data['extracted_symptoms'].apply(len) > 0).sum(),
            'top_symptoms': dict(symptom_counts.most_common(5)),
            'severity_distribution': self.reports_data['severity'].value_counts().to_dict(),
            'affected_locations': self.reports_data['location'].value_counts().head(5).to_dict() if 'location' in self.reports_data.columns else {},
            'data': self.reports_data.to_dict('records')
        }
    
    def cluster_reports(self, num_clusters=3):
        """
        Cluster similar health reports using TF-IDF + KMeans
        
        Args:
            num_clusters (int): Number of clusters to form
            
        Returns:
            dict: Clustering results
        """
        if self.reports_data is None:
            return {"error": "No reports analyzed yet. Call analyze_reports first."}
        
        # Vectorize reports
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        tfidf_matrix = self.vectorizer.fit_transform(self.reports_data['report_text'])
        
        # Cluster
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        self.reports_data['cluster'] = kmeans.fit_predict(tfidf_matrix)
        
        # Analyze each cluster
        clusters_info = {}
        for cluster_id in range(num_clusters):
            cluster_reports = self.reports_data[self.reports_data['cluster'] == cluster_id]
            
            # Most common symptoms in this cluster
            cluster_symptoms = []
            for symptoms in cluster_reports['extracted_symptoms']:
                cluster_symptoms.extend(symptoms)
            
            clusters_info[f"cluster_{cluster_id}"] = {
                'report_count': len(cluster_reports),
                'top_symptoms': dict(Counter(cluster_symptoms).most_common(3)),
                'severity_levels': cluster_reports['severity'].value_counts().to_dict(),
                'sample_reports': cluster_reports['report_text'].head(2).tolist()
            }
        
        return {
            'clustering_results': clusters_info,
            'total_clusters': num_clusters
        }
    
    def get_alert_summary(self):
        """
        Generate alert summary for public health authorities
        
        Returns:
            dict: Alert summary
        """
        if self.reports_data is None:
            return {"error": "No reports analyzed yet."}
        
        critical_reports = self.reports_data[self.reports_data['severity'] == 'critical']
        high_reports = self.reports_data[self.reports_data['severity'] == 'high']
        
        return {
            'alert_date': pd.Timestamp.now().isoformat(),
            'critical_cases': len(critical_reports),
            'high_severity_cases': len(high_reports),
            'total_reports': len(self.reports_data),
            'most_common_symptoms': dict(Counter([s for syms in self.reports_data['extracted_symptoms'] for s in syms]).most_common(5)),
            'affected_areas': self.reports_data['location'].value_counts().head(3).to_dict() if 'location' in self.reports_data.columns else {},
            'alert_status': 'CRITICAL' if len(critical_reports) > 0 else 'HIGH' if len(high_reports) > 3 else 'NORMAL',
            'recommendation': self._generate_recommendation(critical_reports, high_reports)
        }
    
    def _generate_recommendation(self, critical, high):
        """Generate recommendation based on case counts"""
        critical_count = len(critical)
        high_count = len(high)
        
        if critical_count > 0:
            return "🚨 IMMEDIATE ACTION: Activate emergency health response protocols"
        elif high_count > 5:
            return "⚠️ URGENT: Increase surveillance and prepare health resources"
        elif high_count > 0:
            return "📢 ALERT: Monitor situation closely and prepare contingency plans"
        else:
            return "✅ Continue routine health monitoring"


# Example usage
if __name__ == "__main__":
    # Sample citizen health reports
    reports = [
        {
            'date': '2024-01-15',
            'location': 'Ward_A',
            'user_id': 'user_001',
            'report_text': 'My family has severe diarrhea and loose motions for 2 days. Very concerned.'
        },
        {
            'date': '2024-01-15',
            'location': 'Ward_A',
            'user_id': 'user_002',
            'report_text': 'Child has loose stool and fever. Water quality seems poor lately.'
        },
        {
            'date': '2024-01-15',
            'location': 'Ward_B',
            'user_id': 'user_003',
            'report_text': 'Mild skin rash after bathing in community water source.'
        },
        {
            'date': '2024-01-15',
            'location': 'Ward_B',
            'user_id': 'user_004',
            'report_text': 'Normal, feeling healthy today.'
        }
    ]
    
    # Initialize and analyze
    analyzer = CommunityHealthAnalyzer()
    print("\n📊 Analysis Results:")
    results = analyzer.analyze_reports(reports)
    print(json.dumps(results, indent=2, default=str))
    
    print("\n🔗 Clustering Results:")
    clusters = analyzer.cluster_reports(num_clusters=2)
    print(json.dumps(clusters, indent=2, default=str))
    
    print("\n🚨 Alert Summary:")
    alerts = analyzer.get_alert_summary()
    print(json.dumps(alerts, indent=2, default=str))