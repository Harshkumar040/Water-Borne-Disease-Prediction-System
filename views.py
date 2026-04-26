import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from main.models import WaterData
from datetime import datetime


# ── AUTH VIEWS ───────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        password1  = request.POST.get('password1', '')
        password2  = request.POST.get('password2', '')

        if not username or not password1:
            messages.error(request, 'Username and password are required.')
            return render(request, 'register.html')
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" is already taken.')
            return render(request, 'register.html')
        if email and User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'register.html')

        user = User.objects.create_user(
            username=username, email=email, password=password1,
            first_name=first_name, last_name=last_name,
        )
        login(request, user)
        messages.success(request, f'Welcome, {first_name or username}! Account created 🎉')
        return redirect('home')
    return render(request, 'register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'login.html')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}! 👋')
            return redirect(request.GET.get('next', '/'))
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')
    return render(request, 'login.html')


def logout_view(request):
    name = request.user.first_name or request.user.username if request.user.is_authenticated else ''
    logout(request)
    messages.info(request, f'Logged out. See you soon, {name}! 👋')
    return redirect('login')


# ── MAIN VIEWS ───────────────────────────────────────────

@login_required
def home(request):
    if request.method == 'POST':
        ph          = float(request.POST['ph'])
        turbidity   = float(request.POST['turbidity'])
        temperature = float(request.POST['temperature'])
        try:
            response = requests.post('http://127.0.0.1:5000/api/anomaly-check', json={
                'ph': ph, 'turbidity_ntu': turbidity,
                'do_mg_l': temperature, 'bod_mg_l': 5.0,
            })
            prediction = response.json().get('risk_level', 'No result')
        except Exception as e:
            print('ML Server Error:', e)
            prediction = 'ML Server Error ❌'

        # ✅ Save to database in real-time
        WaterData.objects.create(
            ph=ph, turbidity=turbidity, temperature=temperature,
            quality=prediction, disease='Home Prediction',
        )
        return render(request, 'result.html', {'quality': prediction})
    return render(request, 'home.html')


@login_required
def disease_prediction(request):
    if request.method == 'POST':
        ph          = float(request.POST['ph'])
        turbidity   = float(request.POST['turbidity'])
        temperature = float(request.POST['temperature'])
        try:
            response = requests.post('http://127.0.0.1:5000/api/predict-disease-risk', json={
                'ph': ph, 'turbidity': turbidity, 'temperature': temperature,
            })
            data = response.json()
            result = data
            disease_info = str(data.get('disease', 'Disease Prediction'))
            quality = str(data.get('risk_level', 'Unknown'))
        except Exception:
            result = 'Error connecting to ML API'
            disease_info = 'Error'
            quality = 'Unknown'

        # ✅ Save disease prediction to database too
        WaterData.objects.create(
            ph=ph, turbidity=turbidity, temperature=temperature,
            quality=quality, disease=disease_info,
        )
        return render(request, 'disease_result.html', {'result': result})
    return render(request, 'disease_form.html')


@login_required
def dashboard(request):
    try:
        data = requests.get('http://127.0.0.1:5000/api/dashboard').json()
    except Exception:
        data = {}
    return render(request, 'dashboard.html', {'data': data})


@login_required
def alerts(request):
    try:
        data = requests.get('http://127.0.0.1:5000/api/alerts').json()
        alerts_list = data.get('alerts', [])
    except Exception:
        alerts_list = []
    return render(request, 'alerts.html', {'alerts': alerts_list})


@login_required
def chatbot(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []
    if request.method == 'GET':
        request.session['chat_history'] = []
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if message:
            request.session['chat_history'].append({
                'type': 'user', 'message': message,
                'timestamp': datetime.now().isoformat(),
            })
            try:
                response = requests.post('http://127.0.0.1:5000/api/chat', json={
                    'message': message,
                    'history': request.session.get('chat_history', []),
                })
                bot_response = response.json().get('bot_response', "Sorry, couldn't process that.")
            except Exception:
                bot_response = "Sorry, I'm having trouble connecting to the server."
            request.session['chat_history'].append({
                'type': 'bot', 'message': bot_response,
                'timestamp': datetime.now().isoformat(),
            })
            request.session.modified = True
    if len(request.session['chat_history']) > 50:
        request.session['chat_history'] = request.session['chat_history'][-50:]
    return render(request, 'chat.html', {'chat_history': request.session['chat_history']})


@login_required
def history(request):
    records = WaterData.objects.all().order_by('-created_at')

    # ✅ Count by risk level for stats
    low_count      = sum(1 for r in records if 'low'      in r.quality.lower())
    moderate_count = sum(1 for r in records if 'moderate' in r.quality.lower())
    high_count     = sum(1 for r in records if 'high'     in r.quality.lower())
    critical_count = sum(1 for r in records if 'critical' in r.quality.lower())

    return render(request, 'history.html', {
        'records':        records,
        'low_count':      low_count,
        'moderate_count': moderate_count,
        'high_count':     high_count,
        'critical_count': critical_count,
    })


@login_required
def delete_record(request, record_id):
    record = get_object_or_404(WaterData, id=record_id)
    record.delete()
    messages.success(request, 'Record deleted.')
    return redirect('history')


@login_required
def clear_history(request):
    WaterData.objects.all().delete()
    messages.success(request, 'All history cleared.')
    return redirect('history')