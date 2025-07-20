import logging
from datetime import date, datetime

# --- django
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.messages import get_messages
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client as CL
from django.test import TestCase
from unittest.mock import patch
from django.utils import timezone
from django.test import override_settings

# --- modely
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
    OrderBackProtocolToken,
)

# --- oop
from app_sprava_montazi.OOP_emails import CustomEmail

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


class OrderProtocolView(TestCase):
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
        self.team_name_active: str = "active-company"
        self.team_name_not_active: str = "not-active-company"
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
        self.no_active_team = Team.objects.create(
            name=self.team_name_not_active,
            city=self.team_city,
            phone=self.team_phone,
            email=self.team_email,
            active=False,
        )
        # ---
        self.order_with_team = Order.objects.create(
            order_number="703777143100437749-R",
            distrib_hub=self.hub,
            status=Status.ADVICED,
            client=self.customer,
            mandant="SCCZ",
            evidence_termin=date.today(),
            team_type=TeamType.BY_ASSEMBLY_CREW,
            team=self.active_team,
        )
        self.order_without_team = Order.objects.create(
            order_number="703777143100437750-R",
            distrib_hub=self.hub,
            status=Status.ADVICED,
            client=self.customer,
            mandant="SCCZ",
            evidence_termin=date.today(),
            team_type=TeamType.BY_ASSEMBLY_CREW,
        )
        self.order_with_no_active_team = Order.objects.create(
            order_number="703777143100437751-R",
            distrib_hub=self.hub,
            status=Status.ADVICED,
            client=self.customer,
            mandant="SCCZ",
            evidence_termin=date.today(),
            team_type=TeamType.BY_ASSEMBLY_CREW,
            team=self.no_active_team,
        )
        # ---
        self.url_order_with_team = reverse(
            "protocol", kwargs={"pk": self.order_with_team.pk}
        )

        self.url_order_without_team = reverse(
            "protocol", kwargs={"pk": self.order_without_team.pk}
        )

        self.url_order_with_no_active_team = reverse(
            "protocol", kwargs={"pk": self.order_with_no_active_team.pk}
        )

    def test_logged_in_order_with_team(self):
        response = self.client.get(self.url_order_with_team)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_logged_in_order_without_team(self):
        response = self.client.get(self.url_order_without_team)
        self.assertEqual(response.status_code, 302)

    def test_logged_in_order_wit_not_active_team(self):
        response = self.client.get(self.url_order_with_no_active_team)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url_order_with_team)
        self.assertRedirects(
            response, f"{settings.LOGIN_URL}?next={self.url_order_with_team}"
        )

    def test_protocol_view_context_data_with_team(self):
        response = self.client.get(self.url_order_with_team)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)

        # Context
        context = response.context
        self.assertIn("order", context)
        self.assertIn("pdf_exists", context)
        self.assertIn("team", context)
        self.assertIn("recieved_protokol", context)
        self.assertIn("active", context)

        # Konkrétní hodnoty
        self.assertEqual(context["order"], self.order_with_team)
        self.assertEqual(context["team"], self.active_team)
        self.assertFalse(context["pdf_exists"])
        self.assertIsNone(context["recieved_protokol"])
        self.assertEqual(context["active"], "orders_all")

    def test_protocol_view_without_team_redirects(self):
        url = reverse("protocol", kwargs={"pk": self.order_without_team.pk})
        referer_url = reverse("order_detail", kwargs={"pk": self.order_without_team.pk})
        response = self.client.get(url, HTTP_REFERER=referer_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/", response.url)
        self.assertEqual(response.url, referer_url)

    def test_protocol_view_without_team_redirects_message(self):
        url = reverse("protocol", kwargs={"pk": self.order_without_team.pk})
        referer_url = reverse("order_detail", kwargs={"pk": self.order_without_team.pk})
        response = self.client.get(url, HTTP_REFERER=referer_url, follow=True)

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn("Není vybraný žádný montážní tým!", messages)
        self.assertEqual(response.status_code, 200)

    def test_html_content_active_team(self):
        response = self.client.get(self.url_order_with_team)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)
        self.assertContains(response, 'name="no-delete-team"', html=False)
        self.assertContains(response, self.team_name_active, html=False)
        self.assertContains(response, "Praha", html=False)
        self.assertContains(response, "234234234", html=False)
        self.assertContains(response, "ferda.company@gmail.cz", html=False)
        self.assertContains(response, "Aktivní", html=False)

    def test_html_content_not_active_team(self):
        response = self.client.get(self.url_order_with_no_active_team)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)
        self.assertContains(response, 'name="no-delete-team"', html=False)
        self.assertContains(response, self.team_name_not_active, html=False)
        self.assertContains(response, "Praha", html=False)
        self.assertContains(response, "234234234", html=False)
        self.assertContains(response, "ferda.company@gmail.cz", html=False)
        self.assertContains(response, "Neaktivní", html=False)


class OrderHiddenView(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")
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
        self.order_with_new = Order.objects.create(
            order_number="703777143100437749-R",
            distrib_hub=self.hub,
            status=Status.NEW,
            client=self.customer,
            mandant="SCCZ",
            evidence_termin=date.today(),
            team_type=TeamType.BY_ASSEMBLY_CREW,
            team=self.team,
        )

        base_url = reverse("order_hidden", kwargs={"pk": self.order_with_new.pk})
        self.url = f"{base_url}?pk={self.order_with_new.pk}"

    def test_logged_in(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.post(self.url)
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={self.url}")

    def test_protocol_view_redirects_message_success(self):
        response = self.client.post(self.url, follow=True)

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn(
            f"Zakázka: {self.order_with_new.order_number} byla skryta.", messages
        )
        self.assertEqual(response.status_code, 200)

    def test_protocol_view_redirects_message_error(self):
        old_record = self.order_with_new.status
        self.assertEqual(old_record, Status.NEW)
        self.order_with_new.status = Status.HIDDEN
        self.order_with_new.save()
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.order_with_new.refresh_from_db()
        new_record = self.order_with_new.status
        self.assertEqual(new_record, Status.HIDDEN)

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn("Zakázka: nemohla být skryta.", messages)


class SendMailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.client.login(username="testuser", password="pass")
        # order creation
        self.hub = DistribHub.objects.create(code="626", city="Chrastany")
        self.team = Team.objects.create(
            name="Ferda Company",
            city="Praha",
            phone="234234234",
            email="miroslav.viktorin@seznam.cz",
        )
        self.range: int = 10
        for i in range(self.range):
            customer = Client.objects.create(
                name=f"Customer test-{i}", zip_code=f"123{i:02}"
            )
            Order.objects.create(
                order_number=f"ADVICED-{i:05}-R",
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

    @patch(
        "app_sprava_montazi.views_services.CustomEmail.send_email_with_encrypted_pdf"
    )
    def test_send_mail_view_success_for_all_orders(self, mock_send_email):
        """Otestuje SendMailView pro všechny objednávky vytvořené v setUp."""
        mock_send_email.return_value = True  # mockneme odeslání e-mailu

        orders = Order.objects.all()

        for order in orders:
            response = self.client.get(reverse("send_mail", kwargs={"pk": order.pk}))

            # redirect
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(response, reverse("protocol", kwargs={"pk": order.pk}))

            # token vytvořen
            self.assertTrue(OrderBackProtocolToken.objects.filter(order=order).exists())

            # email byl "odeslán"
            mock_send_email.assert_called()

            # order byl aktualizován
            refreshed = Order.objects.get(pk=order.pk)
            self.assertIsNotNone(refreshed.mail_datum_sended)
            self.assertEqual(refreshed.mail_team_sended, self.team.name)

            # kontrola messages (nemusíš kontrolovat každou zprávu, stačí že něco je)
            messages = list(get_messages(response.wsgi_request))
            self.assertTrue(any("byl odeslan" in str(m.message) for m in messages))

    @patch(
        "app_sprava_montazi.views_services.CustomEmail.send_email_with_encrypted_pdf"
    )
    def test_send_mail_view_overwrites_old_token(self, mock_send_email):
        """Ověří, že starý token je smazán a nový vytvořen při každém odeslání e-mailu."""
        mock_send_email.return_value = True
        order = Order.objects.first()

        # 1️⃣ vytvoříme ručně starý token
        old_token_obj = OrderBackProtocolToken.objects.create(
            order=order, token="old_token"
        )

        # 2️⃣ zavoláme view
        response = self.client.get(reverse("send_mail", kwargs={"pk": order.pk}))

        # 3️⃣ zkontrolujeme, že byl vytvořen nový token
        new_token_obj = OrderBackProtocolToken.objects.get(order=order)
        self.assertNotEqual(
            new_token_obj.token, "old_token", msg="Token by se měl přepsat"
        )

        # 4️⃣ jen jeden token existuje
        self.assertEqual(
            OrderBackProtocolToken.objects.filter(order=order).count(),
            1,
            msg="Musí být přesně jeden token po přepsání",
        )

        # 5️⃣ zkontrolujeme redirect (pro jistotu)
        self.assertEqual(response.status_code, 302)
