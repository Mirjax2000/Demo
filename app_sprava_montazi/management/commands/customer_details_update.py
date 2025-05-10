"""Customer Detail update custom command"""

from rich.console import Console
from django.core.management.base import BaseCommand, CommandParser, CommandError
from app_sprava_montazi.models import Client, Order

cons: Console = Console()


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.incomplete_customers: list[str] = self.incomplete_customers_query()
        self.complete_customers: list[str] = self.complete_customers_query()
        self.selenium_function: SeleniumFunction = SeleniumFunction(
            self.incomplete_customers
        )

    def incomplete_customers_query(self) -> list[str]:
        qs = Order.objects.filter(client__incomplete=True)
        seznam: list[str] = []

        for record in qs:
            seznam.append(record.order_number.upper())

        return seznam

    def complete_customers_query(self) -> list[str]:
        qs = Order.objects.filter(client__incomplete=False)
        seznam: list = []

        for record in qs:
            seznam.append(record.order_number.upper())

        return seznam

    def handle(self, *args, **kwargs):
        pass


class SeleniumFunction:
    """Selenium nastroje"""

    def __init__(self, incomplete_customers: list[str]):
        super().__init__()
        self.incomplete_customers: list[str] = incomplete_customers

    def selenium_foo_1(self, incomplete_list: list[str]) -> list:
        """zde logika ziskani vysledku ze selenia"""

        recieved_with_order_number: list = [
            {
                "708809617500494793-O": {
                    "name": "Franta",
                    "zip_code": "12345",
                    "city": "Praha",
                    "street": "Konvalinkova 15",
                    "phone": "234234234",
                    "email": "franta@seznam.cz",
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

        recieved_columns: list = [
            {
                "name": "Franta",
                "zip_code": "12345",
                "city": "Praha",
                "street": "Konvalinkova 15",
                "phone": "234234234",
                "email": "franta@seznam.cz",
            },
            {
                "name": "Pepa",
                "zip_code": "54321",
                "city": "Brno",
                "street": "Jabloňová 3",
                "phone": "777888999",
                "email": "pepa@centrum.cz",
            },
            {
                "name": "Lucie",
                "zip_code": "10000",
                "city": "Ostrava",
                "street": "Školní 22",
                "phone": "602123456",
                "email": "lucie@volny.cz",
            },
            {
                "name": "Karel",
                "zip_code": "11000",
                "city": "Plzeň",
                "street": "Hlavní 5",
                "phone": "601987654",
                "email": "karel@email.cz",
            },
        ]
        return recieved_with_order_number


# for item in recieved_with_order_number:
#     for order_number, data in item.items():
#         try:
#             order = Order.objects.get(order_number=order_number)
#             client = order.client
#             if client:
#                 client.name = data["name"]
#                 client.city = data.get("city", "")
#                 client.zip_code = data["zip_code"]
#                 client.street = data.get("street", "")
#                 client.phone = data.get("phone", "")
#                 client.email = data.get("email", "")
#                 client.save()  # slug se aktualizuje automaticky
#         except Order.DoesNotExist:
#             print(f"Order {order_number} not found")
