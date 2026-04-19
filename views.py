import requests
from django.shortcuts import render
from main.models import WaterData
from datetime import datetime

def home(request):
    if request.method == "POST":
        ph = float(request.POST['ph'])
        turbidity = float(request.POST['turbidity'])
        temperature = float(request.POST['temperature'])

        try:
            url = "http://127.0.0.1:5000/api/anomaly-check"

            payload = {
                "ph": ph,
                "turbidity_ntu": turbidity,
                "do_mg_l": temperature,
                "bod_mg_l": 5.0
            }

            response = requests.post(url, json=payload)
            data = response.json()

            print("RESPONSE:", data)

            prediction = data.get("risk_level", "No result")

        except Exception as e:
            print("ERROR:", e)
            prediction = "ML Server Error ❌"

        WaterData.objects.create(
            ph=ph,
            turbidity=turbidity,
            temperature=temperature,
            quality=prediction,
            disease="From ML"
        )

        return render(request, "result.html", {
            "quality": prediction
        })

    return render(request, "home.html")

def disease_prediction(request):
    if request.method == "POST":
        try:
            url = "http://127.0.0.1:5000/api/predict-disease-risk"

            payload = {
                "ph": float(request.POST['ph']),
                "turbidity": float(request.POST['turbidity']),
                "temperature": float(request.POST['temperature'])
            }

            response = requests.post(url, json=payload)
            data = response.json()

            return render(request, "disease_result.html", {
                "result": data
            })

        except Exception as e:
            return render(request, "disease_result.html", {
                "result": "Error connecting to ML API"
            })

    return render(request, "disease_form.html")

def dashboard(request):
    url = "http://127.0.0.1:5000/api/dashboard"

    response = requests.get(url)
    data = response.json()

    print("DASHBOARD DATA:", data)

    return render(request, "dashboard.html", {"data": data})

def alerts(request):
    url = "http://127.0.0.1:5000/api/alerts"

    response = requests.get(url)
    data = response.json()

    # FIX: API returns {"alerts": [...]} — extract the list
    alerts_list = data.get("alerts", [])

    return render(request, "alerts.html", {"alerts": alerts_list})

def chatbot(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    # Start a fresh conversation when opening the page via GET
    if request.method == "GET":
        request.session['chat_history'] = []

    if request.method == "POST":
        message = request.POST['message'].strip()
        if message:
            # Add user message to history
            request.session['chat_history'].append({
                'type': 'user',
                'message': message,
                'timestamp': datetime.now().isoformat()
            })
            
            try:
                url = "http://127.0.0.1:5000/api/chat"
                response = requests.post(url, json={
                    "message": message,
                    "history": request.session.get('chat_history', [])
                })
                data = response.json()
                bot_response = data.get("bot_response", "Sorry, I couldn't process your request.")
                
                # Add bot response to history
                request.session['chat_history'].append({
                    'type': 'bot',
                    'message': bot_response,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception:
                bot_response = "Sorry, I'm having trouble connecting to the server."
                request.session['chat_history'].append({
                    'type': 'bot',
                    'message': bot_response,
                    'timestamp': datetime.now().isoformat()
                })
            
            request.session.modified = True
    
    # Keep only last 50 messages to prevent session bloat
    if len(request.session['chat_history']) > 50:
        request.session['chat_history'] = request.session['chat_history'][-50:]
    
    return render(request, "chat.html", {
        'chat_history': request.session['chat_history']
    })