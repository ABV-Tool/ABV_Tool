from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.db.models import Q
from django.utils.html import strip_tags
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from datetime import date, datetime, timedelta

from .mails import mailAstellerEingangsbestaetigung
from .models import Referat, Sitzung, Antrag, Antragssteller, Antragstyp, Beschluss, Anlage
from .forms import ReferatForm, BeschlussForm, SitzungVertagenForm, AntragVertagenForm, SitzungAnlegenForm
from .forms import LoginForm, AntragAllgemeinForm, AntragFinanziellForm, AntragVeranstaltungForm, AntragMitgliedForm, AntragAmtForm, AntragBenehmenForm

# Kann bei einer render()-Funktion mitgeliefert werden, um entsprechendes Feedback anzuzeigen
# Hinweis: Komponente muss am Ende der Seite eingebunden sein
# => type: SUCCESS, ERROR, WARNING, INFO (siehe templates/components/alert.html)
# => text: Text, der angezeigt werden soll
# => back_url: URL, auf welche der 'Zurück'-Button verweist
class FrontendFeedback:
    type = ''
    text = ''
    back_url = ''

# ========== Hauptseiten ========== #

def HomePage(request):
    return render(request, 'pages/home.html', context={'title': 'Home'})


def ArchivPage(request):
    return render(request, 'pages/archive.html', context={'title': 'Archiv'})

# ========== Interner Bereich ========== #

# ++++++ Referatsverwaltung ++++++ #

def ReferatsverwaltungPage(request):
    referate = Referat.objects.all().order_by('refID')
    context = {'title': 'Referatsverwaltung', 'referate': referate}
    return render(request, 'pages/intern/referatsverwaltung.html', context=context)


def ReferatErstellenPage(request):
    feedback = FrontendFeedback()
    if request.method == 'POST':
        form = ReferatForm(request.POST)
        if form.is_valid():
            referat_id = Referat.objects.latest('refID').refID + 1
            print(referat_id)
            referat = Referat(
                refID=referat_id,
                refName=form.cleaned_data['referat_name'],
                refZyklus=form.cleaned_data['referat_zyklus'],
                refEmail=form.cleaned_data['referat_email']
            )
            referat.save()
            feedback.type = "SUCCESS"
            feedback.text = 'Referat ' + referat.refName + ' erfolgreich erstellt!'
            feedback.back_url = '/intern/referatsverwaltung/'
        else:
            feedback.type = "ERROR"
            feedback.text = 'Fehler beim Erstellen des Referats! Bitte aktualisiere die Seite und versuche es erneut.'
            print(form.errors)
    else:
        form = ReferatForm()
        
    return render(request, 'pages/intern/referat.html', context={
        'title': 'Referat erstellen', 
        'aktion':'ERSTELLEN',
        'form': form,
        'feedback': feedback
    })


def ReferatBearbeitenPage(request, refID):
    feedback = FrontendFeedback()
    referat = Referat.objects.get(refID=refID)
    
    if request.method == 'POST':
        form = ReferatForm(request.POST)
        if form.is_valid():
            referat.refName = form.cleaned_data['referat_name']
            referat.refZyklus = form.cleaned_data['referat_zyklus']
            referat.refEmail = form.cleaned_data['referat_email']
            referat.save()
            feedback.type = "SUCCESS"
            feedback.text = 'Referat ' + referat.refName + ' erfolgreich bearbeitet!'
            feedback.back_url = '/intern/referatsverwaltung/'
        else:
            feedback.type = "ERROR"
            feedback.text = 'Fehler beim Bearbeiten des Referats! Bitte aktualisieren die Seite und versuche es erneut.'
    else:
        form = ReferatForm()
    
    return render(request, 'pages/intern/referat.html', context={
        'title': 'Referat bearbeiten', 
        'aktion':'BEARBEITEN', 
        'referat': referat,
        'form': form,
        'feedback': feedback
    })


def ReferatLoeschenPage(request, refID):
    feedback = FrontendFeedback()
    referat = Referat.objects.get(refID=refID)
    form = ReferatForm()

    if request.method == 'POST':
        referat.delete()
        feedback.type = "SUCCESS"
        feedback.text = 'Referat ' + referat.refName + ' erfolgreich gelöscht!'
        feedback.back_url = '/intern/referatsverwaltung/'
    else:
        form = ReferatForm()

    return render(request, 'pages/intern/referat.html', context={
        'title': 'Referat löschen', 
        'aktion':'LOESCHEN', 
        'referat': referat,
        'form': form,
        'feedback': feedback
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
    feedback = FrontendFeedback()
    referate = Referat.objects.all().order_by('refID')
    date = datetime.now().date() + timedelta(days=7)
    
    if request.method == 'POST':
        form = SitzungAnlegenForm(request.POST)
        if form.is_valid():
            sitzung = Sitzung()
            sitzung.sitzDate = form.cleaned_data['datum_sitzung']
            sitzung.refID = form.cleaned_data['referat']
            sitzung.save()

            feedback.type = "SUCCESS"
            feedback.text = 'Die Sitzung wurde wurde für den ' + sitzung.sitzDate.strftime("%d.%m.%Y") + ' angelegt!'
            feedback.back_url = '/intern/sitzungsverwaltung/'
        else:
            feedback.type = "ERROR"
            feedback.text = 'Die Sitzung konnte nicht angelegt werden. ' + strip_tags(str(form.errors.get('datum_sitzung')))
    else:
        form = SitzungAnlegenForm()
        
    return render(request, 'pages/intern/sitzung/anlegen.html', context={
        'title': 'Sitzung anlegen',
        'referate': referate,
        'form': form,
        'date': date,
        'feedback': feedback
    })


def SitzungAnzeigenPage(request, sitzID):
    antraege = Antrag.objects.filter(sitzID=sitzID)
    sitzung = Sitzung.objects.get(sitzID=sitzID)
    return render(request, 'pages/intern/sitzung/anzeigen.html', context={
        'title': 'Sitzung anzeigen',
        'antraege': antraege,
        'sitzung': sitzung
    })


def SitzungVertagenPage(request, sitzID):
    feedback = FrontendFeedback()
    sitzung = Sitzung.objects.get(sitzID=sitzID)
    date = sitzung.sitzDate + timedelta(days=7)
    
    if request.method == 'POST':
        form = SitzungVertagenForm(request.POST)
        if form.is_valid():
            sitzung.sitzDate = form.cleaned_data['datum_neu']
            sitzung.save()

            feedback.type = "SUCCESS"
            feedback.text = 'Die Sitzung wurde auf den ' + sitzung.sitzDate.strftime("%d.%m.%Y") + ' vertagt!'
            feedback.back_url = '/intern/sitzungsverwaltung/'
        else:
            feedback.type = "ERROR"
            feedback.text = 'Die Sitzung konnte nicht vertagt werden. ' + strip_tags(str(form.errors.get('datum_neu')))
    else:
        form = SitzungVertagenForm()
    
    return render(request, 'pages/intern/sitzung/vertagen.html', context={
        'title': 'Sitzung vertagen',
        'sitzung': sitzung,
        'form': form,
        'date': date,
        'feedback': feedback
    })


def SitzungLoeschenPage(request, sitzID):
    feedback = FrontendFeedback()
    sitzung = Sitzung.objects.get(sitzID=sitzID)
    
    if request.method == 'POST':
        # Prüfe, ob ein Antrag immer noch die zu löschende Sitzung referenziert
        antraege_sitzung = Antrag.objects.filter(sitzID=sitzID).count()
        if antraege_sitzung == 0:
            sitzung.delete()

            feedback.type = "SUCCESS"
            feedback.text = 'Die Sitzung wurde erfolgreich gelöscht!'
            feedback.back_url = '/intern/sitzungsverwaltung/'
        else:
            feedback.type = "ERROR"
            feedback.text = 'Die Sitzung konnte nicht gelöscht werden, da es noch Anträge gibt, welche dieser Sitzung zugeordnet sind!'
            feedback.back_url = '/intern/sitzung/' + str(sitzung.sitzID) + '/anzeigen'
    
    return render(request, 'pages/intern/sitzung/loeschen.html', context={
        'title': 'Sitzung löschen',
        'sitzung': sitzung,
        'feedback': feedback
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

def renderAntragPage(request, url, antrag, title, aktion):
    return render(request, url, context={
        'title': title,
        'antrag': antrag,
        'form': getFormVonAntragstyp(antrag),
        'aktion': aktion
    })
    

def AntragsverwaltungPage(request):
    antraege = Antrag.objects.all()
    return render(request, 'pages/intern/antragsverwaltung.html', context={
        'title': 'Antragsverwaltung',
        'antraege': antraege
    })
        

def AntragAnzeigenPage(request, antragID):
    antrag = Antrag.objects.get(antragID=antragID)
    return renderAntragPage(request, 'pages/antrag.html', antrag, 'Antrag anzeigen', 'ANZEIGEN')


def AntragBearbeitenPage(request, antragID):
    # TODO: Logik für Antrag bearbeiten einbauen
    antrag = Antrag.objects.get(antragID=antragID)
    return renderAntragPage(request, 'pages/antrag.html', antrag, 'Antrag bearbeiten', 'BEARBEITEN')


def AntragLoeschenPage(request, antragID):
    antrag = Antrag.objects.get(antragID=antragID)
    return renderAntragPage(request, 'pages/intern/antrag/loeschen.html', antrag, 'Antrag löschen', 'ANZEIGEN')
    

def AntragVertagenPage(request, antragID):
    feedback = FrontendFeedback()
    antrag = Antrag.objects.get(antragID=antragID)
    sitzung = Sitzung.objects.get(sitzID=antrag.sitzID.sitzID)
    
    if request.method == 'POST':
        form = AntragVertagenForm(request.POST)
        if form.is_valid():
            # Erstelle leeren Beschluss, um Vertagung zu kennzeichnen 
            beschluss = Beschluss()
            beschluss.sitzID = antrag.sitzID
            beschluss.beschlussText = 'Der Antrag wurde vertagt. Die ursprüngliche Sitzung war: ' + str(antrag.sitzID)
            beschluss.beschlussErgebnis = 'Vertagt'
            beschluss.beschlussAusfertigung = "Alte Sitzungs-ID: " + str(antrag.sitzID.sitzID) + "\nVertagt durch: " + str(request.user.username)
            beschluss.save()
            
            # Setze den leeren Beschluss als Beschluss für den Antrag
            antrag.beschlussID = beschluss
            antrag.save()
            
            # Setzte antragID auf None, damit das Objekt in der neuen Sitzung neu erstellt wird
            antrag.sitzID = form.cleaned_data['sitzung']
            antrag.antragID = None
            antrag.beschlussID = None
            antrag.save()

            feedback.type = "SUCCESS"
            feedback.text = 'Der Antrag wurde in die Sitzung ' + str(antrag.sitzID.refID.refName) +  ' am ' + antrag.sitzID.sitzDate.strftime("%d.%m.%Y") + ' vertagt!'
            feedback.back_url = '/intern/sitzungsverwaltung/'
        else:
            feedback.type = "ERROR"
            feedback.text = 'Der Antrag konnte nicht vertagt werden! Bitte aktualisiere die Seite und versuche es erneut.'
    else:
        form = AntragVertagenForm()
    
    return render(request, 'pages/intern/antrag/vertagen.html', context={
        'title': 'Antrag vertagen',
        'antrag': antrag,
        'sitzung': sitzung,
        'aktion': 'VERTAGEN',
        'form': form,
        'feedback': feedback
    })
    
    
def AntragBeschliessenPage(request, antragID):
    feedback = FrontendFeedback()
    antrag = Antrag.objects.get(antragID=antragID)
    sitzung = Sitzung.objects.get(sitzID=antrag.sitzID.sitzID)
    
    print(sitzung.sitzID)
    
    if request.method == 'POST':
        form = BeschlussForm(request.POST)
        if form.is_valid():
            
            beschluss, __ = Beschluss.objects.update_or_create(
                sitzID = sitzung,
                
                defaults={
                    "beschlussFaehigkeit" : form.cleaned_data['beschluss_faehigkeit'],
                
                    "stimmenJa" : form.cleaned_data['stimmen_ja'],
                    "stimmenNein" : form.cleaned_data['stimmen_nein'],
                    "stimmenEnthaltung" : form.cleaned_data['stimmen_enthaltung'],
                    "beschlussErgebnis" : form.cleaned_data['beschluss_ergebnis'],
                    
                    "beschlussText" : form.cleaned_data['beschluss_text'],
                    "beschlussAusfertigung" : form.cleaned_data['beschluss_ausfertigung'],
                }
            )
            
            antrag.beschlussID = beschluss
            antrag.save()
            
            feedback.type = "SUCCESS"
            feedback.text = 'Beschluss erfolgreich eingepflegt! Der Antragsteller wird per E-Mail über das Ergebnis informiert.'
            feedback.back_url = '/intern/sitzung/' + str(sitzung.sitzID) + '/anzeigen'
        else:
            feedback.type = "ERROR"
            feedback.text = 'Fehler beim Einpflegen des Beschlusses! Bitte aktualisiere die Seite und versuche es erneut.'
    else:
        form = BeschlussForm()
    
    return render(request, 'pages/intern/antrag/beschliessen.html', context={
        'title': 'Antrag beschließen',
        'antrag': antrag,
        'sitzung': sitzung,
        'form': form,
        'aktion': 'BESCHLIESSEN',
        'feedback': feedback
    })
    
# ------ Antragsverwaltung ------ #


# ++++++ Benutzerauthentifizierung ++++++ #

def LoginPage(request):
    feedback = FrontendFeedback()
    
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
                feedback.type = "ERROR"
                feedback.text = 'Die eingegebenen Daten sind ungültig! Versuche es erneut.'
    else: 
        form = LoginForm()
              
    return render(request, 'pages/login.html', context={
        'title': 'Anmelden', 
        'form': form, 
        'feedback': feedback
    })


def LogoutPage(request):
    logout(request)
    return redirect('index')

# ------ Benutzerauthentifizierung ------ #



# ========== Antragsseiten ========== #

# ++++++ Funktionen ++++++ #

# Prüfe, ob der Antragsteller bereits in der Datenbank existiert und gib diesen zurück
def checkAntragsteller(form):
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
def checkSitzungen(form):
    refID = form.cleaned_data['referat']
    sitzungen = Sitzung.objects.filter(refID=refID).filter(sitzDate__gt=date.today()).order_by('sitzDate')
    return sitzungen


# Kurzfassung der render-Funktion für Antragsseiten
def renderAntrag(request, title, form, feedback):
    # Frage die nächsten 2 Sitzungen jedes Referates ab und gibt diese an die Seite weiter
    sitzungen = Sitzung.objects.filter(sitzDate__gt=date.today()).order_by('sitzDate')
    return render(request, 'pages/antrag.html', context={
        'title': title, 
        'form': form,
        'feedback': feedback,
        'sitzungen': sitzungen
    })


def anlagenSpeichern(request, antrag):
    dateien = request.FILES.getlist('anlagen')

    anlagen_liste = []
    for datei in dateien:
        anlage = Anlage()
        anlage.anlage = datei
        anlage.anlage.name = str(antrag.antragID) + '/' + datei.name
        anlagen_liste.append(anlage)
        
    if anlagen_liste:
        Anlage.objects.bulk_create(anlagen_liste)
        
    return anlagen_liste

# ------ Funktionen ------ #


# ++++++ Anträge ++++++ #

FEEDBACK_ANTRAG_SUCCESS = 'Dein Antrag wurde erfolgreich eingereicht! Du erhältst in Kürze eine E-Mail mit der Bestätigung.'

def AntragAllgemein(request):
    feedback = FrontendFeedback()
    feedback.back_url = '/'
    if request.method == 'POST':
        form = AntragAllgemeinForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = checkSitzungen(form)
            # Definiere den Antragstyp anhand der Slug
            antragstyp = Antragstyp.objects.get(typSlug='antrag-ohne-finanzielle-mittel')
            # Prüfe, ob Antragsteller bereits existiert
            asteller = checkAntragsteller(form)
            
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
            
            # File-Upload
            anlagen = anlagenSpeichern(request, antrag)
            print(anlagen)
            
            antrag.save()
            
            feedback.type='SUCCESS'
            feedback.text=FEEDBACK_ANTRAG_SUCCESS
    else:
        form = AntragAllgemeinForm()

    return renderAntrag(request, 'Allgemeiner Antrag', form, feedback)


def AntragFinanziell(request):
    feedback = FrontendFeedback()
    feedback.back_url = '/'
    if request.method == 'POST':
        form = AntragFinanziellForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = checkSitzungen(form)
            # Definiere den Antragstyp anhand der Slug
            antragstyp = Antragstyp.objects.get(typSlug='antrag-mit-finanziellen-mitteln')
            # Prüfe, ob Antragsteller bereits existiert
            asteller = checkAntragsteller(form)
            
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
            
            feedback.type='SUCCESS'
            feedback.text=FEEDBACK_ANTRAG_SUCCESS
    else:
        form = AntragFinanziellForm()
    
    return renderAntrag(request, 'Antrag mit finanziellen Mitteln', form, feedback)


def AntragVeranstaltung(request):
    feedback = FrontendFeedback()
    feedback.back_url = '/'
    if request.method == 'POST':
        form = AntragVeranstaltungForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = checkSitzungen(form)
            # Definiere den Antragstyp anhand der Slug
            antragstyp = Antragstyp.objects.get(typSlug='antrag-fuer-veranstaltungen')
            # Prüfe, ob Antragsteller bereits existiert
            asteller = checkAntragsteller(form)
            
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
                  
            print(form.cleaned_data['anlagen'])
                        
            antrag.save()
            
            feedback.type='SUCCESS'
            feedback.text=FEEDBACK_ANTRAG_SUCCESS
    else:
        form = AntragVeranstaltungForm()
    
    return renderAntrag(request, 'Antrag für Veranstaltungen', form, feedback)


def AntragMitglied(request):
    feedback = FrontendFeedback()
    feedback.back_url = '/'
    if request.method == 'POST':
        form = AntragMitgliedForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = checkSitzungen(form)
            # Definiere den Antragstyp anhand der Slug
            antragstyp = Antragstyp.objects.get(typSlug='beratendes-mitglied')
            # Prüfe, ob Antragsteller bereits existiert
            asteller = checkAntragsteller(form)
            
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
                        
            feedback.type='SUCCESS'
            feedback.text=FEEDBACK_ANTRAG_SUCCESS
    else:
        form = AntragMitgliedForm()
    
    return renderAntrag(request, 'Antrag zum beratenden MItglied', form, feedback)


def AntragAmt(request):
    feedback = FrontendFeedback()
    feedback.back_url = '/'
    if request.method == 'POST':
        form = AntragAmtForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = checkSitzungen(form)
            # Definiere den Antragstyp anhand der Slug
            antragstyp = Antragstyp.objects.get(typSlug='wahl-auf-stelle-oder-amt')
            # Prüfe, ob Antragsteller bereits existiert & Mitglied ist
            asteller = checkAntragsteller(form)
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
                        
            feedback.type='SUCCESS'
            feedback.text=FEEDBACK_ANTRAG_SUCCESS
    else:
        form = AntragAmtForm()
    
    return renderAntrag(request, 'Antrag zur Wahl auf Stelle/Amt', form, feedback)


def AntragBenehmen(request):
    feedback = FrontendFeedback()
    feedback.back_url = '/'
    if request.method == 'POST':
        form = AntragBenehmenForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = checkSitzungen(form)
            # Definiere den Antragstyp anhand der Slug
            antragstyp = Antragstyp.objects.get(typSlug='herstellung-des-benehmens')
            # Prüfe, ob Antragsteller bereits existiert
            asteller = checkAntragsteller(form)
            
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
                        
            feedback.type='SUCCESS'
            feedback.text=FEEDBACK_ANTRAG_SUCCESS
    else:
        form = AntragBenehmenForm()
    
    return renderAntrag(request, 'Antrag auf Herstellung des Benehmens', form, feedback)

# ------ Anträge ------ #