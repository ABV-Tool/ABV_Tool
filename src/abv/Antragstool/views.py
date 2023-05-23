from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.core.mail import send_mail
from datetime import date
from .models import Referat, Sitzung, Antrag, Antragssteller, Antragstyp
from .forms import ReferatForm
from .forms import LoginForm, AntragAllgemeinForm, AntragFinanziellForm, AntragVeranstaltungForm, AntragMitgliedForm, AntragAmtForm, AntragBenehmenForm


class FrontendFeedback:
    type = ''
    text = ''
    back_url = ''

# ========== Hauptseiten ========== #

def HomePage(request):
    return render(request, 'pages/home.html', context={'title': 'Home'})


def AboutPage(request):
    return render(request, 'pages/about.html', context={'title': 'Über Uns'})


def ArchivPage(request):
    return render(request, 'pages/archive.html', context={'title': 'Archiv'})

# ========== Interner Bereich ========== #

# ++++++ Referatsverwaltung ++++++ #

def ReferatsverwaltungPage(request):
    referate = Referat.objects.all().order_by('refID')
    context = {'title': 'Referatsverwaltung', 'referate': referate, 'fixed_footer': True}
    return render(request, 'pages/intern/referatsverwaltung.html', context=context)


def ReferatErstellenPage(request):
    feedback = FrontendFeedback()
    if request.method == 'POST':
        form = ReferatForm(request.POST)
        if form.is_valid():
            refID = Referat.objects.latest('refID').refID + 1
            referat = Referat(
                refID=refID,
                refName=form.cleaned_data['referat_name'],
                refZyklus=form.cleaned_data['referat_zyklus']
            )
            referat.save()
            feedback.type = "SUCCESS"
            feedback.text = 'Referat ' + referat.refName + ' erfolgreich erstellt!'
            feedback.back_url = '/intern/referatsverwaltung/'
        else:
            feedback.type = "ERROR"
            feedback.text = 'Fehler beim Erstellen des Referats! Bitte aktualisieren die Seite und versuche es erneut.'
    else:
        form = ReferatForm()
    return render(request, 'pages/intern/referat.html', context={
        'title': 'Referat erstellen', 
        'action':'CREATE',
        'form': form,
        'feedback': feedback,
        'fixed_footer': True
    })


def ReferatBearbeitenPage(request, refID):
    feedback = FrontendFeedback()
    referat = Referat.objects.get(refID=refID)
    
    if request.method == 'POST':
        form = ReferatForm(request.POST)
        if form.is_valid():
            referat.refName = form.cleaned_data['referat_name']
            referat.refZyklus = form.cleaned_data['referat_zyklus']
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
        'action':'EDIT', 
        'referat': referat,
        'form': form,
        'feedback': feedback,
        'fixed_footer': True
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
        'action':'DELETE', 
        'referat': referat,
        'form': form,
        'feedback': feedback,
        'fixed_footer': True
    })

# ------ Referatsverwaltung ------ #


# ++++++ Sitzungsverwaltung ++++++ #

def SitzungsverwaltungPage(request):
    sitzungen = Sitzung.objects.all().order_by('sitzDate')
    context = {'title': 'Sitzungsverwaltung', 'sitzungen': sitzungen, 'fixed_footer': True}
    return render(request, 'pages/intern/sitzungsverwaltung.html', context=context)


def SitzungAnlegenPage(request):
    return render(request, 'pages/intern/sitzung.html', context={'title': 'Sitzung anlegen'})


def SitzungAnzeigenPage(request, sitzID):
    antraege = Antrag.objects.filter(sitzID=sitzID)
    return render(request, 'pages/intern/sitzung.html', context={
        'title': 'Sitzung anzeigen',
        'antraege': antraege
    })


def SitzungVertagenPage(request, sitzID):
    return render(request, 'pages/intern/sitzung.html', context={'title': 'Sitzung vertagen'})


def SitzungLoeschenPage(request, sitzID):
    return render(request, 'pages/intern/sitzung.html', context={'title': 'Sitzung löschen'})

# ------ Sitzungsverwaltung ------ #


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
        'feedback': feedback, 
        'fixed_footer': True
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
        asteller.astellerVorname = form.cleaned_data['vorname']
        asteller.astellerName = form.cleaned_data['nachname']
        asteller.astellerEmail = astellerEmail
        asteller.save() 
    return asteller


# Prüfe, wann die nächste Sitzung des Referats stattfindet und gib diese zurück
# TODO: Prüfung auf Eilantrag einbauen & E-Mail an Referat senden
def checkSitzungen(form):
    refID = form.cleaned_data['referat']
    sitzungen = Sitzung.objects.filter(refID=refID).filter(sitzDate__gt=date.today()).order_by('sitzDate')
    return sitzungen


# Sende eine Bestätigungsmail an den Antragsteller
def sendConfirmationMail(asteller, antrag):
    send_mail(
        f"Dein { antrag.typID.typName } ist eingegeangen!",
        f"Hi { asteller.astellerVorname },\n\nDein Antrag ist bei uns eingegangen und wird in der nächsten Sitzung des Referats behandelt.\n\nViele Grüße,\nDein StuRa-Team",
        "abv@stura.htw-dresden.de",
        [asteller.astellerEmail],
        fail_silently=False,
    )   
    

# Kurzfassung der render-Funktion für Antragsseiten
def renderAntrag(request, title, form, feedback):
    return render(request, 'pages/antrag.html', context={
        'title': title, 
        'form': form,
        'feedback': feedback
    })

# ------ Funktionen ------ #


# ++++++ Anträge ++++++ #

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
            
            antrag.save()
            
            feedback.type='SUCCESS'
            feedback.text='Dein Antrag wurde erfolgreich eingereicht! Du erhältst in Kürze eine Bestätigungsmail.'
            
            sendConfirmationMail(asteller, antrag)
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
            feedback.text='Dein Antrag wurde erfolgreich eingereicht! Du erhältst in Kürze eine Bestätigungsmail.'
            
            sendConfirmationMail(asteller, antrag)
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
                        
            antrag.save()
            
            feedback.type='SUCCESS'
            feedback.text='Dein Antrag wurde erfolgreich eingereicht! Du erhältst in Kürze eine Bestätigungsmail.'
            
            sendConfirmationMail(asteller, antrag)
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
            feedback.text='Dein Antrag wurde erfolgreich eingereicht! Du erhältst in Kürze eine Bestätigungsmail.'
            
            sendConfirmationMail(asteller, antrag)
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
            feedback.text='Dein Antrag wurde erfolgreich eingereicht! Du erhältst in Kürze eine Bestätigungsmail.'
            
            sendConfirmationMail(asteller, antrag)
    else:
        form = AntragAmtForm()
    
    return renderAntrag(request, 'Antrag zur Wahl für Stelle/Amt', form, feedback)


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
            feedback.text='Dein Antrag wurde erfolgreich eingereicht! Du erhältst in Kürze eine Bestätigungsmail.'
            
            sendConfirmationMail(asteller, antrag)
    else:
        form = AntragAmtForm()
    
    return renderAntrag(request, 'Antrag zur Wahl für Stelle/Amt', form, feedback)

# ------ Anträge ------ #