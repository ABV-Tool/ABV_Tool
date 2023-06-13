import uuid
from django.db import models
from django.utils import timezone
from djmoney.models.fields import MoneyField
from djmoney.money import Currency


class Referat(models.Model):
    class Meta:
        db_table = 'referat'
    refID = models.PositiveIntegerField(primary_key=True,
                                        default=int,
                                        unique=True,
                                        db_column='ref_id')
    refName = models.TextField(db_column='ref_name', max_length=200)
    refZyklus = models.IntegerField(db_column='zyklus', blank=True)
    refEmail = models.EmailField(db_column='ref_email', max_length=100, blank=True)
    
    def __str__(self):
        return self.refName


class Sitzung(models.Model):
    class Meta:
        db_table = 'sitzung'
        
    class SitzungStatus(models.TextChoices):
        OFFEN = 'Offen'
        VERTAGT = 'Vertagt'
        STATTGEFUNDEN = 'Stattgefunden'
        
    sitzStatus = models.CharField(max_length=50, choices=SitzungStatus.choices, default=SitzungStatus.OFFEN, db_column='sit_status')
        
    sitzID = models.UUIDField(primary_key=True,
                              default=uuid.uuid4,
                              editable=False,
                              db_column='sitz_id')
    refID = models.ForeignKey(Referat,
                              db_column='ref_id',
                              on_delete=models.CASCADE)
    sitzDate = models.DateField(db_column='sitz_date')
    anzAntraege = models.PositiveIntegerField(db_column='anz_antraege', default=0)
    
    def __str__(self):
        # TODO: Sollte eine Sitzung vorverlegt werden, so stimmt die Reihenfolge der Sitzungen nicht mehr
        anzahl_sitz_jahr = Sitzung.objects.filter(sitzDate__year=self.sitzDate.year).filter(refID=self.refID).count()
        return str(anzahl_sitz_jahr) + ". Sitzung " + self.refID.refName + " " + str(self.sitzDate.year)


class Antragssteller(models.Model):
    class Meta:
        db_table = 'antragssteller'
    astellerID = models.UUIDField(primary_key=True,
                                  default=uuid.uuid4,
                                  editable=False,
                                  db_column='asteller_id')
    astellerName = models.TextField(max_length=50, db_column='asteller_name')
    astellerEmail = models.EmailField(max_length=50, db_column='asteller_email', null=True)
    astellerIstMitglied = models.BooleanField(db_column='asteller_ist_mitglied', default=False)
    
    def __str__(self):
        return self.astellerName


class Beschluss(models.Model):
    class Meta:
        db_table = 'beschluss'
        
    class BeschlussErgebnis(models.TextChoices):
        UNBEHANDELT = 'Unbehandelt'
        ANGENOMMEN = 'Angenommen'
        ABGELEHNT = 'Abgelehnt'
        
    def get_beschluss_ergebnisse(self):
        return list(self.BeschlussErgebnis)
        
    beschlussID = models.UUIDField(primary_key=True,
                                   default=uuid.uuid4,
                                   editable=False,
                                   db_column='beschluss_id')
    sitzID = models.ForeignKey(Sitzung,
                               on_delete=models.CASCADE,
                               db_column='sitz_id')
    beschlussDate = models.DateField(db_column='beschluss_date', default=timezone.now)
    beschlussFaehigkeit = models.BooleanField(db_column='beschluss_faehigkeit', default=False)
    
    stimmenJa = models.PositiveIntegerField(db_column='stimmen_ja', default=0)
    stimmenNein = models.PositiveIntegerField(db_column='stimmen_nein', default=0)
    stimmenEnthaltung = models.PositiveIntegerField(db_column='stimmen_enthaltung', default=0)
    
    beschlussErgebnis = models.CharField(max_length=20, 
                                         choices=BeschlussErgebnis.choices, 
                                         default=BeschlussErgebnis.UNBEHANDELT)
    
    beschlussText = models.TextField(db_column='beschluss_text', max_length=1000)
    beschlussAusfertigung = models.TextField(db_column='beschluss_ausfertigung', max_length=200)
    
    def get_ergebnis(self):
        return self.beschlussErgebnis


class Antragstyp(models.Model):
    class Meta:
        db_table = 'antragstyp'
    typID = models.PositiveIntegerField(primary_key=True,
                                        default=int,
                                        db_column='typ_id')
    typName = models.TextField(max_length=200, db_column='typ_name', default="", blank=False)
    typSlug = models.TextField(max_length=200, db_column='typ_slug', default="", blank=False)
    
    def __str__(self):
        return self.typName


class Antrag(models.Model):
    class Meta:
        db_table = 'antrag'
        
    # Stammdaten jedes Antrags
    antragID = models.UUIDField(primary_key=True,
                                default=uuid.uuid4,
                                editable=False,
                                db_column='antrag_id')
    sitzID = models.ForeignKey(Sitzung,
                               on_delete=models.CASCADE,
                               db_column='sitz_id')
    typID = models.ForeignKey(Antragstyp,
                              on_delete=models.CASCADE,
                              db_column='typ_id')
    astellerID = models.ForeignKey(Antragssteller,
                                   on_delete=models.CASCADE,
                                   db_column='asteller_id')
    beschlussID = models.ForeignKey(Beschluss,
                                    on_delete=models.SET_NULL,
                                    db_column='beschluss_id',
                                    null=True,
                                    blank=True)
    antragTitel = models.TextField(db_column='antrag_titel', default="", max_length=200, blank=False)
    antragText = models.TextField(db_column='antrag_text', default="", max_length=2000, blank=False)

    antragAnlagen = models.FileField(db_column='antrag_anlagen', blank=True)
    prioritaet = models.PositiveIntegerField(db_column='prioritaet', default=0)
    
    istEilantrag = models.BooleanField(db_column='ist_eilantrag', default=False, blank=False)
    
    # Antragsspezifische Daten
    # TODO: Überlegung zu besserer Strukturierung in DB
    antragGrund = models.TextField(db_column='antrag_grund', blank=True)
    antragVorschlag = models.TextField(db_column='antrag_vorschlag', blank=True)
    antragKostenposition = models.TextField(db_column='antrag_kostenposition', blank=True)
    antragSumme = MoneyField(db_column='antrag_summe',
                             max_digits=10,
                             decimal_places=2,
                             default_currency=Currency('EUR'),
                             default=0) # type: ignore
    antragVorstellungPerson = models.TextField(db_column='antrag_vorstellung_person', blank=True)
    antragFragenZumAmt = models.TextField(db_column='antrag_fragen_zum_amt', blank=True)
    antragZeitraum = models.TextField(db_column='antrag_zeitraum', blank=True)
    antragVerantwortlichkeit = models.TextField(db_column='antrag_verantwortlichkeit', blank=True)
    
    erstelltDate = models.DateField(db_column='erstellt_date', auto_now_add=True)
    bearbeitetDate = models.DateField(db_column='bearbeitet_date', auto_now=True)
    
    def __str__(self):
        return str(self.antragTitel) + " von " + self.astellerID.astellerVorname + " " + self.astellerID.astellerName
