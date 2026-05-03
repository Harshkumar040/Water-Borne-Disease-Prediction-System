import requests
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from main.models import WaterData, ContactQuery, SurveyResult
from datetime import datetime

# ✅ FIX: Import the chatbot directly — no Flask server needed
from main.chatbot_health_advisor import HealthAdvisorChatbot

# ✅ FIX: Initialize once at module level (not on every request)
_chatbot_instance = None

def get_chatbot():
    """Lazy-load chatbot so it only initializes on first use"""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = HealthAdvisorChatbot()
    return _chatbot_instance


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
    past_surveys = SurveyResult.objects.filter(
        user=request.user.username
    ).order_by('-created_at')[:5]

    if request.method == 'POST':
        answers = {}
        score   = 0

        q1 = request.POST.get('q1', '')
        answers['water_appearance'] = q1
        score += {'crystal_clear': 0, 'slightly_yellow': 10, 'cloudy': 20, 'brown_dirty': 30}.get(q1, 0)

        q2 = request.POST.get('q2', '')
        answers['water_smell'] = q2
        score += {'no_smell': 0, 'chlorine': 2, 'rotten_egg': 20, 'earthy': 12, 'metallic': 18}.get(q2, 0)

        q3 = request.POST.get('q3', '')
        answers['water_source'] = q3
        score += {'bottled': 0, 'municipal': 5, 'borewell': 12, 'open_well': 18, 'river': 25}.get(q3, 0)

        q4 = request.POST.get('q4', '')
        answers['boil_water'] = q4
        score += {'always': 0, 'sometimes': 8, 'rarely': 15, 'never': 22}.get(q4, 0)

        q5 = request.POST.get('q5', '')
        answers['water_storage'] = q5
        score += {'closed_clean': 0, 'open_container': 12, 'old_container': 18, 'no_storage': 8}.get(q5, 0)

        q6 = request.POST.get('q6', '')
        answers['sanitation'] = q6
        score += {'good': 0, 'average': 8, 'poor': 18, 'very_poor': 25}.get(q6, 0)

        q7 = request.POST.get('q7', '')
        answers['recent_illness'] = q7
        score += {'none': 0, 'mild': 10, 'moderate': 18, 'severe': 28}.get(q7, 0)

        q8 = request.POST.get('q8', '')
        answers['area_type'] = q8
        score += {'urban': 2, 'semi_urban': 6, 'rural': 12, 'slum': 18}.get(q8, 0)

        q9 = request.POST.get('q9', '')
        answers['nearby_contamination'] = q9
        score += {'none': 0, 'some': 10, 'significant': 20, 'severe': 28}.get(q9, 0)

        q10 = request.POST.get('q10', '')
        answers['hand_washing'] = q10
        score += {'always': 0, 'usually': 5, 'sometimes': 12, 'rarely': 20}.get(q10, 0)

        q11 = request.POST.get('q11', '')
        answers['children_under5'] = q11
        score += {'no': 0, 'yes': 5}.get(q11, 0)

        q12 = request.POST.get('q12', '')
        answers['elderly'] = q12
        score += {'no': 0, 'yes': 5}.get(q12, 0)

        q13 = request.POST.get('q13', '')
        answers['flooding'] = q13
        score += {'no': 0, 'light': 5, 'moderate': 12, 'heavy': 20}.get(q13, 0)

        q14 = request.POST.get('q14', '')
        answers['water_treatment'] = q14
        score += {'filter_boil': 0, 'filter_only': 5, 'boil_only': 5, 'chlorine': 3, 'nothing': 20}.get(q14, 0)

        q15 = request.POST.get('q15', '')
        answers['previous_illness'] = q15
        score += {'never': 0, 'once': 8, 'twice': 14, 'multiple': 20}.get(q15, 0)

        if score <= 30:
            risk_level = 'Low Risk'
        elif score <= 70:
            risk_level = 'Moderate Risk'
        elif score <= 110:
            risk_level = 'High Risk'
        else:
            risk_level = 'Critical Risk'

        SurveyResult.objects.create(
            user=request.user.username,
            score=score,
            risk_level=risk_level,
            answers=json.dumps(answers),
        )

        past_surveys = SurveyResult.objects.filter(
            user=request.user.username
        ).order_by('-created_at')[:5]

        return render(request, 'home.html', {
            'submitted':    True,
            'score':        score,
            'risk_level':   risk_level,
            'answers':      answers,
            'past_surveys': past_surveys,
        })

    return render(request, 'home.html', {
        'submitted':    False,
        'past_surveys': past_surveys,
    })


def map_symptoms_to_disease(post):
    symptoms     = post.getlist('symptoms')
    duration     = post.get('duration', 'less_24')
    people       = post.get('people_affected', 'just_me')
    age_group    = post.get('age_group', 'adult')
    after_water  = post.get('after_water', 'unsure')
    water_source = post.get('water_source', 'municipal')
    treatment    = post.get('treatment', 'always')
    sanitation   = post.get('sanitation', 'good')
    fever_pattern = post.get('fever_pattern', 'none')

    scores = {
        'Cholera': 0, 'Typhoid': 0, 'Hepatitis A': 0,
        'Dysentery': 0, 'Gastroenteritis': 0, 'Giardia': 0,
    }

    if 'watery_diarrhea' in symptoms:
        scores['Cholera'] += 4
    if 'vomiting' in symptoms and 'watery_diarrhea' in symptoms:
        scores['Cholera'] += 2
    if 'bloody_diarrhea' in symptoms:
        scores['Dysentery'] += 5
    if 'stomach_cramps' in symptoms:
        scores['Dysentery'] += 2
    if 'diarrhea' in symptoms:
        scores['Gastroenteritis'] += 2
    if 'vomiting' in symptoms:
        scores['Gastroenteritis'] += 2
    if duration == 'less_24':
        scores['Gastroenteritis'] += 3
    if fever_pattern == 'high_constant':
        scores['Typhoid'] += 4
    if duration in ['3_7_days', 'more_week']:
        scores['Typhoid'] += 2
    if 'fatigue' in symptoms:
        scores['Typhoid'] += 1
    if 'jaundice' in symptoms:
        scores['Hepatitis A'] += 6
    if 'fatigue' in symptoms:
        scores['Hepatitis A'] += 2
    if 'bloating' in symptoms:
        scores['Giardia'] += 4
    if duration == 'more_week':
        scores['Giardia'] += 3
    if people in ['2_3_people', 'whole_household']:
        scores['Cholera'] += 2
        scores['Gastroenteritis'] += 2
    if after_water == 'yes':
        for k in scores:
            scores[k] *= 1.2
    if water_source in ['surface', 'borewell']:
        scores['Cholera'] += 1
        scores['Giardia'] += 1
        scores['Dysentery'] += 1
    if treatment == 'never':
        for k in scores:
            scores[k] *= 1.2
    if sanitation == 'poor':
        scores['Dysentery'] += 2
        scores['Typhoid'] += 1

    total = sum(scores.values()) or 1
    probabilities = {k: (v / total) for k, v in scores.items()}
    top_disease = max(probabilities, key=probabilities.get)
    confidence  = int(probabilities[top_disease] * 100)
    severity_boost = age_group in ['child', 'elderly']

    if confidence > 70 or severity_boost:
        severity = 'HIGH'
    elif confidence > 40:
        severity = 'MEDIUM'
    else:
        severity = 'LOW'

    disease_info = {
        'Cholera':         {'description': 'Acute diarrheal infection causing severe dehydration due to contaminated water.', 'go_to_hospital': 'Immediately if dehydration signs appear.', 'immediate': 'Start ORS immediately and seek urgent care.'},
        'Typhoid':         {'description': 'Bacterial infection with sustained high fever and systemic symptoms.', 'go_to_hospital': 'If fever persists beyond 3 days.', 'immediate': 'Rest, hydration, medical evaluation required.'},
        'Hepatitis A':     {'description': 'Viral liver infection indicated by jaundice and fatigue.', 'go_to_hospital': 'Yes, for liver monitoring.', 'immediate': 'Rest, avoid fatty food, stay hydrated.'},
        'Dysentery':       {'description': 'Intestinal infection with blood in stool and inflammation.', 'go_to_hospital': 'If bleeding persists or fever present.', 'immediate': 'ORS and medical consultation.'},
        'Gastroenteritis': {'description': 'Short-term infection causing vomiting and diarrhea.', 'go_to_hospital': 'If unable to retain fluids.', 'immediate': 'Rest and hydration.'},
        'Giardia':         {'description': 'Parasitic infection causing long-term digestive issues and bloating.', 'go_to_hospital': 'If symptoms persist beyond a week.', 'immediate': 'Hydration and medical treatment needed.'},
    }

    return {
        'disease':        top_disease,
        'confidence':     confidence,
        'severity':       severity,
        'probabilities':  {k: round(v * 100, 1) for k, v in probabilities.items()},
        'info':           disease_info.get(top_disease, {}),
        'severity_boost': severity_boost,
    }


@login_required
def disease_prediction(request):
    if request.method == 'POST':
        result = map_symptoms_to_disease(request.POST)
        return render(request, 'disease_result.html', {'result': result})
    return render(request, 'disease_form.html')


@login_required
def alerts(request):
    try:
        data        = requests.get('http://127.0.0.1:5000/api/alerts', timeout=5).json()
        alerts_list = data.get('alerts', [])
    except Exception:
        alerts_list = []
    return render(request, 'alerts.html', {'alerts': alerts_list})


# ── CHATBOT VIEW (fixed) ─────────────────────────────────

@login_required
def chatbot(request):
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    # Clear history on fresh page load
    if request.method == 'GET':
        request.session['chat_history'] = []

    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if message:
            # Save user message
            request.session['chat_history'].append({
                'type':      'user',
                'message':   message,
                'timestamp': datetime.now().isoformat(),
            })

            # ✅ FIX: Call local chatbot directly — no Flask needed
            try:
                bot = get_chatbot()
                result = bot.chat(message)
                bot_response = result.get('bot_response', "Sorry, I couldn't process that.")
            except Exception as e:
                bot_response = f"Sorry, something went wrong: {str(e)}"

            # Save bot response
            request.session['chat_history'].append({
                'type':      'bot',
                'message':   bot_response,
                'timestamp': datetime.now().isoformat(),
            })

            request.session.modified = True

    # Keep session from growing too large
    if len(request.session['chat_history']) > 50:
        request.session['chat_history'] = request.session['chat_history'][-50:]

    return render(request, 'chat.html', {
        'chat_history': request.session['chat_history']
    })


# ── HISTORY VIEWS ────────────────────────────────────────

@login_required
def history(request):
    records        = WaterData.objects.all().order_by('-created_at')
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
    get_object_or_404(WaterData, id=record_id).delete()
    messages.success(request, 'Record deleted.')
    return redirect('history')


@login_required
def clear_history(request):
    WaterData.objects.all().delete()
    messages.success(request, 'All history cleared.')
    return redirect('history')


@login_required
def contact(request):
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not name or not email or not subject or not message:
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'contact.html')

        ContactQuery.objects.create(
            name=name, email=email,
            subject=subject, message=message
        )
        messages.success(request, 'Your query has been submitted! We will get back to you soon. 📬')
        return redirect('contact')
    return render(request, 'contact.html')


# ── QUICK CHECK SCORING ──────────────────────────────────

RISK_ORDER = {'NORMAL': 0, 'MEDIUM': 1, 'HIGH': 2, 'SEVERE': 3}

def has_worsened(old, new):
    return RISK_ORDER.get(new, 0) > RISK_ORDER.get(old, 0)

def score_quick_check(post):
    scores = []

    appearance_map = {'clear': 0, 'slight_cloudy': 1, 'very_cloudy': 2, 'brown': 3, 'greenish': 3}
    scores.append(appearance_map.get(post.get('appearance', 'clear'), 0))

    smell_map = {'none': 0, 'earthy': 1, 'chlorine': 1, 'rotten_egg': 2, 'chemical': 3, 'sewage': 3}
    smell = post.get('smell', 'none')
    scores.append(smell_map.get(smell, 0))

    taste_map = {'normal': 0, 'salty': 1, 'metallic': 2, 'bitter': 2, 'sour': 2}
    scores.append(taste_map.get(post.get('taste', 'normal'), 0))

    deposit_map = {'none': 0, 'white_chalky': 1, 'reddish': 2, 'black': 2, 'oily': 3}
    deposits = post.get('deposits', 'none')
    scores.append(deposit_map.get(deposits, 0))

    source_map = {'municipal': 0, 'tanker': 1, 'rainwater': 1, 'borewell': 2, 'river': 3}
    scores.append(source_map.get(post.get('source', 'municipal'), 0))

    storage_map = {'sealed': 0, 'plastic_sun': 1, 'open': 2, 'old_pipes': 2}
    scores.append(storage_map.get(post.get('storage', 'sealed'), 0))

    events     = post.getlist('events')
    event_map  = {'none': 0, 'power_cut': 1, 'construction': 1, 'illness': 2, 'flooding': 3}
    scores.append(max([event_map.get(e, 0) for e in events] or [0]))

    symptoms     = post.getlist('symptoms')
    symptom_map  = {'none': 0, 'stomach': 1, 'nausea': 1, 'diarrhea': 2, 'vomiting': 2, 'multiple_sick': 3}
    scores.append(max([symptom_map.get(s, 0) for s in symptoms] or [0]))

    if smell in ['sewage', 'chemical'] or deposits == 'oily' or 'flooding' in events:
        scores.append(3)

    worst    = max(scores)
    weights  = [0.20, 0.18, 0.15, 0.12, 0.15, 0.08, 0.07, 0.05]
    weighted = sum(s * w for s, w in zip(scores[:8], weights))
    final    = (worst * 0.6) + (weighted * 0.4)

    if final >= 2.5: return 'SEVERE'
    if final >= 1.8: return 'HIGH'
    if final >= 0.9: return 'MEDIUM'
    return 'NORMAL'


def get_quick_cause(post):
    smell      = post.get('smell', 'none')
    appearance = post.get('appearance', 'clear')
    deposits   = post.get('deposits', 'none')
    source     = post.get('source', 'municipal')
    events     = post.getlist('events')
    causes     = []

    if smell == 'rotten_egg':  causes.append("rotten egg smell suggests hydrogen sulphide — likely anaerobic bacteria or corroded pipes")
    if smell == 'sewage':      causes.append("sewage odour strongly indicates fecal contamination")
    if smell == 'chemical':    causes.append("chemical smell suggests industrial or pesticide contamination")
    if appearance == 'brown':  causes.append("brown/yellow colour indicates iron, rust, or manganese contamination")
    if appearance == 'greenish': causes.append("greenish colour indicates algal bloom — possible cyanotoxin risk")
    if deposits == 'oily':     causes.append("oily film on surface indicates petroleum or chemical contamination")
    if deposits == 'reddish':  causes.append("reddish-brown deposits suggest iron or rust from corroded pipes")
    if 'flooding' in events:   causes.append("recent flooding significantly increases risk of sewage overflow")
    if source == 'borewell':   causes.append("borewell water has no treatment — higher risk of bacterial contamination")
    if source == 'river':      causes.append("river water carries high pathogen load without treatment")

    if not causes:
        return "No specific contamination indicators detected based on your observations."
    return "Based on your observations: " + "; ".join(causes) + "."


def auto_alert_if_worsened(pincode, new_risk):
    try:
        previous = WaterData.objects.filter(pincode=pincode).order_by('-created_at')[1:2]
        old_risk = previous[0].risk_level if previous else 'NORMAL'
        if has_worsened(old_risk, new_risk):
            users_resp = requests.get(f"http://127.0.0.1:5000/api/users-by-pincode/{pincode}", timeout=5)
            users = users_resp.json().get('users', [])
            for user_id in users:
                requests.post("http://127.0.0.1:5000/api/send-alert", json={
                    "user_id": user_id,
                    "alert_type": "WATER_CONTAMINATION",
                    "severity": new_risk,
                    "details": {"region": f"Pincode {pincode}", "previous_risk": old_risk, "current_risk": new_risk}
                }, timeout=5)
    except Exception as e:
        print(f"Auto-alert error: {e}")


# ── DETAILED ANALYSIS VIEW ────────────────────────────────

@login_required
def detailed_analysis(request):
    if request.method == 'POST':
        pincode = request.POST.get('pincode', '000000').strip()

        def safe_float(key):
            try:
                return float(request.POST[key]) if request.POST.get(key) else None
            except:
                return None

        ph          = safe_float('ph')
        turbidity   = safe_float('turbidity')
        temperature = safe_float('temperature')
        do_val      = safe_float('do_mg_l')
        bod         = safe_float('bod_mg_l')
        tds         = safe_float('tds')
        chlorine    = safe_float('chlorine')
        nitrate     = safe_float('nitrate')

        try:
            resp = requests.post('http://127.0.0.1:5000/api/anomaly-check', json={
                'ph': ph or 7.2, 'turbidity_ntu': turbidity or 5.0,
                'do_mg_l': do_val or temperature or 25.0, 'bod_mg_l': bod or 5.0,
            }, timeout=5)
            data          = resp.json()
            risk_level    = data.get('risk_level', 'NORMAL')
            anomaly_score = data.get('anomaly_score', 0)
            is_anomaly    = data.get('is_anomaly', False)
        except Exception:
            risk_level, anomaly_score, is_anomaly = 'NORMAL', 0, False

        analysis = []
        risk_factors = []
        safe_factors = []

        if ph is not None:
            if ph < 6.5:   analysis.append("Acidic water may corrode pipes and leach harmful metals."); risk_factors.append("acidic pH")
            elif ph > 8.5: analysis.append("Alkaline water may indicate contamination or mineral imbalance."); risk_factors.append("alkaline pH")
            else:          safe_factors.append("balanced pH")

        if turbidity is not None:
            if turbidity > 5:   analysis.append("High turbidity indicates suspended particles that can carry pathogens."); risk_factors.append("high turbidity")
            elif turbidity > 1: analysis.append("Moderate turbidity detected — filtration recommended."); risk_factors.append("moderate turbidity")
            else:               safe_factors.append("clear water")

        if temperature is not None:
            if temperature > 30: analysis.append("Elevated temperature accelerates microbial growth."); risk_factors.append("high temperature")
            else:                safe_factors.append("stable temperature")

        if tds is not None:
            if tds > 900:   analysis.append("Very high dissolved solids — unsafe for drinking."); risk_factors.append("very high TDS")
            elif tds > 600: analysis.append("High TDS may affect taste and long-term health."); risk_factors.append("high TDS")
            else:           safe_factors.append("acceptable TDS")

        if nitrate is not None:
            if nitrate > 50:   analysis.append("High nitrate levels pose serious health risks, especially for infants."); risk_factors.append("high nitrate")
            elif nitrate > 30: analysis.append("Moderate nitrate levels — caution advised."); risk_factors.append("moderate nitrate")
            else:              safe_factors.append("safe nitrate levels")

        summary = f"Water quality is classified as {risk_level}. "
        if risk_factors: summary += "Key concerns include " + ", ".join(risk_factors[:3]) + ". "
        if safe_factors: summary += "Positive indicators such as " + ", ".join(safe_factors[:2]) + " are observed. "

        if risk_level == "SEVERE":   action = "Immediate intervention required. Avoid consumption completely and use an alternative safe source. RO/UV purification is strongly recommended."
        elif risk_level == "HIGH":   action = "Water is unsafe for direct use. Boiling and filtration or RO treatment is required."
        elif risk_level == "MEDIUM": action = "Moderate contamination detected. Boiling or filtration is advised before use."
        else:                        action = "Water is within safe limits. Regular monitoring is recommended."

        param_scores = {}
        if ph is not None:
            if 6.5 <= ph <= 8.5:                         param_scores['pH'] = 0
            elif (5.5 <= ph < 6.5) or (8.5 < ph <= 9.5): param_scores['pH'] = 1
            elif (4.5 <= ph < 5.5) or (9.5 < ph <= 10.5):param_scores['pH'] = 2
            else:                                          param_scores['pH'] = 3

        if turbidity is not None:
            if turbidity <= 5:   param_scores['Turbidity'] = 0
            elif turbidity <= 20: param_scores['Turbidity'] = 1
            elif turbidity <= 50: param_scores['Turbidity'] = 2
            else:                 param_scores['Turbidity'] = 3

        if temperature is not None:
            if temperature <= 25:  param_scores['Temperature'] = 0
            elif temperature <= 35: param_scores['Temperature'] = 1
            elif temperature <= 45: param_scores['Temperature'] = 2
            else:                   param_scores['Temperature'] = 3

        if tds is not None:
            if tds <= 300:  param_scores['TDS'] = 0
            elif tds <= 600: param_scores['TDS'] = 1
            elif tds <= 900: param_scores['TDS'] = 2
            else:            param_scores['TDS'] = 3

        if nitrate is not None:
            if nitrate <= 10:  param_scores['Nitrate'] = 0
            elif nitrate <= 30: param_scores['Nitrate'] = 1
            elif nitrate <= 50: param_scores['Nitrate'] = 2
            else:               param_scores['Nitrate'] = 3

        worst_param = max(param_scores, key=param_scores.get) if param_scores else 'pH'

        WaterData.objects.create(
            check_type='detailed', ph=ph, turbidity=turbidity, temperature=temperature,
            risk_level=risk_level, quality=risk_level, pincode=pincode,
            summary=summary, disease='Detailed Analysis',
        )

        auto_alert_if_worsened(pincode, risk_level)

        return render(request, 'result.html', {
            'quality': risk_level, 'risk_level': risk_level,
            'anomaly_score': round(anomaly_score, 1), 'is_anomaly': is_anomaly,
            'worst_param': worst_param, 'param_scores': param_scores,
            'pincode': pincode, 'check_type': 'detailed',
            'ph': ph, 'turbidity': turbidity, 'temperature': temperature,
            'summary': summary, 'analysis': analysis, 'action': action,
        })

    return render(request, 'detailed_analysis.html')


# ── DASHBOARD (community water safety) ───────────────────

@login_required
def dashboard(request):
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta

    total_checks = WaterData.objects.count()
    today        = timezone.now().date()
    today_checks = WaterData.objects.filter(created_at__date=today).count()

    risk_counts = {
        'NORMAL': WaterData.objects.filter(risk_level='NORMAL').count(),
        'MEDIUM': WaterData.objects.filter(risk_level='MEDIUM').count(),
        'HIGH':   WaterData.objects.filter(risk_level='HIGH').count(),
        'SEVERE': WaterData.objects.filter(risk_level='SEVERE').count(),
    }

    trend_labels, trend_data = [], []
    for i in range(6, -1, -1):
        day   = today - timedelta(days=i)
        count = WaterData.objects.filter(created_at__date=day, risk_level__in=['HIGH', 'SEVERE']).count()
        trend_labels.append(day.strftime('%a'))
        trend_data.append(count)

    pincode_data   = list(WaterData.objects.values('pincode', 'risk_level').annotate(count=Count('id')).order_by('-count')[:10])
    quick_count    = WaterData.objects.filter(check_type='quick').count()
    detailed_count = WaterData.objects.filter(check_type='detailed').count()
    recent         = WaterData.objects.all()[:8]
    pincode_count  = WaterData.objects.values('pincode').distinct().count()

    try:
        flask_resp  = requests.get('http://127.0.0.1:5000/api/alerts', timeout=3)
        alerts_sent = len(flask_resp.json().get('alerts', []))
    except:
        alerts_sent = 0

    return render(request, 'dashboard.html', {
        'total_checks':      total_checks,
        'today_checks':      today_checks,
        'pincode_count':     pincode_count,
        'alerts_sent':       alerts_sent,
        'risk_counts':       json.dumps(risk_counts),
        'risk_counts_raw':   risk_counts,
        'trend_labels':      json.dumps(trend_labels),
        'trend_data':        json.dumps(trend_data),
        'pincode_data':      pincode_data,
        'pincode_data_json': json.dumps(pincode_data),
        'quick_count':       quick_count,
        'detailed_count':    detailed_count,
        'recent':            recent,
    })


# ── SMS API ROUTES ────────────────────────────────────────

@csrf_exempt
def register_sms(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            resp = requests.post('http://127.0.0.1:5000/api/register-sms', json=data)
            return JsonResponse(resp.json())
        except Exception as e:
            return JsonResponse({'status': 'failed', 'reason': str(e)})

@csrf_exempt
def send_sms_alert(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            resp = requests.post('http://127.0.0.1:5000/api/send-alert', json=data)
            return JsonResponse(resp.json())
        except Exception as e:
            return JsonResponse({'status': 'failed', 'reason': str(e)})