from django.urls import path
from django.views.generic import RedirectView
from django.contrib import admin
from views import (
    home, dashboard, alerts, chatbot,
    disease_prediction, history,
    register_view, login_view, logout_view,
    delete_record, clear_history,
    contact, detailed_analysis,
    register_sms, send_sms_alert,
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('register/', register_view, name='register'),
    path('login/',    login_view,    name='login'),
    path('logout/',   logout_view,   name='logout'),

    # Main app
    path('',                                home,               name='home'),
    path('detailed-analysis/',              detailed_analysis,  name='detailed_analysis'),
    path('survey/',                         dashboard,          name='dashboard'),
    path('dashboard/',                      RedirectView.as_view(url='/survey/', permanent=True)),
    path('alerts/',                         alerts,             name='alerts'),
    path('chat/',                           chatbot,            name='chat'),
    path('disease_form/',                   disease_prediction, name='disease'),
    path('history/',                        history,            name='history'),
    path('contact/',                        contact,            name='contact'),

    # History actions
    path('history/delete/<int:record_id>/', delete_record,      name='delete_record'),
    path('history/clear/',                  clear_history,      name='clear_history'),

    # SMS API
    path('api/register-sms/',              register_sms,       name='register_sms'),
    path('api/send-alert/',                send_sms_alert,     name='send_sms_alert'),
]