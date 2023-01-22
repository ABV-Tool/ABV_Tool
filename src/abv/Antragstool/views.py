from django.shortcuts import render
from .models import Referat


def AppHome(request):
    return render(request, 'Antragstool/index.html')


def ReferatListe(request):
    referate = Referat.objects.all()
    return render(
        request,
        'Antragstool/list.html',
        {
            'referate': referate
        }
    )
