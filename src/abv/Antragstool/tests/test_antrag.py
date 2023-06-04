import unittest
from django.test import Client

from Antragstool.models import Antrag


class AntragAllgemeinTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.vorname = "Reiner"
        self.nachname = "Zufall"
        self.email = "reiner@zufall.de"
        self.titel = "Test"
        self.text = "Dies ist ein Testantrag"
        self.grund = "Testgrund"
        self.vorschlag = "Testvorschlag"
    
    def test_antrag_allgemein_erstellen(self):
        response = self.client.post('/antrag/allgemein/', {
            'vorname': self.vorname,
            'nachname': self.nachname,
            'email': self.email,
            'titel': self.titel,
            'referat': '1',
            'ist_eilantrag': False,
            'text': self.text,
            'grund': self.grund,
            'vorschlag': self.vorschlag,
            'anlagen': ''
        })
        self.assertEqual(response.status_code, 200)

        # Überprüfe, ob der Antrag in der Datenbank erstellt wurde
        self.assertTrue(
        Antrag.objects.filter(
            ).filter(
                astellerID__astellerVorname=self.vorname
            ).filter(
                astellerID__astellerName=self.nachname
            ).filter(
                astellerID__astellerEmail=self.email
            ).filter(
                antragTitel=self.titel
            ).filter(
                antragText=self.text
            ).filter(
                antragVorschlag=self.vorschlag
            ).filter(
                antragGrund=self.grund
            ).exists()
        )

    def test_antrag_allgemein_delete(self):
        response = self.client.post('/antrag/allgemein/', {
            'vorname': self.vorname,
            'nachname': self.nachname,
            'email': self.email,
            'titel': self.titel,
            'referat': '1',
            'ist_eilantrag': False,
            'text': self.text,
            'grund': self.grund,
            'vorschlag': self.vorschlag,
            'anlagen': ''
        })
        self.assertEqual(response.status_code, 200)

        # Überprüfe, ob der Antrag in der Datenbank erstellt wurde
        antrag = Antrag.objects.filter(
            ).filter(
                astellerID__astellerVorname=self.vorname
            ).filter(
                astellerID__astellerName=self.nachname
            ).filter(
                astellerID__astellerEmail=self.email
            ).filter(
                antragTitel=self.titel
            ).filter(
                antragText=self.text
            ).filter(
                antragVorschlag=self.vorschlag
            ).filter(
                antragGrund=self.grund
            )
            
        antrag.delete()
        
        self.assertFalse(antrag.exists())
