from django.shortcuts import render
from .models import Referat, Sitzung, Antrag


def AppHome(request):
    return render(request, 'Antragstool/index.html')

def Login(request):
    return render(request, 'registration/login.html')

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


def AntraegeVonSitzung(request, sitzid):
    antraege = Antrag.objects.filter(sitzID=sitzid)
    sitzung = Sitzung.objects.get(sitzID=sitzid)
    return render(
        request,
        'Antragstool/antraege.html',
        {
            'antraege': antraege,
            'sitzung': sitzung
        }
    )
