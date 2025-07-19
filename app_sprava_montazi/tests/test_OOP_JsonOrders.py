"""test for OOP_JsonOrders"""

from datetime import date, datetime
import json
import re
from rich.console import Console

# --- django
from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.db.models import QuerySet
from django.contrib.auth.models import User

# --- models
from ..models import Order, Client, DistribHub, Team, Status, TeamType

# --- OOP
from ..OOP_JsonOrders import JsonOrders, Utils, FilterDict, JsonHeader

# ---
cons: Console = Console()


class OrderDataTablesTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        # --- zalogujeme
        self.client.login(username="testuser", password="testpass")
        # --- ditrib hub
        self.distrib_hub_code: str = "626"
        self.distrib_hub_city: str = "Chrastany"
        self.hub = DistribHub.objects.create(
            code=self.distrib_hub_code, city=self.distrib_hub_city
        )
        # --- team
        self.team_name_active: str = "Active Company"
        self.team_name_not_active: str = "Not Active Company"
        self.team_city: str = "Praha"
        self.team_phone: str = "234234234"
        self.team_email: str = "ferda.company@gmail.cz"
        self.active_team = Team.objects.create(
            name=self.team_name_active,
            city=self.team_city,
            phone=self.team_phone,
            email=self.team_email,
            active=True,
        )
        self.not_active_team = Team.objects.create(
            name=self.team_name_not_active,
            city=self.team_city,
            phone=self.team_phone,
            email=self.team_email,
            active=False,
        )
        # --- mandant
        self.mandant = "SCCZ"
        # --- settings
        self.range: int = 10
        self.pagination: int = 15

        self.date_evidence = date(2025, 1, 1)
        self.date_evidence_cz = self.date_evidence.strftime("%d.%m.%Y")

        self.date_delivery = date(2025, 2, 10)
        self.date_delivery_cz = self.date_delivery.strftime("%d.%m.%Y")

        self.date_montage = timezone.make_aware(datetime(2025, 4, 10, 10, 0))
        self.time_zone = timezone.localtime(self.date_montage)
        self.date_montage_cz = self.time_zone.strftime("%d.%m.%Y %H:%M")
        # Vytvoříme  objednávky
        # ---
        # 1 status new by assembly crew
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-1-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"NEW-BY-CREW-{i:05}-R",
                distrib_hub=self.hub,
                mandant=self.mandant,
                client=customer,
                evidence_termin=self.date_evidence,
                delivery_termin=self.date_delivery,
                status=Status.NEW,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                notes="New",
            )
        # 2 status new by customer
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-2-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"NEW-BY-CUSTOMER-{i:05}-R",
                distrib_hub=self.hub,
                mandant=self.mandant,
                client=customer,
                evidence_termin=self.date_evidence,
                delivery_termin=self.date_delivery,
                status=Status.NEW,
                team_type=TeamType.BY_CUSTOMER,
                notes="New",
            )
        # 3 status adviced no mail sended !!!
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-3-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"ADVICED-NOMAIL-{i:05}-R",
                distrib_hub=self.hub,
                mandant=self.mandant,
                client=customer,
                evidence_termin=self.date_evidence,
                delivery_termin=self.date_delivery,
                montage_termin=self.date_montage,
                status=Status.ADVICED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.active_team,
                notes="Zaterminovano",
            )
        # 4 status adviced mail sended !!!
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-4-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"ADVICED-MAIL-{i:05}-R",
                distrib_hub=self.hub,
                mandant=self.mandant,
                client=customer,
                evidence_termin=self.date_evidence,
                delivery_termin=self.date_delivery,
                montage_termin=self.date_montage,
                status=Status.ADVICED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.active_team,
                mail_datum_sended=timezone.make_aware(datetime(2025, 4, 11, 12, 0)),
                notes="Zaterminovano",
            )
        # 5 status Hidden by customer
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-5-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"HIDDEN-CUSTOMER-{i:05}-R",
                distrib_hub=self.hub,
                mandant=self.mandant,
                client=customer,
                evidence_termin=self.date_evidence,
                delivery_termin=self.date_delivery,
                status=Status.HIDDEN,
                team_type=TeamType.BY_CUSTOMER,
                notes="Skryto",
            )
        # 6 status Realized
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-6-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"REALIZED-{i:05}-R",
                distrib_hub=self.hub,
                mandant=self.mandant,
                client=customer,
                evidence_termin=self.date_evidence,
                delivery_termin=self.date_delivery,
                montage_termin=self.date_montage,
                status=Status.REALIZED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.active_team,
                notes="Realizovano",
            )
        # 7 status Canceled
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-7-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"CANCELED-{i:05}-R",
                distrib_hub=self.hub,
                mandant=self.mandant,
                client=customer,
                evidence_termin=self.date_evidence,
                delivery_termin=self.date_delivery,
                montage_termin=self.date_montage,
                status=Status.CANCELED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.active_team,
                notes="Zruseno",
            )
        # 8 status Billed
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-8-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"BILLED-{i:05}-R",
                distrib_hub=self.hub,
                mandant=self.mandant,
                client=customer,
                evidence_termin=self.date_evidence,
                delivery_termin=self.date_delivery,
                montage_termin=self.date_montage,
                status=Status.BILLED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.active_team,
                notes="Vyuctovano",
            )
        # 9 status Adviced no active team
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-8-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"ADVICED-NO-ACTIVE-TEAM-{i:03}-R",
                distrib_hub=self.hub,
                mandant=self.mandant,
                client=customer,
                evidence_termin=self.date_evidence,
                delivery_termin=self.date_delivery,
                montage_termin=self.date_montage,
                status=Status.ADVICED,
                team_type=TeamType.BY_ASSEMBLY_CREW,
                team=self.not_active_team,
                notes="Zaterminovano",
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
                "columns[0][data]": "evidence_termin",
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
        # --- kontrola počtu (máš tam 90 objednávek, 10 z každého typu)
        self.assertEqual(data["recordsTotal"], Order.objects.count())
        for i in range(0, self.pagination):
            # order number v datech z JSONA
            order_html = data["data"][i]["order_number"]
            order_pattern = (
                r'<a href="/order/\d+/detail/" name="order-number" '
                r'class="L-table__link copy_link_order_number">\w+(?:-\w+)*-\d{5}-R</a>'
            )
            self.assertRegex(order_html, order_pattern)  # regex
            self.assertIn('name="order-number"', order_html)  # name

            # distribhub v datech z JSONA
            distrib_hub_html = data["data"][i]["distrib_hub"]
            distrib_hub_content = f"{self.distrib_hub_code}-{self.distrib_hub_city}"
            distrib_hub_pattern = r'<span name="distrib-hub">.+?</span>'
            self.assertRegex(distrib_hub_html, distrib_hub_pattern)  # regex
            self.assertIn(distrib_hub_content, distrib_hub_html)  # obsah
            self.assertIn('name="distrib-hub"', distrib_hub_html)  # name

            # mandant v datech z JSONA
            mandant_html = data["data"][i]["mandant"]
            mandant_pattern = r'<span name="mandant">[A-Za-z]{1,4}</span>'
            self.assertRegex(mandant_html, mandant_pattern)  # regex
            self.assertIn(self.mandant, mandant_html)  # obsah
            self.assertIn('name="mandant"', mandant_html)  # name

            # evidence_termin v datech z JSONA
            evidence_termin_html = data["data"][i]["evidence_termin"]
            evidence_termin_pattern = (
                r'<span\s+name="evidence-termin"(?:\s+class="[^"]*")?>'
                r"\d{2}\.\d{2}\.\d{4}</span>"
            )

            self.assertIn(self.date_evidence_cz, evidence_termin_html)  # obsah
            self.assertRegex(evidence_termin_html, evidence_termin_pattern)  # regex
            self.assertIn('name="evidence-termin"', evidence_termin_html)  # name

            # delivery_termin v datech z JSONA
            delivery_termin_html = data["data"][i]["delivery_termin"]
            delivery_termin_pattern = (
                r'<span\s+name="delivery-termin"(?:\s+class="[^"]*")?>'
                r"\d{2}\.\d{2}\.\d{4}</span>"
            )
            self.assertIn(self.date_delivery_cz, delivery_termin_html)  # obsah
            self.assertRegex(delivery_termin_html, delivery_termin_pattern)  # regex
            self.assertIn('name="delivery-termin"', delivery_termin_html)  # name

            # client v datech z JSONA
            client_html = data["data"][i]["client"]
            client_pattern = re.compile(
                r'<div[^>]*title="[^"]+"[^>]*name="client"[^>]*>'
                r"(?:.|\n)*?<i[^>]*>"
                r"(?:.|\n)*?<span[^>]*>",
                re.DOTALL,
            )
            self.assertRegex(client_html, client_pattern)  # regex
            self.assertIn("Customer", client_html)  # obsah
            self.assertIn('name="client"', client_html)  # name

            # team_type v datech z JSONA
            team_type_html = data["data"][i]["team_type"]
            team_type_pattern = (
                r'<span\s+name="team-type"\s+class="[^"]*\bu-s-none\b[^"]*">.*?</span>'
            )
            self.assertRegex(team_type_html, team_type_pattern)  # regex
            self.assertIn('name="team-type"', team_type_html)  # name

            # team v datech z JSONA
            team_html = data["data"][i]["team"]
            team_pattern = r'<div[^>]*\btitle="[^"]*"\s+name="team"[^>]*>.*?<span[^>]*>.*?</span>.*?</div>'

            self.assertRegex(team_html, team_pattern)  # regex
            self.assertIn('name="team"', team_html)  # name

            # montage_termin v datech z JSONA
            montage_termin_html = data["data"][i]["montage_termin"]
            montage_termin_pattern = (
                r'<div\b[^>]*\bname="montage-termin"[^>]*>'
                r".*?"  # obsah mezi tagy (non-greedy)
                r"(?:\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}|Nevybráno|–)?"  # nepovinný čas nebo text
                r"</div>"
            )
            self.assertRegex(montage_termin_html, montage_termin_pattern)  # regex
            self.assertIn('name="montage-termin"', montage_termin_html)  # name

            # status v datech z JSONA
            status_html = data["data"][i]["status"]
            status_pattern = r'<div\b[^>]*\bname="status"[^>]*>.*?</div>'
            self.assertRegex(status_html, status_pattern)  # regex
            self.assertIn('name="status"', status_html)  # name

            # articles v datech z JSONA
            articles_html = data["data"][i]["articles"]
            articles_pattern = r'<div\b[^>]*\bname="articles"[^>]*>.*?</div>'
            self.assertRegex(articles_html, articles_pattern)  # regex
            self.assertIn('name="articles"', articles_html)  # name

            # notes v datech z JSONA
            notes_html = data["data"][i]["notes"]
            notes_pattern = r'<span\b[^>]*\bname="notes"[^>]*>.*?</span>'
            self.assertRegex(notes_html, notes_pattern)  # regex
            self.assertIn('name="notes"', notes_html)  # name

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
                "columns[0][data]": "evidence_termin",
                "status": "New",
            },
        )
        request.user = self.user
        json_orders = JsonOrders(request)
        response = json_orders.get_json_data()
        data = json.loads(response.content.decode("utf-8"))
        # --- kontrola že je to JsonResponse
        self.assertEqual(response.status_code, 200)
        # --- New filtr
        self.assertEqual(data["recordsFiltered"], 20)
        # --- mělo by se vrátit max self.pagination(15) záznamů
        self.assertEqual(len(data["data"]), self.pagination)
        for i in range(0, self.pagination):
            # order number v datech z JSONA
            order_html = data["data"][i]["order_number"]
            order_pattern = (
                r'<a href="/order/\d+/detail/" name="order-number" '
                r'class="L-table__link copy_link_order_number">\w+(?:-\w+)*-\d{5}-R</a>'
            )
            self.assertRegex(order_html, order_pattern)  # regex
            self.assertIn('name="order-number"', order_html)  # name

            # distribhub v datech z JSONA
            distrib_hub_html = data["data"][i]["distrib_hub"]
            distrib_hub_content = f"{self.distrib_hub_code}-{self.distrib_hub_city}"
            distrib_hub_pattern = r'<span name="distrib-hub">.+?</span>'
            self.assertRegex(distrib_hub_html, distrib_hub_pattern)  # regex
            self.assertIn(distrib_hub_content, distrib_hub_html)  # obsah
            self.assertIn('name="distrib-hub"', distrib_hub_html)  # name

            # mandant v datech z JSONA
            mandant_html = data["data"][i]["mandant"]
            mandant_pattern = r'<span name="mandant">[A-Za-z]{1,4}</span>'
            self.assertRegex(mandant_html, mandant_pattern)  # regex
            self.assertIn(self.mandant, mandant_html)  # obsah
            self.assertIn('name="mandant"', mandant_html)  # name

            # evidence_termin v datech z JSONA
            evidence_termin_html = data["data"][i]["evidence_termin"]
            evidence_termin_pattern = (
                r'<span\s+name="evidence-termin"(?:\s+class="[^"]*")?>'
                r"\d{2}\.\d{2}\.\d{4}</span>"
            )

            self.assertIn(self.date_evidence_cz, evidence_termin_html)  # obsah
            self.assertRegex(evidence_termin_html, evidence_termin_pattern)  # regex
            self.assertIn('name="evidence-termin"', evidence_termin_html)  # name

            # delivery_termin v datech z JSONA
            delivery_termin_html = data["data"][i]["delivery_termin"]
            delivery_termin_pattern = (
                r'<span\s+name="delivery-termin"(?:\s+class="[^"]*")?>'
                r"\d{2}\.\d{2}\.\d{4}</span>"
            )
            self.assertIn(self.date_delivery_cz, delivery_termin_html)  # obsah
            self.assertRegex(delivery_termin_html, delivery_termin_pattern)  # regex
            self.assertIn('name="delivery-termin"', delivery_termin_html)  # name

            # team_type v datech z JSONA
            team_type_html = data["data"][i]["team_type"]
            team_type_pattern = (
                r'<span\s+name="team-type"\s+class="[^"]*\bu-s-none\b[^"]*">.*?</span>'
            )
            team_type_pattern_new = (
                r'<span name="team-type" class="u-s-none(?: u-txt-success)?">'
                r"(?:Montážníky|Zákazníkem)</span>"
            )
            self.assertRegex(team_type_html, team_type_pattern_new)  # obsah
            self.assertRegex(team_type_html, team_type_pattern)  # regex
            self.assertIn('name="team-type"', team_type_html)  # name

            # team v datech z JSONA
            team_html = data["data"][i]["team"]
            team_pattern = r'<div[^>]*\btitle="[^"]*"\s+name="team"[^>]*>.*?<span[^>]*>.*?</span>.*?</div>'

            team_pattern_new = (
                r'<span class="u-s-none(?: u-txt-warning)?">'
                r"(?:Nevybráno|-)</span>"
            )
            self.assertRegex(team_html, team_pattern_new)  # obsah
            self.assertRegex(team_html, team_pattern)  # regex
            self.assertIn('name="team"', team_html)  # name

            # montage_termin v datech z JSONA
            montage_termin_html = data["data"][i]["montage_termin"]
            montage_termin_pattern_new = (
                r'<div name="montage-termin" class="u-s-none(?: u-txt-warning)?">'
                r'(?:<i class="[^"]+"></i>)?'
                r"<span>(?:Nevybráno|–)</span>"
                r"</div>"
            )
            self.assertRegex(montage_termin_html, montage_termin_pattern_new)
            self.assertIn('name="montage-termin"', montage_termin_html)  # name

            # status v datech z JSONA
            status_html = data["data"][i]["status"]
            status_pattern = r'<div\b[^>]*\bname="status"[^>]*>.*?</div>'
            self.assertRegex(status_html, status_pattern)  # regex
            self.assertIn('name="status"', status_html)  # name
            self.assertIn('<div name="status">Nový </div>', status_html)  # obsah

            # articles v datech z JSONA
            articles_html = data["data"][i]["articles"]
            articles_pattern = r'<div\b[^>]*\bname="articles"[^>]*>.*?</div>'
            self.assertRegex(articles_html, articles_pattern)  # regex
            self.assertIn('name="articles"', articles_html)  # name
            self.assertIn(
                '<div name="articles" "class="u-s-none u-txt-center u-txt-error">0</div>',
                articles_html,
            )  # obsah

            # notes v datech z JSONA
            notes_html = data["data"][i]["notes"]
            notes_pattern = r'<span\b[^>]*\bname="notes"[^>]*>.*?</span>'
            self.assertRegex(notes_html, notes_pattern)  # regex
            self.assertIn('name="notes"', notes_html)  # name
            self.assertIn(
                '<span name="notes" title="New">New</span>', notes_html
            )  # obsah

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
                "columns[0][data]": "evidence_termin",
                "status": "Hidden",
            },
        )
        request.user = self.user
        json_orders = JsonOrders(request)
        response = json_orders.get_json_data()
        data = json.loads(response.content.decode("utf-8"))
        # --- kontrola že je to JsonResponse
        self.assertEqual(response.status_code, 200)
        # --- New filtr
        self.assertEqual(data["recordsFiltered"], 10)
        # --- mělo by se vrátit max self.pagination(15) záznamů
        self.assertEqual(len(data["data"]), 10)
        for i in range(0, 9):
            # order number v datech z JSONA
            order_html = data["data"][i]["order_number"]
            order_pattern = (
                r'<a href="/order/\d+/detail/" name="order-number" '
                r'class="L-table__link copy_link_order_number">\w+(?:-\w+)*-\d{5}-R</a>'
            )
            self.assertRegex(order_html, order_pattern)  # regex
            self.assertIn('name="order-number"', order_html)  # name

            # distribhub v datech z JSONA
            distrib_hub_html = data["data"][i]["distrib_hub"]
            distrib_hub_content = f"{self.distrib_hub_code}-{self.distrib_hub_city}"
            distrib_hub_pattern = r'<span name="distrib-hub">.+?</span>'
            self.assertRegex(distrib_hub_html, distrib_hub_pattern)  # regex
            self.assertIn(distrib_hub_content, distrib_hub_html)  # obsah
            self.assertIn('name="distrib-hub"', distrib_hub_html)  # name

            # mandant v datech z JSONA
            mandant_html = data["data"][i]["mandant"]
            mandant_pattern = r'<span name="mandant">[A-Za-z]{1,4}</span>'
            self.assertRegex(mandant_html, mandant_pattern)  # regex
            self.assertIn(self.mandant, mandant_html)  # obsah
            self.assertIn('name="mandant"', mandant_html)  # name

            # evidence_termin v datech z JSONA
            evidence_termin_html = data["data"][i]["evidence_termin"]
            evidence_termin_pattern = (
                r'<span\s+name="evidence-termin"(?:\s+class="[^"]*")?>'
                r"\d{2}\.\d{2}\.\d{4}</span>"
            )

            self.assertIn(self.date_evidence_cz, evidence_termin_html)  # obsah
            self.assertRegex(evidence_termin_html, evidence_termin_pattern)  # regex
            self.assertIn('name="evidence-termin"', evidence_termin_html)  # name

            # delivery_termin v datech z JSONA
            delivery_termin_html = data["data"][i]["delivery_termin"]
            delivery_termin_pattern = (
                r'<span\s+name="delivery-termin"(?:\s+class="[^"]*")?>'
                r"\d{2}\.\d{2}\.\d{4}</span>"
            )
            self.assertIn(self.date_delivery_cz, delivery_termin_html)  # obsah
            self.assertRegex(delivery_termin_html, delivery_termin_pattern)  # regex
            self.assertIn('name="delivery-termin"', delivery_termin_html)  # name

            # team_type v datech z JSONA
            team_type_html = data["data"][i]["team_type"]
            team_type_pattern = (
                r'<span\s+name="team-type"\s+class="[^"]*\bu-s-none\b[^"]*">.*?</span>'
            )
            team_type_pattern_new = (
                r'<span name="team-type" class="u-s-none(?: u-txt-success)?">'
                r"(?:Montážníky|Zákazníkem)</span>"
            )
            self.assertRegex(team_type_html, team_type_pattern_new)  # obsah
            self.assertRegex(team_type_html, team_type_pattern)  # regex
            self.assertIn('name="team-type"', team_type_html)  # name

            # team v datech z JSONA
            team_html = data["data"][i]["team"]
            team_pattern = r'<div[^>]*\btitle="[^"]*"\s+name="team"[^>]*>.*?<span[^>]*>.*?</span>.*?</div>'

            team_pattern_new = (
                r'<span class="u-s-none(?: u-txt-warning)?">'
                r"(?:Nevybráno|-)</span>"
            )
            self.assertRegex(team_html, team_pattern_new)  # obsah
            self.assertRegex(team_html, team_pattern)  # regex
            self.assertIn('name="team"', team_html)  # name

            # montage_termin v datech z JSONA
            montage_termin_html = data["data"][i]["montage_termin"]
            montage_termin_pattern_new = (
                r'<div name="montage-termin" class="u-s-none(?: u-txt-warning)?">'
                r'(?:<i class="[^"]+"></i>)?'
                r"<span>(?:Nevybráno|–)</span>"
                r"</div>"
            )
            self.assertRegex(montage_termin_html, montage_termin_pattern_new)
            self.assertIn('name="montage-termin"', montage_termin_html)  # name

            # status v datech z JSONA
            status_html = data["data"][i]["status"]
            status_pattern = r'<div\b[^>]*\bname="status"[^>]*>.*?</div>'
            self.assertRegex(status_html, status_pattern)  # regex
            self.assertIn('name="status"', status_html)  # name
            self.assertIn('<div name="status">Skryto </div>', status_html)  # obsah

            # articles v datech z JSONA
            articles_html = data["data"][i]["articles"]
            articles_pattern = r'<div\b[^>]*\bname="articles"[^>]*>.*?</div>'
            self.assertRegex(articles_html, articles_pattern)  # regex
            self.assertIn('name="articles"', articles_html)  # name
            self.assertIn(
                '<div name="articles" "class="u-s-none u-txt-center u-txt-error">0</div>',
                articles_html,
            )  # obsah

            # notes v datech z JSONA
            notes_html = data["data"][i]["notes"]
            notes_pattern = r'<span\b[^>]*\bname="notes"[^>]*>.*?</span>'
            self.assertRegex(notes_html, notes_pattern)  # regex
            self.assertIn('name="notes"', notes_html)  # name
            self.assertIn(
                '<span name="notes" title="Skryto">Skryto</span>', notes_html
            )  # obsah

    def test_filter_status_adviced(self):
        factory = RequestFactory()
        request = factory.get(
            "/fake-url/",
            {
                "draw": "1",
                "start": "0",
                "length": str(self.pagination),
                "order[0][column]": "0",
                "order[0][dir]": "asc",
                "columns[0][data]": "evidence_termin",
                "status": "Adviced",
            },
        )
        request.user = self.user
        json_orders = JsonOrders(request)
        response = json_orders.get_json_data()
        data = json.loads(response.content.decode("utf-8"))
        # --- kontrola že je to JsonResponse
        self.assertEqual(response.status_code, 200)
        # --- New filtr
        self.assertEqual(data["recordsFiltered"], 30)
        # --- mělo by se vrátit max self.pagination(15) záznamů
        self.assertEqual(len(data["data"]), 15)
        for i in range(0, 9):
            # order number v datech z JSONA
            order_html = data["data"][i]["order_number"]
            order_pattern = (
                r'<a href="/order/\d+/detail/" name="order-number" '
                r'class="L-table__link copy_link_order_number(?: u-txt-error)?">\w+(?:-\w+)*-\d{5}-R</a>'
            )
            self.assertRegex(order_html, order_pattern)  # regex
            self.assertIn('name="order-number"', order_html)  # name

            # distribhub v datech z JSONA
            distrib_hub_html = data["data"][i]["distrib_hub"]
            distrib_hub_content = f"{self.distrib_hub_code}-{self.distrib_hub_city}"
            distrib_hub_pattern = r'<span name="distrib-hub">.+?</span>'
            self.assertRegex(distrib_hub_html, distrib_hub_pattern)  # regex
            self.assertIn(distrib_hub_content, distrib_hub_html)  # obsah
            self.assertIn('name="distrib-hub"', distrib_hub_html)  # name

            # mandant v datech z JSONA
            mandant_html = data["data"][i]["mandant"]
            mandant_pattern = r'<span name="mandant">[A-Za-z]{1,4}</span>'
            self.assertRegex(mandant_html, mandant_pattern)  # regex
            self.assertIn(self.mandant, mandant_html)  # obsah
            self.assertIn('name="mandant"', mandant_html)  # name

            # evidence_termin v datech z JSONA
            evidence_termin_html = data["data"][i]["evidence_termin"]
            evidence_termin_pattern = (
                r'<span\s+name="evidence-termin"(?:\s+class="[^"]*")?>'
                r"\d{2}\.\d{2}\.\d{4}</span>"
            )

            self.assertIn(self.date_evidence_cz, evidence_termin_html)  # obsah
            self.assertRegex(evidence_termin_html, evidence_termin_pattern)  # regex
            self.assertIn('name="evidence-termin"', evidence_termin_html)  # name

            # delivery_termin v datech z JSONA
            delivery_termin_html = data["data"][i]["delivery_termin"]
            delivery_termin_pattern = (
                r'<span\s+name="delivery-termin"(?:\s+class="[^"]*")?>'
                r"\d{2}\.\d{2}\.\d{4}</span>"
            )
            self.assertIn(self.date_delivery_cz, delivery_termin_html)  # obsah
            self.assertRegex(delivery_termin_html, delivery_termin_pattern)  # regex
            self.assertIn('name="delivery-termin"', delivery_termin_html)  # name

            # team_type v datech z JSONA
            team_type_html = data["data"][i]["team_type"]
            team_type_pattern = (
                r'<span\s+name="team-type"\s+class="[^"]*\bu-s-none\b[^"]*">.*?</span>'
            )
            team_type_pattern_new = (
                r'<span name="team-type" class="u-s-none(?: u-txt-success)?">'
                r"(?:Montážníky|Zákazníkem)</span>"
            )
            self.assertRegex(team_type_html, team_type_pattern_new)  # obsah
            self.assertRegex(team_type_html, team_type_pattern)  # regex
            self.assertIn('name="team-type"', team_type_html)  # name

            # team v datech z JSONA
            team_html = data["data"][i]["team"]
            team_pattern = r'<div[^>]*\btitle="[^"]*"\s+name="team"[^>]*>.*?<span[^>]*>.*?</span>.*?</div>'

            self.assertRegex(team_html, team_pattern)  # regex
            self.assertIn('name="team"', team_html)  # name

            # montage_termin v datech z JSONA
            montage_termin_html = data["data"][i]["montage_termin"]
            montage_termin_pattern_new = (
                r'<div name="montage-termin" class="u-s-none(?: u-txt-warning)?">'
                r'(?:<i class="[^"]+"></i>)?'
                r"<span><strong>\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}</strong></span>"
                r"</div>"
            )
            self.assertRegex(montage_termin_html, montage_termin_pattern_new)
            self.assertIn('name="montage-termin"', montage_termin_html)  # name

            # status v datech z JSONA
            status_html = data["data"][i]["status"]
            status_pattern = r'<div\b[^>]*\bname="status"[^>]*>.*?</div>'
            self.assertRegex(status_html, status_pattern)  # regex
            self.assertIn('name="status"', status_html)  # name
            self.assertIn(
                '<div name="status">Zatermín <a href="/order', status_html
            )  # obsah

            # articles v datech z JSONA
            articles_html = data["data"][i]["articles"]
            articles_pattern = r'<div\b[^>]*\bname="articles"[^>]*>.*?</div>'
            self.assertRegex(articles_html, articles_pattern)  # regex
            self.assertIn('name="articles"', articles_html)  # name
            self.assertIn(
                '<div name="articles" "class="u-s-none u-txt-center u-txt-error">0</div>',
                articles_html,
            )  # obsah

            # notes v datech z JSONA
            notes_html = data["data"][i]["notes"]
            notes_pattern = r'<span\b[^>]*\bname="notes"[^>]*>.*?</span>'
            self.assertRegex(notes_html, notes_pattern)  # regex
            self.assertIn('name="notes"', notes_html)  # name
            self.assertIn(
                '<span name="notes" title="Zaterminovano"', notes_html
            )  # obsah
