from http import client
from typing import TypedDict
from rich.console import Console
from django.core.management.base import BaseCommand, CommandParser, CommandError
from app_sprava_montazi.models import Client, Order

cons: Console = Console()


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.incomplete_customers: list[str] = self.incomplete_customers_query()
        self.complete_customers: list[str] = self.complete_customers_query()

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

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("status", type=str, help="dotaz na status")

    def handle(self, *args, **kwargs):
        call_foo: dict = {
            "complete": self.complete_customers,
            "incomplete": self.incomplete_customers,
        }

        status = kwargs["status"]

        if status not in call_foo:
            raise CommandError("Status musí být 'complete' nebo 'incomplete'.")

        cons.log(call_foo[status])


class SeleniumFunction(Command):
    recieved = [
        "SDFSDFSDFS":{"name": "franta",
                      "zip_code":"12345",
                      },
        "708809617500494793-O",
        "708807379000495388-R",
        "708806960800494870-R",
        "708804205600494935-O",
    ]



    def selenium_1(self):
        customers_incomplete = Command.incomplete_customers
