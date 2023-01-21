import uuid
from django.db import models
from djmoney.models.fields import MoneyField


class Sitzung(models.Model):
    sitzID = models.UUIDField(primary_key=True,
                              default=uuid.uuid4,
                              editable=False)
    refID = models.UUIDField()
    sitzDate = models.DateField()


class Antragssteller(models.Model):
    astellerID = models.UUIDField(primary_key=True,
                                  default=uuid.uuid4,
                                  editable=False)
    astellerName = models.TextField(max_length=50)
    astellerVorname = models.TextField(max_length=50)


class Antrag(models.Model):
    antragID = models.UUIDField(primary_key=True,
                                default=uuid.uuid4,
                                editable=False)
    sitzID = models.ForeignKey(Sitzung)
    typID = models.UUIDField()
    astellerID = models.ForeignKey(Antragssteller)
    antragText = models.TextField()
    antragSumme = MoneyField(default_currency='EUR')
