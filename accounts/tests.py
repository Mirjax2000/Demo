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
            username="testuser", email="ferda@seznam.cz", password="testpass123"
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
        """Přihlášený uživatel vytvoří nový účet, odhlásí se a přihlásí jako nový uživatel."""

        # Přihlášení jako testovací uživatel
        login_ok = self.client.login(username="testuser", password="testpass123")
        self.assertTrue(login_ok, "Nepodařilo se přihlásit jako testuser")

        # Vytvoření nového uživatele
        new_username = "newuser"
        new_email = "email@email.cz"
        new_password = "Testpass123!"

        response = self.client.post(
            reverse("signup"),
            {
                "username": new_username,
                "email": new_email,
                "password1": new_password,
                "password2": new_password,
            },
        )

        # Ověření, že uživatel byl vytvořen
        self.assertTrue(User.objects.filter(username=new_username).exists())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")

        # --- New Assertions ---
        # Get the newly created user object
        created_user = User.objects.get(username=new_username)

        # Verify the email
        self.assertEqual(created_user.email, new_email)

        # Verify that the user is not a superuser
        self.assertFalse(created_user.is_superuser)

        # Verify that the user is not an admin (is_staff)
        self.assertFalse(created_user.is_staff)
        # --- End of New Assertions ---

        # Odhlášení
        response_logout = self.client.post("/accounts/logout/")
        self.assertEqual(response_logout.status_code, 302)
        self.assertRedirects(response_logout, "/accounts/login/")

        # Přihlášení jako nově vytvořený uživatel
        login_new_ok = self.client.login(username=new_username, password=new_password)
        self.assertTrue(login_new_ok, "Nepodařilo se přihlásit jako newuser")

    def test_register_negative(self):
        """Testuje neplatnou registraci:"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser%",  # neplatné znaky
                "email": "email@email.cz",
                "password1": "password123",
                "password2": "Testpass123!",  # neshoda hesel
            },
        )
        # Uživatel by neměl být vytvořen
        self.assertFalse(User.objects.filter(username="newuser%").exists())
        # Měl by se vrátit k registračnímu formuláři (200 = chyba ve formuláři)
        self.assertEqual(response.status_code, 200)

    def test_register_email_negative(self):
        """Testuje neplatnou registraci:"""
        self.client.login(username="testuser", password="testpass123")

        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",  # neplatné znaky
                "email": "email@email",
                "password1": "password123",
                "password2": "Testpass123",  # neshoda hesel
            },
        )
        # Uživatel by neměl být vytvořen
        self.assertFalse(User.objects.filter(username="newuser").exists())
        # Měl by se vrátit k registračnímu formuláři (200 = chyba ve formuláři)
        self.assertEqual(response.status_code, 200)
