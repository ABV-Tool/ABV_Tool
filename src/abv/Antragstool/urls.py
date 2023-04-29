from django.urls import path
from .views import AppHome, LoginPage, LogoutPage, ReferatListe, SitzungenVonReferat, AntraegeVonSitzung
from .views import AntragAllgemein, AntragFinanziell, AntragMitglied, AntragAmt, AntragBenehmen


urlpatterns = [
    path('', AppHome, name='index'),
    
    path('referate', ReferatListe, name='referate'),
    path('sitzungen/<uuid:sitzid>/', SitzungenVonReferat, name='SitzungenVonReferat'),
    path('sitzung/<uuid:sitzid>/', AntraegeVonSitzung, name='AntraegeVonSitzung'),
    
    path('accounts/login/', LoginPage, name='login'),
    path('accounts/logout/', LogoutPage, name='logout'),
    
    path('antrag/allgemein/', AntragAllgemein, name='antrag-allgemein'),
    path('antrag/finanziell/', AntragFinanziell, name='antrag-finanziell'),
    path('antrag/mitglied/', AntragMitglied, name='antrag-mitglied'),
    path('antrag/amt/', AntragAmt, name='antrag-amt'),
    path('antrag/benehmen/', AntragBenehmen, name='antrag-benehmen'),
]
