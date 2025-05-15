"""View tests"""

from datetime import date, datetime
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client as CL
from django.test import TestCase
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone

from app_sprava_montazi.models import (
    Article,
    Client,
    DistribHub,
    Order,
    Status,
    Team,
    TeamType,
    Upload,
)

from .forms import UploadForm


class IndexViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.url = reverse("index")
        self.template = "base.html"
        self.client.login(username="testuser", password="testpass")

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")


class HomePageViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.url = reverse("homepage")
        self.template = "app_sprava_montazi/homepage/homepage.html"

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
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


class CreatePageViewTest(TestCase):
    """Nastavení testu: vytvoření uživatele a přihlášení."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="testuser", password="testpass")

    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.url = reverse("createpage")
        self.template = "app_sprava_montazi/create/create.html"
        self.client.login(username="testuser", password="testpass")

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    def test_valid_form_submission(self):
        # Simulujeme upload CSV souboru
        csv_file = SimpleUploadedFile(
            "test.csv", b"col1,col2\nval1,val2", content_type="text/csv"
        )
        response = self.client.post(
            reverse("createpage"), {"file": csv_file}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Upload.objects.count(), 1)

    def test_invalid_form_submission(self):
        """bez zadani souboru do formulare"""

        response = self.client.post(reverse("createpage"), {}, follow=True)

        # Měla by se objevit chybová hláška
        self.assertContains(response, "Soubor je povinný!")
        self.assertEqual(Upload.objects.count(), 0)

    def test_upload_creates_db_entry(self):
        initial_count = Upload.objects.count()

        csv_file = SimpleUploadedFile(
            "valid.csv", b"header1,header2\n1,2", content_type="text/csv"
        )
        response = self.client.post(
            reverse("createpage"), {"file": csv_file}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Upload.objects.count(), initial_count + 1)

    @patch(
        "app_sprava_montazi.views.call_command", side_effect=KeyError("missing column")
    )
    def test_key_error_handling(self, mock_command):
        csv_file = SimpleUploadedFile(
            "bad.csv", b"wrong,format\n1,2", content_type="text/csv"
        )
        response = self.client.post(
            reverse("createpage"), {"file": csv_file}, follow=True
        )

        self.assertContains(response, "Špatný soubor CSV")

    @patch(
        "app_sprava_montazi.views.call_command",
        side_effect=Exception("unexpected error"),
    )
    def test_unknown_exception_handling(self, mock_command):
        csv_file = SimpleUploadedFile("bad.csv", b"ok", content_type="text/csv")
        response = self.client.post(
            reverse("createpage"), {"file": csv_file}, follow=True
        )

        self.assertContains(response, "Neznamá chyba!")

    @patch(
        "app_sprava_montazi.views.call_command", side_effect=ValueError("wrong value")
    )
    def test_value_error_handling(self, mock_command):
        csv_file = SimpleUploadedFile("bad.csv", b"ok", content_type="text/csv")
        response = self.client.post(
            reverse("createpage"), {"file": csv_file}, follow=True
        )

        self.assertContains(response, "Chyba hodnoty v souboru CSV! wrong value")

    @patch("app_sprava_montazi.views.call_command", side_effect=DistribHub.DoesNotExist)
    def test_distribhub_doesnotexist_handling(self, mock_command):
        csv_file = SimpleUploadedFile("bad.csv", b"ok", content_type="text/csv")
        response = self.client.post(
            reverse("createpage"), {"file": csv_file}, follow=True
        )
        self.assertContains(response, "Neexistujicí místo určení v CSV souboru!")


class DashboardViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.url = reverse("dashboard")
        self.template = "app_sprava_montazi/dashboard/dashboard.html"
        self.client.login(username="testuser", password="testpass")

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")


class ClientUpdateViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele

        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
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

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    def test_context_data(self):
        """test spravneho zobrazeni"""
        response = self.client.get(self.url)
        self.assertEqual(response.context["form_type"], "update")
        self.assertEqual(response.context["order"], self.order)
        self.assertQuerySetEqual(
            response.context["articles"],
            Article.objects.filter(order=self.order.pk),
            transform=lambda x: x,
        )
        self.assertEqual(response.context["active"], "orders_all")

    def test_success_message_displayed(self):
        data = {
            "name": "Karel",
            "zip_code": "12345",
        }
        response = self.client.post(self.url, data, follow=True)
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn("Zákazník: Karel aktualizován.", messages)

    def test_post_invalid_data_name(self):
        data = {
            "name": "",  # jméno je povinné
            "zip_code": "12345",
        }
        response = self.client.post(self.url, data)

        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertIn("Jméno je povinné!", str(form.errors["name"]))

    def test_post_invalid_data_zip_code(self):
        data = {
            "name": "ferda",  # jméno je povinné
            "zip_code": "",
        }
        response = self.client.post(self.url, data)

        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertIn("PSČ je povinné!", str(form.errors["zip_code"]))

    def test_post_valid_data(self):
        data = {
            "name": "Karel",
            "zip_code": "12345",
            "street": "Kopretinova 15",
            "city": "Kolin",
            "phone": "234234234",
            "email": "karel@seznam.cz",
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertRedirects(
            response, reverse("order_detail", kwargs={"pk": self.order.pk})
        )
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, "Karel")
        self.assertEqual(self.customer.zip_code, "12345")
        self.assertEqual(self.customer.street, "Kopretinova 15")
        self.assertEqual(self.customer.city, "Kolin")
        self.assertEqual(self.customer.phone, "234234234")
        self.assertEqual(self.customer.email, "karel@seznam.cz")


class OrderCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.template = "app_sprava_montazi/orders/order_form.html"
        self.url = reverse("order_create")
        self.client = CL()
        self.client.login(username="testuser", password="testpass")
        self.valid_status_key = Status.NEW
        self.valid_team_type_key = TeamType.BY_ASSEMBLY_CREW
        self.hub = DistribHub.objects.create(code="111", city="Praha")
        self.customer = Client.objects.create(name="Pedro Pascal", zip_code="12345")
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

        # Základní validní data pro formuláře
        self.valid_customer_data = {
            "name": "Ferdinand",
            "street": "Kopretinova 15",
            "city": "Praha",
            "zip_code": "12345",
            "phone": "232232232",
            "email": "ferdinand@seznam.cz",
        }

        self.valid_order_data = {
            "order_number": "703777143100437749-O",
            "distrib_hub": self.hub.id,
            "mandant": "CCCC",
            "status": self.valid_status_key,
            "delivery_termin": "2024-05-15",
            "evidence_termin": "2024-05-20",
            "montage_termin": "2024-05-25T10:30",
            "team_type": self.valid_team_type_key,
            "team": self.team.id,
            "notes": "This is a test order note.",
        }

        self.formset_management_data = {
            "article_set-TOTAL_FORMS": 0,
            "article_set-INITIAL_FORMS": 0,
            "article_set-MIN_NUM_FORMS": 0,
            "article_set-MAX_NUM_FORMS": 1000,
        }

        self.valid_article_data = {
            "article_set-TOTAL_FORMS": 1,
            "article_set-INITIAL_FORMS": 0,
            "article_set-MIN_NUM_FORMS": 0,
            "article_set-MAX_NUM_FORMS": 1000,
            "article_set-0-name": "Postel",
            "article_set-0-quantity": 1,
            "article_set-0-price": 10000,
            "article_set-0-note": "Tvrda postel",
            "article_set-0-id": "",
            "article_set-0-DELETE": "",
        }

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá GET stránku
        a je použita správná šablona a formuláře v kontextu.
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)
        # Zkontrolujeme, že formuláře jsou v kontextu
        self.assertIn("order_form", response.context)
        self.assertIn("client_form", response.context)
        self.assertIn("article_formset", response.context)
        # Zkontrolujeme, že formuláře v kontextu nejsou vázané na data (jsou prázdné)
        self.assertFalse(response.context["order_form"].is_bound)
        self.assertFalse(response.context["client_form"].is_bound)
        self.assertFalse(response.context["article_formset"].is_bound)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    @patch("django.contrib.messages.success")
    def test_successful_order_creation_with_articles(self, mock_success_message):
        """
        Testuje úspěšné vytvoření objednávky s klientem a články při validních datech.
        """
        initial_order_count = Order.objects.count()
        initial_client_count = Client.objects.count()
        initial_article_count = Article.objects.count()

        # Kombinujeme data pro POST - všechny formuláře validní, s jedním článkem
        post_data = {
            **self.valid_customer_data,
            **self.valid_order_data,
            **self.valid_article_data,
        }

        response = self.client.post(self.url, post_data)

        # Zkontrolujeme vazby
        created_order = Order.objects.latest("id")  # Získáme nově vytvořenou objednávku
        created_client = Client.objects.latest("id")  # Získáme nově vytvořeného klienta
        # Očekáváme přesměrování na detail objednávky
        self.assertEqual(response.status_code, 302)
        # Zkontrolujeme, že přesměrování je na URL detailu objednávky
        self.assertRedirects(
            response, reverse("order_detail", kwargs={"pk": created_order.pk})
        )

        # Zkontrolujeme, že data byla uložena do databáze
        self.assertEqual(Order.objects.count(), initial_order_count + 1)
        self.assertEqual(Client.objects.count(), initial_client_count + 1)
        self.assertEqual(
            Article.objects.count(),
            initial_article_count + self.valid_article_data["article_set-TOTAL_FORMS"],
        )

        self.assertEqual(created_order.client, created_client)
        self.assertEqual(
            created_order.articles.count(),
            self.valid_article_data["article_set-TOTAL_FORMS"],
        )

        created_article = created_order.articles.first()
        self.assertEqual(
            created_article.name, self.valid_article_data["article_set-0-name"]
        )
        self.assertEqual(
            created_article.quantity, self.valid_article_data["article_set-0-quantity"]
        )
        self.assertEqual(
            float(created_article.price), self.valid_article_data["article_set-0-price"]
        )  # Decimal vs float

        mock_success_message.assert_called_once()
        args, kwargs = mock_success_message.call_args
        self.assertEqual(args[1], "Objednávka vytvořena.")

    @patch("django.contrib.messages.error")
    def test_invalid_order_data_shows_errors(self, mock_error_message):
        invalid_data = self.valid_order_data.copy()
        invalid_data["order_number"] = ""
        invalid_data["evidence_termin"] = ""
        invalid_data["distrib_hub"] = ""
        invalid_data["mandant"] = ""
        post_data = {
            **self.valid_customer_data,
            **invalid_data,
            **self.formset_management_data,
        }
        response = self.client.post(self.url, post_data)
        order_form = response.context.get("order_form")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "číslo objednávky je povinné!", str(order_form.errors["order_number"])
        )
        self.assertIn("Mandant je povinný!", str(order_form.errors["mandant"]))
        self.assertIn(
            "Toto pole je vyžadováno", str(order_form.errors["evidence_termin"])
        )
        self.assertIn("místo určení je povinné!", str(order_form.errors["distrib_hub"]))

        mock_error_message.assert_called_once()
        args, kwargs = mock_error_message.call_args
        self.assertEqual(args[1], "Nastala chyba při ukládání objednávky.")

    @patch("django.contrib.messages.error")
    def test_unique_order_data_shows_errors(self, mock_error_message):
        invalid_data = self.valid_order_data.copy()
        invalid_data["order_number"] = "703777143100437749-R"
        post_data = {
            **self.valid_customer_data,
            **invalid_data,
            **self.formset_management_data,
        }
        response = self.client.post(self.url, post_data)
        order_form = response.context.get("order_form")

        self.assertEqual(response.status_code, 200)
        self.assertIn("objednávka uz existuje!", str(order_form.errors["order_number"]))

        mock_error_message.assert_called_once()
        args, kwargs = mock_error_message.call_args
        self.assertEqual(args[1], "Nastala chyba při ukládání objednávky.")

    @patch("django.contrib.messages.success")
    def test_successful_order_creation_without_articles(self, mock_success_message):
        """
        Testuje úspěšné vytvoření objednávky s klientem, ale bez článků.
        Používá validní data vytvořená v setUp.
        """

        initial_order_count = Order.objects.count()
        initial_client_count = Client.objects.count()
        initial_article_count = Article.objects.count()

        # Kombinujeme data pro POST - validní Order a Client, prázdný formset
        # Zajistíme unikátní order_number pro tento test
        order_data = self.valid_order_data.copy()
        order_data["order_number"] = "703143100437749-R"
        post_data = {
            **self.valid_customer_data,
            **order_data,
            **self.formset_management_data,
        }

        response = self.client.post(self.url, post_data)
        created_order = Order.objects.latest("id")
        created_client = Client.objects.latest("id")

        self.assertEqual(response.status_code, 302)
        # Zkontrolujeme vazby

        self.assertEqual(response.status_code, 302)
        # Zkontrolujeme, že přesměrování je na URL detailu objednávky
        self.assertRedirects(
            response, reverse("order_detail", kwargs={"pk": created_order.pk})
        )

        self.assertEqual(Order.objects.count(), initial_order_count + 1)
        self.assertEqual(Client.objects.count(), initial_client_count + 1)
        self.assertEqual(Article.objects.count(), initial_article_count)

        self.assertEqual(created_order.client, created_client)
        self.assertEqual(created_order.articles.count(), 0)
        self.assertEqual(created_order.distrib_hub, self.hub)
        self.assertEqual(created_order.team, self.team)
        self.assertEqual(created_order.status, self.valid_status_key)
        self.assertEqual(created_order.team_type, self.valid_team_type_key)

        mock_success_message.assert_called_once()
        args, kwargs = mock_success_message.call_args
        self.assertEqual(args[1], "Objednávka vytvořena.")


class OrdersAllViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.url = reverse("orders")
        self.hub = DistribHub.objects.create(code="626", city="Chrastany")
        self.template = "app_sprava_montazi/orders/orders_all.html"
        self.client.login(username="testuser", password="testpass")
        self.range: int = 50

        # Vytvoříme  objednávky
        # status new
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Franta test-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"{i:05}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2024, 1, 1),
                delivery_termin=date(2024, 4, 10),
                montage_termin=timezone.make_aware(datetime(2024, 5, 20, 8, 0)),
                status=Status.NEW,
                team_type=TeamType.BY_ASSEMBLY_CREW,
            )
        # status adviced
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Ferda test-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"{i:06}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2024, 2, 2),
                delivery_termin=date(2024, 3, 4),
                montage_termin=timezone.make_aware(datetime(2024, 4, 10, 10, 0)),
                status=Status.ADVICED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
            )
        # OD 701
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Karel test-{i}", zip_code=f"321{i:02}"
            )
            Order.objects.create(
                order_number=f"701{i:05}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2024, 2, 2),
                delivery_termin=date(2024, 3, 4),
                montage_termin=timezone.make_aware(datetime(2024, 4, 10, 10, 0)),
                status=Status.REALIZED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
            )

    def test_filter_by_status_new(self):
        """filtruje status NEW"""
        response = self.client.get(self.url, {"status": "New"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["orders"]), self.range)
        self.assertNotEqual(len(response.context["orders"]), 20)
        for order in response.context["orders"]:
            self.assertEqual(order.status, "New")

    def test_filter_by_status_adviced(self):
        """filtruje status Adviced"""
        response = self.client.get(self.url, {"status": "Adviced"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["orders"]), self.range)
        self.assertNotEqual(len(response.context["orders"]), 20)
        for order in response.context["orders"]:
            self.assertEqual(order.status, "Adviced")

    def test_filter_by_status_realized(self):
        """Filtruje status Realized"""
        response = self.client.get(self.url, {"status": "Realized"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["orders"]), self.range)
        self.assertNotEqual(len(response.context["orders"]), 20)
        for order in response.context["orders"]:
            self.assertEqual(order.status, "Realized")

    def test_filter_by_status_od_701(self):
        """Filtruje OD 701"""
        response = self.client.get(self.url, {"od": "701"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["orders"]), self.range)
        for order in response.context["orders"]:
            self.assertTrue(order.order_number.startswith("701"))

    def test_filter_by_start_date(self):
        response = self.client.get(self.url, {"start_date": "2024-01-10"})
        self.assertEqual(response.status_code, 200)
        for order in response.context["orders"]:
            self.assertGreaterEqual(order.evidence_termin, date(2024, 1, 10))

    def test_filter_by_end_date(self):
        response = self.client.get(self.url, {"end_date": "2024-01-10"})
        self.assertEqual(response.status_code, 200)
        for order in response.context["orders"]:
            self.assertLessEqual(order.evidence_termin, date(2024, 1, 10))

    def test_combined_filters(self):
        response = self.client.get(
            self.url,
            {
                "status": "New",
                "od": "703",
                "start_date": "2024-01-01",
                "end_date": "2024-01-30",
            },
        )
        self.assertEqual(response.status_code, 200)
        for order in response.context["orders"]:
            self.assertEqual(order.status, "New")
            self.assertTrue(order.order_number.startswith("703"))
            self.assertGreaterEqual(order.evidence_termin, date(2024, 1, 1))
            self.assertLessEqual(order.evidence_termin, date(2024, 1, 30))

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_orders_all_view(self):
        """
        Test pro zobrazení všech objednávek.
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")


class TeamsViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.url = reverse("teams")
        self.template = "app_sprava_montazi/teams/teams_all.html"

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
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


class TeamCreateTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.url = reverse("team_create")
        self.template = "app_sprava_montazi/teams/team_form.html"

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
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

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
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


class ClientOrdersViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.customer = Client.objects.create(name="Franta Pina", zip_code="12345")
        self.url = reverse("client_orders", kwargs={"slug": self.customer.slug})
        self.template = "app_sprava_montazi/orders/client_orders.html"
        self.client.login(username="testuser", password="testpass")

    def test_logged_in(self):
        """
        Testuje, zda přihlášený uživatel úspěšně získá indexovou stránku
        a je použita správná šablona.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        """
        Testuje, zda je uživatel přesměrován na přihlašovací stránku,
        pokud není přihlášen a pokusí se zobrazit indexovou stránku.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")
