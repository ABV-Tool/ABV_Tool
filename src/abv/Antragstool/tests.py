from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from Antragstool.models import Antragssteller, Antragstyp, Referat, Sitzung, Antrag
from django.contrib.auth import authenticate, login, logout
from .views import LoginPage, LogoutPage

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

# Test Login Successful
class LoginPageTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_successful(self):
        request = self.factory.post('/login/', {
            'username': 'testuser',
            'password': 'testpassword'
        })

        response = LoginPage(request)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/index/')  # Adjust the redirect URL if necessary

        # Check if the user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_invalid_credentials(self):
        request = self.factory.post('/login/', {
            'username': 'invaliduser',
            'password': 'invalidpassword'
        })

        response = LoginPage(request)
        self.assertEqual(response.status_code, 200)

        # Check if the user is not logged in
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        # Check the error message
        self.assertEqual(response.context['feedback'].type, 'ERROR')
        self.assertEqual(response.context['feedback'].text, 'Die eingegebenen Daten sind ungültig! Versuche es erneut.')

    def test_logout(self):
        request = self.factory.get('/logout/')

        # Log in the user to perform the logout
        user = authenticate(username='testuser', password='testpassword')
        login(request, user)

        response = LogoutPage(request)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/index/')  # Adjust the redirect URL if necessary

        # Check if the user is logged out
        self.assertFalse(response.wsgi_request.user.is_authenticated)
