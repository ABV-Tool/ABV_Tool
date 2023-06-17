from django.contrib.auth.decorators import user_passes_test, login_required
from django.urls import path, re_path, include
from .views import  LoginPage, LogoutPage
from .views import HomePage, ArchivPage
from .views import ReferatsverwaltungPage, ReferatErstellenPage, ReferatBearbeitenPage, ReferatLoeschenPage
from .views import SitzungsverwaltungPage, SitzungAnlegenPage, SitzungVerwaltenPage, SitzungVertagenPage, SitzungLoeschenPage
from .views import AntragsverwaltungPage, AntragAnzeigenPage, AntragBearbeitenPage, AntragLoeschenPage, AntragBeschliessenPage, AntragVertagenPage
from .views import AntragAllgemein, AntragFinanziell, AntragVeranstaltung, AntragMitglied, AntragAmt, AntragBenehmen

#TODO: Internen Bereich nur für superuser freigeben

def is_admin(user):
    return user.is_authenticated and user.is_superuser

urlpatterns = [
    # Hauptseiten
    path('', HomePage, name='index'),
    path('archiv/', ArchivPage, name='archiv'),
    
    # Interner Bereich
    path('intern/referatsverwaltung/', login_required(user_passes_test(is_admin)(ReferatsverwaltungPage)), name='referatsverwaltung'),
    path('intern/referat/erstellen', login_required(user_passes_test(is_admin)(ReferatErstellenPage)), name='referat-erstellen'),
    path('intern/referat/<int:refID>/bearbeiten', login_required(user_passes_test(is_admin)(ReferatBearbeitenPage)), name='referat-bearbeiten'),
    path('intern/referat/<int:refID>/loeschen', login_required(user_passes_test(is_admin)(ReferatLoeschenPage)), name='referat-loeschen'),
    
    path('intern/sitzungsverwaltung/', login_required(user_passes_test(is_admin)(SitzungsverwaltungPage)), name='sitzungsverwaltung'),
    path('intern/sitzung/anlegen', login_required(user_passes_test(is_admin)(SitzungAnlegenPage)), name='sitzung-anlegen'),
    path('intern/sitzung/<uuid:sitzID>/anzeigen', login_required(user_passes_test(is_admin)(SitzungVerwaltenPage)), name='sitzung-verwalten'),
    path('intern/sitzung/<uuid:sitzID>/vertagen', login_required(user_passes_test(is_admin)(SitzungVertagenPage)), name='sitzung-vertagen'),
    path('intern/sitzung/<uuid:sitzID>/loeschen', login_required(user_passes_test(is_admin)(SitzungLoeschenPage)), name='sitzung-loeschen'),
    
    path('intern/antragsverwaltung/', login_required(user_passes_test(is_admin)(AntragsverwaltungPage)), name='antragsverwaltung'),
    path('intern/antrag/<uuid:antragID>/anzeigen', login_required(user_passes_test(is_admin)(AntragAnzeigenPage)), name='antrag-anzeigen'),
    path('intern/antrag/<uuid:antragID>/bearbeiten', login_required(user_passes_test(is_admin)(AntragBearbeitenPage)), name='antrag-bearbeiten'),
    path('intern/antrag/<uuid:antragID>/loeschen', login_required(user_passes_test(is_admin)(AntragLoeschenPage)), name='antrag-loeschen'),
    path('intern/antrag/<uuid:antragID>/beschliessen', login_required(user_passes_test(is_admin)(AntragBeschliessenPage)), name='antrag-beschliessen'),
    path('intern/antrag/<uuid:antragID>/vertagen', login_required(user_passes_test(is_admin)(AntragVertagenPage)), name='antrag-vertagen'),
    
    # Benutzerverwaltung
    path('accounts/login/', LoginPage, name='login'),
    path('accounts/logout/', LogoutPage, name='logout'),
    
    # Antragsverwaltung
    path('antrag/allgemein/', AntragAllgemein, name='antrag-allgemein'),
    path('antrag/finanziell/', AntragFinanziell, name='antrag-finanziell'),
    path('antrag/veranstaltung/', AntragVeranstaltung, name='antrag-veranstaltung'),
    path('antrag/mitglied/', AntragMitglied, name='antrag-mitglied'),
    path('antrag/amt/', AntragAmt, name='antrag-amt'),
    path('antrag/benehmen/', AntragBenehmen, name='antrag-benehmen')
]
