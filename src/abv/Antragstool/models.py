import uuid
from django.db import models
from djmoney.models.fields import MoneyField
import jsonfield


class Referat(models.Model):
    class Meta:
        db_table = 'referat'
    refID = models.UUIDField(primary_key=True,
                             default=uuid.uuid4,
                             editable=False,
                             db_column='ref_id')
    refName = models.TextField(db_column='ref_name', max_length=200)
    refZyklus = models.IntegerField(db_column='zyklus')


class Sitzung(models.Model):
    class Meta:
        db_table = 'sitzung'
    sitzID = models.UUIDField(primary_key=True,
                              default=uuid.uuid4,
                              editable=False,
                              db_column='sitz_id')
    refID = models.ForeignKey(Referat,
                              db_column='ref_id',
                              on_delete=models.CASCADE)
    sitzDate = models.DateField(db_column='sitz_date')


class Antragssteller(models.Model):
    class Meta:
        db_table = 'antragssteller'
    astellerID = models.UUIDField(primary_key=True,
                                  default=uuid.uuid4,
                                  editable=False,
                                  db_column='asteller_id')
    astellerName = models.TextField(max_length=50, db_column='asteller_name')
    astellerVorname = models.TextField(max_length=50,
                                       db_column='asteller_vorname')


class Antragstyp(models.Model):
    class Meta:
        db_table = 'antragstyp'
    typID = models.UUIDField(primary_key=True,
                             default=uuid.uuid4,
                             editable=False,
                             db_column='typ_id')
    typName = models.TextField(max_length=200, db_column='typ_name')
    form = jsonfield.JSONField(db_column='form')


class Antrag(models.Model):
    class Meta:
        db_table = 'antrag'
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
    antragText = models.TextField(db_column='antrag_text')
    antragSumme = MoneyField(default_currency='EUR',
                             max_digits=10,
                             db_column='antrag_summe')
