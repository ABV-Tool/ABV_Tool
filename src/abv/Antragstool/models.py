import uuid
from django.db import models
from djmoney.models.fields import MoneyField


class Antrag(models.Model):
    antragID = models.UUIDField(primary_key=True,
                                default=uuid.uuid4,
                                editable=False)
    sitzID = models.UUIDField()
    typID = models.UUIDField()
    astellerID = models.UUIDField()
    antragText = models.TextField()
    antragSumme = MoneyField(default_currency='EUR')
