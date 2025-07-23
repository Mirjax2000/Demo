"""Customer Detail update custom command"""

from time import sleep
from django.db import transaction
from rich.console import Console
from django.core.management.base import BaseCommand, CommandParser, CommandError
from app_sprava_montazi.models import Client, Order
from django.conf import settings

cons: Console = Console()


class Command(BaseCommand):
    """Custom command"""

    def incomplete_customers_query(self) -> list[str]:
        qs = Order.objects.filter(client__incomplete=True)
        qs = qs.exclude(status="Hidden")
        seznam: list[str] = []

        for record in qs:
            seznam.append(record.order_number.upper())

        cons.log(f"zobrazuji prvnich 5: {seznam[:5]}")
        return seznam

    def update_customers(self, customer_details: list) -> None:
        """Update modelu Client"""
        for item in customer_details:
            for order_number, data in item.items():
                try:
                    order = Order.objects.get(order_number=order_number)
                    client = order.client
                    if client:
                        cons.log(f"zacatek {client.name} ma {client.incomplete}")
                        try:
                            with transaction.atomic():
                                # client.name = data["name"].strip()
                                client.city = data.get("city", "").strip()
                                # client.zip_code = data["zip_code"].strip()
                                client.street = data.get("street", "").strip()
                                client.phone = data.get("phone", "").strip()
                                client.email = data.get("email", "").strip()
                                client.save()
                                if settings.DEBUG:
                                    cons.log(
                                        f"{client.name} {client.zip_code}: byl aktualizovan."
                                    )
                                    cons.log(
                                        f"konec: {client.name} {client.zip_code} ma {client.incomplete}"
                                    )

                        except Exception:
                            if settings.DEBUG:
                                cons.log(
                                    f"{client.name} {client.zip_code}: Update selhal, nic se neulozilo."
                                )

                    else:
                        if settings.DEBUG:
                            cons.log(f"{client}: nenalezen")

                except Order.DoesNotExist:
                    if settings.DEBUG:
                        cons.log(f"Order {order_number} not found")

    def handle(self, *args, **kwargs):
        """Hlavni funkce"""
        incomplete_list: list[str] = self.incomplete_customers_query()
        customer_details = SeleniumFunction.selenium_foo_1(incomplete_list)
        try:
            self.update_customers(customer_details)
            cons.log("Funkce probehla v poradku", style="green")

        except Exception as e:
            cons.log(f"chyba {str(e)}")


class SeleniumFunction:
    """Selenium nastroje"""

    @staticmethod
    def selenium_foo_1(incomplete_list: list[str]) -> list:
        """zde logika ziskani vysledku ze selenia"""
        cons.log("ziskavam data pres Selenium", style="blue")
        sleep(3)
        recieved_with_order_number: list = [
            {
                "709809544700494450-O": {
                    "name": "Zakordonets Kateryna",
                    "zip_code": "30100",
                    "city": "Praha",
                    "street": "Konvalinkova 15",
                    "phone": "234234234",
                    "email": "katerina@seznam.cz",
                },
            },
            {
                "708807379000495388-R": {
                    "name": "Pepa",
                    "zip_code": "54321",
                    "city": "Brno",
                    "street": "Jabloňová 3",
                    "phone": "777888999",
                    "email": "pepa@centrum.cz",
                },
            },
            {
                "708806960800494870-R": {
                    "name": "Lucie",
                    "zip_code": "10000",
                    "city": "Ostrava",
                    "street": "Školní 22",
                    "phone": "602123456",
                    "email": "lucie@volny.cz",
                },
            },
            {
                "708804205600494935-O": {
                    "name": "Karel",
                    "zip_code": "11000",
                    "city": "Plzeň",
                    "street": "Hlavní 5",
                    "phone": "601987654",
                    "email": "karel@email.cz",
                },
            },
        ]

        return recieved_with_order_number
