import uuid
from django.db import models
from djmoney.models.fields import MoneyField


class Sitzung(models.Model):
    sitzID = models.UUIDField(primary_key=True,
                              default=uuid.uuid4,
                              editable=False)
    refID = models.UUIDField()
    sitzDate = models.DateField()


class Antrag(models.Model):
    antragID = models.UUIDField(primary_key=True,
                                default=uuid.uuid4,
                                editable=False)
    sitzID = models.ForeignKey(Sitzung)
    typID = models.UUIDField()
    astellerID = models.UUIDField()
    antragText = models.TextField()
    antragSumme = MoneyField(default_currency='EUR')
