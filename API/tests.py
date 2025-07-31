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
        self.assertIsInstance(data, list)
        self.assertTrue(all(isinstance(item, str) for item in data))
        #  mame 70 zakazek ale 10 je skryto
        self.assertTrue(len(data), 60)
