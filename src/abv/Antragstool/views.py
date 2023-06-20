from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.db.models import Q, Max
from django.conf import settings
from django.template.loader import render_to_string

from datetime import date, datetime, timedelta

from .models import Referat, Sitzung, Antrag, Antragssteller, Antragstyp, Beschluss, Anlage
from .forms import ReferatForm, BeschlussForm, SitzungVertagenForm, AntragVertagenForm, SitzungAnlegenForm
from .forms import LoginForm, AntragAllgemeinForm, AntragFinanziellForm, AntragVeranstaltungForm, AntragMitgliedForm, AntragAmtForm, AntragBenehmenForm

from .api import list_pads, create_pad, set_html


def formFehlerAusgeben(request, form):
    for field_name, errors in form.errors.items():
        field = form.fields[field_name]
        error_messages = [f"{field.label} {error}" for error in errors]
        messages.warning(request, "\n".join(error_messages))


# ========== Hauptseiten ========== #

def HomePage(request):
    return render(request, 'pages/home.html', context={'title': 'Home'})


def ArchivPage(request):
    archivierte_antraege =  Antrag.objects.filter(beschlussID__isnull=False).filter(~Q(beschlussID__beschlussErgebnis="Vertagt"))
    
    return render(request, 'pages/archiv.html', context={
        'title': 'Archiv',
        'antraege': archivierte_antraege,
        'aktion': 'ANZEIGEN'
    })

# ========== Interner Bereich ========== #

# ++++++ Referatsverwaltung ++++++ #

def ReferatsverwaltungPage(request):
    referate = Referat.objects.all().order_by('refID')
    context = {'title': 'Referatsverwaltung', 'referate': referate}
    return render(request, 'pages/intern/referatsverwaltung.html', context=context)


def ReferatErstellenPage(request):
    if request.method == 'POST':  
        form = ReferatForm(request.POST)
        if form.is_valid():
            referat_id = Referat.objects.latest('refID').refID + 1
            referat_name = form.cleaned_data['referat_name']
            referat_email = form.cleaned_data['referat_email']
            
            try:
                referat = Referat.objects.get(refName=referat_name, refEmail=referat_email)
                messages.error(request, 'Das Referat ' + referat.refName + ' existiert bereits!')
            except Referat.DoesNotExist:
                referat = Referat(refID=referat_id, refName=referat_name, refEmail=referat_email)
                referat.save()
                messages.success(request, 'Das Referat ' + referat.refName + ' erfolgreich erstellt!')
                return redirect('referat-erstellen')
            
        else:
            messages.error(request, 'Fehler beim Erstellen des Referats! Bitte aktualisiere die Seite und versuche es erneut.')
            return redirect('referat-erstellen')
    else:
        form = ReferatForm()
        
    return render(request, 'pages/intern/referat.html', context={
        'title': 'Referat erstellen', 
        'aktion':'ERSTELLEN',
        'form': form
    })


def ReferatBearbeitenPage(request, refID):
    referat = Referat.objects.get(refID=refID)
    
    if request.method == 'POST':
        form = ReferatForm(request.POST)
        if form.is_valid():
            referat.refName = form.cleaned_data['referat_name']
            referat.refEmail = form.cleaned_data['referat_email']
            referat.save()
            
            messages.success(request, 'Das Referat ' + referat.refName + ' wurde erfolgreich bearbeitet!')
            return redirect('referat-bearbeiten', refID=refID)
        else:
            messages.error(request, 'Fehler beim Bearbeiten des Referats! Bitte aktualisieren die Seite und versuche es erneut.')
            return redirect('referat-bearbeiten', refID=refID)
    else:
        form = ReferatForm()
    
    return render(request, 'pages/intern/referat.html', context={
        'title': 'Referat bearbeiten', 
        'aktion':'BEARBEITEN', 
        'referat': referat,
        'form': form
    })


def ReferatLoeschenPage(request, refID):
    referat = Referat.objects.get(refID=refID)

    if request.method == 'POST':
        referat.delete()
        messages.success(request, 'Das Referat ' + referat.refName + ' wurde erfolgreich gelöscht!')
        return redirect('referatsverwaltung')
    else:
        form = ReferatForm()

    return render(request, 'pages/intern/referat.html', context={
        'title': 'Referat löschen', 
        'aktion':'LOESCHEN', 
        'referat': referat,
        'form': form
    })

# ------ Referatsverwaltung ------ #


# ++++++ Sitzungsverwaltung ++++++ #

def SitzungsverwaltungPage(request):
    # Anzahl der Anträge pro Sitzung berechnen | Filtere Anträge, die vertagt wurden
    for sitzung in Sitzung.objects.all():
        anz_antraege = Antrag.objects.filter(sitzID=sitzung.sitzID).filter(~Q(beschlussID__beschlussErgebnis="Vertagt")).count()
        sitzung.anzAntraege = anz_antraege
        sitzung.save()
    # Sitzungen nach Datum sortieren
    sitzungen = Sitzung.objects.all().order_by('sitzDate')
        
    return render(request, 'pages/intern/sitzungsverwaltung.html', context={
        'title': 'Sitzungsverwaltung', 
        'sitzungen': sitzungen
    })


def SitzungAnlegenPage(request):
    referate = Referat.objects.all().order_by('refID')
    date = datetime.now().date() + timedelta(days=7)
    
    if request.method == 'POST':
        form = SitzungAnlegenForm(request.POST)
        if form.is_valid():
            sitzung = Sitzung()
            sitzung.sitzDate = form.cleaned_data['datum_sitzung']
            sitzung.refID = form.cleaned_data['referat']
            sitzung.save()

            messages.success(request, 'Die Sitzung wurde wurde für den ' + sitzung.sitzDate.strftime("%d.%m.%Y") + ' angelegt!')
            return redirect('sitzung-anlegen')
        else:
            messages.error(request, 'Die Sitzung konnte nicht angelegt werden. Bitte beachte die nachfolgenden Fehler.')
            formFehlerAusgeben(request, form)
            return redirect('sitzung-anlegen')
    else:
        form = SitzungAnlegenForm()
        
    return render(request, 'pages/intern/sitzung/anlegen.html', context={
        'title': 'Sitzung anlegen',
        'referate': referate,
        'form': form,
        'date': date
    })


def SitzungVerwaltenPage(request, sitzID):
    # Anzahl der Anlagen pro Antrag in Sitzung berechnen
    antraege = Antrag.objects.filter(sitzID=sitzID).order_by('-prioritaet','erstelltDate')
    for antrag in antraege:
        antrag.anzAnlagen = Anlage.objects.filter(antragID=antrag.antragID).count()
        antrag.save
        
    sitzung = Sitzung.objects.get(sitzID=sitzID)
    return render(request, 'pages/intern/sitzung/verwalten.html', context={
        'title': 'Sitzung verwalten',
        'antraege': antraege,
        'sitzung': sitzung
    })


def SitzungVertagenPage(request, sitzID): 
    sitzung = Sitzung.objects.get(sitzID=sitzID)
    date = sitzung.sitzDate + timedelta(days=7)
    
    if request.method == 'POST':
        form = SitzungVertagenForm(request.POST)
        if form.is_valid():
            sitzung.sitzDate = form.cleaned_data['datum_neu']
            sitzung.save()

            messages.success(request, 'Die Sitzung wurde auf den ' + sitzung.sitzDate.strftime("%d.%m.%Y") + ' vertagt!')
            return redirect('sitzung-vertagen', sitzID=sitzID)
        else:
            messages.error(request, 'Die Sitzung konnte nicht vertagt werden. Bitte beachte die nachfolgenden Fehler.')
            formFehlerAusgeben(request, form)
            return redirect('sitzung-vertagen', sitzID=sitzID)
    else:
        form = SitzungVertagenForm()
    
    return render(request, 'pages/intern/sitzung/vertagen.html', context={
        'title': 'Sitzung vertagen',
        'sitzung': sitzung,
        'form': form,
        'date': date
    })


def SitzungLoeschenPage(request, sitzID):
    sitzung = Sitzung.objects.get(sitzID=sitzID)
    
    if request.method == 'POST':
        # Prüfe, ob ein Antrag immer noch die zu löschende Sitzung referenziert
        antraege_sitzung = Antrag.objects.filter(sitzID=sitzID).count()
        if antraege_sitzung == 0:
            sitzung.delete()

            messages.success(request, 'Die Sitzung wurde erfolgreich gelöscht!')
            return redirect('sitzungsverwaltung')
        else:
            messages.error(request, 'Die Sitzung konnte nicht gelöscht werden, da es noch Anträge gibt, welche dieser Sitzung zugeordnet sind!')
            return redirect('sitzungsverwaltung')
    
    return render(request, 'pages/intern/sitzung/loeschen.html', context={
        'title': 'Sitzung löschen',
        'sitzung': sitzung
    })
    

def SitzungAbschliessenPage(request, sitzID):
    sitzung = Sitzung.objects.get(sitzID=sitzID)
    
    if request.method == 'POST':
        # Prüfe, ob alle Anträge der Sitzung einen Beschluss haben oder vertagt wurden
        nicht_beschlossene_antraege = Antrag.objects.filter(sitzID=sitzID).filter(beschlussID__isnull=True).filter(~Q(beschlussID__beschlussErgebnis="Vertagt")).count()
        
        if nicht_beschlossene_antraege == 0:
            sitzung.sitzStatus = 'Stattgefunden'
            sitzung.save()

            messages.success(request, 'Die Sitzung wurde erfolgreich abgeschlossen!')
            return redirect('sitzung-abschliessen', sitzID=sitzID)
        else:
            messages.error(request, 'Die Sitzung konnte nicht abgeschlossen werden, da es noch Anträge gibt, welche keinen Beschluss haben!')
            return redirect('sitzung-abschliessen', sitzID=sitzID)
    
    return render(request, 'pages/intern/sitzung/abschliessen.html', context={
        'title': 'Sitzung abschließen',
        'sitzung': sitzung
    })

# ------ Sitzungsverwaltung ------ #



# ++++++ Antragsverwaltung ++++++ #

def getFormVonAntragstyp(antrag):
    # TODO: Überlegung für Erweiterbarkeit machen, sollte ein neuer Antragstyp hinzukommen
    form = None
    typ_id = antrag.typID.typID
    if typ_id == 1:
        form = AntragAllgemeinForm()
    elif typ_id == 2:
        form = AntragFinanziellForm()
    elif typ_id == 3:
        form = AntragVeranstaltungForm()
    elif typ_id == 4:
        form = AntragMitgliedForm()
    elif typ_id == 5:
        form = AntragAmtForm()
    elif typ_id== 6:
        form = AntragBenehmenForm()
    return form


def AntragsverwaltungPage(request):
    antraege = Antrag.objects.all().order_by('-erstelltDate')
    return render(request, 'pages/intern/antragsverwaltung.html', context={
        'title': 'Antragsverwaltung',
        'antraege': antraege
    })
        

def AntragAnzeigenPage(request, antragID):
    antrag = Antrag.objects.get(antragID=antragID)
    anlagen = Anlage.objects.filter(antragID=antragID)
    return render(request, 'pages/antrag.html', context={
        'title': 'Antrag anzeigen',
        'antrag': antrag,
        'form': getFormVonAntragstyp(antrag),
        'aktion': 'ANZEIGEN',
        'anlagen': anlagen
    })


def AntragBearbeitenPage(request, antragID):
    # TODO: Logik für Antrag bearbeiten einbauen
    antrag = Antrag.objects.get(antragID=antragID)
    return render(request, 'pages/antrag.html', context={
        'title': 'Antrag bearbeiten',
        'antrag': antrag,
        'form': getFormVonAntragstyp(antrag),
        'aktion': 'BEARBEITEN'
    })


def AntragLoeschenPage(request, antragID):
    antrag = Antrag.objects.get(antragID=antragID)
    return render(request, 'pages/intern/antrag/loeschen.html', context={
        'title': 'Antrag löschen',
        'antrag': antrag,
        'form': getFormVonAntragstyp(antrag),
        'aktion': 'LOESCHEN'
    })
    

def AntragVertagenPage(request, antragID):
    """
    Vertage den Antrag in eine andere Sitzung
    """
    antrag = Antrag.objects.get(antragID=antragID)
    sitzung = Sitzung.objects.get(sitzID=antrag.sitzID.sitzID)
    
    if request.method == 'POST':
        form = AntragVertagenForm(request.POST)
        # Prüfe, on der Antrag bereits einen Beschluss hat
        if antrag.beschlussID is not None or antrag.wurdeVertagt is True:
            messages.error(request, 'Der Antrag konnte nicht vertagt werden, da er bereits einen Beschluss hat oder bereits vertagt wurde!')
            return redirect('antrag-vertagen', antragID=antragID)
        elif form.is_valid():
            alte_sitzID = antrag.sitzID
            neue_sitzID = form.cleaned_data['sitzung']
            
            print(alte_sitzID)
            print(neue_sitzID)
            
            # Ürsprünglicher Antrag wird in neue Sitzung verschoben
            antrag.sitzID = neue_sitzID
            antrag.save()
            
            # Erstelle leeren Beschluss in aktueller Sitzung, um Vertagung zu kennzeichnen 
            beschluss = Beschluss()
            beschluss.sitzID = alte_sitzID
            beschluss.beschlussText = 'Der Antrag wurde vertagt. Die neue Sitzung ist: ' + str(neue_sitzID)
            beschluss.beschlussErgebnis = 'Vertagt'
            beschluss.beschlussAusfertigung = "Vertagt durch: " + str(request.user.username)
            beschluss.save()
            
            # Erstelle Kopie des Antrags mit und speichere ihn in der alten Sitzung zur Dokumentation
            antrag.antragID = None # type: ignore
            antrag.sitzID = alte_sitzID
            antrag.beschlussID = beschluss
            antrag.wurdeVertagt = True
            antrag.save()
            
            messages.success(request, 'Der Antrag wurde in die Sitzung ' + str(antrag.sitzID.refID.refName) +  ' am ' + antrag.sitzID.sitzDate.strftime("%d.%m.%Y") + ' vertagt!')
            return redirect('antrag-vertagen', antragID=antragID)
        else:
            messages.error(request, 'Der Antrag konnte nicht vertagt werden! Bitte aktualisiere die Seite und versuche es erneut.')
            return redirect('antrag-vertagen', antragID=antragID)
    else:
        form = AntragVertagenForm()
    
    return render(request, 'pages/intern/antrag/vertagen.html', context={
        'title': 'Antrag vertagen',
        'antrag': antrag,
        'sitzung': sitzung,
        'aktion': 'VERTAGEN',
        'form': form
    })
    
    
def AntragBeschliessenPage(request, antragID):
    antrag = Antrag.objects.get(antragID=antragID)
    sitzung = Sitzung.objects.get(sitzID=antrag.sitzID.sitzID)
    
    if request.method == 'POST':
        form = BeschlussForm(request.POST)
        if form.is_valid():
            
            beschluss = Beschluss(
                sitzID = sitzung,
                
                beschlussFaehigkeit = form.cleaned_data['beschluss_faehigkeit'],
                beschlussBehandlung = form.cleaned_data['beschluss_behandlung'],
                
                stimmenJa = form.cleaned_data['stimmen_ja'],
                stimmenNein = form.cleaned_data['stimmen_nein'],
                stimmenEnthaltung = form.cleaned_data['stimmen_enthaltung'],
                beschlussErgebnis = form.cleaned_data['beschluss_ergebnis'],
                
                beschlussText = form.cleaned_data['beschluss_text'],
                beschlussAusfertigung = form.cleaned_data['beschluss_ausfertigung'],
            )
            beschluss.save()
            
            antrag.beschlussID = beschluss
            antrag.save()
            
            messages.success(request, 'Der Beschluss wurde erfolgreich eingepflegt! Der Antragsteller wird nach Abschluss der Sitzung per E-Mail über das Ergebnis informiert.')
            return redirect('antrag-beschliessen', antragID=antragID)
        else:
            messages.error(request, 'Der Beschluss konnte nicht eingepflegt werden! Bitte aktualisiere die Seite und versuche es erneut.')
            return redirect('antrag-beschliessen', antragID=antragID)
    else:
        form = BeschlussForm()
    
    return render(request, 'pages/intern/antrag/beschliessen.html', context={
        'title': 'Antrag beschließen',
        'antrag': antrag,
        'sitzung': sitzung,
        'form': form,
        'aktion': 'BESCHLIESSEN'
    })
    
def AntragPriorisierenPage(request, antragID):
    antrag = Antrag.objects.get(antragID=antragID)
    sitzung = Sitzung.objects.get(sitzID=antrag.sitzID.sitzID)
    
    hoechste_prioritaet = Antrag.objects.filter(sitzID=sitzung).aggregate(Max('prioritaet'))['prioritaet__max']
    print(hoechste_prioritaet)
    antrag.prioritaet = hoechste_prioritaet + 1
    antrag.save()
        
    return redirect('sitzung-verwalten', sitzID=sitzung.sitzID)
    
# ------ Antragsverwaltung ------ #


# ++++++ Benutzerauthentifizierung ++++++ #

def LoginPage(request):
    # redirect if user is already logged in
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Der Benutzername oder das Passwort ist falsch!')
                formFehlerAusgeben(request, form)
                return redirect('login')
    else: 
        form = LoginForm()
              
    return render(request, 'pages/login.html', context={
        'title': 'Anmelden', 
        'form': form
    })


def LogoutPage(request):
    logout(request)
    return redirect('index')

# ------ Benutzerauthentifizierung ------ #



# ========== Antragsseiten ========== #

# ++++++ Funktionen ++++++ #

# Prüfe, ob der Antragsteller bereits in der Datenbank existiert und gib diesen zurück
def astellerAbfragenOderErstellen(form):
    astellerEmail = form.cleaned_data['email']
    if Antragssteller.objects.filter(astellerEmail=astellerEmail).exists():
        asteller = Antragssteller.objects.get(astellerEmail=astellerEmail)
    else:
        asteller = Antragssteller()
        asteller.astellerName = form.cleaned_data['name']
        asteller.astellerEmail = astellerEmail
        asteller.save() 
    return asteller


# Prüfe, wann die nächste Sitzung des Referats stattfindet und gib diese zurück
# TODO: Prüfung auf Eilantrag einbauen & E-Mail an Referat senden
def sitzungenAbfragen(form):
    refID = form.cleaned_data['referat']
    sitzungen = Sitzung.objects.filter(refID=refID).filter(sitzDate__gt=date.today()).order_by('sitzDate')
    return sitzungen


# Kurzfassung der render-Funktion für Antragsseiten
def renderAntrag(request, title, form):
    # Frage die nächsten 2 Sitzungen jedes Referates ab und gibt diese an die Seite weiter
    sitzungen = Sitzung.objects.filter(sitzDate__gt=date.today()).order_by('sitzDate')
    return render(request, 'pages/antrag.html', context={
        'title': title, 
        'form': form,
        'sitzungen': sitzungen
    })


def anlagenSpeichern(request, antrag):
    dateien = request.FILES.getlist('anlagen')
    anlagen_liste = []
    
    for datei in dateien:
        anlage = Anlage()
        # Füge Datei als Anlage hinzu
        anlage.anlage = datei
        # Überschreibe den Pfad, sodass die Anlage im Format <AntragsID>/<Dateiname> gespeichert wird
        anlage.anlage.name = str(antrag.antragID) + '/' + datei.name
        # Referenziere die Anlage auf den Antrag
        anlage.antragID = antrag
        # Dateiname extra für Anzeige speichern
        anlage.anlageName = datei.name
        
        anlagen_liste.append(anlage)
        
    if anlagen_liste:
        Anlage.objects.bulk_create(anlagen_liste)
        
    return anlagen_liste

# ------ Funktionen ------ #


# ++++++ Anträge ++++++ #

FEEDBACK_ANTRAG_SUCCESS = 'Dein Antrag wurde erfolgreich eingereicht! Du erhältst in Kürze eine E-Mail mit der Bestätigung.'

def AntragAllgemein(request):
    if request.method == 'POST':
        form = AntragAllgemeinForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = sitzungenAbfragen(form)
            # Definiere den Antragstyp anhand der Slug
            antragstyp = Antragstyp.objects.get(typSlug='antrag-ohne-finanzielle-mittel')
            # Prüfe, ob Antragsteller bereits existiert
            asteller = astellerAbfragenOderErstellen(form)
            
            # Erstelle den Antrag
            antrag = Antrag()
            antrag.sitzID = sitzungen[0]
            antrag.typID = antragstyp
            antrag.astellerID = asteller
            antrag.antragTitel = form.cleaned_data['titel']
            antrag.antragText = form.cleaned_data['text']
            antrag.istEilantrag = form.cleaned_data['ist_eilantrag']
            
            antrag.antragGrund = form.cleaned_data['grund']
            antrag.antragVorschlag = form.cleaned_data['vorschlag']
            
            antrag.save()
            
            anlagenSpeichern(request, antrag)
            
            messages.success(request, FEEDBACK_ANTRAG_SUCCESS)
            return redirect('antrag-allgemein')
        else:
            messages.error(request, 'Dein Antrag konnte nicht abgeschickt werden. Bitte beachte die nachfolgenden Fehler.')
            formFehlerAusgeben(request, form)
            return redirect('antrag-allgemein')
    else:
        form = AntragAllgemeinForm()

    return renderAntrag(request, 'Allgemeiner Antrag', form)


def AntragFinanziell(request):
    if request.method == 'POST':
        form = AntragFinanziellForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = sitzungenAbfragen(form)
            # Definiere den Antragstyp anhand der Slug
            antragstyp = Antragstyp.objects.get(typSlug='antrag-mit-finanziellen-mitteln')
            # Prüfe, ob Antragsteller bereits existiert
            asteller = astellerAbfragenOderErstellen(form)
            
            # Erstelle den Antrag
            antrag = Antrag()
            antrag.sitzID = sitzungen[0]
            antrag.typID = antragstyp
            antrag.astellerID = asteller
            antrag.antragTitel = form.cleaned_data['titel']
            antrag.antragText = form.cleaned_data['text']
            antrag.istEilantrag = form.cleaned_data['ist_eilantrag']
            
            antrag.antragGrund = form.cleaned_data['grund']
            antrag.antragKostenposition = form.cleaned_data['position']
            antrag.antragSumme = form.cleaned_data['summe']
            antrag.antragVorschlag = form.cleaned_data['vorschlag']
            
            antrag.save()
            
            anlagenSpeichern(request, antrag)
            
            messages.success(request, FEEDBACK_ANTRAG_SUCCESS)
            return redirect('antrag-finanziell')
        else:
            messages.error(request, 'Dein Antrag konnte nicht abgeschickt werden. Bitte beachte die nachfolgenden Fehler.')
            formFehlerAusgeben(request, form)
            return redirect('antrag-finanziell')
    else:
        form = AntragFinanziellForm()
    
    return renderAntrag(request, 'Antrag mit finanziellen Mitteln', form)


def AntragVeranstaltung(request):
    if request.method == 'POST':
        form = AntragVeranstaltungForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = sitzungenAbfragen(form)
            # Definiere den Antragstyp anhand der Slug
            antragstyp = Antragstyp.objects.get(typSlug='antrag-fuer-veranstaltungen')
            # Prüfe, ob Antragsteller bereits existiert
            asteller = astellerAbfragenOderErstellen(form)
            
            # Erstelle den Antrag
            antrag = Antrag()
            antrag.sitzID = sitzungen[0]
            antrag.typID = antragstyp
            antrag.astellerID = asteller
            antrag.antragTitel = form.cleaned_data['titel']
            antrag.antragText = form.cleaned_data['text']
            antrag.istEilantrag = form.cleaned_data['ist_eilantrag']
            
            antrag.antragGrund = form.cleaned_data['grund']
            antrag.antragKostenposition = form.cleaned_data['position']
            antrag.antragSumme = form.cleaned_data['summe']
            antrag.antragVerantwortlichkeit = form.cleaned_data['verantwortlichkeit']
            antrag.antragZeitraum = form.cleaned_data['zeitraum']
            antrag.antragVorschlag = form.cleaned_data['vorschlag']
                  
            antrag.save()
            
            anlagenSpeichern(request, antrag)
            
            messages.success(request, FEEDBACK_ANTRAG_SUCCESS)
            return redirect('antrag-veranstaltung')
        else:
            messages.error(request, 'Dein Antrag konnte nicht abgeschickt werden. Bitte beachte die nachfolgenden Fehler.')
            formFehlerAusgeben(request, form)
            return redirect('antrag-veranstaltung')
    else:
        form = AntragVeranstaltungForm()
    
    return renderAntrag(request, 'Antrag für Veranstaltungen', form)


def AntragMitglied(request):
    if request.method == 'POST':
        form = AntragMitgliedForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = sitzungenAbfragen(form)
            # Definiere den Antragstyp anhand der Slug
            antragstyp = Antragstyp.objects.get(typSlug='beratendes-mitglied')
            # Prüfe, ob Antragsteller bereits existiert
            asteller = astellerAbfragenOderErstellen(form)
            
            # Erstelle den Antrag
            antrag = Antrag()
            antrag.sitzID = sitzungen[0]
            antrag.typID = antragstyp
            antrag.astellerID = asteller
            antrag.antragTitel = form.cleaned_data['titel']
            antrag.antragText = form.cleaned_data['text']
            antrag.istEilantrag = form.cleaned_data['ist_eilantrag']
            
            antrag.antragVorstellungPerson = form.cleaned_data['vorstellung_person']
            
            antrag.save()
            
            anlagenSpeichern(request, antrag)
                        
            messages.success(request, FEEDBACK_ANTRAG_SUCCESS)
            return redirect('antrag-mitglied')
        else:
            messages.error(request, 'Dein Antrag konnte nicht abgeschickt werden. Bitte beachte die nachfolgenden Fehler.')
            formFehlerAusgeben(request, form)
            return redirect('antrag-mitglied')
    else:
        form = AntragMitgliedForm()
    
    return renderAntrag(request, 'Antrag zum beratenden MItglied', form)


def AntragAmt(request):
    if request.method == 'POST':
        form = AntragAmtForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = sitzungenAbfragen(form)
            # Definiere den Antragstyp anhand der Slug
            antragstyp = Antragstyp.objects.get(typSlug='wahl-auf-stelle-oder-amt')
            # Prüfe, ob Antragsteller bereits existiert & Mitglied ist
            asteller = astellerAbfragenOderErstellen(form)
            asteller.astellerIstMitglied = form.cleaned_data['ist_mitglied']
            asteller.save()
            
            # Erstelle den Antrag
            antrag = Antrag()
            antrag.sitzID = sitzungen[0]
            antrag.typID = antragstyp
            antrag.astellerID = asteller
            antrag.antragTitel = form.cleaned_data['titel']
            antrag.antragText = form.cleaned_data['text']
            antrag.istEilantrag = form.cleaned_data['ist_eilantrag']
            
            antrag.antragVorstellungPerson = form.cleaned_data['vorstellung_person']
            antrag.antragFragenZumAmt = form.cleaned_data['fragen_amt']
                        
            antrag.save()
            
            anlagenSpeichern(request, antrag)
                        
            messages.success(request, FEEDBACK_ANTRAG_SUCCESS)
            return redirect('antrag-amt')
        else:
            messages.error(request, 'Dein Antrag konnte nicht abgeschickt werden. Bitte beachte die nachfolgenden Fehler.')
            formFehlerAusgeben(request, form)
            return redirect('antrag-amt')
    else:
        form = AntragAmtForm()
    
    return renderAntrag(request, 'Antrag zur Wahl auf Stelle/Amt', form)


def AntragBenehmen(request):
    if request.method == 'POST':
        form = AntragBenehmenForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = sitzungenAbfragen(form)
            # Definiere den Antragstyp anhand der Slug
            antragstyp = Antragstyp.objects.get(typSlug='herstellung-des-benehmens')
            # Prüfe, ob Antragsteller bereits existiert
            asteller = astellerAbfragenOderErstellen(form)
            
            # Erstelle den Antrag
            antrag = Antrag()
            antrag.sitzID = sitzungen[0]
            antrag.typID = antragstyp
            antrag.astellerID = asteller
            antrag.antragTitel = form.cleaned_data['titel']
            antrag.antragText = form.cleaned_data['text']
            antrag.istEilantrag = form.cleaned_data['ist_eilantrag']
            
            antrag.antragGrund = form.cleaned_data['grund']
            antrag.antragVorschlag = form.cleaned_data['vorschlag']

            antrag.save()
            
            anlagenSpeichern(request, antrag)
                        
            messages.success(request, FEEDBACK_ANTRAG_SUCCESS)
            return redirect('antrag-benehmen')
        else:
            messages.error(request, 'Dein Antrag konnte nicht abgeschickt werden. Bitte beachte die nachfolgenden Fehler.')
            formFehlerAusgeben(request, form)
            return redirect('antrag-benehmen')
    else:
        form = AntragBenehmenForm()
    
    return renderAntrag(request, 'Antrag auf Herstellung des Benehmens', form)

# ------ Anträge ------ #



# ++++++ Tagesordnung ++++++ #

def TagesordnungVorschauPage(request, sitzID):
    sitzung = Sitzung.objects.get(sitzID=sitzID)
    antraege = Antrag.objects.filter(sitzID=sitzID).order_by('-prioritaet','erstelltDate')
    
    antraege_liste = []
    counter = 3
    for antrag in antraege:
        anlagen = Anlage.objects.filter(antragID=antrag.antragID)
        antraege_liste.append([counter, antrag, anlagen])
        counter +=1
    
    return render(request, 'pages/intern/tagesordnung.html', context={
        'title': 'Vorschau der Tagesordnung',
        'sitzung': sitzung,
        'antraege': antraege,
    })


def TagesordnungErstellenPage(request, sitzID):
    sitzung = Sitzung.objects.get(sitzID=sitzID)
    antraege = Antrag.objects.filter(sitzID=sitzID).order_by('-prioritaet','erstelltDate')
    
    # TODO: Sitzungsnummer automatisch generieren lassen
    sitzung_nummer = '22_23-003-01'
    
    # Anträge mit Anlagen & TOP-Nummer in Liste schreiben
    antraege_liste = []
    top_counter = 3
    for antrag in antraege:
        anlagen = Anlage.objects.filter(antragID=antrag.antragID)
        antraege_liste.append([top_counter, antrag, anlagen])
        top_counter +=1
    
    # Template mit Daten rendern
    template_rendered = render_to_string('etherpad/tagesordnung.html', context={
        'sitzung': sitzung,
        'antraege': antraege_liste,
        'request': request,
    })
    
    
    # Prüfe, ob die Sitzung bereits ein Etherpad hat
    pads = []
    result = list_pads()
    if result['message'] != 'ok':
        messages.error(request, "Die Verbindung mit dem Etherpad konnte nicht hergestellt werden. Bitte kontaktiere einen Administrator.")
        messages.debug(request, str(result))
        return redirect('tagesordnung-vorschau', sitzID=sitzID)
    else:
        pads = result['data']['padIDs']
      
        
    # Wenn nicht, erstelle ein neues Etherpad
    if sitzung_nummer not in pads:
        result = create_pad(sitzung_nummer)
        if result['message'] != 'ok':
            messages.error(request, "Das Etherpad für die Sitzung konnte nicht erstellt werden. Bitte kontaktiere einen Administrator.")
            messages.debug(request, str(result))
            return redirect('tagesordnung-vorschau', sitzID=sitzID)
        else:
            messages.debug(request, str(result))
          
            
    # Gerendertes Template in Etherpad schreiben
    result = set_html(sitzung_nummer, template_rendered)
    if result['message'] != 'ok':
        messages.error(request, "Die Tagesordnung konnte nicht im Etherpad gespeichert werden. Bitte kontaktiere einen Administrator.")
        messages.debug(request, str(result))
        return redirect('tagesordnung-vorschau', sitzID=sitzID)
    else:
        messages.success(request, "Die Tagesordnung wurde erfolgreich erstellt und im Etherpad eingefügt.")

        # Etherpad-Link in Sitzung speichern
        sitzung.etherpadLink = settings.ETHERPAD_PAD_ENDPOINT + sitzung_nummer
        sitzung.save()
 
    return redirect('tagesordnung-vorschau', sitzID=sitzID)

# ------ Tagesordnung ------ #