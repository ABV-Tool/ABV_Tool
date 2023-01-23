from django.urls import path
from .views import AppHome, ReferatListe, SitzungenVonReferat, AntraegeVonSitzung


urlpatterns = [
    path('', AppHome, name='index'),
    path('referate', ReferatListe, name='referate'),
    path('sitzungen/<uuid:sitzid>/', SitzungenVonReferat, name='SitzungenVonReferat'),
    path('sitzung/<uuid:sitzid>/', AntraegeVonSitzung, name='AntraegeVonSitzung'),
]
