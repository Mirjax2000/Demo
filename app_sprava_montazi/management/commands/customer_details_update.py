from http import client
from typing import TypedDict
from rich.console import Console
from django.core.management.base import BaseCommand, CommandParser, CommandError
from app_sprava_montazi.models import Client, Order

cons: Console = Console()


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.incomplete_customers: dict = {}

    def incomplete_customers_query(self):
        qs = Order.objects.filter(client__incomplete=True)
        seznam: list = []

        for record in qs:
            seznam.append(record.order_number.upper())

        return seznam

    def complete_customers_query(self):
        qs = Order.objects.filter(client__incomplete=False)
        seznam: list = []

        for record in qs:
            seznam.append(record.order_number.upper())

        return seznam

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("status", type=str, help="dotaz na status")

    def handle(self, *args, **kwargs):
        call_foo: dict = {
            "complete": self.complete_customers_query,
            "incomplete": self.incomplete_customers_query,
        }

        status = kwargs["status"]

        if status not in call_foo:
            raise CommandError("Status musí být 'complete' nebo 'incomplete'.")

        cons.log(call_foo[status]())
