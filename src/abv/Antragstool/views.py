from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .models import Referat, Sitzung, Antrag
from .forms import LoginForm


def AppHome(request):
    return render(request, 'Antragstool/index.html')


def LoginPage(request):
    # redirect if user is already logged in
    if request.user.is_authenticated:
        return redirect('index')
    
    form = LoginForm()
    msg = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                msg = 'Die eingegebenen Daten sind ungültig! Versuche es erneut.'
              
    return render(
        request, 'registration/login.html', context={'form': form, 'msg': msg}
    )
    
    
def LogoutPage(request):
    logout(request)
    return redirect('index')


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
