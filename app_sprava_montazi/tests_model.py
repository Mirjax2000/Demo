"""Model testy"""

from datetime import date, timedelta, datetime

from django.forms import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.db import models
from django.db import IntegrityError
from django.utils.text import slugify
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from .models import DistribHub, Client, Order, Team, Status, TeamType
from .models import Article, CallLog, Upload, AdviceStatus

User = get_user_model()


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

    def test_model_field_types(self) -> None:
        """Ověří, že pole jsou typu CharField."""
        code_field = DistribHub._meta.get_field("code")
        city_field = DistribHub._meta.get_field("city")
        slug_field = DistribHub._meta.get_field("slug")
        self.assertIsInstance(code_field, models.CharField)
        self.assertIsInstance(city_field, models.CharField)
        self.assertIsInstance(slug_field, models.SlugField)

    def test_field_max_lengths(self) -> None:
        """Ověří max_length u jednotlivých polí."""
        self.assertEqual(DistribHub._meta.get_field("code").max_length, 3)
        self.assertEqual(DistribHub._meta.get_field("city").max_length, 32)

    def test_unique_constraints(self) -> None:
        """Ověří, že pole code a slug mají unique=True."""
        code_field = DistribHub._meta.get_field("code")
        slug_field = DistribHub._meta.get_field("slug")
        self.assertTrue(code_field.unique)
        self.assertTrue(slug_field.unique)

    def test_slug_autogeneration_on_change(self) -> None:
        """Slug se změní, když se změní code nebo city."""
        self.hub.code = "222"
        self.hub.city = "Brno"
        self.hub.save()
        self.assertEqual(self.hub.slug, "222-brno")

    def test_blank_fields(self) -> None:
        """Strukturalni test"""
        self.assertFalse(DistribHub._meta.get_field("code").blank)
        self.assertFalse(DistribHub._meta.get_field("city").blank)
        self.assertTrue(DistribHub._meta.get_field("slug").blank)

    def test_str_method(self):
        """Test __str__ metody."""
        self.assertEqual(str(self.hub), "111-Praha")


class ClientModelTests(TestCase):
    def test_field_types(self):
        """Strukturalni test"""
        self.assertIsInstance(Client._meta.get_field("name"), models.CharField)
        self.assertIsInstance(Client._meta.get_field("street"), models.CharField)
        self.assertIsInstance(Client._meta.get_field("city"), models.CharField)
        self.assertIsInstance(Client._meta.get_field("zip_code"), models.CharField)
        self.assertIsInstance(Client._meta.get_field("phone"), PhoneNumberField)
        self.assertIsInstance(Client._meta.get_field("email"), models.EmailField)
        self.assertIsInstance(Client._meta.get_field("incomplete"), models.BooleanField)
        self.assertIsInstance(Client._meta.get_field("slug"), models.SlugField)

    def test_max_length_constraints(self):
        """Strukturalni test"""
        self.assertEqual(Client._meta.get_field("name").max_length, 75)
        self.assertEqual(Client._meta.get_field("street").max_length, 50)
        self.assertEqual(Client._meta.get_field("city").max_length, 32)
        self.assertEqual(Client._meta.get_field("zip_code").max_length, 5)
        self.assertEqual(Client._meta.get_field("phone").max_length, 17)

    def test_blank_fields(self):
        """Strukturalni test"""
        self.assertFalse(Client._meta.get_field("name").blank)
        self.assertTrue(Client._meta.get_field("street").blank)
        self.assertTrue(Client._meta.get_field("city").blank)
        self.assertFalse(Client._meta.get_field("zip_code").blank)
        self.assertTrue(Client._meta.get_field("phone").blank)
        self.assertTrue(Client._meta.get_field("email").blank)
        self.assertFalse(Client._meta.get_field("incomplete").blank)
        self.assertTrue(Client._meta.get_field("slug").blank)

    def test_verbose_names(self):
        """Strukturalni test"""
        self.assertEqual(Client._meta.get_field("name").verbose_name, "Jméno zákazníka")
        self.assertEqual(Client._meta.get_field("street").verbose_name, "Ulice")
        self.assertEqual(Client._meta.get_field("city").verbose_name, "Město")
        self.assertEqual(Client._meta.get_field("zip_code").verbose_name, "PSČ")
        self.assertEqual(Client._meta.get_field("phone").verbose_name, "Telefon")
        self.assertEqual(Client._meta.get_field("email").verbose_name, "E-mail")
        self.assertEqual(
            Client._meta.get_field("incomplete").verbose_name, "Neúplný záznam"
        )

    def test_client_creation(self):
        """
        Testuje vytvoření nové instance modelu Client a ověřuje, že hodnoty polí jsou správně nastaveny.
        """
        customer = Client.objects.create(
            name="Pavel Dvořák",
            street="Hlavní 123",
            city="Praha",
            zip_code="10000",
            phone="777123456",
            email="pavel.dvorak@example.com",
        )
        self.assertTrue(isinstance(customer, Client))
        self.assertEqual(customer.name, "Pavel Dvořák")
        self.assertEqual(customer.city, "Praha")
        self.assertEqual(customer.zip_code, "10000")
        self.assertEqual(customer.phone, "777123456")
        self.assertEqual(customer.email, "pavel.dvorak@example.com")
        self.assertEqual(customer.first_15(), "Pavel Dvořák")

    def test_incomplete_field_true_when_data_missing(self):
        """
        Testuje, že pole 'incomplete' je True, pokud chybí některá povinná data klienta.
        """
        customer = Client.objects.create(name="Franta Pina", zip_code="12345")
        self.assertTrue(customer.incomplete)

    def test_incomplete_field_false_when_all_data_present(self):
        """
        Testuje, že pole 'incomplete' je False, pokud jsou u klienta vyplněna všechna potřebná data.
        """
        customer = Client.objects.create(
            name="Franta Pina",
            street="Ulice 1",
            city="Město",
            zip_code="54321",
            phone="+420123456789",
        )
        self.assertFalse(customer.incomplete)

    def test_slug_is_created_correctly(self):
        """
        Testuje, že slug je správně vytvořen při uložení klienta.
        """
        customer = Client.objects.create(
            name="Jan Novák", street="Hlavní", city="Praha", zip_code="10000"
        )
        expected_slug = slugify("Jan NovákPrahaHlavní")
        self.assertEqual(customer.slug, expected_slug)

    def test_first_15_short_name(self):
        """
        Testuje, zda metoda first_15 vrací správně zkrácené jméno klienta, pokud je jeho délka kratší nebo rovna 15 znakům.
        """
        customer = Client.objects.create(name="Krátké jméno", zip_code="12345")
        self.assertEqual(customer.first_15(), "Krátké jméno")

    def test_first_15_long_name(self):
        """
        Testuje metodu `first_15()` modelu Client, která by měla vrátit prvních 15 znaků jména klienta následovaných třemi tečkami, pokud je jméno delší než 15 znaků.
        """
        customer = Client.objects.create(
            name="Toto je opravdu dlouhé jméno", zip_code="12345"
        )
        self.assertEqual(customer.first_15(), "Toto je opravdu...")

    def test_str_method(self):
        """
        Testuje, že metoda __str__ vrací správné jméno klienta.
        """
        customer = Client.objects.create(name="Alena Testovka", zip_code="00000")
        self.assertEqual(str(customer), "Alena Testovka")


class ClientMethodTests(TestCase):
    def setUp(self) -> None:
        self.customer = Client.objects.create(
            name="Franta Pina", zip_code="11155", phone="602234234"
        )

    def test_format_psc_and_phone_from_db(self):
        self.assertEqual(self.customer.format_psc(), "111 55")
        self.assertEqual(self.customer.format_phone(), "+420 602 234 234")

    def test_format_psc_with_valid_zip(self):
        client = Client(name="Ferda", zip_code="12345")
        self.assertEqual(client.format_psc(), "123 45")

    def test_format_psc_with_invalid_zip(self):
        client = Client(name="Ferda", zip_code="1234")
        self.assertEqual(client.format_psc(), "1234")

    def test_format_psc_with_empty_zip(self):
        client = Client(name="Ferda", zip_code="")
        self.assertEqual(client.format_psc(), "")

    def test_format_psc_with_none(self):
        client = Client(name="Ferda", zip_code=None)
        self.assertEqual(client.format_psc(), "")

    def test_format_phone_with_valid_number(self):
        client = Client(name="Ferda", phone="+420123456789")
        self.assertEqual(client.format_phone(), "+420 123 456 789")

    def test_format_phone_with_invalid_number(self):
        client = Client(name="Ferda", phone="123456789")
        self.assertEqual(client.format_phone(), "123456789")

    def test_format_phone_with_empty_number(self):
        client = Client(name="Ferda", phone="")
        self.assertEqual(client.format_phone(), "")

    def test_format_phone_with_none(self):
        client = Client(name="Ferda", phone=None)
        self.assertEqual(client.format_phone(), "")


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

    def test_format_datetime_none(self):
        """Test: Pokud je hodnota None, vrátí prázdný řetězec."""
        order = Order()
        self.assertEqual(order.format_datetime(None), "")

    def test_format_datetime_valid(self):
        """Test: Pokud je zadán validní datetime, vrátí správně naformátovaný text."""
        order = Order()
        dt = datetime(2024, 12, 24, 14, 30)  # Štědrý den odpoledne
        self.assertEqual(order.format_datetime(dt), "24.12.2024 / 14:30")

    def test_format_datetime_midnight(self):
        """Test: Kontrola půlnoci."""
        order = Order()
        dt = datetime(2025, 1, 1, 0, 0)
        self.assertEqual(order.format_datetime(dt), "01.01.2025 / 00:00")

    def test_datetime_from_order(self):
        montage_str = "01.01.2025 / 00:00"
        montage_dt = timezone.make_aware(
            datetime.strptime(montage_str, "%d.%m.%Y / %H:%M")
        )
        order = Order.objects.create(
            order_number="703777143100431151-R",
            distrib_hub=self.hub,
            mandant="SCCZ",
            status=Status.NEW,
            client=self.customer,
            delivery_termin=date.today(),
            evidence_termin=date.today(),
            montage_termin=montage_dt,
            notes="",
        )
        self.assertEqual(
            order.format_datetime(order.montage_termin), "01.01.2025 / 00:00"
        )


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

    def test_name_field(self):
        """Strukturlani test"""
        field = Article._meta.get_field("name")
        self.assertEqual(field.max_length, 32)

    def test_quantity_field(self):
        """Strukturalni test"""
        field = Article._meta.get_field("quantity")
        self.assertEqual(field.default, 1)

    def test_note_field(self):
        """Strukturalni test"""
        field = Article._meta.get_field("note")
        self.assertTrue(field.blank)

    def test_price_field(self):
        field = Article._meta.get_field("price")
        self.assertEqual(field.max_digits, 10)
        self.assertEqual(field.decimal_places, 2)
        self.assertTrue(field.null)
        self.assertTrue(field.blank)

    def test_order_field(self):
        """Strukturalni test"""
        field = Article._meta.get_field("order")
        self.assertEqual(field.related_model, Order)
        self.assertEqual(field.remote_field.on_delete, models.PROTECT)
        self.assertEqual(field.related_query_name(), "articles")

    def test_field_types(self):
        """Strukturalni test"""
        model = Article()

        self.assertIsInstance(model._meta.get_field("order"), models.ForeignKey)
        self.assertIsInstance(model._meta.get_field("name"), models.CharField)
        self.assertIsInstance(model._meta.get_field("price"), models.DecimalField)
        self.assertIsInstance(
            model._meta.get_field("quantity"), models.PositiveIntegerField
        )
        self.assertIsInstance(model._meta.get_field("note"), models.TextField)

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

    def test_field_attributes(self):
        """Strukturalni test"""
        field = Team._meta.get_field("name")
        self.assertTrue(field.unique)
        self.assertEqual(field.max_length, 32)

        self.assertEqual(Team._meta.get_field("city").max_length, 32)
        self.assertEqual(Team._meta.get_field("region").max_length, 32)

        self.assertEqual(Team._meta.get_field("phone").max_length, 17)
        self.assertEqual(Team._meta.get_field("email").max_length, 64)

        self.assertEqual(Team._meta.get_field("price_per_hour").max_digits, 6)
        self.assertEqual(Team._meta.get_field("price_per_hour").decimal_places, 2)

        self.assertEqual(Team._meta.get_field("price_per_km").max_digits, 6)
        self.assertEqual(Team._meta.get_field("price_per_km").decimal_places, 2)

        self.assertTrue(Team._meta.get_field("slug").unique)

    def test_field_types(self):
        """Strukturalni test"""
        model = Team()

        self.assertIsInstance(model._meta.get_field("name"), models.CharField)
        self.assertIsInstance(model._meta.get_field("city"), models.CharField)
        self.assertIsInstance(model._meta.get_field("region"), models.CharField)
        self.assertIsInstance(model._meta.get_field("phone"), PhoneNumberField)
        self.assertIsInstance(model._meta.get_field("email"), models.EmailField)
        self.assertIsInstance(model._meta.get_field("active"), models.BooleanField)
        self.assertIsInstance(
            model._meta.get_field("price_per_hour"), models.DecimalField
        )
        self.assertIsInstance(
            model._meta.get_field("price_per_km"), models.DecimalField
        )
        self.assertIsInstance(model._meta.get_field("notes"), models.TextField)
        self.assertIsInstance(model._meta.get_field("slug"), models.SlugField)

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
        cls.hub = DistribHub.objects.create(code="CB", city="České Budějovice")
        cls.customer = Client.objects.create(
            name="Jan Novák",
            zip_code="11150",
            phone="234234234",
            street="kopretinova 15",
            city="Praha",
        )
        cls.team = Team.objects.create(
            name="Alfa Team", city="České Budějovice", active=True
        )
        cls.incomplete_customer = Client.objects.create(
            name="Pavel Dvořák",
            zip_code="10000",
        )

    def _create_base_order_data(self, **kwargs):
        """Helper to create a base order dictionary."""
        data = {
            "order_number": "ORD-TEST",
            "distrib_hub": self.hub,
            "mandant": "SCCZ",
            "status": Status.NEW,
            "client": self.customer,
            "delivery_termin": timezone.now().date() + timedelta(days=3),
            "evidence_termin": timezone.now().date(),
            "montage_termin": timezone.now() + timedelta(days=3),
            "team_type": TeamType.BY_ASSEMBLY_CREW,
            "team": self.team,
        }
        data.update(kwargs)
        return data

    def test_order_creation(self):
        """
        Testuje vytvoření nové objednávky (Order) s předdefinovanými hodnotami.
        """
        distrib_hub = DistribHub.objects.get(code="CB")
        customer = Client.objects.get(name="Jan Novák")
        team = Team.objects.get(name="Alfa Team")
        order = Order.objects.create(
            order_number="12345",
            distrib_hub=distrib_hub,
            mandant="ABC",
            status=Status.NEW,
            client=customer,
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
        self.assertEqual(order.status, Status.ADVICED)
        self.assertEqual(order.client, customer)
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

    def test_zaterminovano_on_create_success(self):
        """
        Tests that status changes to ADVICED when all conditions are met on creation.
        """
        order_data = self._create_base_order_data(order_number="ORD001")
        order = Order.objects.create(**order_data)
        self.assertEqual(order.status, Status.ADVICED)

    def test_zaterminovano_on_create_missing_team_by_assembly_crew(self):
        """
        Tests that status remains NEW if team is missing for BY_ASSEMBLY_CREW on creation.
        """
        order_data = self._create_base_order_data(
            order_number="ORD002", team=None, team_type=TeamType.BY_ASSEMBLY_CREW
        )
        order = Order.objects.create(**order_data)
        self.assertEqual(order.status, Status.NEW)

    def test_zaterminovano_on_create_team_type_not_assembly_crew(self):
        """
        Tests that status changes to ADVICED even with no team if team_type is not BY_ASSEMBLY_CREW.
        """
        order_data = self._create_base_order_data(
            order_number="ORD003", team=None, team_type=TeamType.BY_CUSTOMER
        )
        order = Order.objects.create(**order_data)
        self.assertNotEqual(order.status, Status.ADVICED)

    def test_zaterminovano_on_create_not_new_status(self):
        """
        Tests that status remains unchanged if initial status is not NEW on creation.
        """
        order_1_data = self._create_base_order_data(
            order_number="ORD004", status=Status.REALIZED
        )
        order_2_data = self._create_base_order_data(
            order_number="ORD005", status=Status.ADVICED
        )
        order_3_data = self._create_base_order_data(
            order_number="ORD006", status=Status.NEW
        )

        order_1 = Order.objects.create(**order_1_data)
        self.assertEqual(order_1.status, Status.REALIZED)

        order_2 = Order.objects.create(**order_2_data)
        self.assertEqual(order_2.status, Status.ADVICED)

        order_3 = Order.objects.create(**order_3_data)
        self.assertEqual(order_3.status, Status.ADVICED)

    def test_zaterminovano_on_create_missing_client(self):
        """
        Tests that status remains NEW if client is missing on creation.
        """
        order_data = self._create_base_order_data(order_number="ORD005", client=None)
        order = Order.objects.create(**order_data)
        self.assertEqual(order.status, Status.NEW)

    def test_zaterminovano_on_create_incomplete_client(self):
        """
        Tests that status remains NEW if client is incomplete on creation.
        """
        order_data = self._create_base_order_data(
            order_number="ORD006", client=self.incomplete_customer
        )
        order = Order.objects.create(**order_data)
        self.assertEqual(order.status, Status.NEW)

    def test_zaterminovano_on_create_missing_montage_termin(self):
        """
        Tests that status remains NEW if montage_termin is missing on creation.
        """
        order_data = self._create_base_order_data(
            order_number="ORD007", montage_termin=None
        )
        order = Order.objects.create(**order_data)
        self.assertEqual(order.status, Status.NEW)

    def test_zaterminovano_on_create_missing_delivery_termin(self):
        """
        Tests that status remains NEW if delivery_termin is missing on creation.
        """
        order_data = self._create_base_order_data(
            order_number="ORD008", delivery_termin=None
        )
        order = Order.objects.create(**order_data)
        self.assertEqual(order.status, Status.NEW)

    def test_zaterminovano_on_update_success_from_new(self):
        """
        Tests that status changes to ADVICED when all conditions are met on update,
        starting from NEW status.
        """

        order = Order.objects.create(
            **self._create_base_order_data(order_number="ORD009", montage_termin=None)
        )
        self.assertEqual(order.status, Status.NEW)
        order.montage_termin = timezone.now() + timedelta(days=3)
        order.save()
        self.assertEqual(order.status, Status.ADVICED)

    def test_zaterminovano_on_update_no_change_if_not_new_status(self):
        """
        Tests that status does not change if it's already ADVICED (or other non-NEW)
        and other fields are updated.
        """
        order = Order.objects.create(
            **self._create_base_order_data(order_number="ORD010")
        )
        self.assertEqual(order.status, Status.ADVICED)

        order.notes = "Some new notes"
        order.save()
        self.assertEqual(order.status, Status.ADVICED)

        order.status = Status.BILLED
        order.save()
        self.assertEqual(order.status, Status.BILLED)

        order.status = Status.NEW
        order.team = None
        order.save()
        self.assertEqual(order.status, Status.NEW)

        order.team = self.team
        order.save()
        self.assertEqual(order.status, Status.ADVICED)


class CallLogModelTest(TestCase):
    def setUp(self):
        self.customer = Client.objects.create(name="Franta Pina test", zip_code="12345")
        self.user = User.objects.create_user(username="miros", password="testpass")

        self.call_log = CallLog.objects.create(
            client=self.customer,
            user=self.user,
            note="Called about the delivery.",
            was_successful="Success",
        )

    def test_field_types(self):
        self.assertIsInstance(CallLog._meta.get_field("client"), models.ForeignKey)
        self.assertIsInstance(CallLog._meta.get_field("user"), models.ForeignKey)
        self.assertIsInstance(
            CallLog._meta.get_field("called_at"), models.DateTimeField
        )
        self.assertIsInstance(CallLog._meta.get_field("note"), models.TextField)
        self.assertIsInstance(
            CallLog._meta.get_field("was_successful"), models.CharField
        )

    def test_user_relation(self):
        field = CallLog._meta.get_field("user")
        self.assertEqual(field.related_model, User)
        self.assertEqual(field.remote_field.on_delete, models.PROTECT)

    def test_called_at_auto_now_add(self):
        field = CallLog._meta.get_field("called_at")
        self.assertTrue(field.auto_now_add)

    def test_note_blank_allowed(self):
        field = CallLog._meta.get_field("note")
        self.assertTrue(field.blank)

    def test_client_relation(self):
        field = CallLog._meta.get_field("client")
        self.assertEqual(field.related_model, Client)
        self.assertEqual(field.remote_field.on_delete, models.PROTECT)

    def test_str_method(self):
        str_value = str(self.call_log)
        expected_prefix = f"{self.customer.name} - "
        self.assertTrue(str_value.startswith(expected_prefix))
        self.assertIn(self.call_log.called_at.strftime("%Y-%m-%d %H:%M"), str_value)

    def test_meta_ordering(self):
        self.assertEqual(CallLog._meta.ordering, ["-called_at"])

    def test_was_successful_choices(self):
        field = CallLog._meta.get_field("was_successful")
        self.assertEqual(field.choices, AdviceStatus.choices)
        self.assertEqual(field.max_length, 10)

    def test_calllog_creation_success(self):
        call_log = CallLog.objects.create(
            client=self.customer,
            user=self.user,
            note="Called about the delivery.",
            was_successful="Success",
        )
        self.assertTrue(isinstance(call_log, CallLog))
        self.assertEqual(call_log.client, self.customer)
        self.assertEqual(call_log.user, self.user)
        self.assertEqual(call_log.note, "Called about the delivery.")
        self.assertEqual(call_log.was_successful, "Success")
        self.assertIsNotNone(call_log.called_at)

    def test_calllog_creation_optional_note(self):
        call_log = CallLog.objects.create(
            client=self.customer,
            user=self.user,
            was_successful="Failed",
        )
        self.assertTrue(isinstance(call_log, CallLog))
        self.assertEqual(call_log.client, self.customer)
        self.assertEqual(call_log.user, self.user)
        self.assertEqual(call_log.note, "")
        self.assertEqual(call_log.was_successful, "Failed")
        self.assertIsNotNone(call_log.called_at)

    def test_calllog_required_fields(self):
        with self.assertRaises(Exception):
            CallLog.objects.create(
                note="This should fail",
                was_successful="Success",
                # client missing
                user=self.user,
            )
        with self.assertRaises(Exception):
            CallLog.objects.create(
                client=self.customer,
                was_successful="Success",
                # user missing
            )

    def test_calllog_invalid_was_successful_choice(self):
        with self.assertRaises(ValidationError) as cm:
            call_log = CallLog(
                client=self.customer,
                user=self.user,
                note="Trying invalid choice",
                was_successful="InvalidChoice",
            )
            call_log.full_clean()

        self.assertIn("was_successful", cm.exception.message_dict)

    def test_calllog_str_method(self):
        """
        Test, jestli metoda __str__ vrací očekávaný formát řetězce.
        """
        call_log = CallLog.objects.create(
            client=self.customer, user=self.user, was_successful="Success"
        )

        local_called_at_str = call_log.called_at.strftime("%Y-%m-%d %H:%M")
        expected_str = f"{self.customer.name} - {local_called_at_str}"

        self.assertEqual(str(call_log), expected_str)


class UploadModelStructureTest(TestCase):
    """Strukturlani testy"""

    def test_field_types(self):
        model = Upload()

        self.assertIsInstance(model._meta.get_field("file"), models.FileField)
        self.assertIsInstance(model._meta.get_field("created"), models.DateTimeField)

    def test_file_field_upload_to(self):
        field = Upload._meta.get_field("file")
        self.assertEqual(field.upload_to, "uploads/")

    def test_created_field_auto_now_add(self):
        field = Upload._meta.get_field("created")
        self.assertTrue(field.auto_now_add)

    def test_str_method_with_file(self):
        instance = Upload(file="uploads/test_file.txt")
        self.assertEqual(str(instance), "uploads/test_file.txt")

    def test_str_method_without_file(self):
        instance = Upload(file=None)
        self.assertEqual(str(instance), "No file")

    def test_meta_ordering(self):
        self.assertEqual(Upload._meta.ordering, ["-created"])


class OrderModelStructuralTest(TestCase):
    def test_fields(self):
        model = Order
        fields = model._meta.fields_map
        distrib_hub_field = model._meta.get_field("distrib_hub")

        self.assertIsInstance(model._meta.get_field("order_number"), models.CharField)
        self.assertTrue(model._meta.get_field("order_number").unique)
        self.assertEqual(
            model._meta.get_field("order_number").verbose_name, "Číslo zakázky"
        )

        self.assertIsInstance(model._meta.get_field("distrib_hub"), models.ForeignKey)
        self.assertEqual(distrib_hub_field.remote_field.on_delete, models.PROTECT)

        self.assertEqual(model._meta.get_field("mandant").verbose_name, "Mandant")
        self.assertEqual(model._meta.get_field("mandant").max_length, 4)

        self.assertEqual(model._meta.get_field("status").choices, Status.choices)
        self.assertEqual(model._meta.get_field("status").default, Status.NEW)

        self.assertIsInstance(model._meta.get_field("client"), models.ForeignKey)
        self.assertTrue(model._meta.get_field("client").null)
        self.assertTrue(model._meta.get_field("client").blank)

        self.assertIsInstance(
            model._meta.get_field("delivery_termin"), models.DateField
        )
        self.assertTrue(model._meta.get_field("delivery_termin").null)
        self.assertTrue(model._meta.get_field("delivery_termin").blank)

        self.assertIsInstance(
            model._meta.get_field("evidence_termin"), models.DateField
        )
        self.assertFalse(model._meta.get_field("evidence_termin").null)

        self.assertIsInstance(
            model._meta.get_field("montage_termin"), models.DateTimeField
        )
        self.assertTrue(model._meta.get_field("montage_termin").null)
        self.assertTrue(model._meta.get_field("montage_termin").blank)

        self.assertEqual(model._meta.get_field("team_type").choices, TeamType.choices)
        self.assertEqual(
            model._meta.get_field("team_type").default, TeamType.BY_ASSEMBLY_CREW
        )

        self.assertIsInstance(model._meta.get_field("team"), models.ForeignKey)
        self.assertTrue(model._meta.get_field("team").null)
        self.assertTrue(model._meta.get_field("team").blank)

        self.assertIsInstance(model._meta.get_field("notes"), models.TextField)
        self.assertTrue(model._meta.get_field("notes").blank)

    def test_str_method(self):
        obj = Order(order_number="ZK2025001")
        self.assertEqual(str(obj), "ZK2025001")

    def test_meta_ordering(self):
        self.assertEqual(Order._meta.ordering, ["-order_number"])
