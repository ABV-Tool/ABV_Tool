from django.test import TestCase
from Antragstool.models import Antragssteller, Antragstyp, Referat, Sitzung, Antrag
from django.test import TestCase


# Test Model init
class ModelInitializationTest(TestCase):
    def test_models_are_initialized(self):
        # Check if Antragssteller model is initialized
        self.assertIsNotNone(Antragssteller._meta.db_table)
        self.assertIsNotNone(Antragssteller._meta.get_field('astellerID'))
        self.assertIsNotNone(Antragssteller._meta.get_field('astellerName'))
        self.assertIsNotNone(Antragssteller._meta.get_field('astellerVorname'))

        # Check if Antragstyp model is initialized
        self.assertIsNotNone(Antragstyp._meta.db_table)
        self.assertIsNotNone(Antragstyp._meta.get_field('typID'))
        self.assertIsNotNone(Antragstyp._meta.get_field('typName'))

        # Check if Referat model is initialized
        self.assertIsNotNone(Referat._meta.db_table)
        self.assertIsNotNone(Referat._meta.get_field('refID'))
        self.assertIsNotNone(Referat._meta.get_field('refName'))
        self.assertIsNotNone(Referat._meta.get_field('refZyklus'))

        # Check if Sitzung model is initialized
        self.assertIsNotNone(Sitzung._meta.db_table)
        self.assertIsNotNone(Sitzung._meta.get_field('sitzID'))
        self.assertIsNotNone(Sitzung._meta.get_field('sitzDate'))
        self.assertIsNotNone(Sitzung._meta.get_field('refID'))

        # Check if Antrag model is initialized
        self.assertIsNotNone(Antrag._meta.db_table)
        self.assertIsNotNone(Antrag._meta.get_field('antragID'))
        self.assertIsNotNone(Antrag._meta.get_field('antragText'))
        self.assertIsNotNone(Antrag._meta.get_field('astellerID'))
        self.assertIsNotNone(Antrag._meta.get_field('sitzID'))
        self.assertIsNotNone(Antrag._meta.get_field('typID'))

