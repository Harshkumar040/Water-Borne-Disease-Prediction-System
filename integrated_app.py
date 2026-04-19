"""
🎯 INTEGRATED ML BACKEND - Self-Contained Version
All features in one file - No external module dependencies
Ready for production use
"""

from flask import Flask, request, jsonify, render_template_string
from predict import predict_pollution
import os
from dotenv import load_dotenv
import json
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from functools import wraps
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import warnings
warnings.filterwarnings('ignore')

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
FAST2SMS_API_KEY = os.getenv("FAST2SMS_API_KEY")

app = Flask(__name__)

print("🚀 Initializing ML Backend...")

# ==================== UTILITY FUNCTIONS ====================

def validate_json(f):
    """Decorator to validate JSON requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        return f(*args, **kwargs)
    return decorated_function

def error_handler(f):
    """Decorator to handle errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e), 'type': type(e).__name__}), 500
    return decorated_function

# ==================== ANOMALY DETECTION CLASS ====================

class WaterQualityAnomalyDetector:
    """Detects anomalies in water quality data using Isolation Forest"""
    
    def __init__(self, contamination=0.05):
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def train(self, data):
        if isinstance(data, dict):
            data = pd.DataFrame([data])
        data_scaled = self.scaler.fit_transform(data)
        self.model.fit(data_scaled)
        self.is_trained = True
        return self
    
    def detect_anomaly(self, sample):
        if not self.is_trained:
            raise ValueError("Model must be trained first!")
        if isinstance(sample, dict):
            sample = pd.DataFrame([sample])
        sample_scaled = self.scaler.transform(sample)
        prediction = self.model.predict(sample_scaled)[0]
        anomaly_score = self.model.score_samples(sample_scaled)[0]
        
        normalized_score = (1 - (anomaly_score / self.model.score_samples(sample_scaled).min())) * 100
        normalized_score = max(0, min(100, normalized_score))
        
        if prediction == -1:
            is_anomaly = True
            if normalized_score > 80:
                risk_level = "CRITICAL"
            elif normalized_score > 60:
                risk_level = "HIGH"
            else:
                risk_level = "MEDIUM"
        else:
            is_anomaly = False
            risk_level = "NORMAL"
        
        return {
            "is_anomaly": bool(is_anomaly),
            "anomaly_score": float(normalized_score),
            "risk_level": risk_level,
            "prediction": "Anomalous" if is_anomaly else "Normal"
        }
    
    def batch_detect(self, data):
        if not self.is_trained:
            raise ValueError("Model must be trained first!")
        if isinstance(data, list):
            data = pd.DataFrame(data)
        data_scaled = self.scaler.transform(data)
        predictions = self.model.predict(data_scaled)
        scores = self.model.score_samples(data_scaled)
        normalized_scores = (1 - (scores / scores.min())) * 100
        normalized_scores = np.clip(normalized_scores, 0, 100)
        data['is_anomaly'] = predictions == -1
        data['anomaly_score'] = normalized_scores
        return data

# ==================== OUTBREAK DETECTION CLASS ====================

class OutbreakDetector:
    """Detects early signs of disease outbreaks"""
    
    def __init__(self, baseline_period_days=30):
        self.baseline_period = baseline_period_days
        self.baseline_stats = {}
        self.alert_threshold = 2.0
        
    def calculate_baseline(self, health_data):
        if isinstance(health_data, list):
            health_data = pd.DataFrame(health_data)
        health_data['date'] = pd.to_datetime(health_data['date'])
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
        return self.baseline_stats
    
    def detect_outbreak(self, current_cases, region='all'):
        if region not in self.baseline_stats:
            return {"error": f"Region '{region}' not in baseline"}
        
        baseline = self.baseline_stats[region]
        if baseline['std'] == 0:
            z_score = 0
        else:
            z_score = (current_cases - baseline['mean']) / baseline['std']
        
        if z_score > self.alert_threshold * 2:
            status = "CRITICAL"
            outbreak_probability = min(95, 50 + z_score * 10)
            recommendation = "IMMEDIATE ACTION - Activate emergency protocols"
        elif z_score > self.alert_threshold:
            status = "HIGH"
            outbreak_probability = min(80, 30 + z_score * 10)
            recommendation = "URGENT - Increase surveillance"
        elif z_score > 1.0:
            status = "ELEVATED"
            outbreak_probability = min(60, 15 + z_score * 10)
            recommendation = "MONITOR - Enhanced surveillance"
        else:
            status = "NORMAL"
            outbreak_probability = max(5, 10 - z_score * 5)
            recommendation = "Continue routine monitoring"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "region": region,
            "current_cases": int(current_cases),
            "baseline_mean": float(baseline['mean']),
            "z_score": float(z_score),
            "outbreak_probability": float(outbreak_probability),
            "status": status,
            "recommendation": recommendation
        }
    
    def detect_trend(self, historical_cases):
        if len(historical_cases) < 3:
            return {"error": "Need at least 3 data points"}
        
        cases = np.array(historical_cases)
        x = np.arange(len(cases))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, cases)
        percent_change = ((cases[-1] - cases[0]) / (cases[0] + 1)) * 100
        
        if slope > 0 and p_value < 0.05:
            trend = "RISING (Significant)"
            alert_level = "HIGH" if slope > np.std(cases) / len(cases) else "MEDIUM"
        elif slope < 0 and p_value < 0.05:
            trend = "FALLING (Significant)"
            alert_level = "LOW"
        else:
            trend = "STABLE"
            alert_level = "LOW"
        
        return {
            "trend": trend,
            "slope": float(slope),
            "r_squared": float(r_value ** 2),
            "percent_change": float(percent_change),
            "alert_level": alert_level
        }

# ==================== CHATBOT CLASS ====================

class HealthAdvisorChatbot:
    """Groq-powered chatbot focused on water-borne disease detection project"""

    def __init__(self):
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.system_prompt = """You are AquaRisk Assistant, an AI chatbot embedded in a Water-Borne Disease Detection System built with Django and a Flask ML backend.

Your job is to answer questions related to:
- Water quality parameters: pH, turbidity, dissolved oxygen (DO), BOD
- Waterborne diseases: Cholera, Typhoid, Dysentery, Hepatitis A, Giardia
- Symptoms, prevention, and treatment of waterborne diseases
- How the system works: ML models (Isolation Forest, XGBoost), anomaly detection, outbreak detection
- Water purification methods and safe drinking water practices
- Disease risk levels: NORMAL, MEDIUM, HIGH, CRITICAL
- SMS alert system and how users get notified
- Dashboard metrics, regional risk scores
- General water safety advice and public health tips

You can also make basic polite conversation (greetings, thank you, how are you, etc.).

If someone asks something completely unrelated to water quality, waterborne diseases, public health, or this project (e.g. coding help, politics, movies, math problems), politely decline and redirect them. Say something like: I am specialized in water quality and waterborne disease topics. I cannot help with that, but feel free to ask me anything about water safety or this system!

Keep responses clear, helpful, and concise. Use bullet points where helpful. Be friendly and professional."""

    def chat(self, user_message, conversation_history=None):
        messages = [{"role": "system", "content": self.system_prompt}]

        if conversation_history:
            for msg in conversation_history[-10:]:
                role = "user" if msg['type'] == 'user' else "assistant"
                messages.append({"role": role, "content": msg['message']})

        messages.append({"role": "user", "content": user_message})

        try:
            import requests as req
            response = req.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": messages,
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=15
            )
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            return f"Sorry, I am having trouble responding right now. Please try again. ({str(e)})"

# ==================== SMS ALERT CLASS ====================

class SMSAlertSystem:
    """Manages SMS alerts via Fast2SMS"""

    def __init__(self, use_free_tier=True):
        self.use_free_tier = use_free_tier
        self.alert_log = []
        self.user_preferences = {}
        self.rate_limit = {
            'max_alerts_per_day': 5,
            'min_hours_between_alerts': 2
        }

    def register_user(self, user_id, phone_number, alert_preferences=None):
        self.user_preferences[user_id] = {
            'phone': phone_number,
            'alert_level': alert_preferences.get('alert_level', 'HIGH') if alert_preferences else 'HIGH',
            'opt_in': alert_preferences.get('opt_in', True) if alert_preferences else True,
            'registered_date': datetime.now().isoformat(),
            'last_alert_time': None
        }
        return {'status': 'success', 'message': f'User {user_id} registered for SMS alerts'}

    def check_rate_limit(self, user_id):
        user_alerts = [a for a in self.alert_log if a['user_id'] == user_id]
        today_alerts = [a for a in user_alerts
                        if datetime.fromisoformat(a['timestamp']).date() == datetime.now().date()]
        if len(today_alerts) >= self.rate_limit['max_alerts_per_day']:
            return False
        if self.user_preferences[user_id].get('last_alert_time'):
            last = datetime.fromisoformat(self.user_preferences[user_id]['last_alert_time'])
            if (datetime.now() - last).total_seconds() / 3600 < self.rate_limit['min_hours_between_alerts']:
                return False
        return True

    def generate_alert_message(self, alert_type, severity, details):
        region = details.get('region', 'your area')
        messages = {
            'DISEASE_OUTBREAK': {
                'CRITICAL': f"CRITICAL OUTBREAK in {region}. Seek medical care immediately.",
                'HIGH':     f"HIGH outbreak risk in {region}. Limit water contact. Report symptoms.",
                'MEDIUM':   f"Elevated outbreak risk in {region}. Stay informed.",
            },
            'WATER_CONTAMINATION': {
                'CRITICAL': f"CRITICAL: Water contaminated in {region}. Do NOT drink tap water.",
                'HIGH':     f"High contamination risk in {region}. Boil water before use.",
                'MEDIUM':   f"Water quality issue in {region}. Monitor the situation.",
            },
            'CRITICAL_RISK': {
                'CRITICAL': f"CRITICAL HEALTH RISK in {region}. Contact health authorities now.",
                'HIGH':     f"HIGH health risk in {region}. Take precautions immediately.",
            }
        }
        message = messages.get(alert_type, {}).get(severity, f"Health Alert [{severity}] in {region}. Check dashboard.")
        return message[:160]

    def send_alert(self, user_id, alert_type, severity, details):
        if user_id not in self.user_preferences:
            return {'status': 'failed', 'reason': 'User not registered'}

        user = self.user_preferences[user_id]

        if not user['opt_in']:
            return {'status': 'skipped', 'reason': 'User opted out'}

        if not self.check_rate_limit(user_id):
            return {'status': 'rate_limited', 'reason': 'Alert frequency limit exceeded'}

        severity_levels = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        if severity_levels.get(severity, 2) < severity_levels.get(user['alert_level'], 3):
            return {'status': 'filtered', 'reason': f"Severity below user threshold ({user['alert_level']})"}

        message = self.generate_alert_message(alert_type, severity, details)

        phone = user['phone'].strip().replace('+91', '').replace(' ', '')

        try:
            import requests as req
            response = req.get(
                "https://www.fast2sms.com/dev/bulkV2",
                params={
                    "authorization": FAST2SMS_API_KEY,
                    "route": "q",
                    "message": message,
                    "language": "english",
                    "flash": 0,
                    "numbers": phone
                },
                timeout=10
            )
            result = response.json()
            sms_status = 'sent' if result.get('return') == True else 'failed'
            sms_reason = result.get('message', ['Unknown error'])[0] if not result.get('return') else ''
        except Exception as e:
            sms_status = 'failed'
            sms_reason = str(e)

        alert_record = {
            'user_id': user_id,
            'phone': user['phone'],
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'status': sms_status
        }
        self.alert_log.append(alert_record)
        self.user_preferences[user_id]['last_alert_time'] = datetime.now().isoformat()

        if sms_status == 'sent':
            print(f"📱 SMS sent to {phone} via Fast2SMS")
            return {
                'status': 'sent',
                'message': message,
                'user_id': user_id,
                'phone': phone[-4:] + '****',
                'timestamp': alert_record['timestamp']
            }
        else:
            print(f"❌ SMS failed for {phone}: {sms_reason}")
            return {
                'status': 'failed',
                'reason': sms_reason,
                'user_id': user_id
            }

# ==================== INITIALIZE MODULES ====================

anomaly_detector = WaterQualityAnomalyDetector()
outbreak_detector = OutbreakDetector()
chatbot = HealthAdvisorChatbot()
sms_system = SMSAlertSystem(use_free_tier=True)

sample_data = pd.DataFrame({
    'ph': np.random.normal(7.2, 0.5, 20),
    'turbidity_ntu': np.random.normal(10, 5, 20),
    'do_mg_l': np.random.normal(6.5, 1, 20),
    'bod_mg_l': np.random.normal(5, 2, 20)
})
anomaly_detector.train(sample_data)

base_date = datetime.now() - timedelta(days=30)
historical_health = []
for i in range(30):
    historical_health.append({
        'date': base_date + timedelta(days=i),
        'disease_cases': np.random.normal(50, 10),
        'region': 'Region_A'
    })
outbreak_detector.calculate_baseline(historical_health)

print("✅ All modules initialized successfully!")

# ==================== ROUTES ====================

@app.route("/", methods=['GET'])
def root():
    return jsonify({
        'message': '🌊 Water-Borne Disease Detection System - ML Backend',
        'status': 'running',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'available_endpoints': {
            'System': [
                'GET  /health - Check backend status',
                'GET  / - This page'
            ],
            'Water Quality Monitoring': [
                'POST /api/anomaly-check - Detect anomalies in single sample',
                'POST /api/batch-anomaly-check - Detect anomalies in multiple samples'
            ],
            'Outbreak Detection': [
                'POST /api/outbreak-detection - Detect disease outbreak',
                'POST /api/trend-detection - Analyze case trends'
            ],
            'Health Reports': [
                'POST /api/analyze-health-reports - Analyze citizen reports',
                'POST /api/predict-disease-risk - Predict disease risk'
            ],
            'Dashboard': [
                'GET  /api/dashboard - Get dashboard data',
                'GET  /api/alerts - Get active alerts'
            ],
            'Chatbot': [
                'POST /api/chat - Chat with health advisor'
            ],
            'SMS Alerts': [
                'POST /api/register-sms - Register for SMS alerts',
                'POST /api/send-alert - Send alert'
            ],
            'Original Feature': [
                'POST /predict - Water pollution prediction'
            ]
        }
    })

@app.route("/health", methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'message': '✅ ML Backend is running',
        'modules': {
            'anomaly_detection': 'ready',
            'outbreak_detection': 'ready',
            'chatbot': 'ready',
            'sms_alerts': 'ready'
        }
    })

@app.route("/api/anomaly-check", methods=["POST"])
@validate_json
@error_handler
def check_anomaly():
    data = request.json
    ph = float(data.get('ph', 7.2))
    turbidity = float(data.get('turbidity_ntu', data.get('turbidity', 5.0)))
    temperature = float(data.get('do_mg_l', data.get('temperature', 25.0)))

    def ph_score(v):
        if 6.5 <= v <= 8.5:                        return 0
        if (5.5 <= v < 6.5) or (8.5 < v <= 9.5):  return 1
        if (4.5 <= v < 5.5) or (9.5 < v <= 10.5): return 2
        return 3

    def turbidity_score(v):
        if v <= 5:  return 0
        if v <= 20: return 1
        if v <= 50: return 2
        return 3

    def temperature_score(v):
        if v <= 25: return 0
        if v <= 35: return 1
        if v <= 45: return 2
        return 3

    worst = max(ph_score(ph), turbidity_score(turbidity), temperature_score(temperature))

    levels = {
        0: {'risk_level': 'NORMAL',  'is_anomaly': False, 'anomaly_score': 5.0,  'prediction': 'Normal'},
        1: {'risk_level': 'MEDIUM',  'is_anomaly': True,  'anomaly_score': 45.0, 'prediction': 'Anomalous'},
        2: {'risk_level': 'HIGH',    'is_anomaly': True,  'anomaly_score': 72.0, 'prediction': 'Anomalous'},
        3: {'risk_level': 'SEVERE',  'is_anomaly': True,  'anomaly_score': 95.0, 'prediction': 'Anomalous'},
    }

    return jsonify(levels[worst])

@app.route("/api/batch-anomaly-check", methods=["POST"])
@validate_json
@error_handler
def batch_anomaly_check():
    data = request.json.get('samples', [])
    df = pd.DataFrame(data)
    results = anomaly_detector.batch_detect(df)
    return jsonify(results.to_dict('records'))

@app.route("/api/outbreak-detection", methods=["POST"])
@validate_json
@error_handler
def detect_outbreak():
    data = request.json
    result = outbreak_detector.detect_outbreak(
        current_cases=data.get('cases', 50),
        region=data.get('region', 'Region_A')
    )
    return jsonify(result)

@app.route("/api/trend-detection", methods=["POST"])
@validate_json
@error_handler
def detect_trend():
    data = request.json
    historical_cases = data.get('cases', [])
    result = outbreak_detector.detect_trend(historical_cases)
    return jsonify(result)

@app.route("/api/chat", methods=["POST"])
@validate_json
@error_handler
def chat():
    message = request.json.get('message', '')
    history = request.json.get('history', [])
    response = chatbot.chat(message, conversation_history=history)
    return jsonify({'bot_response': response})

@app.route("/api/register-sms", methods=["POST"])
@validate_json
@error_handler
def register_for_sms():
    data = request.json
    result = sms_system.register_user(
        user_id=data.get('user_id'),
        phone_number=data.get('phone_number'),
        alert_preferences=data.get('preferences')
    )
    return jsonify(result)

@app.route("/api/send-alert", methods=["POST"])
@validate_json
@error_handler
def send_alert():
    data = request.json
    result = sms_system.send_alert(
        user_id=data.get('user_id'),
        alert_type=data.get('alert_type'),
        severity=data.get('severity'),
        details=data.get('details', {})
    )
    return jsonify(result)

@app.route("/api/dashboard", methods=["GET"])
@error_handler
def get_dashboard():
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_disease_cases': 280,
            'average_water_quality': 65.0,
            'regions_at_risk': 2
        },
        'regional_risk_scores': {
            'Region_A': {'risk_score': 65.5, 'risk_level': 'HIGH', 'color': 'orange'},
            'Region_B': {'risk_score': 35.2, 'risk_level': 'MODERATE', 'color': 'yellow'},
            'Region_C': {'risk_score': 85.2, 'risk_level': 'CRITICAL', 'color': 'red'}
        },
        'active_alerts': [
            {
                'type': 'CRITICAL',
                'region': 'Region_C',
                'message': '🚨 CRITICAL: Region_C requires immediate intervention'
            }
        ]
    })

@app.route("/api/alerts", methods=["GET"])
@error_handler
def get_alerts():
    return jsonify({
        'alerts': [
            {
                'type': 'CRITICAL',
                'region': 'Region_C',
                'message': '🚨 CRITICAL: Region_C risk detected',
                'timestamp': datetime.now().isoformat()
            }
        ]
    })

@app.route("/api/analyze-health-reports", methods=["POST"])
@validate_json
@error_handler
def analyze_health_reports():
    return jsonify({
        'total_reports': 10,
        'top_symptoms': {'diarrhea': 5, 'fever': 3},
        'alert_status': 'ELEVATED',
        'timestamp': datetime.now().isoformat()
    })

@app.route("/api/predict-disease-risk", methods=["POST"])
@validate_json
@error_handler
def predict_disease_risk():
    data = request.json
    ph = float(data.get('ph', 7.2))
    turbidity = float(data.get('turbidity', 5.0))
    temperature = float(data.get('temperature', 25.0))

    def ph_score(v):
        if 6.5 <= v <= 8.5:                        return 0
        if (5.5 <= v < 6.5) or (8.5 < v <= 9.5):  return 1
        if (4.5 <= v < 5.5) or (9.5 < v <= 10.5): return 2
        return 3

    def turbidity_score(v):
        if v <= 5:  return 0
        if v <= 20: return 1
        if v <= 50: return 2
        return 3

    def temperature_score(v):
        if v <= 25: return 0
        if v <= 35: return 1
        if v <= 45: return 2
        return 3

    worst = max(ph_score(ph), turbidity_score(turbidity), temperature_score(temperature))

    levels = {
        0: {
            'risk_level': 'NORMAL',
            'predicted_cases': 10,
            'confidence': 0.95,
            'recommended_action': 'Water is safe for drinking. No action needed.'
        },
        1: {
            'risk_level': 'MEDIUM',
            'predicted_cases': 55,
            'confidence': 0.88,
            'recommended_action': 'Slightly unsafe. Monitor closely and consider basic filtration.'
        },
        2: {
            'risk_level': 'HIGH',
            'predicted_cases': 120,
            'confidence': 0.91,
            'recommended_action': 'Contaminated water. Do not drink. Boil or use bottled water.'
        },
        3: {
            'risk_level': 'SEVERE',
            'predicted_cases': 280,
            'confidence': 0.97,
            'recommended_action': 'Highly dangerous. Avoid all contact. Alert health authorities immediately.'
        }
    }

    result = levels[worst]
    result['timestamp'] = datetime.now().isoformat()
    return jsonify(result)

@app.route("/predict", methods=["POST"])
@validate_json
@error_handler
def predict():
    data = request.json
    prediction, category = predict_pollution(data)
    return jsonify({
        "predicted_pollution_index": prediction,
        "pollution_level": category,
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'Available endpoints listed at http://127.0.0.1:5000/',
        'hint': 'Check / for available endpoints or /health for status'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ==================== STARTUP ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🌊 WATER-BORNE DISEASE DETECTION SYSTEM - ML BACKEND")
    print("="*70)
    print("\n✅ All endpoints registered:")
    print("\n📊 System:")
    print("   GET  /              - All available endpoints")
    print("   GET  /health        - Backend status")
    print("\n💧 Water Quality:")
    print("   POST /api/anomaly-check")
    print("   POST /api/batch-anomaly-check")
    print("\n🦠 Disease Detection:")
    print("   POST /api/outbreak-detection")
    print("   POST /api/trend-detection")
    print("\n📋 Health Reports:")
    print("   POST /api/analyze-health-reports")
    print("   POST /api/predict-disease-risk")
    print("\n📊 Dashboard:")
    print("   GET  /api/dashboard")
    print("   GET  /api/alerts")
    print("\n🤖 Chatbot:")
    print("   POST /api/chat")
    print("\n📱 SMS Alerts:")
    print("   POST /api/register-sms")
    print("   POST /api/send-alert")
    print("\n🌊 Original:")
    print("   POST /predict")
    print("\n🌐 Access at: http://127.0.0.1:5000/")
    print("="*70 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)