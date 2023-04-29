# authentication/forms.py
from django import forms

# template for custom login form
class LoginForm(forms.Form):
    username = forms.CharField(label="Benutzername", max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'mb-3'}))
    password = forms.CharField(label="Passwort", max_length=100, required=True, widget=forms.PasswordInput)
    
    
# TODO: Referate aus DB laden
REFERATE = [
    (1, 'Finanzen'), (2, 'Hochschulpolitik'), (3, 'Internationales'), (4, 'Kultur'), (5, 'Öffentlichkeitsarbeit'), (6, 'Personal'), 
    (7, 'Qualitätsmanagement'), (8, 'Soziales'), (9, 'Sport'), (10, 'stud. Selbstverwaltung & Organisation'), (11, 'Studium')
]


class StammdatenForm(forms.Form):
    referat = forms.ChoiceField(widget=forms.RadioSelect, choices=REFERATE)
    
    vorname = forms.CharField(label="Vorname", max_length=100, required=True, widget=forms.TextInput())
    nachname = forms.CharField(label="Nachname", max_length=100, required=True, widget=forms.TextInput())
    email = forms.EmailField(label="E-Mail Adresse", max_length=100, required=True, widget=forms.EmailInput())
    
    titel = forms.CharField(label="Antragstitel", max_length=100, required=True, widget=forms.TextInput())
    text = forms.CharField(label="Antragstext", max_length=1000, required=True, widget=forms.Textarea())
    
    anlagen = forms.FileField(label="Anlagen", widget=forms.ClearableFileInput(attrs={"multiple": True}))
    
# Wiederholende Felder
grund_feld = forms.CharField(label="Begründung zum Antrag", max_length=500, required=True, widget=forms.Textarea())
vorschlag_feld = forms.CharField(label="Vorschlag zum weiteren Verfahren", max_length=500, required=True, widget=forms.Textarea())
positions_feld = forms.CharField(label="Kostenposition im Haushaltsplan", max_length=100, required=True, widget=forms.TextInput())
vorstellung_person_feld = forms.CharField(label="Vorstellung der Person", max_length=2000, required=True, widget=forms.Textarea())
    
    
    
class AntragAllgemeinForm(StammdatenForm):
    grund = grund_feld
    vorschlag = vorschlag_feld


class AntragFinanziellForm(StammdatenForm):
    grund = grund_feld
    position = positions_feld
    vorschlag = vorschlag_feld


class AntragVeranstaltungForm(StammdatenForm):
    grund = grund_feld
    position = positions_feld
    verantwortlichkeit = forms.CharField(label="Verantwortlichkeit für Nachbearbeitung", max_length=100, required=True, widget=forms.TextInput())
    zeitraum = forms.CharField(label="Zeitraum für Nachbearbeitung", max_length=100, required=True, widget=forms.TextInput())
    vorschlag = vorschlag_feld


# TODO: Vorstellung der Person: Details über benötigte Punkte anzeigen lassen
class AntragMitgliedForm(StammdatenForm):
    vorstellung_person = vorstellung_person_feld


# TODO: Vorstellung der Person/Allgemeine Fragen: Details über benötigte Punkte anzeigen lassen
class AntragAmtForm(StammdatenForm):
    ist_mitglied = forms.BooleanField(label="Bist du bereits ein StuRa Mitglied? (Leer für Nein)", required=True)
    vorstellung_person = vorstellung_person_feld
    fragen_amt = forms.CharField(label="Allgemeine Fragen zum beworbenen Amt", max_length=1000, required=True, widget=forms.Textarea())


class AntragBenehmenForm(StammdatenForm):
    grund = grund_feld
    vorschlag = vorschlag_feld
    