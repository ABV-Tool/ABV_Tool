from django.urls import path
from .views import AppHome, LoginPage, LogoutPage, ReferatListe, SitzungenVonReferat, AntraegeVonSitzung


urlpatterns = [
    path('', AppHome, name='index'),
    path('referate', ReferatListe, name='referate'),
    path('sitzungen/<uuid:sitzid>/', SitzungenVonReferat, name='SitzungenVonReferat'),
    path('sitzung/<uuid:sitzid>/', AntraegeVonSitzung, name='AntraegeVonSitzung'),
    path('accounts/login/', LoginPage, name='login'),
    path('accounts/logout/', LogoutPage, name='logout')
]
