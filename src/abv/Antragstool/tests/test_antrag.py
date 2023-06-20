import mailbox
from django.test import TestCase
from ..models import Antrag, Antragstyp
from django.urls import reverse
import requests
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.urls import path
from .. import views
from django.shortcuts import render

import unittest
from django.test import Client
from ..models import Referat, Sitzung, Antrag, Antragstyp, Antragssteller


class AntragAllgemeinTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_antrag_allgemein(self):
        response = self.client.post('/antrag/allgemein/', {
            'name': 'Patecky',
            'email': 'maxpatecky@outlook.com',
            'titel': 'Testantrag',
            'referat': '1',
            'ist_eilantrag': False,
            'text': 'Dies ist ein Testantrag',
            'grund': 'Testgrund',
            'vorschlag': 'Testvorschlag',
            'anlagen': ''
        })
        self.assertEqual(response.status_code, 200)

        # Überprüfe, ob der Antrag in der Datenbank erstellt wurde
        antrag = Antrag.objects.filter(antragTitel='Testantrag').first()
        self.assertEqual(antrag.astellerID.astellerName, 'Patecky')
        self.assertEqual(antrag.antragText, 'Dies ist ein Testantrag')
        self.assertEqual(antrag.istEilantrag, False)
        self.assertEqual(antrag.antragGrund, 'Testgrund')
        self.assertEqual(antrag.antragVorschlag, 'Testvorschlag')