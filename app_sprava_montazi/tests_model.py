"""Model testy"""

from datetime import date
from django.test import TestCase
from django.db import IntegrityError
from django.utils.text import slugify
from django.utils import timezone
from .models import DistribHub, Client, Order, Team, Status, TeamType
from .models import Article


class DistribHubModelTest(TestCase):
    def setUp(self):
        self.hub = DistribHub.objects.create(code="111", city="Praha")

    def test_distrib_hub_creation(self):
        """
        Testuje vytvoření instance modelu DistribHub.
        """
        distrib_hub = self.hub
        self.assertTrue(isinstance(distrib_hub, DistribHub))
        self.assertEqual(distrib_hub.code, "111")
        self.assertEqual(distrib_hub.city, "Praha")
        self.assertEqual(self.hub.slug, "111-praha")

    def test_distrib_hub_unique_code(self):
        """je to unique? code"""
        with self.assertRaises(Exception):
            DistribHub.objects.create(code="111", city="Opava")

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
    def test_client_creation(self):
        """
        Testuje vytvoření nové instance modelu Client a ověřuje, že hodnoty polí jsou správně nastaveny.
        """
        client = Client.objects.create(
            name="Pavel Dvořák",
            street="Hlavní 123",
            city="Praha",
            zip_code="10000",
            phone="777123456",
            email="pavel.dvorak@example.com",
        )
        self.assertTrue(isinstance(client, Client))
        self.assertEqual(client.name, "Pavel Dvořák")
        self.assertEqual(client.city, "Praha")
        self.assertEqual(client.zip_code, "10000")
        self.assertEqual(client.phone, "777123456")
        self.assertEqual(client.email, "pavel.dvorak@example.com")
        self.assertEqual(client.first_15(), "Pavel Dvořák")

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


class OrderModelTestV1(TestCase):
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


class ArticleModelTestV1(TestCase):
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

    def test_article_creation(self):
        """
        Testuje vytvoření instance modelu Article.
        """
        article = Article.objects.create(
            order=self.order,
            name="Postel",
            price=1000.00,
            quantity=1,
            note="Standardní postel",
        )
        self.assertTrue(isinstance(article, Article))
        self.assertEqual(article.name, "Postel")
        self.assertEqual(article.price, 1000.00)
        self.assertEqual(article.quantity, 1)
        self.assertIsInstance(article.quantity, int)
        self.assertIsInstance(article.price, float)
        self.assertEqual(article.note, "Standardní postel")

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

    def test_team_creation(self):
        """Team creation"""
        team = self.team
        self.assertTrue(isinstance(team, Team))
        self.assertEqual(team.name, "Test Company")
        self.assertEqual(team.city, "Praha")
        self.assertEqual(team.region, "Střední Čechy")
        self.assertEqual(team.email, "test@company.cz")
        self.assertEqual(team.phone, "123456789")
        self.assertEqual(team.price_per_hour, 150.50)
        self.assertEqual(team.price_per_km, 12.30)
        self.assertEqual(team.notes, "Toto je testovací poznámka.")
        self.assertEqual(team.first_15(), "Toto je testova...")
        self.assertEqual(team.price_per_hour_float(), 150.50)
        self.assertEqual(team.price_per_km_float(), 12.30)
        self.assertIsInstance(team.price_per_hour_float(), float)
        self.assertIsInstance(team.price_per_km_float(), float)
        self.assertTrue(team.active)
        self.assertIsInstance(team.active, bool)

    def test_team_unique_name(self):
        """
        Testuje, že nelze vytvořit dva týmy se stejným názvem (name).
        """
        Team.objects.create(name="Gamma Team", city="Plzeň")
        with self.assertRaises(Exception):
            Team.objects.create(name="Gamma Team", city="Karlovy Vary")

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


class OrderModelTestV2(TestCase):
    @classmethod
    def setUpTestData(cls):
        DistribHub.objects.create(code="CB", city="České Budějovice")
        Client.objects.create(name="Jan Novák", zip_code="11150")
        Team.objects.create(name="Alfa Team", city="České Budějovice", active=True)

    def test_order_creation(self):
        """
        Testuje vytvoření nové objednávky (Order) s předdefinovanými hodnotami.
        """
        distrib_hub = DistribHub.objects.get(code="CB")
        client = Client.objects.get(name="Jan Novák")
        team = Team.objects.get(name="Alfa Team")
        order = Order.objects.create(
            order_number="12345",
            distrib_hub=distrib_hub,
            mandant="ABC",
            status=Status.NEW,
            client=client,
            delivery_termin=timezone.now().date(),
            evidence_termin=timezone.now().date(),
            montage_termin=timezone.now(),
            team_type=TeamType.BY_ASSEMBLY_CREW,
            team=team,
            notes="Testovací poznámka",
        )
        self.assertTrue(isinstance(order, Order))
        self.assertEqual(order.order_number, "12345")
        self.assertEqual(order.distrib_hub, distrib_hub)
        self.assertIsInstance(order.distrib_hub, DistribHub)
        self.assertEqual(order.mandant, "ABC")
        self.assertEqual(order.status, Status.NEW)
        self.assertEqual(order.client, client)
        self.assertIsInstance(order.client, Client)
        self.assertEqual(order.team_type, TeamType.BY_ASSEMBLY_CREW)
        self.assertEqual(order.team, team)
        self.assertIsInstance(order.team, Team)
        self.assertEqual(order.notes, "Testovací poznámka")
        if order.team is not None:
            self.assertEqual(order.team.price_per_km_float(), 0.0)
            self.assertEqual(order.team.price_per_hour_float(), 0.0)
            self.assertEqual(order.team.slug, "alfa-team")
        else:
            self.assertIsNone(order.team)

    def test_notes_first_10_method(self):
        """
        Testuje metodu `notes_first_10` modelu Order.
        - Pokud poznámka není zadána, vrací znak "-".
        """
        order_short_notes = Order.objects.create(
            order_number="67890",
            distrib_hub=DistribHub.objects.get(code="CB"),
            mandant="DEF",
            notes="Short",
            evidence_termin=timezone.now().date(),
        )
        self.assertEqual(order_short_notes.notes_first_10(), "Short")

        order_long_notes = Order.objects.create(
            order_number="11223",
            distrib_hub=DistribHub.objects.get(code="CB"),
            evidence_termin=timezone.now().date(),
            mandant="GHI",
            notes="This is a very long note",
        )
        self.assertEqual(order_long_notes.notes_first_10(), "This is a ...")

        order_no_notes = Order.objects.create(
            order_number="44556",
            evidence_termin=timezone.now().date(),
            distrib_hub=DistribHub.objects.get(code="CB"),
            mandant="JKL",
        )
        self.assertEqual(order_no_notes.notes_first_10(), "-")

    def test_is_missing_team_method(self):
        """
        Testuje metodu is_missing_team u modelu Order.
        Ověřuje, že metoda vrací True, pokud je typ týmu BY_ASSEMBLY_CREW a tým není přiřazen,
        a vrací False v ostatních případech.
        """
        order_with_team = Order.objects.create(
            order_number="77889",
            distrib_hub=DistribHub.objects.get(code="CB"),
            mandant="MNO",
            evidence_termin=timezone.now().date(),
            team_type=TeamType.BY_ASSEMBLY_CREW,
            team=Team.objects.get(name="Alfa Team"),
        )
        self.assertFalse(order_with_team.is_missing_team())

        order_without_team = Order.objects.create(
            order_number="00112",
            distrib_hub=DistribHub.objects.get(code="CB"),
            evidence_termin=timezone.now().date(),
            mandant="PQR",
            team_type=TeamType.BY_ASSEMBLY_CREW,
            team=None,
        )
        self.assertTrue(order_without_team.is_missing_team())

        order_different_team_type = Order.objects.create(
            order_number="33445",
            distrib_hub=DistribHub.objects.get(code="CB"),
            mandant="STU",
            evidence_termin=timezone.now().date(),
            team_type=TeamType.BY_CUSTOMER,
            team=None,
        )
        self.assertFalse(order_different_team_type.is_missing_team())

    def test_order_unique_order_number(self):
        """
        Testuje, že není možné vytvořit dvě objednávky (Order) se stejným číslem objednávky (order_number).
        """
        DistribHub.objects.create(code="LM", city="Liberec")
        Order.objects.create(
            order_number="unique1",
            evidence_termin=timezone.now().date(),
            distrib_hub=DistribHub.objects.get(code="LM"),
            mandant="VWX",
        )
        with self.assertRaises(Exception):
            Order.objects.create(
                order_number="unique1",
                evidence_termin=timezone.now().date(),
                distrib_hub=DistribHub.objects.get(code="LM"),
                mandant="YZA",
            )

    def test_order_ordering(self):
        """
        Testuje, zda jsou objednávky (Order) správně seřazeny podle čísla objednávky (order_number) v sestupném pořadí.
        """
        DistribHub.objects.create(code="PL", city="Plzeň")
        Order.objects.create(
            order_number="300",
            evidence_termin=timezone.now().date(),
            distrib_hub=DistribHub.objects.get(code="PL"),
            mandant="BBB",
        )
        Order.objects.create(
            order_number="100",
            evidence_termin=timezone.now().date(),
            distrib_hub=DistribHub.objects.get(code="PL"),
            mandant="AAA",
        )
        Order.objects.create(
            order_number="200",
            evidence_termin=timezone.now().date(),
            distrib_hub=DistribHub.objects.get(code="PL"),
            mandant="CCC",
        )
        orders = Order.objects.all()
        self.assertEqual(
            list(orders.values_list("order_number", flat=True)), ["300", "200", "100"]
        )
