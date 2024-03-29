from django import forms
from django.utils import timezone
from Antragstool.models import Referat, Beschluss, Sitzung, Antragstyp



class MultipleFileInput(forms.ClearableFileInput):
    
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    """ Datei-Upload-Handler
    
        https://docs.djangoproject.com/en/4.2/topics/http/file-uploads/#uploading-multiple-files
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class LoginForm(forms.Form):
    """Template for custom Login Form"""
    username = forms.CharField(label="Benutzername:", max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'mb-3'}))
    password = forms.CharField(label="Passwort:", max_length=100, required=True, widget=forms.PasswordInput)



class StammdatenForm(forms.Form):
    """Felder, die jeder Antrag besitzt"""
    referat = forms.ModelChoiceField(label="An wen ist der Antrag gerichtet?:", queryset=Referat.objects.all().order_by('refID'), required=True, empty_label="Bitte wählen...")
    
    name = forms.CharField(label="Name / Stelle:", max_length=100, required=True, widget=forms.TextInput())
    email = forms.EmailField(label="Kontakt E-Mail-Adresse:", max_length=200, required=True, widget=forms.EmailInput())
    
    titel = forms.CharField(label="Antragstitel:", max_length=100, required=True, widget=forms.TextInput())
    text = forms.CharField(label="Antragstext:", max_length=5000, required=True, widget=forms.Textarea())
    
    ist_eilantrag = forms.BooleanField(label="Ist dies ein Eilantrag?:", required=False)
    
    anlagen = MultipleFileField(label="Anlagen:", required=False)


    
# Wiederholende Felder
grund_feld = forms.CharField(label="Begründung zum Antrag:", max_length=1000, required=True, widget=forms.Textarea())
vorschlag_feld = forms.CharField(label="Vorschlag zum weiteren Verfahren:", max_length=1000, required=True, widget=forms.Textarea())
positions_feld = forms.CharField(label="Kostenposition im Haushaltsplan:", max_length=100, required=True, widget=forms.TextInput())
summe_feld = forms.DecimalField(label="Summe [€]:", max_digits=10, decimal_places=2, required=True, widget=forms.NumberInput())
vorstellung_person_feld = forms.CharField(label="Vorstellung der Person:", max_length=5000, required=True, widget=forms.Textarea())
    
    
class AntragAllgemeinForm(StammdatenForm):
    """Felder, die Antrag ohne finanzielle Mittel besitzt"""
    grund = grund_feld
    vorschlag = vorschlag_feld


class AntragFinanziellForm(StammdatenForm):
    """Felder, die Antrag mit finanziellen Mitteln besitzt"""
    grund = grund_feld
    position = positions_feld
    summe = summe_feld
    vorschlag = vorschlag_feld
    
    # Unterstützung für Komma in Summe
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['summe'].localize = True
        self.fields['summe'].widget.is_localized = True


class AntragVeranstaltungForm(StammdatenForm):
    """Felder, die Antrag für Veranstaltungen besitzt"""
    grund = grund_feld
    position = positions_feld
    summe = summe_feld
    verantwortlichkeit = forms.CharField(label="Verantwortlichkeit für Nachbearbeitung:", max_length=100, required=True, widget=forms.TextInput())
    zeitraum = forms.CharField(label="Zeitraum für Nachbearbeitung:", max_length=100, required=True, widget=forms.TextInput())
    vorschlag = vorschlag_feld
    
    # Unterstützung für Komma in Summe
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['summe'].localize = True
        self.fields['summe'].widget.is_localized = True


class AntragMitgliedForm(StammdatenForm):
    """Felder, die Antrag für Beratendes Mitglied besitzt"""
    vorstellung_person = vorstellung_person_feld


class AntragAmtForm(StammdatenForm):
    """Felder, die Antrag für Wahl auf Amt besitzt"""
    ist_mitglied = forms.BooleanField(label="Bist du bereits ein StuRa Mitglied? (Leer für Nein):", required=False, widget=forms.CheckboxInput())
    vorstellung_person = vorstellung_person_feld
    fragen_amt = forms.CharField(label="Allgemeine Fragen zum Amt:", max_length=5000, required=True, widget=forms.Textarea())


class AntragBenehmenForm(StammdatenForm):
    """Felder, die Antrag für Herstellung des Benehmens besitzt"""
    grund = grund_feld
    vorschlag = vorschlag_feld
    
    
    
# Referate
class ReferatForm(forms.Form):
    """Felder, die Referate besitzt"""
    referat_name = forms.CharField(label="Referats-Name:", max_length=100, required=True, widget=forms.TextInput())
    referat_email = forms.EmailField(label="Referats-E-Mail:", max_length=200, required=True, widget=forms.EmailInput())
    


# Beschluss
class BeschlussForm(forms.Form):
    """Felder, die ein Beschluss besitzt"""
    beschluss_behandlung = forms.CharField(label="Behandlung:", max_length=100, required=True, widget=forms.TextInput())
    beschluss_faehigkeit = forms.BooleanField(label="Beschluss-Fähigkeit:", required=False, widget=forms.CheckboxInput())
    stimmen_ja = forms.IntegerField(label="Ja-Stimmen:", required=True, widget=forms.NumberInput())
    stimmen_nein = forms.IntegerField(label="Nein-Stimmen:", required=True, widget=forms.NumberInput())
    stimmen_enthaltung = forms.IntegerField(label="Enthaltene Stimmen:", required=True, widget=forms.NumberInput())
    beschluss_ergebnis = forms.ChoiceField(label="Beschluss-Ergebnis:", choices=Beschluss.BeschlussErgebnis.choices, required=True, widget=forms.Select())
    beschluss_text = forms.CharField(label="Beschluss-Text:", max_length=2000, required=True, widget=forms.Textarea())
    beschluss_ausfertigung = forms.CharField(label="Ausfertigung:", max_length=200, required=True, widget=forms.TextInput())
    
    
    
# Vertagung Sitzung
class SitzungVertagenForm(forms.Form):
    """Felder, die SitzungVertagen Seite besitzt"""
    datum_neu = forms.DateField(label="Neues Datum:", required=True, widget=forms.DateInput())
    


# Vertagung eines Antrags
class AntragVertagenForm(forms.Form):
    """Felder, die AntragVertagen Seite besitzt"""
    sitzung = forms.ModelChoiceField(label="Sitzung:", queryset=Sitzung.objects.all().order_by('sitzDate'), required=True, empty_label="Bitte wählen...")



# Anlegen einer Sitzung
class SitzungAnlegenForm(forms.Form):
    """Felder, die SitzungAnlegen Seite besitzt"""
    referat = forms.ModelChoiceField(label="Referat:", queryset=Referat.objects.all().order_by('refID'), required=True, empty_label="Bitte wählen...")
    datum_sitzung = forms.DateField(label="Datum der Sitzung:", required=True, widget=forms.DateInput(), help_text="Format: TT.MM.JJJJ")
    
    def clean_datum_sitzung(self):
        datum_sitzung = self.cleaned_data['datum_sitzung']
        if datum_sitzung <= timezone.now().date():
            raise forms.ValidationError("Das Datum muss in der Zukunft liegen und im Format TT.MM.JJJJ angegeben sein.")
        return datum_sitzung
    

class ArchivSuchenForm(forms.Form):
    """Felder, die ArchivSuchen Seite besitzt"""
    # Suchbegriff
    q = forms.CharField(label="Suchbegriff:", max_length=300, required=False, widget=forms.TextInput())
    
    # Antragstyp
    atyp = forms.ModelChoiceField(label="Antragstyp:", queryset=Antragstyp.objects.all().order_by('typID'), required=False, empty_label="Kein Filter")

    # Datum Von
    dv = forms.DateField(label="Datum von:", required=False, widget=forms.DateInput(format="%d.%m.%Y"), input_formats=["%d.%m.%Y"], help_text="Format: TT.MM.JJJJ")
    # Datum Bis
    db = forms.DateField(label="Datum bis:", required=False, widget=forms.DateInput(format="%d.%m.%Y"), input_formats=["%d.%m.%Y"], help_text="Format: TT.MM.JJJJ")
    
    def clean(self):
        cleaned_data = super().clean()
        dv = cleaned_data.get('dv')
        db = cleaned_data.get('db')

        if dv and db and dv > db:
            raise forms.ValidationError('Datum von darf nicht größer als Datum bis sein.')
        
        return cleaned_data
    
    
class AntragsverwaltungSuchenForm(ArchivSuchenForm):
    """Felder, die AntragsverwaltungSuchen Seite besitzt"""
    # Beschluss
    choices = Beschluss.BeschlussErgebnis.choices
    choices.insert(0, ("", "Kein Filter"))
    b = forms.ChoiceField(label="Beschluss:", choices=choices, required=False, widget=forms.Select())
    
    
class SitzungsverwaltungSuchenForm(forms.Form):
    """Felder, die SitzungsverwaltungSuchen Seite besitzt"""
    # Referat
    ref = forms.ModelChoiceField(label="Referat:", queryset=Referat.objects.all().order_by('refID'), required=False, empty_label="Alle Referate")
    
    # Sitzungs-Status
    choices = Sitzung.SitzungStatus.choices
    choices.insert(0, ("", "Kein Filter"))
    s = forms.ChoiceField(label="Sitzungs-Status:", choices=choices, required=False, widget=forms.Select())

    # Datum Von
    dv = forms.DateField(label="Datum von:", required=False, widget=forms.DateInput(format="%d.%m.%Y"), input_formats=["%d.%m.%Y"], help_text="Format: TT.MM.JJJJ")
    # Datum Bis
    db = forms.DateField(label="Datum bis:", required=False, widget=forms.DateInput(format="%d.%m.%Y"), input_formats=["%d.%m.%Y"], help_text="Format: TT.MM.JJJJ")
    
    def clean(self):
        cleaned_data = super().clean()
        dv = cleaned_data.get('dv')
        db = cleaned_data.get('db')

        if dv and db and dv > db:
            raise forms.ValidationError('Datum von darf nicht größer als Datum bis sein.')
        
        return cleaned_data
    
    