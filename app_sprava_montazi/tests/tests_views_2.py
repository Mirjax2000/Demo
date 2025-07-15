import logging
from datetime import date, datetime

from django.urls import reverse
from django.contrib.auth.models import User

from django.conf import settings
from django.contrib.messages import get_messages
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client as CL
from django.test import TestCase
from django.utils import timezone
from django.test import override_settings

from app_sprava_montazi.models import (
    Article,
    Client,
    DistribHub,
    Order,
    OrderPDFStorage,
    Status,
    Team,
    TeamType,
    Upload,
)

# --- oop

# --- utils
from ..utils import format_date

# ---
test_logger = logging.getLogger("test_logger_login")
test_logger.setLevel(logging.INFO)
test_handler = (
    logging.StreamHandler()
)  # Or a FileHandler/NullHandler depending on your needs
test_logger.addHandler(test_handler)
test_logger.propagate = False  # Prevent logs from going to the root logger
LOGIN_URL = reverse("login")


class IndexViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
        self.template = "app_sprava_montazi/orders/montazni_protokol.html"
        # --- ditrib hub
        self.distrib_hub_code: str = "626"
        self.distrib_hub_city: str = "Chrastany"
        self.hub = DistribHub.objects.create(
            code=self.distrib_hub_code, city=self.distrib_hub_city
        )
        self.customer = Client.objects.create(name="franta", zip_code="11111")
        # --- team
        self.team_name: str = "Ferda Company"
        self.team_city: str = "Praha"
        self.team_phone: str = "234234234"
        self.team_email: str = "ferda.company@gmail.cz"
        self.team = Team.objects.create(
            name=self.team_name,
            city=self.team_city,
            phone=self.team_phone,
            email=self.team_email,
        )
        self.order = Order.objects.create(
            order_number="703777143100437749-R",
            distrib_hub=self.hub,
            status=Status.NEW,
            client=self.customer,
            mandant="SCCZ",
            evidence_termin=date.today(),
            team_type=TeamType.BY_ASSEMBLY_CREW,
            team=self.team,
        )
        base_url = reverse("protocol", kwargs={"pk": self.order.pk})
        self.url = f"{base_url}?pk={self.order.pk}"

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
