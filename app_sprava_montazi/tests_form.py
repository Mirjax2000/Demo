"""Form testy"""

from django.test import TestCase
from .forms import ClientForm, DistribHubForm, OrderForm, ArticleForm, TeamForm
from .models import DistribHub, Order, Team, Status, TeamType


class ClientFormTest(TestCase):
    def test_valid_data(self):
        """
        Testuje, zda formulář ClientForm je platný při zadání správných dat.
        """
        form = ClientForm(
            data={
                "name": "Jan Novák",
                "street": "Hlavní",
                "city": "Praha",
                "zip_code": "10000",
                "phone": "212345678",
                "email": "jan@example.com",
            }
        )
        self.assertTrue(form.is_valid())

    def test_missing_required_field_name(self):
        """
        Testuje, zda formulář ClientForm je neplatny při zadání nesprávných dat.
        """
        form = ClientForm(
            data={
                "name": "",
                "street": "Hlavní",
                "city": "Praha",
                "zip_code": "10000",
                "phone": "212345678",
                "email": "jan@example.com",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertEqual(form.errors["name"][0], "Jméno je povinné!")

    def test_invalid_email_format(self):
        """
        Testuje, zda formulář ClientForm správně detekuje neplatný formát e-mailové adresy.
        """
        form = ClientForm(
            data={
                "name": "Jan Novák",
                "street": "Hlavní",
                "city": "Praha",
                "zip_code": "10000",
                "phone": "212345678",
                "email": "špatnýemail",  # neplatný e-mail
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_zip_code_required(self):
        """
        Testuje, že pole 'zip_code' je ve formuláři ClientForm povinné.
        """
        form = ClientForm(
            data={
                "name": "Jan Novák",
                "street": "Hlavní",
                "city": "Praha",
                "zip_code": "",  # chybí PSČ
                "phone": "212345678",
                "email": "jan@example.com",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("zip_code", form.errors)
        self.assertEqual(form.errors["zip_code"][0], "PSČ je povinné!")

    def test_valid_client_form(self):
        form_data = {
            "name": "Eva Svobodová",
            "street": "Vedlejší 456",
            "city": "Brno",
            "zip_code": "60200",
            "phone": "737987654",
            "email": "eva.svobodova@example.com",
        }
        form = ClientForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_client_form_missing_required_fields(self):
        form_data: dict = {}
        form = ClientForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("zip_code", form.errors)

    def test_invalid_client_form_invalid_phone_format(self):
        form_data = {
            "name": "Test",
            "street": "Test",
            "city": "Test",
            "zip_code": "12345",
            "phone": "123",
            "email": "test@example.com",
        }
        form = ClientForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_invalid_client_form_long_name_city(self):
        """dlouha jmena, presah pres max-length"""
        long_name = "a" * 80
        long_city = "a" * 33
        form_data = {
            "name": long_name,
            "street": "Test",
            "city": long_city,
            "zip_code": "12345",
            "phone": "123456789",
            "email": "test@example.com",
        }
        form = ClientForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("city", form.errors)


class DistribHubFormTest(TestCase):
    def test_invalid_distrib_hub_form_missing_required_fields(self):
        """Prazdnej form"""
        form_data: dict = {}
        form = DistribHubForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("code", form.errors)
        self.assertIn("city", form.errors)

    def test_invalid_distrib_hub_form_long_city(self):
        """Presah pres max-length"""
        long_string = "a" * 33
        form_data = {"code": "TES", "city": long_string}
        form = DistribHubForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("city", form.errors)

    def test_invalid_distrib_hub_form_duplicate_code(self):
        """Duplicate"""
        DistribHub.objects.create(code="ZLN", city="Zlín")
        form_data = {"code": "ZLN", "city": "Another City"}
        form = DistribHubForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("code", form.errors)

    def test_valid_form(self):
        """
        Testuje, zda je formulář DistribHubForm platný při zadání správných dat.
        """
        form = DistribHubForm(
            data={
                "code": "A01",
                "city": "Brno",
            }
        )
        self.assertTrue(form.is_valid())

    def test_missing_code(self):
        """
        Testuje, zda formulář DistribHubForm správně vyžaduje pole 'code'.
        """
        form = DistribHubForm(
            data={
                "code": "",
                "city": "Brno",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("code", form.errors)
        self.assertEqual(form.errors["code"][0], "Kod je povinný!")

    def test_code_too_long(self):
        """
        Testuje, zda formulář DistribHubForm správně detekuje příliš dlouhý kód.
        """
        form = DistribHubForm(
            data={
                "code": "ABCDE",  # moc dlouhé
                "city": "Brno",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("code", form.errors)

    def test_duplicate_code(self):
        """
        Testuje, zda formulář DistribHubForm správně detekuje duplicitní kód distribučního hubu.
        """
        DistribHub.objects.create(code="A01", city="Praha")
        form = DistribHubForm(
            data={
                "code": "A01",  # duplicitní
                "city": "Brno",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("code", form.errors)
        self.assertEqual(form.errors["code"][0], "Tento kod uz existuje!")

    def test_missing_city(self):
        """
        Testuje, zda formulář DistribHubForm správně detekuje chybějící hodnotu pole 'city'.
        """
        form = DistribHubForm(
            data={
                "code": "B01",
                "city": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("city", form.errors)
        self.assertEqual(form.errors["city"][0], "Jméno je povinné!")


class OrderFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        DistribHub.objects.create(code="PHA", city="Praha")
        Team.objects.create(name="Omega Team", city="Praha", active=True)

    def test_valid_order_form(self):
        """
        Testuje, zda je formulář OrderForm platný při zadání správných dat.
        """
        form_data = {
            "order_number": "54321",
            "distrib_hub": DistribHub.objects.get(code="PHA").id,
            "mandant": "DEF",
            "status": Status.NEW,
            "delivery_termin": "2025-05-10",
            "evidence_termin": "2025-05-09",
            "montage_termin": "2025-05-11 10:00",
            "team_type": TeamType.BY_ASSEMBLY_CREW,
            "team": Team.objects.get(name="Omega Team").id,
            "notes": "Další testovací poznámka",
        }
        form = OrderForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_order_form_missing_required_fields(self):
        """prazdnej form"""
        form_data: dict = {}
        form = OrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("order_number", form.errors)
        self.assertIn("distrib_hub", form.errors)
        self.assertIn("mandant", form.errors)
        self.assertIn("evidence_termin", form.errors)

    def test_invalid_order_form_duplicate_order_number(self):
        DistribHub.objects.create(code="KVK", city="Karlovy Vary")
        Order.objects.create(
            order_number="duplicate",
            mandant="GHI",
            distrib_hub=DistribHub.objects.get(code="KVK"),
            evidence_termin="2025-05-09",
        )
        form_data = {
            "order_number": "duplicate",
            "distrib_hub": DistribHub.objects.get(code="PHA").id,
            "mandant": "JKL",
            "evidence_termin": "2025-05-15",
        }
        form = OrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("order_number", form.errors)

    def test_order_form_default_values(self):
        """Defoultni hodnoty"""
        form = OrderForm()
        self.assertEqual(form.fields["team_type"].initial, TeamType.BY_ASSEMBLY_CREW)
        self.assertEqual(form.fields["status"].initial, Status.NEW)


class ArticleFormTest(TestCase):
    def test_valid_article_form(self):
        form_data = {
            "name": "Postel",
            "price": 1000.00,
            "quantity": 1,
            "note": "Dobra postel",
        }
        form = ArticleForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_article_form_missing_required_fields(self):
        form_data: dict = {}
        form = ArticleForm(data=form_data)
        self.assertFalse(form.is_valid())


class TeamFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Team.objects.create(name="Ferda Team", city="Praha")

    def test_valid_team_form(self):
        """Validni form"""
        form_data = {
            "name": "New Team",
            "city": "Berlin",
            "region": "Jihoceksy kraj",
            "phone": "232456789",
            "email": "new@example.com",
            "active": True,
            "price_per_hour": 250.00,
            "price_per_km": 8.00,
            "notes": "Spolehlivy tym",
        }
        form = TeamForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_team_form_missing_required_fields(self):
        """Prazdnej form"""
        form_data: dict = {}
        form = TeamForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("city", form.errors)
        self.assertIn("phone", form.errors)

    def test_invalid_team_form_long_name_city(self):
        """presah pres max-length"""
        long_string = "a" * 33
        form_data = {"name": long_string, "city": long_string, "phone": "123456789"}
        form = TeamForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("city", form.errors)

    def test_invalid_team_form_duplicate_name(self):
        form_data = {"name": "Ferda Team", "city": "New City", "phone": "987654321"}
        form = TeamForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
