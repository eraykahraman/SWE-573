from django.urls import path
from . import views
from .views import home, create_post, fetch_tags

urlpatterns = [
    path('', home, name='home'),
    path('create/', create_post, name='create_post'),
    path('fetch-tags/', fetch_tags, name='fetch_tags'),
    
    
]