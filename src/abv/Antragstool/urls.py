from django.contrib.auth.decorators import user_passes_test
from django.urls import path, re_path, include
from .views import  LoginPage, LogoutPage
from .views import HomePage, AboutPage, ArchivPage
from .views import ReferatsverwaltungPage, ReferatErstellenPage, ReferatBearbeitenPage, ReferatLoeschenPage
from .views import SitzungsverwaltungPage, SitzungAnlegenPage, SitzungAnzeigenPage, SitzungVertagenPage, SitzungLoeschenPage
from .views import AntragAllgemein, AntragFinanziell, AntragVeranstaltung, AntragMitglied, AntragAmt, AntragBenehmen

#TODO: Internen Bereich nur für superuser freigeben

urlpatterns = [
    # Hauptseiten
    path('', HomePage, name='index'),
    path('about/', AboutPage, name='about'),
    path('archiv/', ArchivPage, name='archiv'),
    
    # Interner Bereich
    path('intern/referatsverwaltung/', ReferatsverwaltungPage, name='referatsverwaltung'),
    path('intern/referat/erstellen', ReferatErstellenPage, name='referat-erstellen'),
    path('intern/referat/<int:refID>/bearbeiten', ReferatBearbeitenPage, name='referat-bearbeiten'),
    path('intern/referat/<int:refID>/loeschen', ReferatLoeschenPage, name='referat-loeschen'),
    
    path('intern/sitzungsverwaltung/', SitzungsverwaltungPage, name='sitzungsverwaltung'),
    path('intern/sitzung/anlegen', SitzungAnlegenPage, name='sitzung-anlegen'),
    path('intern/sitzung/<uuid:sitzID>/anzeigen', SitzungAnzeigenPage, name='sitzung-anzeigen'),
    path('intern/sitzung/<uuid:sitzID>/vertragen', SitzungVertagenPage, name='sitzung-vertagen'),
    path('intern/sitzung/<uuid:sitzID>/loeschen', SitzungLoeschenPage, name='sitzung-loeschen'),
    
    # Benutzerverwaltung
    path('accounts/login/', LoginPage, name='login'),
    path('accounts/logout/', LogoutPage, name='logout'),
    
    # Antragsverwaltung
    path('antrag/allgemein/', AntragAllgemein, name='antrag-allgemein'),
    path('antrag/finanziell/', AntragFinanziell, name='antrag-finanziell'),
    path('antrag/veranstaltung/', AntragVeranstaltung, name='antrag-veranstaltung'),
    path('antrag/mitglied/', AntragMitglied, name='antrag-mitglied'),
    path('antrag/amt/', AntragAmt, name='antrag-amt'),
    path('antrag/benehmen/', AntragBenehmen, name='antrag-benehmen'),

    path('martor/', include('martor.urls')),
]
