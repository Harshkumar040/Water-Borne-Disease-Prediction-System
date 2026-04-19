from django.urls import path
from views import home,dashboard, alerts, chatbot, disease_prediction

urlpatterns = [
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('alerts/', alerts, name='alerts'),
    path('chat/', chatbot, name='chat'),
    path('disease_form/', disease_prediction, name='disease'),
   
]