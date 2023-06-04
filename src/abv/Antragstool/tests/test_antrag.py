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


# class AntragAllgemeinTests(TestCase):
#     def test_antrag_erfolgreich_einreichen(self):

#         url = 'http://127.0.0.1:8000/antrag/allgemein/'
#         # Erstelle einen POST-Request mit gültigen Daten für den allgemeinen Antrag
#         data = {
#             # Füge hier gültige Daten für den Antrag hinzu
#             'sitzID': '86fc5688-cee0-4d0c-9edb-1a89d718ff11',
#             'antragTitel': 'Mein Antrag',
#             'astellerID': 'fb3c9779-7dd8-4b22-85d7-ab9e3950ac1a',
#             # 'astellerVorname': 'Reiner',
#             # 'astellerName': 'Zufall',
#             # 'astellerEmail': 'a@a.de',
#             'antragText': 'Hier ist der Text meines Antrags.',
#             'istEilantrag': False,
#             'antragGrund': 'Der Grund für meinen Antrag',
#             'antragVorschlag': 'Mein Vorschlag',

#         }
        
       
#        # response = self.client.post(reverse('antrag-allgemein'), data)
#         response = requests.post(url, data=data)

#         # Überprüfe den HTTP-Statuscode
#         self.assertEqual(response.status_code, 200)

#         # Überprüfe, ob der Antrag erfolgreich eingereicht wurde
#         # self.assertEqual(response.context['feedback'].type, 'SUCCESS')
#         # self.assertEqual(response.context['feedback'].text, 'Dein Antrag wurde erfolgreich eingereicht! Du erhältst in Kürze eine Bestätigungsmail.')

#         # Überprüfe, ob der Antrag in der Datenbank gespeichert wurde
#         self.assertEqual(Antrag.objects.count(), 1)
#         antrag = Antrag.objects.first()
#         self.assertEqual(antrag.typID.typSlug, 'antrag-ohne-finanzielle-mittel')
#         #Testdaten
#         self.assertEqual(antrag.astellerID, 1)
#         self.assertEqual(antrag.antragID, 1)
#         self.assertEqual(antrag.antragTitel, 'Mein Antrag')
#         self.assertEqual(antrag.antragText, 'Hier ist der Text meines Antrags.')
#         self.assertEqual(antrag.istEilantrag, False)
#         self.assertEqual(antrag.antragGrund, 'Der Grund für meinen Antrag')
#         self.assertEqual(antrag.antragVorschlag, 'Mein Vorschlag')
#         # Überprüfe weitere Antragsattribute

#         # Überprüfe, ob die E-Mail-Bestätigung gesendet wurde
#         # Füge hier ggf. den entsprechenden Code hinzu

#     def test_antrag_form_ungültige_daten(self):
#         # Erstelle einen POST-Request mit ungültigen Daten für den allgemeinen Antrag
#         data = {
#             # Füge hier ungültige Daten für den Antrag hinzu
#         }
#         response = self.client.post(reverse('antrag-allgemein'), data)

#         # Überprüfe den HTTP-Statuscode
#         self.assertEqual(response.status_code, 200)

#         self.assertIn('feedback', response.context)
#         # Überprüfe, dass der Antrag nicht erfolgreich eingereicht wurde
#         self.assertNotEqual(response.context['feedback'].type, 'SUCCESS')
#         self.assertNotEqual(response.context['feedback'].text, 'Dein Antrag wurde erfolgreich eingereicht! Du erhältst in Kürze eine Bestätigungsmail.')

#         # Überprüfe, dass der Antrag nicht in der Datenbank gespeichert wurde
#         self.assertEqual(Antrag.objects.count(), 0)

#         # Überprüfe, ob keine E-Mail-Bestätigung gesendet wurde
#         # Füge hier ggf. den entsprechenden Code hinzu


# class AntragAllgemeinTest(TestCase):
#     def setUp(self):
#         self.antrag_allgemein_url = reverse('antrag-allgemein')
#         self.index_url = reverse('index')
#         self.username = 'testuser'
#         self.password = 'testpassword'
#         self.user = User.objects.create_user(username=self.username, password=self.password)
#         self.antragstyp = Antragstyp.objects.create(typSlug='antrag-ohne-finanzielle-mittel')

#     def test_antrag_allgemein_get(self):
#         self.client.force_login(self.user)
#         response = self.client.get(self.antrag_allgemein_url)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'pages/antrag.html')
#         self.assertContains(response, 'Allgemeiner Antrag')

#     def test_antrag_allgemein_post_valid_data(self):
#         self.client.force_login(self.user)
#         form_data = {
#             'titel': 'Testantrag',
#             'text': 'Dies ist ein Testantrag.',
#             'ist_eilantrag': False,
#             'grund': 'Testgrund',
#             'vorschlag': 'Testvorschlag',
#         }
#         response = self.client.post(self.antrag_allgemein_url, data=form_data, follow=True)
#         self.assertRedirects(response, self.index_url)
#         self.assertEqual(Antrag.objects.count(), 1)
#         antrag = Antrag.objects.first()
#         self.assertEqual(antrag.antragTitel, 'Testantrag')
#         self.assertEqual(antrag.antragText, 'Dies ist ein Testantrag.')
#         self.assertEqual(antrag.istEilantrag, False)
#         self.assertEqual(antrag.antragGrund, 'Testgrund')
#         self.assertEqual(antrag.antragVorschlag, 'Testvorschlag')
#         self.assertContains(response, 'Dein Antrag wurde erfolgreich eingereicht!', html=True)
#         # Additional assertions for checking other aspects of the method

#     def test_antrag_allgemein_post_invalid_data(self):
#         self.client.force_login(self.user)
#         form_data = {
#             'titel': '',  # Invalid data, title is required
#             'text': 'Dies ist ein Testantrag.',
#             'ist_eilantrag': False,
#             'grund': 'Testgrund',
#             'vorschlag': 'Testvorschlag',
#         }
#         response = self.client.post(self.antrag_allgemein_url, data=form_data)
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'pages/antrag.html')
#         self.assertContains(response, '', html=True) # 'Feld darf nicht leer sein'

#     # def test_render_antrag(self):
#     #     feedback = {
#     #         'type': 'SUCCESS',
#     #         'text': 'Dein Antrag wurde erfolgreich eingereicht! Du erhältst in Kürze eine Bestätigungsmail.'
#     #     }
#     #     response = render(self.client.get(self.index_url), 'pages/antrag.html', {'feedback': feedback})
#     #     self.assertEqual(response.status_code, 200)
#     #     self.assertTemplateUsed(response, 'pages/antrag.html')
#     #     self.assertContains(response, 'Antragseite')
#     #     self.assertContains(response, 'Dein Antrag wurde erfolgreich eingereicht!')

#     # Additional tests for other scenarios and functionalities

#     def tearDown(self):
#         Antrag.objects.all().delete()
#         Antragstyp.objects.all().delete()
#         User.objects.all().delete()

class AntragAllgemeinTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        # self.referat = 8
        # self.sitzung = '66a0eadc-c78d-42bd-80f9-0ef86feb23f6'
    
    def test_antrag_allgemein(self):
        response = self.client.post('/antrag/allgemein/', {
            'vorname': 'Reiner',
            'nachname': 'Zufall',
            'email': 'reiner@zufall.de',
            'titel': 'Testantrag',
            'referat': 1,
            'text': 'Dies ist ein Testantrag',
            'ist_eilantrag': False,
            'grund': 'Testgrund',
            'vorschlag': 'Testvorschlag'
        })
        self.assertEqual(response.status_code, 200)
        
        # Überprüfe, ob der Antrag in der Datenbank erstellt wurde
        antrag = Antrag.objects.filter(antragTitel='Testantrag').filter(antragText='Dies ist ein Testantrag').first()
        print(antrag)
        self.assertEqual(antrag.typID.typSlug, 'antrag-ohne-finanzielle-mittel')
        self.assertEqual(antrag.sitzID.sitzID, self.sitzung.sitzID)
        self.assertEqual(antrag.astellerID.astellerVorname, 'Vorname')
        self.assertEqual(antrag.astellerID.astellerName, 'Nachname')
        self.assertEqual(antrag.antragText, 'Dies ist ein Testantrag')
        self.assertEqual(antrag.istEilantrag, False)
        self.assertEqual(antrag.antragGrund, 'Testgrund')
        self.assertEqual(antrag.antragVorschlag, 'Testvorschlag')
        
        # Überprüfe, ob eine Bestätigungsmail gesendet wurde
        self.assertEqual(len(mailbox.outbox), 1)
        self.assertEqual(mailbox.outbox[0].subject, 'Dein Antrag ist eingegangen!')
        self.assertEqual(mailbox.outbox[0].to, ['example@example.com'])