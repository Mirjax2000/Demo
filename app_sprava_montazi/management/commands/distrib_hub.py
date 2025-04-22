from django.core.management.base import BaseCommand
from rich.console import Console
from app_sprava_montazi.models import DistribHub
from typing import TypedDict

cons: Console = Console()


class Hub(TypedDict):
    code: str
    city: str


hubs: list[Hub] = [
    {"code": "626", "city": "Chrášťany"},
    {"code": "652", "city": "Brno"},
    {"code": "653", "city": "Ostrava"},
]


class Command(BaseCommand):
    help = "vytvori tabulku DistribHub"

    def handle(self, *args, **kwargs) -> None:
        for hub in hubs:
            _, created = DistribHub.objects.get_or_create(
                code=hub["code"], city=hub["city"]
            )
            if created:
                cons.log(f"HUB: {hub['code']}-{hub['city']} vytvoren.", style="blue")
            else:
                cons.log(f"HUB: {hub['code']}-{hub['city']} uz existuje!", style="red")
