from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Main view for the app
    path('result/<int:xray_id>/', views.result, name='result'),  # Result view
    path('pneumo/', views.index, name='pneumo'),  # Add this line
]