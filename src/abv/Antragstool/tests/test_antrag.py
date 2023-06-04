from Antragstool.models import Antrag
import unittest
from django.test import Client



class AntragAllgemeinTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_antrag_allgemein(self):
        response = self.client.post('/antrag/allgemein/', {
            'vorname': 'Reiner',
            'nachname': 'Zufall',
            'email': 'reiner@z.de',
            'titel': 'TestantragTEST',
            'referat': '1',
            'ist_eilantrag': False,
            'text': 'Dies ist ein Testantrag',
            'grund': 'Testgrund',
            'vorschlag': 'Testvorschlag',
            'anlagen': ''
        })
        self.assertEqual(response.status_code, 200)

        # Überprüfe, ob der Antrag in der Datenbank erstellt wurde
        antrag = Antrag.objects.filter(antragTitel='TestantragTEST').filter(antragText='Dies ist ein Testantrag').filter(antragVorschlag='Testvorschlag').first()
        self.assertEqual(antrag.astellerID.astellerVorname, 'Reiner')
        self.assertEqual(antrag.astellerID.astellerName, 'Zufall')
        self.assertEqual(antrag.antragText, 'Dies ist ein Testantrag')
        self.assertEqual(antrag.istEilantrag, False)
        self.assertEqual(antrag.antragGrund, 'Testgrund')
        self.assertEqual(antrag.antragVorschlag, 'Testvorschlag')

        antrag.delete()

    def test_antrag_delete(self):
        antrag = Antrag.objects.filter(antragTitel='TestantragTEST').filter(antragText='Dies ist ein Testantrag').filter(antragVorschlag='Testvorschlag').first()
        self.assertIsNone(antrag)
