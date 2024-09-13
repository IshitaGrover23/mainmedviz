from django.urls import path
from . import views

urlpatterns = [
    path('', views.heart_view, name='heart'),
]
