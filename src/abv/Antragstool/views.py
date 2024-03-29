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
from .forms import ArchivSuchenForm, SitzungsverwaltungSuchenForm, AntragsverwaltungSuchenForm

from .mails import mailAstellerEingangsbestaetigung, mailAstellerVertagungAntrag, mailAstellerVertagungSitzung, mailAstellerErgebnisAntrag
from .mails import mailReferatAntragEingegangen

from .api import list_pads, create_pad, set_html


def generiere_abv_nummern_sitzung(sitzID):
    
    def berechne_legislatur_periode(date):
        """
        Berechnet die Legislaturperiode für ein gegebenes Datum. Gibt die Legislaturperiode sowie den Start- und Endzeitpunkt der Legislaturperiode zurück.
        """
        prev_year = date.year - 1
        current_year = date.year
        next_year = date.year + 1

        import datetime
        
        if date >= datetime.date(current_year, 9, 1):
            # Alles ab dem 1. September gehört zur nächsten Legislaturperiode
            periode_start = datetime.date(current_year, 9, 1)
            periode_ende = datetime.date(next_year, 8, 31)
            legislatur_periode = str(current_year) + "/" + str(next_year)
        else:
            # Alles vor dem 1. September gehört zur vorherigen Legislaturperiode
            periode_start = datetime.date(prev_year, 9, 1)
            periode_ende = datetime.date(current_year, 8, 31)
            legislatur_periode = str(prev_year) + "/" + str(current_year)

        return periode_start, periode_ende, legislatur_periode
    
    # Hole Sitzung
    sitzung = Sitzung.objects.get(sitzID=sitzID)
    
    # Berechne Legislaturperiode für Sitzung sowie Start- und Endzeitpunkt der Legislaturperiode
    periode_start, periode_ende, legislatur_periode = berechne_legislatur_periode(sitzung.sitzDate)
    
    # Filtere alle Sitzungen der Legislaturperiode
    sitzungen_referat = Sitzung.objects.filter(refID=sitzung.refID).filter(sitzDate__gte=periode_start).filter(sitzDate__lte=periode_ende).order_by('sitzDate')
    
    # Berechne die Sitzungsnummer
    sitzung_nummer_legislatur = 0
    for index, sitzung_referat in enumerate(sitzungen_referat, 1):
        if sitzung_referat.sitzID == sitzung.sitzID:
            sitzung_nummer_legislatur = index
            
    # Hole die Anträge der Sitzung
    antraege_sitzung = Antrag.objects.filter(sitzID=sitzung.sitzID).order_by('-prioritaet','erstelltDate')
    
    # Berechne die ABV-Nummer für jeden Antrag
    for index, antrag in enumerate(antraege_sitzung, 1):
        antrag.abvNummer = str(legislatur_periode) + "-" + str(sitzung_nummer_legislatur) + "-" + str(index)
        antrag.save()


def formFehlerAusgeben(request, form):
    for field_name, errors in form.errors.items():
        field = form.fields[field_name]
        error_messages = [f"{field.label} {error}" for error in errors]
        messages.warning(request, "\n".join(error_messages))

# ========== Hauptseiten ========== #

def HomePage(request):
    """ Gibt beim Aufruf die Home-Seite zurück.
        Zeige die Home-Seite an.
    """
    return render(request, 'pages/home.html', context={'title': 'Home'})


def ArchivPage(request):
    """ Gibt beim Aufruf die Archiv-Seite zurück.
        Zeige die Archivseite an und suche nach den Filtern.
    """
    form = ArchivSuchenForm(request.GET)
    
    if request.method == 'GET' and form.is_valid():
        suchbegriff = request.GET.get("q")
        antrags_typ = request.GET.get("atyp")
        datum_von = request.GET.get("dv")
        datum_bis = request.GET.get("db")
        
        # Filtere Anträge, sodass nur welche angezeigt werden, die einen Beschluss haben oder nicht vertagt wurden
        gefilterte_antraege = Antrag.objects.filter(
            beschlussID__isnull=False
            ).filter(
                ~Q(beschlussID__beschlussErgebnis="Vertagt")
            ).filter(
                Q(sitzID__sitzStatus="Stattgefunden")
            ).order_by('-erstelltDate')
        
        # Filtere Texte nach Suchbegriff
        if suchbegriff:
            gefilterte_antraege = gefilterte_antraege.filter(
                Q(antragTitel__icontains=suchbegriff) | Q(antragText__icontains=suchbegriff) | Q(antragGrund__icontains=suchbegriff) | Q(antragVorschlag__icontains=suchbegriff) | Q(antragVorstellungPerson__icontains=suchbegriff) | Q(antragFragenZumAmt__icontains=suchbegriff)
            )
        
        # Filtere nach Antragstyp, falls antrags_typ nicht None ist
        if antrags_typ:
            gefilterte_antraege = gefilterte_antraege.filter(typID=antrags_typ)
        
        # Filtere nach Datum, falls datum_von und/oder datum_bis nicht None sind
        if datum_von:
            # Konvertiere String in Date-Objekt
            datum_von = datetime.strptime(datum_von, '%d.%m.%Y').date()
            gefilterte_antraege = gefilterte_antraege.filter(erstelltDate__gte=datum_von)
            
        if datum_bis:
            datum_bis = datetime.strptime(datum_bis, '%d.%m.%Y').date()
            gefilterte_antraege = gefilterte_antraege.filter(erstelltDate__lte=datum_bis)
    else:
        gefilterte_antraege = Antrag.objects.filter(beschlussID__isnull=False).filter(~Q(beschlussID__beschlussErgebnis="Vertagt"))
        messages.debug(request, str([form.errors[field_name] for field_name in form.errors]))
            

    return render(request, 'pages/archiv.html', context={
        'title': 'Archiv',
        'antraege': gefilterte_antraege, #type: ignore
        'aktion': 'ANZEIGEN',
        'form': form
    })

# ========== Interner Bereich ========== #

# ++++++ Referatsverwaltung ++++++ #

def ReferatsverwaltungPage(request):
    """ Gibt beim Aufruf die Refaratsverwaltung-Seite zurück.
        Zeige die Referatsverwaltungsseite an.
    """
    referate = Referat.objects.all().order_by('refID')
    context = {'title': 'Referatsverwaltung', 'referate': referate}
    return render(request, 'pages/intern/referatsverwaltung.html', context=context)


def ReferatErstellenPage(request):
    """ Gibt beim Aufruf die ReferatErstellen-Seite zurück.
        Erstelle ein neues Referat.
    """
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
    """ Gibt beim Aufruf die ReferatBearbeiten-Seite für das ausgewählte Referat zurück.
        Bearbeite das ausgewählte Referat.
    
        refID:int
    """
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
    """ Gibt beim Aufruf die ReferatLöschen-Seite für das ausgewählte Referat zurück.
        Lösche das ausgewählte Referat.
        
        refID:int
    """
    referat = Referat.objects.get(refID=refID)

    if request.method == 'POST':
        # Prüfe, ob das Referat noch Anträge oder Sitzungen hat
        if Sitzung.objects.filter(refID=refID).exists():
            messages.error(request, 'Das Referat ' + referat.refName + ' kann nicht gelöscht werden, da ihm Sitzungen mit Anträgen zugewiesen sind!')
            return redirect('referat-loeschen', refID=refID)
        else:
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
    """ Gibt beim Aufruf die Sitzungsverwaltung-Seite für das ausgewählte Referat zurück.
        Zeige die Sitzungsverwaltungsseite an
    """
    # Alle Referate und Sitzugnen
    referate = Referat.objects.all().order_by('refID')
    
    # Alle Sitzungen, welche in 14+ Tagen stattfinden und nicht vertagt wurden
    sitzungen_14_tage = Sitzung.objects.all().filter(sitzDate__gt=date.today() + timedelta(days=7)).filter(~Q(sitzStatus="Vertagt")).order_by('sitzDate')
    referate_ohne_sitzung = []
    
    # Anzahl der Anträge pro Sitzung berechnen | Filtere Anträge, die vertagt wurden
    for sitzung in Sitzung.objects.all():
        anz_antraege = Antrag.objects.filter(sitzID=sitzung.sitzID).filter(~Q(beschlussID__beschlussErgebnis="Vertagt")).count()
        sitzung.anzAntraege = anz_antraege
        sitzung.save()
    
    # Prüfe, ob es Referate gibt, die in den nächsten 14 Tagen keine Sitzung haben
    for referat in referate:
        if referat.refID not in sitzungen_14_tage.values_list('refID', flat=True):
            referate_ohne_sitzung.append(referat)
           
            
    form = SitzungsverwaltungSuchenForm(request.GET)
    
    if request.method == 'GET' and form.is_valid():
        referat_id = request.GET.get("ref")
        sitzung_status = request.GET.get("s")
        datum_von = request.GET.get("dv")
        datum_bis = request.GET.get("db")
        
        # Alle Sitzungen
        gefilterte_sitzungen = Sitzung.objects.all().order_by('refID').order_by('sitzDate')
        
        # Filtere nach Referat, falls referat_id nicht None ist
        if referat_id and referat_id.isdigit():
            gefilterte_sitzungen = gefilterte_sitzungen.filter(refID=referat_id)
        
        # Filtere nach Sitzungsstatus, falls sitzung_status nicht None ist
        if sitzung_status:
            gefilterte_sitzungen = gefilterte_sitzungen.filter(sitzStatus=sitzung_status)
        else:
            gefilterte_sitzungen = gefilterte_sitzungen.filter(sitzStatus='Offen')
        
        # Filtere nach Datum, falls datum_von und/oder datum_bis nicht None sind
        if datum_von:
            # Konvertiere String in Date-Objekt
            datum_von = datetime.strptime(datum_von, '%d.%m.%Y').date()
            gefilterte_sitzungen = gefilterte_sitzungen.filter(sitzDate__gte=datum_von)
            
        if datum_bis:
            datum_bis = datetime.strptime(datum_bis, '%d.%m.%Y').date()
            gefilterte_sitzungen = gefilterte_sitzungen.filter(sitzDate__lte=datum_bis)
            
    else:
        # Alle offenen Sitzungen nach dem heutigen Datum
        gefilterte_sitzungen = Sitzung.objects.all().filter(sitzDate__gte=date.today()).filter(sitzStatus="Offen").order_by('refID').order_by('sitzDate')
        messages.debug(request, str([form.errors[field_name] for field_name in form.errors]))
        
    return render(request, 'pages/intern/sitzungsverwaltung.html', context={
        'title': 'Sitzungsverwaltung', 
        'sitzungen': gefilterte_sitzungen,
        'referate_ohne_sitzung': referate_ohne_sitzung,
        'form': form
    })


def SitzungAnlegenPage(request):
    """ Gibt beim Aufruf die SitzungsAnlegen-Seite für das ausgewählte Referat zurück.
        Lege eine Sitzung an.
    """
    referate = Referat.objects.all().order_by('refID')
    date = datetime.now().date() + timedelta(days=14)
    
    if request.method == 'POST':
        form = SitzungAnlegenForm(request.POST)
        if form.is_valid():
            sitzDate = form.cleaned_data['datum_sitzung']
            refID = form.cleaned_data['referat']
            
            # Prüfe, ob es bereits eine Sitzung vom gleichen Referat mit dem Datum gibt
            if Sitzung.objects.filter(sitzDate=sitzDate, refID=refID).exists():
                messages.error(request, 'Es gibt bereits eine Sitzung vom ' + sitzDate.strftime("%d.%m.%Y") + ' für das Referat ' + Referat.objects.get(refID=refID.refID).refName + '!')
                return redirect('sitzung-anlegen')
            else:
                sitzung = Sitzung(sitzDate=sitzDate, refID=refID)
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
    """ Gibt beim Aufruf die SitzungVerwalten-Seite für die ausgewählte Sitzung zurück.
        Verwalte die ausgewählte Sitzung.
    
        sitzID:int
    """
    sitzung = Sitzung.objects.get(sitzID=sitzID)
    
    # Leite Admin weiter, sollte die Sitzung vertagt worden sein
    if sitzung.sitzStatus == 'Vertagt':
        return redirect('sitzungsverwaltung')
    
    # Anzahl der Anlagen pro Antrag in Sitzung berechnen
    antraege = Antrag.objects.filter(sitzID=sitzID).order_by('-prioritaet','erstelltDate')
    for antrag in antraege:
        antrag.anzAnlagen = Anlage.objects.filter(antragID=antrag.antragID).count()
        antrag.save    

    return render(request, 'pages/intern/sitzung/verwalten.html', context={
        'title': 'Sitzung verwalten',
        'antraege': antraege,
        'sitzung': sitzung
    })


def SitzungVertagenPage(request, sitzID):
    """ Gibt beim Aufruf die SitzungVertagen-Seite für die ausgewählte Sitzung zurück.
        Vertage die Sitzung auf einen anderen Tag.

        sitzID:int
    """
    sitzung = Sitzung.objects.get(sitzID=sitzID)
    date = sitzung.sitzDate + timedelta(days=7)
    
    # Leite Admin weiter, sollte die Sitzung nicht mehr offen sein
    if sitzung.sitzStatus != 'Offen':
        return redirect('sitzungsverwaltung')
    
    if request.method == 'POST':
        form = SitzungVertagenForm(request.POST)
        if form.is_valid():
            if sitzung.sitzStatus == 'Stattgefunden':
                messages.error(request, 'Die Sitzung hat bereits stattgefunden und kann nicht mehr bearbeitet werden!')
                return redirect('sitzung-vertagen', sitzID=sitzID)
            
            altes_sitzDate = sitzung.sitzDate
            neues_sitzDate = form.cleaned_data['datum_neu']
            
            # Prüfe, ob das neue Datum nach dem alten Datum liegt
            if neues_sitzDate <= altes_sitzDate:
                messages.error(request, 'Das neue Datum muss nach dem alten Datum liegen!')
                return redirect('sitzung-vertagen', sitzID=sitzID)
            
            # Vertage die Sitzung mitsamt aller Antraäge
            sitzung.sitzDate = neues_sitzDate
            sitzung.save()
            
            # Erstelle Kopie der Sitzung, um die Vertagung nachvollziehen zu können
            sitzung.sitzID = None
            sitzung.sitzStatus = 'Vertagt'
            sitzung.sitzDate = altes_sitzDate
            sitzung.save()
            
            # Sende eine E-Mail an alle Antragsteller, dass die Sitzung vertagt wurde
            mailAstellerVertagungSitzung(sitzung=sitzung)

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
    """ Gibt beim Aufruf die SitzungLoeschenVertagen-Seite für die ausgewählte Sitzung zurück.
        Lösche die ausgewählte Sitzung.

        sitzID:int
    """
    # Prüfe, ob die Sitzung existiert
    if not Sitzung.objects.filter(sitzID=sitzID).exists():
        return redirect('sitzungsverwaltung')
    else:
        sitzung = Sitzung.objects.get(sitzID=sitzID)
        
    # Leite Admin weiter, sollte die Sitzung nicht mehr offen sein
    if sitzung.sitzStatus != 'Offen':
        return redirect('sitzungsverwaltung')
    
    if request.method == 'POST':
        # Prüfe, ob die Sitzung bereits stattgefunden hat
        if sitzung.sitzStatus == 'Stattgefunden':
            messages.error(request, 'Die Sitzung hat bereits stattgefunden und kann nicht mehr gelöscht werden!')
            return redirect('sitzungsverwaltung')
        
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
    """ Gibt beim Aufruf die SitzungAbschliessenVertagen-Seite für die ausgewählte Sitzung zurück.
        Schließe die Sitzung ab.

        sitzID:int
    """
    sitzung = Sitzung.objects.get(sitzID=sitzID)
    antraege_sitzung = Antrag.objects.filter(sitzID=sitzID).order_by('-prioritaet','erstelltDate')
    
    if request.method == 'POST':
        # Prüfe, ob die Sitzung bereits abgeschlossen wurde
        if sitzung.sitzStatus == 'Stattgefunden':
            messages.error(request, 'Die Sitzung wurde bereits abgeschlossen und kann nicht mehr bearbeitet werden!')
            return redirect('sitzung-abschliessen', sitzID=sitzID)
        
        # Prüfe, ob die Sitzung bereits stattgefunden hat (Datum)
        if sitzung.sitzDate > datetime.now().date():
            messages.error(request, 'Die Sitzung kann nicht abgeschlossen werden, da das Datum der Sitzung noch nicht vergangen ist!')
            return redirect('sitzung-abschliessen', sitzID=sitzID)
        
        # Prüfe, ob alle Anträge der Sitzung einen Beschluss haben oder vertagt wurden
        nicht_beschlossene_antraege = Antrag.objects.filter(sitzID=sitzID).filter(beschlussID__isnull=True).filter(~Q(beschlussID__beschlussErgebnis="Vertagt")).count()
        
        if nicht_beschlossene_antraege == 0:
            sitzung.sitzStatus = 'Stattgefunden'
            sitzung.save()
            
            # Schicke E-Mail an alle Antragsteller, ob ihr Antrag beschlossen oder vertagt wurde
            for i, antrag in enumerate(antraege_sitzung):
                if antrag.beschlussID is not None and antrag.beschlussID.beschlussErgebnis == 'Vertagt':
                    # Hole den vertagten Antrag über die neueSitzID
                    antrag_original = Antrag.objects.get(antragID=antrag.originaleAntragID)
                    mailAstellerVertagungAntrag(antrag_original)
                else:
                    mailAstellerErgebnisAntrag(antrag)
                    
                    # Generiere die ABV-Nummern für die Anträge
                    generiere_abv_nummern_sitzung(sitzung.sitzID)
            
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

def getFormVonAntragstyp(antrag, request):
    """ 
    Gibt auf Anfrage die TypID als Integer anhand des Antrag-Objekts zurück.
    """
    form = None
    typ_id = antrag.typID.typID
    if typ_id == 1:
        form = AntragAllgemeinForm(request.POST or None)
    elif typ_id == 2:
        form = AntragFinanziellForm(request.POST or None)
    elif typ_id == 3:
        form = AntragVeranstaltungForm(request.POST or None)
    elif typ_id == 4:
        form = AntragMitgliedForm(request.POST or None)
    elif typ_id == 5:
        form = AntragAmtForm(request.POST or None)
    elif typ_id== 6:
        form = AntragBenehmenForm(request.POST or None)
    return form


def AntragsverwaltungPage(request):
    """ Gibt beim Aufruf die Antragsverwaltung-Seite zurück.
        Zeige die Antragsverwaltungsseite an.
    """
    form = AntragsverwaltungSuchenForm(request.GET)
    
    if request.method == 'GET' and form.is_valid():
        suchbegriff = request.GET.get("q")
        beschluss = request.GET.get("b")
        antrags_typ = request.GET.get("atyp")
        datum_von = request.GET.get("dv")
        datum_bis = request.GET.get("db")
        
        # Filtere Anträge, sodass nur welche angezeigt werden, die einen Beschluss haben oder nicht vertagt wurden
        gefilterte_antraege = Antrag.objects.order_by('-erstelltDate')
        
        # Filtere Texte nach Suchbegriff
        if suchbegriff:
            gefilterte_antraege = gefilterte_antraege.filter(
                Q(antragTitel__icontains=suchbegriff) | 
                Q(antragText__icontains=suchbegriff) | 
                Q(antragGrund__icontains=suchbegriff) | 
                Q(antragVorschlag__icontains=suchbegriff) |
                Q(antragVorstellungPerson__icontains=suchbegriff) | 
                Q(antragFragenZumAmt__icontains=suchbegriff) | 
                Q(astellerID__astellerName__icontains=suchbegriff)
            )
            
        # Filtere nach Beschluss, falls beschluss nicht None ist
        if beschluss:
            if beschluss == 'Unbehandelt':
                gefilterte_antraege = gefilterte_antraege.filter(Q(beschlussID__isnull=True))
            else:
                gefilterte_antraege = gefilterte_antraege.filter(beschlussID__beschlussErgebnis=beschluss)
        
        # Filtere nach Antragstyp, falls antrags_typ nicht None ist
        if antrags_typ:
            gefilterte_antraege = gefilterte_antraege.filter(typID=antrags_typ)
        
        # Filtere nach Datum, falls datum_von und/oder datum_bis nicht None sind
        if datum_von:
            # Konvertiere String in Date-Objekt
            datum_von = datetime.strptime(datum_von, '%d.%m.%Y').date()
            gefilterte_antraege = gefilterte_antraege.filter(erstelltDate__gte=datum_von)
            
        if datum_bis:
            datum_bis = datetime.strptime(datum_bis, '%d.%m.%Y').date()
            gefilterte_antraege = gefilterte_antraege.filter(erstelltDate__lte=datum_bis)
    else:
        gefilterte_antraege = Antrag.objects.filter(~Q(beschlussID__beschlussErgebnis="Vertagt")).order_by('-erstelltDate')
        messages.debug(request, str([form.errors[field_name] for field_name in form.errors]))
    

    return render(request, 'pages/intern/antragsverwaltung.html', context={
        'title': 'Antragsverwaltung',
        'antraege': gefilterte_antraege,
        'form': form
    })
        

def AntragAnzeigenPage(request, antragID):
    """ Gibt beim Aufruf die AntragAnzeigen-Seite für den ausgewählten Antrag zurück.
        Zeige den ausgewählten Antrag an.

        antragID:int
    """
    antrag = Antrag.objects.get(antragID=antragID)
    anlagen = Anlage.objects.filter(antragID=antragID)
    return render(request, 'pages/antrag.html', context={
        'title': 'Antrag anzeigen',
        'antrag': antrag,
        'form': getFormVonAntragstyp(antrag, request),
        'aktion': 'ANZEIGEN',
        'anlagen': anlagen
    })


def AntragBearbeitenPage(request, antragID):
    """ Gibt beim Aufruf die AntragBearbeiten-Seite für den ausgewählten Antrag zurück.
        Bearbeite den jeweiligen Antrag.
    
        antragID:int
    """
    # TODO: Logik für Antrag bearbeiten einbauen
    antrag = Antrag.objects.get(antragID=antragID)
    form = getFormVonAntragstyp(antrag, request)
    
    if antrag.beschlussID:
        return redirect('antragsverwaltung')
    
    if request.method == 'POST':
        if form.is_valid():
            titel = form.cleaned_data.get('titel')
            antrag.antragTitel = titel
            text = form.cleaned_data.get('text')
            antrag.antragText = text
            
            if form.cleaned_data.get('grund'):
                grund = form.cleaned_data.get('grund')
                antrag.antragGrund = grund
                
            if form.cleaned_data.get('vorschlag'):
                vorschlag = form.cleaned_data.get('vorschlag')
                antrag.antragVorschlag = vorschlag
                
            if form.cleaned_data.get('vorstellung_person'):
                vorstellung_person = form.cleaned_data.get('vorstellung_person')
                antrag.antragVorstellungPerson = vorstellung_person
            
            if form.cleaned_data.get('fragen_amt'):
                fragen_amt = form.cleaned_data.get('fragen_amt')
                antrag.antragFragenZumAmt = fragen_amt
                
            if form.cleaned_data.get('verantwortlichkeit'):
                verantwortlichkeit = form.cleaned_data.get('verantwortlichkeit')
                antrag.antragVerantwortlichkeit = verantwortlichkeit
                
            if form.cleaned_data.get('zeitraum'):
                zeitraum = form.cleaned_data.get('zeitraum')
                antrag.antragZeitraum = zeitraum
                
            if form.cleaned_data.get('position'):
                position = form.cleaned_data.get('position')
                antrag.antragKostenposition = position
                
            if form.cleaned_data.get('summe'):
                summe = form.cleaned_data.get('summe')
                antrag.antragSumme = summe
                
            antrag.save()
            
            messages.success(request, 'Der Antrag wurde erfolgreich bearbeitet.')
            return redirect('antrag-bearbeiten', antragID=antragID)
        else:
            print('Formular ist nicht valide')
            formFehlerAusgeben(request, form)
    
    return render(request, 'pages/antrag.html', context={
        'title': 'Antrag bearbeiten',
        'antrag': antrag,
        'form': form,
        'aktion': 'BEARBEITEN'
    })


def AntragLoeschenPage(request, antragID):
    """ Gibt beim Aufruf die AntragLoeschen-Seite für den ausgewählten Antrag zurück.
        Lösche den ausgewählten Antrag.
    
        antragID:int
    """
    antrag = Antrag.objects.get(antragID=antragID)
    return render(request, 'pages/intern/antrag/loeschen.html', context={
        'title': 'Antrag löschen',
        'antrag': antrag,
        'form': getFormVonAntragstyp(antrag, request),
        'aktion': 'LOESCHEN'
    })
    

def AntragVertagenPage(request, antragID):
    """ Gibt beim Aufruf die AntragVertagen-Seite für den ausgewählten Antrag zurück.
        Vertage den ausgewählten Antrag in eine andere Sitzung.

        antragID:int
    """
    antrag = Antrag.objects.get(antragID=antragID)
    sitzung = Sitzung.objects.get(sitzID=antrag.sitzID.sitzID)
    
    # Leite Admin weiter, sollte der Antrag vertagt worden sein
    if antrag.wurdeVertagt or antrag.beschlussID is not None:
        return redirect('sitzung-verwalten', sitzID=sitzung.sitzID)
    
    if request.method == 'POST':
        form = AntragVertagenForm(request.POST)
        # Prüfe, on der Antrag bereits einen Beschluss hat
        if antrag.beschlussID is not None or antrag.wurdeVertagt is True:
            messages.error(request, 'Der Antrag konnte nicht vertagt werden, da er bereits einen Beschluss hat oder bereits vertagt wurde!')
            return redirect('antrag-vertagen', antragID=antragID)
        elif form.is_valid():
            alte_sitzID = antrag.sitzID
            neue_sitzID = form.cleaned_data['sitzung']
            originale_antragID = antrag.antragID
            
            # Prüfe, ob die Sitzung die Gleiche ist
            if alte_sitzID == neue_sitzID:
                messages.error(request, 'Der Antrag konnte nicht vertagt werden, da die Sitzung die gleiche ist!')
                return redirect('antrag-vertagen', antragID=antragID)
            
            # Prüfe, ob die Sitzung bereits stattgefunden hat oder vertagt wurde
            neue_sitzung = Sitzung.objects.get(sitzID=neue_sitzID.sitzID)
            if neue_sitzung.sitzStatus == 'Stattgefunden' or neue_sitzung.sitzStatus == 'Vertagt':
                messages.error(request, 'Der Antrag konnte nicht vertagt werden, da die Sitzung bereits stattgefunden hat oder vertagt wurde!')
                return redirect('antrag-vertagen', antragID=antragID)
            
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
            antrag.originaleAntragID = originale_antragID
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
    """ Gibt beim Aufruf die AntragBeschliesse-Seite für den ausgewählten Antrag zurück.
        Beschließe den ausgewählten Antrag.

        antragID:int
    """
    antrag = Antrag.objects.get(antragID=antragID)
    sitzung = Sitzung.objects.get(sitzID=antrag.sitzID.sitzID)
    
    # Prüfe, ob der Antrag vertagt wurde; Dies soll verhindert werden, da der Beschluss für eine Vertagung automatisch erstellt wird
    if antrag.beschlussID is not None and antrag.wurdeVertagt is True:
        return redirect('sitzung-verwalten', sitzID=sitzung.sitzID)
    
    
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
    """ Gibt beim Aufruf die SitzungVerwalten-Seite zurück.
        Erhöht die Priorität den ausgewählten Antrag.

        antragID:int
    """
    antrag = Antrag.objects.get(antragID=antragID)
    sitzung = Sitzung.objects.get(sitzID=antrag.sitzID.sitzID)
    
    # Leite Admin weiter, sollte der Antrag vertagt worden sein oder bereits einen Beschluss haben
    if antrag.wurdeVertagt or antrag.beschlussID is not None:
        return redirect('sitzung-verwalten', sitzID=sitzung.sitzID)
    
    hoechste_prioritaet = Antrag.objects.filter(sitzID=sitzung).aggregate(Max('prioritaet'))['prioritaet__max']
    antrag.prioritaet = hoechste_prioritaet + 1
    antrag.save()
        
    return redirect('sitzung-verwalten', sitzID=sitzung.sitzID)
    
# ------ Antragsverwaltung ------ #



# ++++++ Benutzerauthentifizierung ++++++ #

def LoginPage(request):
    """ Gibt beim Aufruf die Login-Seite zurück.
        Anmeldung als Antragverwalter.
    """
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
    """ Gibt beim Aufruf die Logout-Seite zurück.
        Abmeldung als Antragverwalter.
    """
    logout(request)
    return redirect('index')

# ------ Benutzerauthentifizierung ------ #



# ========== Antragsseiten ========== #

# ++++++ Funktionen ++++++ #

def astellerAbfragenOderErstellen(form):
    """Prüfe, ob der Antragsteller bereits in der Datenbank existiert und gib diesen zurück."""
    astellerEmail = form.cleaned_data['email']
    if Antragssteller.objects.filter(astellerEmail=astellerEmail).exists():
        asteller = Antragssteller.objects.get(astellerEmail=astellerEmail)
    else:
        asteller = Antragssteller()
        asteller.astellerName = form.cleaned_data['name']
        asteller.astellerEmail = astellerEmail
        asteller.save() 
    return asteller


def sitzungenAbfragen(form):
    """Prüfe, wann die nächste Sitzung des Referats stattfindet und gib diese zurück."""
    refID = form.cleaned_data['referat']
    sitzungen = []
    
    # Prüfe, ob es sich um einen Eilantrag handelt und gebe entsprechende Sitzungen zurück
    if form.cleaned_data['ist_eilantrag']:
        sitzungen = Sitzung.objects.filter(refID=refID).filter(sitzDate__gt=date.today()).filter(~Q(sitzStatus="Vertagt")).order_by('sitzDate')
    else:
        sitzungen = Sitzung.objects.filter(refID=refID).filter(sitzDate__gt=date.today() + timedelta(days=7)).filter(~Q(sitzStatus="Vertagt")).order_by('sitzDate')
        
    return sitzungen


def renderAntrag(request, title, form, antragstyp):
    """Kurzfassung der render-Funktion für Antragsseiten."""
    # Abfrage der nächsten Sitzungen, für die der Antrag fristgerecht eingereicht werden kann (< 7 Tage)
    sitzungen_fristgerecht = Sitzung.objects.filter(sitzDate__gt=date.today() + timedelta(days=7)).filter(~Q(sitzStatus="Vertagt")).order_by('sitzDate')
    
    # Abfrage der nächsten Sitzungen, für die der Antrag als Eilantrag eingereicht werden kann (>= 7 Tage)
    sitzungen_eilantrag = Sitzung.objects.filter(sitzDate__gt=date.today()).filter(~Q(sitzStatus="Vertagt")).order_by('sitzDate')   
    
    return render(request, 'pages/antrag.html', context={
        'title': title, 
        'form': form,
        'sitzungen_fristgerecht': sitzungen_fristgerecht,
        'sitzungen_eilantrag': sitzungen_eilantrag,
        'antragstyp': antragstyp
    })


def anlagenSpeichern(request, antrag):
    """Speichert die Anlagen vom Antrag."""
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

FEEDBACK_ANTRAG_SUCCESS = 'Dein Antrag wurde erfolgreich eingereicht! Du erhältst in Kürze eine E-Mail mit der Eingangsbestätigung.'

def AntragAllgemein(request):
    """Erstellt einen Antrag ohne finanzielle Mittel"""
    # Definiere den Antragstyp anhand der Slug
    antragstyp = Antragstyp.objects.get(typSlug='antrag-ohne-finanzielle-mittel')
            
    if request.method == 'POST':
        form = AntragAllgemeinForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = sitzungenAbfragen(form)
            if sitzungen.count() == 0:
                messages.error(request, 'Es wurde keine Sitzung des Referates gefunden, zu der der Antrag eingereicht werden kann. Bitte wähle ein anderes Referat aus.')
                return redirect('antrag-allgemein')
            
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
            
            mailAstellerEingangsbestaetigung(antrag)
            mailReferatAntragEingegangen(antrag)
            
            messages.success(request, FEEDBACK_ANTRAG_SUCCESS)
            return redirect('antrag-allgemein')
        else:
            messages.error(request, 'Dein Antrag konnte nicht abgeschickt werden. Bitte beachte die nachfolgenden Fehler.')
            formFehlerAusgeben(request, form)
            return redirect('antrag-allgemein')
    else:
        form = AntragAllgemeinForm(request.GET)

    return renderAntrag(request, 'Allgemeiner Antrag', form, antragstyp)


def AntragFinanziell(request):
    """Erstellt einen Antrag mit finanziellen Mitteln"""
    # Definiere den Antragstyp anhand der Slug
    antragstyp = Antragstyp.objects.get(typSlug='antrag-mit-finanziellen-mitteln')
    
    if request.method == 'POST':
        form = AntragFinanziellForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = sitzungenAbfragen(form)
            if sitzungen.count() == 0:
                messages.error(request, 'Es wurde keine Sitzung des Referates gefunden, zu der der Antrag eingereicht werden kann. Bitte wähle ein anderes Referat aus.')
                return redirect('antrag-allgemein')
            
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
            
            anlagen = anlagenSpeichern(request, antrag)
            if(len(anlagen) == 0):
                messages.error(request, 'Bitte füge eine Kostenaufstellung als Anlage bei!')
                return redirect('antrag-finanziell')
            
            mailAstellerEingangsbestaetigung(antrag)
            mailReferatAntragEingegangen(antrag)
            
            messages.success(request, FEEDBACK_ANTRAG_SUCCESS)
            return redirect('antrag-finanziell')
        else:
            messages.error(request, 'Dein Antrag konnte nicht abgeschickt werden. Bitte beachte die nachfolgenden Fehler.')
            formFehlerAusgeben(request, form)
            return redirect('antrag-finanziell')
    else:
        form = AntragFinanziellForm()
    
    return renderAntrag(request, 'Antrag mit finanziellen Mitteln', form, antragstyp)


def AntragVeranstaltung(request):
    """Erstellt einen Antrag für Veranstaltungen"""
    # Definiere den Antragstyp anhand der Slug
    antragstyp = Antragstyp.objects.get(typSlug='antrag-fuer-veranstaltungen')
            
    if request.method == 'POST':
        form = AntragVeranstaltungForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = sitzungenAbfragen(form)
            if sitzungen.count() == 0:
                messages.error(request, 'Es wurde keine Sitzung des Referates gefunden, zu der der Antrag eingereicht werden kann. Bitte wähle ein anderes Referat aus.')
                return redirect('antrag-allgemein')
            
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
            
            mailAstellerEingangsbestaetigung(antrag)
            mailReferatAntragEingegangen(antrag)
            
            messages.success(request, FEEDBACK_ANTRAG_SUCCESS)
            return redirect('antrag-veranstaltung')
        else:
            messages.error(request, 'Dein Antrag konnte nicht abgeschickt werden. Bitte beachte die nachfolgenden Fehler.')
            formFehlerAusgeben(request, form)
            return redirect('antrag-veranstaltung')
    else:
        form = AntragVeranstaltungForm()
    
    return renderAntrag(request, 'Antrag für Veranstaltungen', form, antragstyp)


def AntragMitglied(request):
    """Erstellt einen Antrag auf Beratendes Mitglied"""
    # Definiere den Antragstyp anhand der Slug
    antragstyp = Antragstyp.objects.get(typSlug='beratendes-mitglied')
    
    if request.method == 'POST':
        form = AntragMitgliedForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = sitzungenAbfragen(form)
            if sitzungen.count() == 0:
                messages.error(request, 'Es wurde keine Sitzung des Referates gefunden, zu der der Antrag eingereicht werden kann. Bitte wähle ein anderes Referat aus.')
                return redirect('antrag-allgemein')
            
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
            
            mailAstellerEingangsbestaetigung(antrag)
            mailReferatAntragEingegangen(antrag)
                        
            messages.success(request, FEEDBACK_ANTRAG_SUCCESS)
            return redirect('antrag-mitglied')
        else:
            messages.error(request, 'Dein Antrag konnte nicht abgeschickt werden. Bitte beachte die nachfolgenden Fehler.')
            formFehlerAusgeben(request, form)
            return redirect('antrag-mitglied')
    else:
        form = AntragMitgliedForm()
    
    return renderAntrag(request, 'Antrag zum beratenden MItglied', form, antragstyp)


def AntragAmt(request):
    """Erstellt einen Antrag auf Wahl auf Amt"""
    # Definiere den Antragstyp anhand der Slug
    antragstyp = Antragstyp.objects.get(typSlug='wahl-auf-stelle-oder-amt')
    
    if request.method == 'POST':
        form = AntragAmtForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = sitzungenAbfragen(form)
            if sitzungen.count() == 0:
                messages.error(request, 'Es wurde keine Sitzung des Referates gefunden, zu der der Antrag eingereicht werden kann. Bitte wähle ein anderes Referat aus.')
                return redirect('antrag-allgemein')
            
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
            
            mailAstellerEingangsbestaetigung(antrag)
            mailReferatAntragEingegangen(antrag)
                        
            messages.success(request, FEEDBACK_ANTRAG_SUCCESS)
            return redirect('antrag-amt')
        else:
            messages.error(request, 'Dein Antrag konnte nicht abgeschickt werden. Bitte beachte die nachfolgenden Fehler.')
            formFehlerAusgeben(request, form)
            return redirect('antrag-amt')
    else:
        form = AntragAmtForm()
    
    return renderAntrag(request, 'Antrag zur Wahl auf Stelle/Amt', form, antragstyp)


def AntragBenehmen(request):
    """Erstellt einen Antrag auf Herstellung des Benehmens"""
    # Definiere den Antragstyp anhand der Slug
    antragstyp = Antragstyp.objects.get(typSlug='herstellung-des-benehmens')
    
    if request.method == 'POST':
        form = AntragBenehmenForm(request.POST, request.FILES)
        if form.is_valid():
            # Prüfe, ob/wann die nächste Sitzung des Referats stattfindet
            sitzungen = sitzungenAbfragen(form)
            if sitzungen.count() == 0:
                messages.error(request, 'Es wurde keine Sitzung des Referates gefunden, zu der der Antrag eingereicht werden kann. Bitte wähle ein anderes Referat aus.')
                return redirect('antrag-allgemein')
            
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
            
            mailAstellerEingangsbestaetigung(antrag)
            mailReferatAntragEingegangen(antrag)
                        
            messages.success(request, FEEDBACK_ANTRAG_SUCCESS)
            return redirect('antrag-benehmen')
        else:
            messages.error(request, 'Dein Antrag konnte nicht abgeschickt werden. Bitte beachte die nachfolgenden Fehler.')
            formFehlerAusgeben(request, form)
            return redirect('antrag-benehmen')
    else:
        form = AntragBenehmenForm()
    
    return renderAntrag(request, 'Antrag auf Herstellung des Benehmens', form, antragstyp)

# ------ Anträge ------ #



# ++++++ Tagesordnung ++++++ #

def TagesordnungVorschauPage(request, sitzID):
    """ Zeigt die Tagesordnungsvorschau Seite für die ausgewählt Sitzung
        
        sitzID:int
    """
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
    """ Zeigt die TagesordnungErstellen Seite für die ausgewählt Sitzung.
        Erstellt die Tagesordnung in der Reihenfolge der Priorität und das dazugehörtige Etherpad.
        
        sitzID:int
    """
    sitzung = Sitzung.objects.get(sitzID=sitzID)
    antraege = Antrag.objects.filter(sitzID=sitzID).order_by('-prioritaet','erstelltDate')
    
    # Prüfe, ob die Sitzung bereits stattgefunden hat
    if sitzung.sitzStatus == 'Stattgefunden':
        messages.error(request, 'Die Sitzung hat bereits stattgefunden. Die Tagesordnung kann nicht mehr bearbeitet werden.')
        return redirect('tagesordnung-vorschau', sitzID=sitzID)
    
    # TODO: Sitzungsnummer automatisch generieren lassen
    sitzung_nummer = str(sitzung.sitzID)
    
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