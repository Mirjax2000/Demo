"""Custom command distrib_hub"""

from rich.console import Console
from django.core.management.base import BaseCommand
from django.db.models import Count
from app_sprava_montazi.models import DistribHub, Client

cons: Console = Console()


class Command(BaseCommand):
    help = "Najde a vypíše duplicity podle name a zip_code"

    def handle(self, *args, **kwargs):
        cons.log("Spoustim kontrolu duplikace")

        duplicates = (
            Client.objects.values("name", "zip_code")
            .annotate(count=Count("id"))
            .filter(count__gt=1)
        )

        if not duplicates:
            self.stdout.write("Žádné duplicity podle name a zip_code nebyly nalezeny.")
            return

        self.stdout.write(f"Nalezeno {len(duplicates)} duplicitních kombinací:\n")

        for item in duplicates:
            name = item["name"]
            zip_code = item["zip_code"]
            count = item["count"]
            self.stdout.write(
                f"Duplicita: '{name}' se ZIP '{zip_code}' - počet: {count}"
            )

            clients = Client.objects.filter(name=name, zip_code=zip_code)
            for client in clients:
                self.stdout.write(
                    f"  - ID: {client.id}, Name: {client.name}, ZIP: {client.zip_code}"
                )
            self.stdout.write("")

        self.stdout.write("KONTROLA DUPLIKÁTŮ DOKONČENA.")
