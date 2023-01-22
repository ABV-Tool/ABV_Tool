from django.urls import path
from .views import AppHome


urlpatterns = [
    path('', AppHome, name='index'),
]
