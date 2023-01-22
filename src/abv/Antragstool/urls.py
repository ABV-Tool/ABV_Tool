from django.urls import path
from .views import AppHome, ReferatListe


urlpatterns = [
    path('', AppHome, name='index'),
    path('referate', ReferatListe, name='referate'),
]
