"""Model testy"""

from datetime import date
from django.test import TestCase
from django.db import IntegrityError
from django.utils.text import slugify
from .models import DistribHub, Order, Team, TeamType, Article, Status, Client


class DistribHubModelTest(TestCase):
    def setUp(self):
        self.hub = DistribHub.objects.create(code="111", city="Praha")

    def test_slug_is_generated_correctly(self):
        """
        Testuje správné generování slug hodnoty pro Hub objekt.
        """
        self.assertEqual(self.hub.slug, "111-praha")

    def test_slug_and_code_are_unique(self):
        """
        Test na kontrolu unikátnosti kódu distribučního hubu.
        """
        with self.assertRaises(IntegrityError):
            DistribHub.objects.create(code="111", city="Praha")
            DistribHub.objects.create(code="111", city="Praha-1")

    def test_slug_with_special_characters(self):
        """Test správného vytvoření slug hodnoty obsahující diakritiku."""
        special = DistribHub.objects.create(code="222", city="České Budějovice")
        self.assertEqual(special.slug, "222-ceske-budejovice")


class ClientModelTests(TestCase):
    def test_incomplete_field_true_when_data_missing(self):
        """
        Testuje, že pole 'incomplete' je True, pokud chybí některá povinná data klienta.
        """
        client = Client.objects.create(name="Franta Pina", zip_code="12345")
        self.assertTrue(client.incomplete)

    def test_incomplete_field_false_when_all_data_present(self):
        """
        Testuje, že pole 'incomplete' je False, pokud jsou u klienta vyplněna všechna potřebná data.
        """
        client = Client.objects.create(
            name="Franta Pina",
            street="Ulice 1",
            city="Město",
            zip_code="54321",
            phone="+420123456789",
        )
        self.assertFalse(client.incomplete)

    def test_slug_is_created_correctly(self):
        """
        Testuje, že slug je správně vytvořen při uložení klienta.
        """
        client = Client.objects.create(
            name="Jan Novák", street="Hlavní", city="Praha", zip_code="10000"
        )
        expected_slug = slugify("Jan NovákPrahaHlavní")
        self.assertEqual(client.slug, expected_slug)

    def test_first_15_short_name(self):
        """
        Testuje, zda metoda first_15 vrací správně zkrácené jméno klienta, pokud je jeho délka kratší nebo rovna 15 znakům.
        """
        client = Client.objects.create(name="Krátké jméno", zip_code="12345")
        self.assertEqual(client.first_15(), "Krátké jméno")

    def test_first_15_long_name(self):
        """
        Testuje metodu `first_15()` modelu Client, která by měla vrátit prvních 15 znaků jména klienta následovaných třemi tečkami, pokud je jméno delší než 15 znaků.
        """
        client = Client.objects.create(
            name="Toto je opravdu dlouhé jméno", zip_code="12345"
        )
        self.assertEqual(client.first_15(), "Toto je opravdu...")

    def test_str_method(self):
        """
        Testuje, že metoda __str__ vrací správné jméno klienta.
        """
        client = Client.objects.create(name="Alena Testovka", zip_code="00000")
        self.assertEqual(str(client), "Alena Testovka")


class OrderModelTest(TestCase):
    def setUp(self):
        # Základní DistribHub pro testy
        self.hub = DistribHub.objects.create(code="111", city="Praha")
        self.customer = Client.objects.create(name="Pedro Pascal", zip_code="12345")

    def test_is_missing_team_true(self):
        """Test kdyz team je None tak vrat True."""
        order = Order.objects.create(
            order_number="703777143100437749-R",
            distrib_hub=self.hub,
            status=Status.NEW,
            client=self.customer,
            mandant="SCCZ",
            evidence_termin=date.today(),
            team_type=TeamType.BY_ASSEMBLY_CREW,
            team=None,
        )
        self.assertTrue(order.is_missing_team())

    def test_is_missing_team_false_with_team(self):
        """Test kdyz team je 'Company' tak vrat False."""
        team = Team.objects.create(
            name="Ferda comp",
            city="Praha",
            phone="+420123456789",
        )
        order = Order.objects.create(
            order_number="703777143100437750-R",
            distrib_hub=self.hub,
            mandant="SCCZ",
            client=self.customer,
            status=Status.NEW,
            evidence_termin=date.today(),
            team_type=TeamType.BY_ASSEMBLY_CREW,
            team=team,
        )
        self.assertFalse(order.is_missing_team())

    def test_is_missing_team_false_with_other_type(self):
        """Test kdyz team je None ale team type je mimo montazni team."""
        order = Order.objects.create(
            order_number="703777143100437751-R",
            distrib_hub=self.hub,
            mandant="SCCZ",
            client=self.customer,
            status=Status.NEW,
            evidence_termin=date.today(),
            team_type=TeamType.BY_CUSTOMER,
            team=None,
        )
        self.assertFalse(order.is_missing_team())

    def test_notes_first_10_long_note(self):
        """
        Testuje metodu `notes_first_10` modelu Order, která by měla vracet prvních 10 znaků poznámky
        """
        order = Order.objects.create(
            order_number="703777143100437751-R",
            distrib_hub=self.hub,
            mandant="SCCZ",
            client=self.customer,
            status=Status.NEW,
            delivery_termin=date.today(),
            evidence_termin=date.today(),
            notes="Toto je opravdu dlouhá poznámka",
        )
        self.assertEqual(order.notes_first_10(), "Toto je op...")

    def test_notes_first_10_short_note(self):
        """
        Testuje metodu `notes_first_10` modelu Order, která by měla vrátit prvních 10 znaků poznámky (notes).
        """
        order = Order.objects.create(
            order_number="703777143100437751-R",
            distrib_hub=self.hub,
            mandant="SCCZ",
            status=Status.NEW,
            client=self.customer,
            delivery_termin=date.today(),
            evidence_termin=date.today(),
            notes="Krátké",
        )
        self.assertEqual(order.notes_first_10(), "Krátké")

    def test_notes_first_10_empty_note(self):
        """
        Testuje metodu `notes_first_10` modelu Order pro případ, kdy je poznámka prázdná.
        Očekává se, že metoda vrátí znak "-", pokud pole `notes` neobsahuje žádný text.
        """
        order = Order.objects.create(
            order_number="703777143100437751-R",
            distrib_hub=self.hub,
            mandant="SCCZ",
            status=Status.NEW,
            client=self.customer,
            delivery_termin=date.today(),
            evidence_termin=date.today(),
            notes="",
        )
        self.assertEqual(order.notes_first_10(), "-")


class ArticleModelTest(TestCase):
    def setUp(self):
        self.hub = DistribHub.objects.create(code="111", city="Praha")
        self.customer = Client.objects.create(name="ferda", zip_code="12345")
        self.order = Order.objects.create(
            order_number="703777143100437751-R",
            distrib_hub=self.hub,
            mandant="SCCZ",
            client=self.customer,
            status=Status.NEW,
            evidence_termin=date.today(),
            team_type=TeamType.BY_CUSTOMER,
            team=None,
        )

    def test_article_str_returns_name(self):
        """
        Testuje, zda metoda __str__ modelu Article vrací správně hodnotu pole name.
        """
        article = Article.objects.create(
            order=self.order,
            name="Test Artikl",
            price=10000,
            quantity=1,
            note="Nějaká poznámka dlouha poznamka o articlu",
        )
        self.assertEqual(str(article), "Test Artikl")

    def test_first_15_with_short_note(self):
        """
        Testuje metodu first_15 třídy Article, která by měla vrátit poznámku (note), pokud je její délka kratší nebo rovna 15 znakům.
        """

        article = Article.objects.create(
            order=self.order, name="Krátký", price=50, quantity=2, note="Krátká pozn."
        )
        self.assertEqual(article.first_15(), "Krátká pozn.")

    def test_first_15_with_long_note(self):
        """
        Testuje metodu `first_15` modelu Article, která by měla vracet prvních 15 znaků z poznámky
        """
        article = Article.objects.create(
            order=self.order,
            name="Dlouhý",
            price=80,
            quantity=1,
            note="Tato poznámka je opravdu dlouhá",
        )
        self.assertEqual(article.first_15(), "Tato poznámka j...")

    def test_first_15_with_empty_note(self):
        """
        Testuje metodu `first_15` modelu Article, když je poznámka (`note`) prázdná.
        Očekává se, že metoda vrátí znak "-", pokud pole poznámky neobsahuje žádný text.
        """
        article = Article.objects.create(
            order=self.order, name="Bez poznámky", price=20, quantity=1, note=""
        )
        self.assertEqual(article.first_15(), "-")


class TeamModelTest(TestCase):
    def setUp(self):
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

    def test_str_representation(self):
        """✅ Testuje, že metoda __str__ vrací název společnosti."""
        self.assertEqual(str(self.team), "Test Company")

    def test_slug_is_generated_on_save(self):
        """✅ Testuje, že slug se automaticky vygeneruje ze jména při uložení."""
        self.assertEqual(self.team.slug, slugify(self.team.name))

    def test_price_per_km_float_conversion(self):
        """✅ Testuje, že metoda price_per_km_float vrací správně převedenou hodnotu z
        Decimal na float."""
        self.assertEqual(self.team.price_per_km_float(), 12.30)

    def test_price_per_km_float_default(self):
        """✅ Testuje, že metoda price_per_km_float
        vrátí 0.0 pokud není cena za km nastavena."""
        self.team.price_per_km = None
        self.assertEqual(self.team.price_per_km_float(), 0.0)

    def test_price_per_hour_float_conversion(self):
        """✅ Testuje, že metoda price_per_hour_float vrací
        správně převedenou hodnotu z Decimal na float."""
        self.assertEqual(self.team.price_per_hour_float(), 150.50)

    def test_price_per_hour_float_default(self):
        """✅ Testuje, že metoda price_per_hour_float vrátí 0.0 pokud
        není cena za hodinu nastavena."""
        self.team.price_per_hour = None
        self.assertEqual(self.team.price_per_hour_float(), 0.0)

    def test_first_15_with_long_note(self):
        """✅ Testuje, že metoda first_15 vrátí prvních 15 znaků poznámky
        s tečkami, pokud je delší než 15 znaků."""
        self.assertEqual(self.team.first_15(), "Toto je testova...")

    def test_first_15_with_short_note(self):
        """✅ Testuje, že metoda first_15 vrátí celou poznámku,
        pokud má 15 znaků nebo méně."""
        self.team.notes = "Krátká poznámka"
        self.assertEqual(self.team.first_15(), "Krátká poznámka")

    def test_first_15_with_empty_note(self):
        """✅ Testuje, že metoda first_15 vrátí '-'
        pokud poznámka není nastavena."""
        self.team.notes = ""
        self.assertEqual(self.team.first_15(), "-")

    def test_unique_name_constraint(self):
        """✅ Testuje, že nelze vytvořit dvě společnosti se stejným názvem."""
        with self.assertRaises(Exception):
            Team.objects.create(name="Test Company", city="Brno", phone="987654321")
