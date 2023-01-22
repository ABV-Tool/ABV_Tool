from django.shortcuts import render
from .models import Referat, Sitzung


def AppHome(request):
    return render(request, 'Antragstool/index.html')


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
