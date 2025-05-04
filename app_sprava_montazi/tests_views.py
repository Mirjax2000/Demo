"""View tests"""

from datetime import date
from django.test import TestCase
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User
from app_sprava_montazi.models import Order, DistribHub, Client, Team, TeamType, Status


class IndexViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.url = reverse("index")
        self.template = "base.html"

    def test_index_view(self):
        """
        Test pro zobrazení indexview.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)


class HomePageViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.url = reverse("homepage")
        self.template = "app_sprava_montazi/homepage/homepage.html"

    def test_index_view(self):
        """
        Test pro zobrazení indexview.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)


class CreatePageViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.url = reverse("createpage")
        self.template = "app_sprava_montazi/create/create.html"

    def test_index_view(self):
        """
        Test pro zobrazení indexview.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)


class DashboardViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.url = reverse("dashboard")
        self.template = "app_sprava_montazi/dashboard/dashboard.html"

    def test_index_view(self):
        """
        Test pro zobrazení indexview.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)


class ClientUpdateViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.template = "app_sprava_montazi/orders/order_update_client-form.html"
        self.hub = DistribHub.objects.create(code="626", city="Chrastany")
        self.customer = Client.objects.create(name="franta", zip_code="11111")
        self.order = Order.objects.create(
            order_number="703777143100437749-R",
            distrib_hub=self.hub,
            status=Status.NEW,
            client=self.customer,
            mandant="SCCZ",
            evidence_termin=date.today(),
            team_type=TeamType.BY_ASSEMBLY_CREW,
            team=None,
        )
        self.url = reverse(
            "client_update",
            kwargs={
                "slug": self.order.client.slug,
                "order_pk": self.order.pk,
            },
        )

    def test_index_view(self):
        """
        Test pro zobrazení indexview.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)


class OrdersAllViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.url = reverse("orders")
        self.hub = DistribHub.objects.create(code="626", city="Chrastany")
        self.template = "app_sprava_montazi/orders/orders_all.html"

        # Vytvoříme 20 objednávek
        for i in range(20):
            Order.objects.create(
                order_number=f"{i:05}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                evidence_termin=date.today(),
            )

    def test_orders_all_view(self):
        """
        Test pro zobrazení všech objednávek.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)


class TeamsViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.url = reverse("teams")
        self.template = "app_sprava_montazi/teams/teams_all.html"

    def test_index_view(self):
        """
        Test pro zobrazení indexview.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)


class TeamCreateTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.url = reverse("team_create")
        self.template = "app_sprava_montazi/teams/team_form.html"

    def test_index_view(self):
        """
        Test pro zobrazení indexview.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)


class TeamUpdateViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.team = Team.objects.create(
            name="Test Company",
            city="Praha",
            region="Střední Čechy",
            phone="123456789",
            email="test@company.cz",
            active=True,
            price_per_hour=150.50,
            price_per_km=12.30,
            notes="Toto je testovací poznámka.",
        )
        self.url = reverse("team_update", kwargs={"slug": self.team.slug})
        self.template = "app_sprava_montazi/teams/team_form.html"

    def test_index_view(self):
        """
        Test pro zobrazení indexview.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)
