from django.urls import path
from . import views

urlpatterns = [
    path('', views.recommender, name='recommender'),
    path('speech/', views.speech_to_text, name='speech_to_text'),
    #path('predict/', views.predict_view, name='predict'),
]
