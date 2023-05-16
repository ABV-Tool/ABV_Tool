# authentication/forms.py
from django import forms
from Antragstool.models import Referat
from djmoney.models.fields import MoneyField
from djmoney.money import Currency

# template for custom login form
class LoginForm(forms.Form):
    username = forms.CharField(label="Benutzername", max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'mb-3'}))
    password = forms.CharField(label="Passwort", max_length=100, required=True, widget=forms.PasswordInput)
    

# Referate aus DB laden
referate_db = Referat.objects.all()
REFERATE = [(entry.refID, entry.refName) for entry in referate_db]

class StammdatenForm(forms.Form):
    referat = forms.ChoiceField(widget=forms.RadioSelect, choices=REFERATE)
    
    vorname = forms.CharField(label="Vorname", max_length=100, required=True, widget=forms.TextInput())
    nachname = forms.CharField(label="Nachname", max_length=100, required=True, widget=forms.TextInput())
    email = forms.EmailField(label="E-Mail Adresse", max_length=200, required=True, widget=forms.EmailInput())
    
    titel = forms.CharField(label="Antragstitel", max_length=200, required=True, widget=forms.TextInput())
    text = forms.CharField(label="Antragstext", max_length=2000, required=True, widget=forms.Textarea())
    
    ist_eilantrag = forms.BooleanField(label="Eilantrag", required=False)
    
    # TODO: Unterstützung für mehrere Dateien einbinden
    anlagen = forms.FileField(label="Anlagen", required=False)
    

# Wiederholende Felder
grund_feld = forms.CharField(label="Begründung zum Antrag", max_length=1000, required=True, widget=forms.Textarea())
vorschlag_feld = forms.CharField(label="Vorschlag zum weiteren Verfahren", max_length=1000, required=True, widget=forms.Textarea())
positions_feld = forms.CharField(label="Kostenposition im Haushaltsplan", max_length=100, required=True, widget=forms.TextInput())
summe_feld = forms.DecimalField(label="Summe", max_digits=10, decimal_places=2, required=True, widget=forms.NumberInput())
vorstellung_person_feld = forms.CharField(label="Vorstellung der Person", max_length=2000, required=True, widget=forms.Textarea())
    
    
class AntragAllgemeinForm(StammdatenForm):
    grund = grund_feld
    vorschlag = vorschlag_feld


class AntragFinanziellForm(StammdatenForm):
    grund = grund_feld
    position = positions_feld
    summe = summe_feld
    vorschlag = vorschlag_feld


class AntragVeranstaltungForm(StammdatenForm):
    grund = grund_feld
    position = positions_feld
    summe = summe_feld
    verantwortlichkeit = forms.CharField(label="Verantwortlichkeit für Nachbearbeitung", max_length=100, required=True, widget=forms.TextInput())
    zeitraum = forms.CharField(label="Zeitraum für Nachbearbeitung", max_length=100, required=True, widget=forms.TextInput())
    vorschlag = vorschlag_feld


# TODO: Vorstellung der Person: Details über benötigte Punkte anzeigen lassen
class AntragMitgliedForm(StammdatenForm):
    vorstellung_person = vorstellung_person_feld


# TODO: Vorstellung der Person/Allgemeine Fragen: Details über benötigte Punkte anzeigen lassen
class AntragAmtForm(StammdatenForm):
    ist_mitglied = forms.BooleanField(label="Bist du bereits ein StuRa Mitglied? (Leer für Nein)", required=False, widget=forms.CheckboxInput())
    vorstellung_person = vorstellung_person_feld
    fragen_amt = forms.CharField(label="Allgemeine Fragen zum beworbenen Amt", max_length=1000, required=True, widget=forms.Textarea())


class AntragBenehmenForm(StammdatenForm):
    grund = grund_feld
    vorschlag = vorschlag_feld
    