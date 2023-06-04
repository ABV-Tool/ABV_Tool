from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from Antragstool.models import Antragssteller, Antragstyp, Referat, Sitzung, Antrag
from django.contrib.auth import authenticate, login, logout
from ..views import LoginPage, LogoutPage
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

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

# Test Login 
class LoginPageTest(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.index_url = reverse('index')
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_page_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/login.html')
        self.assertContains(response, 'Anmelden')

    def test_login_page_post_valid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password,
        })
        self.assertRedirects(response, self.index_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_page_post_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/login.html')
        self.assertContains(response, 'Die eingegebenen Daten sind ungültig!')

    def test_login_page_post_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.post(self.login_url)
        self.assertRedirects(response, self.index_url)

    def test_logout_page(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, self.index_url)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
