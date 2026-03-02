"""Test functions"""

from datetime import date, datetime
from unittest.mock import MagicMock, patch

from rich.console import Console

# --- django
from django.conf import settings
from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.db.models import QuerySet
from django.contrib.auth.models import User
from app_sprava_montazi.OOP_protokols import PdfConfig, Section, Utility

# --- utils
from app_sprava_montazi.utils import call_errors_adviced, check_order_error_adviced

# --- models
from ..models import Order, Client, DistribHub, Team, Status, TeamType

# ---
cons: Console = Console()


if not settings.configured:
    settings.configure(BASE_DIR="/tmp", DEBUG=True)


class OrderErrorFunctions(TestCase):
    def setUp(self):
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

        self.date_evidence = date(2025, 1, 1)
        self.date_evidence_cz = self.date_evidence.strftime("%d.%m.%Y")

        self.date_delivery = date(2025, 2, 10)
        self.date_delivery_cz = self.date_delivery.strftime("%d.%m.%Y")

        self.date_montage = timezone.make_aware(datetime(2025, 4, 10, 10, 0))
        self.time_zone = timezone.localtime(self.date_montage)
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
                mail_team_sended=self.active_team,
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
                mail_datum_sended=timezone.make_aware(datetime(2025, 4, 11, 12, 0)),
                mail_team_sended=self.active_team,
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
                mail_datum_sended=timezone.make_aware(datetime(2025, 4, 11, 12, 0)),
                mail_team_sended=self.active_team,
                notes="Vyuctovano",
            )
        # 9 status Adviced no active team na mail sended
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-9-{i}", zip_code=f"123{i:02}"
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

    def test_db_count_after_creation(self):
        self.assertEqual(Order.objects.count(), 90)

    def test_orders_with_errors(self):
        is_error, errors_count = call_errors_adviced()
        self.assertTrue(is_error)
        self.assertEqual(errors_count, 20)

    def test_changing_active_team_to_no_active_team(self):
        active_team = Team.objects.get(pk=self.active_team.pk)
        self.assertEqual(Team.objects.filter(active=True).count(), 1)
        active_team.active = False
        active_team.save()
        self.assertEqual(Team.objects.filter(active=True).count(), 0)
        # --- jen adviced
        is_error, errors_count = call_errors_adviced()
        self.assertTrue(is_error)
        self.assertEqual(errors_count, 30)
        # ---  neni odelsany mail takze bude error exists
        for i in range(0, self.range):
            order = Order.objects.get(order_number=f"ADVICED-NOMAIL-{i:05}-R")
            error_exists = check_order_error_adviced(order.pk)
            self.assertTrue(error_exists)

        # --- neni active team takze bude error exists
        for i in range(0, self.range):
            order = Order.objects.get(order_number=f"ADVICED-MAIL-{i:05}-R")
            error_exists = check_order_error_adviced(order.pk)
            self.assertTrue(error_exists)

    def test_changing_active_team_to_active_team(self):
        self.assertEqual(Team.objects.filter(active=True).count(), 1)

        # --- jen adviced
        is_error, errors_count = call_errors_adviced()
        self.assertTrue(is_error)
        self.assertEqual(errors_count, 20)
        # ---  neni odelsany mail takze bude error exists
        for i in range(0, self.range):
            order = Order.objects.get(order_number=f"ADVICED-NOMAIL-{i:05}-R")
            error_exists = check_order_error_adviced(order.pk)
            self.assertTrue(error_exists)

        # --- je active team, je email takze nebude error exists
        for i in range(0, self.range):
            order = Order.objects.get(order_number=f"ADVICED-MAIL-{i:05}-R")
            error_exists = check_order_error_adviced(order.pk)
            self.assertFalse(error_exists)
