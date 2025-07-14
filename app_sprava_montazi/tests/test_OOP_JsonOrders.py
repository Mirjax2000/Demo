"""test for OOP_JsonOrders"""

from datetime import date, datetime
import json

# --- django
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone
from django.db.models import QuerySet
from django.contrib.auth.models import User

# --- models
from ..models import Order, Client, DistribHub, Team, Status, TeamType

# --- OOP
from ..OOP_JsonOrders import JsonOrders, Utils, FilterDict, JsonHeader


class OrderDataTablesTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        self.hub = DistribHub.objects.create(code="626", city="Chrastany")
        self.team = Team.objects.create(
            name="Ferda Company",
            city="Praha",
            phone="234234234",
            email="ferda.company@gmail.cz",
        )
        self.range: int = 10
        self.pagination: int = 15

        # Vytvoříme  objednávky
        # status new by assembly crew
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-{i}", zip_code=f"123{i:02}"
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
                name=f"Customer test-{i}", zip_code=f"123{i:02}"
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
                name=f"Customer test-{i}", zip_code=f"123{i:02}"
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
                name=f"Customer test-{i}", zip_code=f"123{i:02}"
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
                name=f"Customer test-{i}", zip_code=f"123{i:02}"
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
                name=f"Customer test-{i}", zip_code=f"123{i:02}"
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
                name=f"Customer test-{i}", zip_code=f"123{i:02}"
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

    def test_get_json_data_response(self):
        factory = RequestFactory()
        request = factory.get(
            "/fake-url/",
            {
                "draw": "1",
                "start": "0",
                "length": str(self.pagination),
                "order[0][column]": "0",
                "order[0][dir]": "asc",
                "columns[0][data]": "order_number",
                "status": "",
            },
        )
        request.user = self.user
        json_orders = JsonOrders(request)
        response = json_orders.get_json_data()
        data = json.loads(response.content.decode("utf-8"))

        # --- kontrola že je to JsonResponse
        self.assertEqual(response.status_code, 200)

        # --- základní klíče
        self.assertIn("draw", data)
        self.assertIn("recordsTotal", data)
        self.assertIn("recordsFiltered", data)
        self.assertIn("data", data)

        # --- kontrola počtu (máš tam 70 objednávek, 10 z každého typu)
        self.assertEqual(data["recordsTotal"], Order.objects.count())
        client_html = data["data"][0]["client"]
        # klient
        self.assertIn("<span", client_html)
        self.assertTrue('<i class="fa-solid' in client_html)
        self.assertTrue('<span title="Customer' in client_html)
        self.assertIn("Customer", client_html)
        # distribhub
        distrib_hub_html = data["data"][0]["distrib_hub"]
        self.assertIn("626-Chrastany", distrib_hub_html)
        # mandant
        mandant_html = data["data"][0]["mandant"]
        self.assertIn("SCCZ", mandant_html)

    def test_filter_status_open(self):
        factory = RequestFactory()
        request = factory.get(
            "/fake-url/",
            {
                "draw": "1",
                "start": "0",
                "length": str(self.pagination),
                "order[0][column]": "0",
                "order[0][dir]": "asc",
                "columns[0][data]": "order_number",
                "status": "",
            },
        )
        request.user = self.user
        json_orders = JsonOrders(request)
        response = json_orders.get_json_data()
        data = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["recordsFiltered"], 40)
        # --- sloupec klient by měl obsahovat jméno (a ikonu)
        client_html = data["data"][0]["client"]
        self.assertIn("<span", client_html)
        # --- implicitní filtr vynechá Hidden, Billed, Canceled-mělo by být 40
        self.assertEqual(data["recordsFiltered"], 40)

        # --- mělo by se vrátit max self.pagination(15) záznamů
        self.assertEqual(len(data["data"]), self.pagination)

        # --- první záznam by měl mít order_number jako odkaz
        order_html = data["data"][0]["order_number"]
        self.assertTrue(order_html.startswith('<a href="/order'))
        self.assertIn('class="L-table__link', order_html)

    def test_filter_status_closed(self):
        factory = RequestFactory()
        request = factory.get(
            "/fake-url/",
            {
                "draw": "1",
                "start": "0",
                "length": str(self.pagination),
                "order[0][column]": "0",
                "order[0][dir]": "asc",
                "columns[0][data]": "order_number",
                "status": "closed",
            },
        )
        request.user = self.user
        json_orders = JsonOrders(request)
        response = json_orders.get_json_data()
        data = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["recordsFiltered"], 20)

    def test_filter_status_hidden(self):
        factory = RequestFactory()
        request = factory.get(
            "/fake-url/",
            {
                "draw": "1",
                "start": "0",
                "length": str(self.pagination),
                "order[0][column]": "0",
                "order[0][dir]": "asc",
                "columns[0][data]": "order_number",
                "status": "Hidden",
            },
        )
        request.user = self.user
        json_orders = JsonOrders(request)
        response = json_orders.get_json_data()
        data = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["recordsFiltered"], 10)

    def test_filter_status_new(self):
        factory = RequestFactory()
        request = factory.get(
            "/fake-url/",
            {
                "draw": "1",
                "start": "0",
                "length": str(self.pagination),
                "order[0][column]": "0",
                "order[0][dir]": "asc",
                "columns[0][data]": "order_number",
                "status": "New",
            },
        )
        request.user = self.user
        json_orders = JsonOrders(request)
        response = json_orders.get_json_data()
        data = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["recordsFiltered"], 20)
