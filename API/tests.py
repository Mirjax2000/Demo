from datetime import date, datetime
from django.utils import timezone

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from app_sprava_montazi.models import Order, Client, DistribHub, Status, TeamType, Team


class ApiStatusViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/status/"
        self.token_url = "/api-token-auth/"
        self.username = "testuser"
        self.password = "testpass"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )

        # ziskani tokenu
        response = self.client.post(
            self.token_url,
            {"username": self.username, "password": self.password},
            format="json",
        )

        # kontrola
        self.assertEqual(response.status_code, 200)
        self.token = response.data["token"]

    def test_api_status_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_api_status_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"api_status": "UP"})


class IncompleteCustomersViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/incomplete-customers/"
        self.token_url = "/api-token-auth/"
        self.username = "testuser1"
        self.password = "testpass1"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.team = Team.objects.create(
            name="Ferda Company",
            city="Praha",
            phone="234234234",
            email="ferda.company@gmail.cz",
        )
        self.hub = DistribHub.objects.create(code="626", city="Chrastany")
        # ziskani tokenu
        response = self.client.post(
            self.token_url,
            {"username": self.username, "password": self.password},
            format="json",
        )

        # kontrola
        self.assertEqual(response.status_code, 200)
        self.token = response.data["token"]

        self.range: int = 10
        # Vytvoříme  objednávky
        # status new by assembly crew
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-1-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"NEW_BY_CREW{i:05}-O",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 1, 1),
                delivery_termin=date(2025, 2, 10),
                status=Status.NEW,
                team_type=TeamType.BY_ASSEMBLY_CREW,
            )
        # status new by customer
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-2-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"NEW_BY_CUST{i:05}-O",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 1, 1),
                delivery_termin=date(2025, 2, 10),
                status=Status.NEW,
                team_type=TeamType.BY_CUSTOMER,
            )
        # status adviced
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-3-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"ADVICED-{i:06}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                montage_termin=timezone.make_aware(datetime(2025, 4, 10, 10, 0)),
                status=Status.ADVICED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.team,
            )
        # status Hidden by customer
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-4-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"HIDDEN_CUST{i:05}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                status=Status.HIDDEN,
                team_type=TeamType.BY_CUSTOMER,
            )
        # status Realized
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-5-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"REALIZED_{i:05}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                montage_termin=timezone.make_aware(datetime(2025, 4, 10, 10, 0)),
                status=Status.REALIZED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.team,
            )
        # status Canceled
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-6-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"CANCELED_{i:05}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                montage_termin=timezone.make_aware(datetime(2025, 4, 10, 10, 0)),
                status=Status.CANCELED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.team,
            )
        # status Billed
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-7-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"BILLED_{i:06}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                montage_termin=timezone.make_aware(datetime(2025, 4, 10, 10, 0)),
                status=Status.BILLED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.team,
            )

        # získání tokenu

    def test_incomplete_customers_view(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn("order_numbers", data)
        self.assertIsInstance(data["order_numbers"], list)
        self.assertTrue(all(isinstance(item, str) for item in data["order_numbers"]))
        self.assertEqual(len(data["order_numbers"]), 60)


class ZaterminovanoDopravouViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/inc-dopravni-zakazka/"
        self.token_url = "/api-token-auth/"
        self.username = "testuser1"
        self.password = "testpass1"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.team = Team.objects.create(
            name="Ferda Company",
            city="Praha",
            phone="234234234",
            email="ferda.company@gmail.cz",
        )
        self.hub = DistribHub.objects.create(code="626", city="Chrastany")
        # ziskani tokenu
        response = self.client.post(
            self.token_url,
            {"username": self.username, "password": self.password},
            format="json",
        )

        # kontrola
        self.assertEqual(response.status_code, 200)
        self.token = response.data["token"]

        self.range: int = 10
        # Vytvoříme  objednávky
        # status new by assembly crew
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-1-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"NEW_BY_CREW{i:05}-O",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 1, 1),
                delivery_termin=date(2025, 2, 10),
                status=Status.NEW,
                team_type=TeamType.BY_ASSEMBLY_CREW,
            )
        # status new by customer
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-2-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"NEW_BY_CUST{i:05}-O",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 1, 1),
                delivery_termin=date(2025, 2, 10),
                status=Status.NEW,
                team_type=TeamType.BY_CUSTOMER,
            )
        # status adviced s montazi
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-3-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"ADVICED-BY-ASSEMBLY{i:03}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                montage_termin=timezone.make_aware(datetime(2025, 4, 10, 10, 0)),
                status=Status.ADVICED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.team,
            )
        # status adviced s dopravou
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-4-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"ADVICED-BY-DELIVERY-{i:03}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                status=Status.ADVICED,
                team_type=TeamType.BY_DELIVERY_CREW,
            )
        # status Hidden by customer
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-5-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"HIDDEN_CUST{i:05}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                status=Status.HIDDEN,
                team_type=TeamType.BY_CUSTOMER,
            )
        # status Realized
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-6-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"REALIZED_{i:05}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                montage_termin=timezone.make_aware(datetime(2025, 4, 10, 10, 0)),
                status=Status.REALIZED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.team,
            )
        # status Canceled
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-7-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"CANCELED_{i:05}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                montage_termin=timezone.make_aware(datetime(2025, 4, 10, 10, 0)),
                status=Status.CANCELED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.team,
            )
        # status Billed
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-8-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"BILLED_{i:06}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                montage_termin=timezone.make_aware(datetime(2025, 4, 10, 10, 0)),
                status=Status.BILLED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.team,
            )

        # získání tokenu

    def test_inc_dopravani_zakazka(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        data = response.json()

        # Zkontrolovat, že odpověď je slovník
        self.assertIsInstance(data, dict)
        self.assertIn("orders", data)

        orders = data["orders"]
        self.assertIsInstance(orders, list)

        # Každý prvek by měl být dict s klíči order_number a evidence_termin
        for order in orders:
            self.assertIn("order_number", order)
            self.assertIn("evidence_termin", order)
            self.assertIsInstance(order["order_number"], str)
            self.assertIsInstance(order["evidence_termin"], str)
            # Zkontrolujeme, že v odpovědi jsou jen objednávky s team_type BY_DELIVERY_CREW
            self.assertTrue(order["order_number"].startswith("ADVICED-BY-DELIVERY-"))

        # Očekává se 10 záznamů s typem BY_DELIVERY_CREW a statusem ADVICED
        self.assertEqual(len(orders), self.range)


class RealizujZakazkyViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/update-dopzak/"
        self.token_url = "/api-token-auth/"
        self.username = "testuser1"
        self.password = "testpass1"
        self.user = User.objects.create_user(
            username=self.username, password=self.password
        )
        self.team = Team.objects.create(
            name="Ferda Company",
            city="Praha",
            phone="234234234",
            email="ferda.company@gmail.cz",
        )
        self.hub = DistribHub.objects.create(code="626", city="Chrastany")
        # ziskani tokenu
        response = self.client.post(
            self.token_url,
            {"username": self.username, "password": self.password},
            format="json",
        )

        # kontrola
        self.assertEqual(response.status_code, 200)
        self.token = response.data["token"]

        self.range: int = 10
        # Vytvoříme  objednávky
        # status new by assembly crew
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-1-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"NEW_BY_CREW{i:05}-O",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 1, 1),
                delivery_termin=date(2025, 2, 10),
                status=Status.NEW,
                team_type=TeamType.BY_ASSEMBLY_CREW,
            )
        # status new by customer
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-2-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"NEW_BY_CUST{i:05}-O",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 1, 1),
                delivery_termin=date(2025, 2, 10),
                status=Status.NEW,
                team_type=TeamType.BY_CUSTOMER,
            )
        # status adviced s montazi
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-3-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"ADVICED-BY-ASSEMBLY{i:03}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                montage_termin=timezone.make_aware(datetime(2025, 4, 10, 10, 0)),
                status=Status.ADVICED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.team,
            )
        # status adviced s dopravou
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-4-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"ADVICED-BY-DELIVERY-{i:03}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                status=Status.ADVICED,
                team_type=TeamType.BY_DELIVERY_CREW,
            )
        # status Hidden by customer
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-5-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"HIDDEN_CUST{i:05}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                status=Status.HIDDEN,
                team_type=TeamType.BY_CUSTOMER,
            )
        # status Realized
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-6-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"REALIZED_{i:05}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                montage_termin=timezone.make_aware(datetime(2025, 4, 10, 10, 0)),
                status=Status.REALIZED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.team,
            )
        # status Canceled
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-7-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"CANCELED_{i:05}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                montage_termin=timezone.make_aware(datetime(2025, 4, 10, 10, 0)),
                status=Status.CANCELED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.team,
            )
        # status Billed
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-8-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"BILLED_{i:06}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                client=customer,
                evidence_termin=date(2025, 2, 2),
                delivery_termin=date(2025, 3, 4),
                montage_termin=timezone.make_aware(datetime(2025, 4, 10, 10, 0)),
                status=Status.BILLED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.team,
            )

    def auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

    def test_realizace_vsech_adviced_delivery_orders(self):
        self.auth()
        orders_good = Order.objects.filter(
            status=Status.ADVICED, team_type=TeamType.BY_DELIVERY_CREW
        )
        orders_bad = Order.objects.filter(
            status=Status.ADVICED, team_type=TeamType.BY_ASSEMBLY_CREW
        )
        orders = list(orders_bad) + list(orders_good)
        order_numbers = [o.order_number for o in orders]

        response = self.client.post(self.url, {"orders": order_numbers}, format="json")

        self.assertEqual(response.status_code, 200)
        # Updated orders = jen ty správné
        updated_numbers = [o.order_number for o in orders_good]
        self.assertCountEqual(response.data["updated"], updated_numbers)

        # Skipped orders = ty špatné
        skipped_numbers = [o.order_number for o in orders_bad]
        self.assertCountEqual(response.data["skipped"], skipped_numbers)

        # Žádné nenalezené
        self.assertEqual(response.data["not_found"], [])

        # Ověření, že všechny objednávky GOOD byly aktualizovány
        for order in orders_good:
            order.refresh_from_db()
            self.assertEqual(order.status, Status.REALIZED)

        # Ověření, že všechny objednávky BAD zůstaly stejné
        for order in orders_bad:
            order.refresh_from_db()
            self.assertEqual(order.status, Status.ADVICED)
