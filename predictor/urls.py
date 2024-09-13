from django.urls import path
from . import views

urlpatterns = [
    path('braintumor/', views.braintumor, name='braintumor'),
    
]
