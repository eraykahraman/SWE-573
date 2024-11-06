from django.urls import path
from .views import house

urlpatterns = [
    path('', house, name='house'),  # Changed from 'home' to 'house'
]