"""View tests"""

from datetime import date
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from app_sprava_montazi.models import Order, DistribHub


class OrdersAllViewTest(TestCase):
    def setUp(self):
        # Vytvoříme testovacího uživatele
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        # Vytvoříme testovací DistribHub
        self.hub = DistribHub.objects.create(code="626", city="Chrastany")

        # Vytvoříme 20 objednávek
        for i in range(20):
            Order.objects.create(
                order_number=f"{i:05}-R",
                distrib_hub=self.hub,
                mandant="SCCZ",
                evidence_termin=date.today(),
            )

    def test_orders_all_view(self):
        """
        Test pro zobrazení všech objednávek.
        """
        response = self.client.get(reverse("orders"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "app_sprava_montazi/orders/orders_all.html")
