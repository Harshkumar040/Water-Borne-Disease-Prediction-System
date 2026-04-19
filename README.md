# 🌊 Water-Borne Disease Detection System

**Advanced ML Backend for Water Quality Monitoring & Disease Outbreak Detection**

## 📋 Overview

A **comprehensive ML backend system** for detecting and predicting water-borne diseases through real-time water quality monitoring, statistical analysis, and machine learning.

### 🎯 Key Capabilities

- ✅ **Real-time Water Quality Monitoring** - Anomaly detection using Isolation Forest
- ✅ **Disease Outbreak Early Warning** - Statistical outbreak probability prediction
- ✅ **Community Health Analysis** - NLP-powered citizen health report analysis
- ✅ **Predictive Risk Assessment** - Multi-day disease risk forecasting
- ✅ **Public Health Dashboard** - Aggregated regional risk metrics
- ✅ **AI Health Chatbot** - NLP-based Q&A system (7+ topics)
- ✅ **SMS Alert System** - Free-tier notification system
- ✅ **Original Pollution Prediction** - Water pollution index calculation

### 📊 Features at a Glance

| Feature | Technology | Status |
|---------|-----------|--------|
| Anomaly Detection | Isolation Forest | ✅ Live |
| Outbreak Detection | Statistical Analysis | ✅ Live |
| Health Analysis | NLP/TF-IDF | ✅ Live |
| Risk Prediction | XGBoost | ✅ Live |
| Dashboard Backend | Flask API | ✅ Live |
| AI Chatbot | NLP | ✅ Live |
| SMS Alerts | Free-tier Integration | ✅ Live |
| Pollution Prediction | XGBoost | ✅ Live |

---

## 🚀 Quick Start (5 Minutes)

1️⃣ Install Dependencies
```bash
pip install -r requirements_full.txt

2️⃣ Start ML Backend
bash
python integrated_app.py

3️⃣ Verify It's Running
bash
curl http://127.0.0.1:5000/health

Response:
JSON
{
  "status": "healthy",
  "message": "✅ ML Backend is running",
  "modules": {
    "anomaly_detection": "ready",
    "outbreak_detection": "ready",
    "chatbot": "ready",
    "sms_alerts": "ready"
  }
}

4️⃣ Access Dashboard
Visit: http://127.0.0.1:5000/


📚 Documentation
Document	Purpose	Audience
WEBDEV_README.md	Setup & Quick Start	Everyone 👈 START HERE
API_DOCUMENTATION.md	Complete API Reference	Developers
INTEGRATION_GUIDE.md	Frontend Integration	Frontend Devs
DATABASE_SCHEMA.sql	Database Setup	Backend Devs


🔌 API Endpoints (15 Total)

System Status (2)

Code
GET  /                    List all endpoints
GET  /health              Backend health check

Water Quality Monitoring (2)

Code
POST /api/anomaly-check                Check single water sample
POST /api/batch-anomaly-check          Check multiple samples

Disease Detection (2)

Code
POST /api/outbreak-detection           Detect disease outbreak
POST /api/trend-detection              Analyze case trends

Public Health Dashboard (2)

Code
GET  /api/dashboard                    Get dashboard data
GET  /api/alerts                       Get active alerts

Health Reports (2)

Code
POST /api/analyze-health-reports       Analyze citizen reports
POST /api/predict-disease-risk         Predict disease risk

AI Chatbot (1)

Code
POST /api/chat                         Chat with health advisor

SMS Alerts (2)

Code
POST /api/register-sms                 Register for SMS alerts
POST /api/send-alert                   Send SMS alert

Original Feature (1)

Code
POST /predict                          Water pollution prediction


💻 API Usage Examples

JavaScript/React

JavaScript
// Check water quality
async function checkWaterQuality() {
  const response = await fetch('http://127.0.0.1:5000/api/anomaly-check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      ph: 7.2,
      turbidity_ntu: 5,
      do_mg_l: 6,
      bod_mg_l: 3
    })
  });
  
  const data = await response.json();
  console.log('Risk Level:', data.risk_level);
  console.log('Anomaly Score:', data.anomaly_score);
}

// Get dashboard
async function getDashboard() {
  const response = await fetch('http://127.0.0.1:5000/api/dashboard');
  const data = await response.json();
  return data;
}

// Chat with bot
async function askBot(message) {
  const response = await fetch('http://127.0.0.1:5000/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({message: message})
  });
  
  const data = await response.json();
  return data.bot_response;
}



Python

Python
import requests

# Check water quality
response = requests.post(
    'http://127.0.0.1:5000/api/anomaly-check',
    json={
        'ph': 7.2,
        'turbidity_ntu': 5,
        'do_mg_l': 6,
        'bod_mg_l': 3
    }
)

print(response.json())
# Output: {'is_anomaly': False, 'anomaly_score': 15.5, 'risk_level': 'NORMAL', ...}

# Get dashboard
dashboard = requests.get('http://127.0.0.1:5000/api/dashboard').json()

# Detect outbreak
outbreak = requests.post(
    'http://127.0.0.1:5000/api/outbreak-detection',
    json={'cases': 150, 'region': 'Region_A'}
).json()



cURL

bash
# Get dashboard
curl http://127.0.0.1:5000/api/dashboard

# Check outbreak
curl -X POST http://127.0.0.1:5000/api/outbreak-detection \
  -H "Content-Type: application/json" \
  -d '{"cases": 150, "region": "Region_A"}'

# Chat with bot
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is water pollution?"}'

# Check anomaly
curl -X POST http://127.0.0.1:5000/api/anomaly-check \
  -H "Content-Type: application/json" \
  -d '{"ph": 7.2, "turbidity_ntu": 5, "do_mg_l": 6, "bod_mg_l": 3}'



🛠️ Installation

Prerequisites

Python 3.8 or higher
pip (Python package manager)
Virtual environment (recommended)


Step 1: Clone Repository

bash
git clone https://github.com/Nitesh-2004/Water-Borne-Disease-Detection-System.git
cd Water-Borne-Disease-Detection-System

Step 2: Create Virtual Environment

bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

Step 3: Install Dependencies

bash
pip install -r requirements_full.txt

Step 4: Verify Installation

bash
python -c "import flask, pandas, xgboost; print('✅ All packages installed!')"

Step 5: Start Backend

bash
python integrated_app.py

Step 6: Test Connection

bash
curl http://127.0.0.1:5000/health



🧠 ML Models & Algorithms

1. Anomaly Detection

Algorithm: Isolation Forest (Scikit-learn)
Purpose: Detect unusual water quality readings
Output: Anomaly score (0-100), Risk level
Training: Unsupervised learning

2. Outbreak Detection

Algorithm: Z-Score based Statistical Analysis
Purpose: Detect early signs of disease outbreaks
Output: Outbreak probability, Z-score, Recommendation
Training: Baseline calculation from historical data

3. Disease Risk Prediction

Algorithm: XGBoost Regressor
Purpose: Forecast disease cases based on water quality
Output: Predicted cases, Risk level, Confidence score
Training: Supervised learning on historical data

4. Health Report Analysis

Algorithm: TF-IDF + K-Means Clustering
Purpose: Extract patterns from citizen health reports
Output: Top symptoms, Severity distribution, Alerts
Training: NLP text analysis

5. Chatbot Q&A

Algorithm: TF-IDF Vectorization + Cosine Similarity
Purpose: Answer health and water quality questions
Output: Bot response, Confidence score
Training: Pre-trained knowledge base



📊 Data Formats

Water Quality Parameters

ph (0-14) - Water pH level
turbidity_ntu (0-100+) - Water turbidity
do_mg_l (0-15) - Dissolved oxygen
bod_mg_l (0-100+) - Biochemical oxygen demand
fecal_coliform (0+) - Fecal coliform count
total_coliform (0+) - Total coliform count
tds_mg_l (0+) - Total dissolved solids
nitrate_mg_l (0-50) - Nitrate levels
fluoride_mg_l (0-10) - Fluoride levels
arsenic_ug_l (0-100) - Arsenic levels


Response Format

JSON
{
  "is_anomaly": boolean,
  "anomaly_score": float,
  "risk_level": "NORMAL|MEDIUM|HIGH|CRITICAL",
  "prediction": "Normal|Anomalous",
  "timestamp": "ISO8601 datetime"
}



🔧 Configuration

Change Port
Edit integrated_app.py (line ~330):

Python
app.run(debug=True, host='127.0.0.1', port=5001)


Enable CORS (for frontend on different port)

bash
pip install flask-cors


Then add to integrated_app.py:

Python
from flask_cors import CORS
CORS(app)


Enable Production Mode

bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 integrated_app:app



🧪 Testing

Health Check

bash
curl http://127.0.0.1:5000/health

Anomaly Detection

bash
curl -X POST http://127.0.0.1:5000/api/anomaly-check \
  -H "Content-Type: application/json" \
  -d '{"ph": 7.2, "turbidity_ntu": 5, "do_mg_l": 6, "bod_mg_l": 3}'

Outbreak Detection

bash
curl -X POST http://127.0.0.1:5000/api/outbreak-detection \
  -H "Content-Type: application/json" \
  -d '{"cases": 150, "region": "Region_A"}'

Chatbot

bash
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is water pollution?"}'

Disease Prediction

bash
curl -X POST http://127.0.0.1:5000/api/predict-disease-risk \
  -H "Content-Type: application/json" \
  -d '{"ph": 7.0, "turbidity_ntu": 12, "do_mg_l": 6, "bod_mg_l": 4}'



🚨 Troubleshooting

Problem: "Connection refused"
Solution:

bash
# Make sure backend is running
python integrated_app.py


Problem: "Module not found"
Solution:

bash
# Install all dependencies
pip install -r requirements_full.txt


Problem: "Port 5000 already in use"
Solution:

bash
# Kill process on port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Or use different port in code
# Change port=5000 to port=5001 in integrated_app.py


Problem: "CORS error in frontend"
Solution:

bash
pip install flask-cors

# Add to integrated_app.py:
from flask_cors import CORS
CORS(app)


Problem: "Model loading error"
Solution:

Verify /models/ folder exists
Check all 3 files in /models/ are present:
pollution_model.pkl
features.json
feature_means.json
Run from correct directory  
