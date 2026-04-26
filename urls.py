from django.urls import path
from views import (
    home, dashboard, alerts, chatbot,
    disease_prediction, history,
    register_view, login_view, logout_view,
    delete_record, clear_history,
)

urlpatterns = [
    # Auth
    path('register/', register_view, name='register'),
    path('login/',    login_view,    name='login'),
    path('logout/',   logout_view,   name='logout'),

    # Main app
    path('',                          home,               name='home'),
    path('dashboard/',                dashboard,          name='dashboard'),
    path('alerts/',                   alerts,             name='alerts'),
    path('chat/',                     chatbot,            name='chat'),
    path('disease_form/',             disease_prediction, name='disease'),
    path('history/',                  history,            name='history'),

    # History actions
    path('history/delete/<int:record_id>/', delete_record, name='delete_record'),
    path('history/clear/',                  clear_history, name='clear_history'),
]