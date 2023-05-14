from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .models import Referat, Sitzung, Antrag, Antragssteller, Antragstyp
from .forms import LoginForm, AntragAllgemeinForm, AntragFinanziellForm, AntragVeranstaltungForm, AntragMitgliedForm, AntragAmtForm, AntragBenehmenForm
from datetime import date

def AppHome(request):
    return render(request, 'pages/home.html', context={'title': 'Home'})


def LoginPage(request):
    # redirect if user is already logged in
    if request.user.is_authenticated:
        return redirect('index')
    
    form = LoginForm()
    msg = ''
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
                msg = 'Die eingegebenen Daten sind ungültig! Versuche es erneut.'
              
    return render(
        request, 'pages/login.html', context={'title': 'Anmelden', 'form': form, 'msg': msg, 'fixed_footer': True}
    )
    
    
def LogoutPage(request):
    logout(request)
    return redirect('index')


def ReferatListe(request):
    referate = Referat.objects.all()
    return render(
        request,
        'Antragstool/referate.html',
        {
            'referate': referate
        }
    )


def SitzungenVonReferat(request, sitzid):
    sitzungen = Sitzung.objects.filter(refID=sitzid)
    return render(
        request,
        'Antragstool/sitzungen.html',
        {
            'sitzungen': sitzungen
        }
    )


def AntraegeVonSitzung(request, sitzid):
    antraege = Antrag.objects.filter(sitzID=sitzid)
    sitzung = Sitzung.objects.get(sitzID=sitzid)
    return render(
        request,
        'Antragstool/antraege.html',
        {
            'antraege': antraege,
            'sitzung': sitzung
        }
    )



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
def checkSitzungen(form):
    refID = form.cleaned_data['referat']
    sitzungen = Sitzung.objects.filter(refID=refID).filter(sitzDate__gt=date.today()).order_by('sitzDate')
    return sitzungen


def AntragAllgemein(request):
    msg=''
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
            
            antrag.antragGrund = form.cleaned_data['grund']
            antrag.antragVorschlag = form.cleaned_data['vorschlag']
            
            antrag.save()
            
            msg='Dein Antrag wurde erfolgreich eingereicht!'
            
    return render(request, 'pages/antrag.html', context={
        'title': 'Allgemeiner Antrag',
        'form': AntragAllgemeinForm(),
        'msg': msg
    })



def AntragFinanziell(request):
    msg=''
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
            
            antrag.antragGrund = form.cleaned_data['grund']
            antrag.antragKostenposition = form.cleaned_data['position']
            antrag.antragSumme = form.cleaned_data['summe']
            antrag.antragVorschlag = form.cleaned_data['vorschlag']
                        
            antrag.save()
            
            msg='Dein Antrag wurde erfolgreich eingereicht!'
    
    return render(request, 'pages/antrag.html', context={
        'title': 'Antrag mit finanzellen Mitteln',
        'form': AntragFinanziellForm(),
        'msg': msg
    })
    
    
    
def AntragVeranstaltung(request):
    msg=''
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
            
            antrag.antragGrund = form.cleaned_data['grund']
            antrag.antragKostenposition = form.cleaned_data['position']
            antrag.antragSumme = form.cleaned_data['summe']
            antrag.antragVerantwortlichkeit = form.cleaned_data['verantwortlichkeit']
            antrag.antragZeitraum = form.cleaned_data['zeitraum']
            antrag.antragVorschlag = form.cleaned_data['vorschlag']
                        
            antrag.save()
            
            msg='Dein Antrag wurde erfolgreich eingereicht!'
            
    return render(request, 'pages/antrag.html', context={
        'title': 'Antrag für eine Veranstaltung',
        'form': AntragVeranstaltungForm(),
        'msg': msg
    })



def AntragMitglied(request):
    msg=''
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
            
            antrag.antragVorstellungPerson = form.cleaned_data['vorstellung_person']
                        
            antrag.save()
            
            msg='Dein Antrag wurde erfolgreich eingereicht!'
            
    return render(request, 'pages/antrag.html', context={
        'title': 'Antrag auf beratenes Mitglied',
        'form': AntragMitgliedForm,
        'msg': msg
    })
    


def AntragAmt(request):
    msg=''
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
            
            antrag.antragVorstellungPerson = form.cleaned_data['vorstellung_person']
            antrag.antragFragenZumAmt = form.cleaned_data['fragen_amt']
                        
            antrag.save()
            
            msg='Dein Antrag wurde erfolgreich eingereicht!'
            
    return render(request, 'pages/antrag.html', context={
        'title': 'Antrag auf Stelle/Amt',
        'form': AntragAmtForm,
        'msg': msg
    })



def AntragBenehmen(request):
    msg=''
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
            
            antrag.antragGrund = form.cleaned_data['grund']
            antrag.antragVorschlag = form.cleaned_data['vorschlag']
            
            antrag.save()
            
            msg='Dein Antrag wurde erfolgreich eingereicht!'
            
    return render(request, 'pages/antrag.html', context={
        'title': 'Antrag auf Herstellung des Benehmens',
        'form': AntragBenehmenForm,
        'msg': msg
    })