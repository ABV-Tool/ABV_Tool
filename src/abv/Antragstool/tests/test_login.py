from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

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