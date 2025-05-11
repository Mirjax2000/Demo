"""Accounts Tests"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class AuthTests(TestCase):
    """Testovací třída pro funkcionalitu autentizace.
    Tato třída testuje operace uživatelské autentizace včetně přihlášení, odhlášení a registrace.
    """

    def setUp(self):
        """Vytváří testovacího uživatele pro autentizační testy."""
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_login(self):
        """Testuje funkcionalitu přihlášení uživatele."""
        response = self.client.post(
            "/accounts/login/",
            {"username": "testuser", "password": "testpass123"},
        )
        # Ověřuje HTTP 302 přesměrovací status
        self.assertEqual(response.status_code, 302)
        # Kontroluje existenci uživatelské session
        self.assertTrue("_auth_user_id" in self.client.session)
        # Ověřuje přesměrování na hlavní stránku
        self.assertRedirects(response, "/")

    def test_logout(self):
        """Testuje funkcionalitu odhlášení uživatele."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post("/accounts/logout/")

        # Ověřuje HTTP 302 přesměrovací status
        self.assertEqual(response.status_code, 302)
        # Potvrzuje odstranění uživatelské session
        self.assertFalse("_auth_user_id" in self.client.session)
        # Ověřuje přesměrování na přihlašovací stránku
        self.assertRedirects(response, "/accounts/login/")

    def test_register_positive(self):
        """Testuje registraci nového uživatele."""
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "password1": "Testpass123!",
                "password2": "Testpass123!",
            },
        )
        # Potvrzuje existenci nového uživatele v databázi
        self.assertTrue(User.objects.filter(username="newuser").exists())
        # Ověřuje HTTP 302 přesměrovací status
        self.assertEqual(response.status_code, 302)
        # Ověřuje přesměrování na hlavní stránku
        self.assertRedirects(response, "/")
        # Potvrzuje automatické vytvoření přihlašovací session
        self.assertIn("_auth_user_id", self.client.session)

    def test_register_negative(self):
        """Testuje neplatnou registraci:"""

        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser%",  # neplatné znaky
                "password1": "password123",
                "password2": "Testpass123!",  # neshoda hesel
            },
        )

        # Uživatel by neměl být vytvořen
        self.assertFalse(User.objects.filter(username="newuser%").exists())
        # Měl by se vrátit k registračnímu formuláři (200 = chyba ve formuláři)
        self.assertEqual(response.status_code, 200)
        # Přihlášení by nemělo proběhnout
        self.assertNotIn("_auth_user_id", self.client.session)
