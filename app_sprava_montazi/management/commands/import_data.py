"""Custom commands"""

from pathlib import Path
import pandas as pd
from django.core.management.base import BaseCommand
from rich.console import Console
from django.utils.text import slugify
from app_sprava_montazi.models import DistribHub, Order, Client


cons: Console = Console()


class Command(BaseCommand):
    def handle(self, *args, **kwargs) -> None:
        directory: Path = Path("./files")
        file: str = "dataset.csv"
        file_path: Path = directory / file
        #
        dataset: pd.DataFrame = pd.read_csv(
            file_path,
            encoding="cp1250",
            delimiter=";",
        )
        dataset.columns = dataset.columns.str.strip()
        dataset.columns = [slugify(col) for col in dataset.columns]
        dataset = dataset[
            [
                "misto-urceni",
                "cislo-zakazky",
                "mandant",
                "prijmeni",
                "krestni-jmeno",
                "psc",
                "montaz",
            ]
        ]
        dataset["krestni-jmeno"] = dataset["krestni-jmeno"].fillna("")
        # filtr datasetu
        # montaz == 1
        # montaz == 0 a cislo_zakazky končí na -R
        filtered_dataset = dataset[
            (dataset["montaz"] == 1)
            | ((dataset["montaz"] == 0) & (dataset["cislo-zakazky"].str.endswith("-R")))
        ]
        cons.print(dataset.info())
        cons.print(filtered_dataset.info())

        dataset_dict: list = filtered_dataset.to_dict(orient="records")
        order_count, client_count, duplicit_count = 0, 0, 0
        #
        for item in dataset_dict:
            # ziskavam FK DistribHubu
            distrib_hub_obj = DistribHub.objects.get(code=item["misto-urceni"])
            # vytvarim FK clienta
            name: str = f"{item['prijmeni']} {item['krestni-jmeno']}"
            client, client_created = Client.objects.get_or_create(
                name=name.strip(), zip_code=item["psc"]
            )
            if client_created:
                cons.log(f"{client} vytvoren", style="blue")
                client_count += 1
            else:
                cons.log(f"{client} jiz existuje", style="yellow")
            #
            # vytvarim Order
            order, order_created = Order.objects.get_or_create(
                order_number=item["cislo-zakazky"],
                distrib_hub=distrib_hub_obj,
                mandant=item["mandant"],
                client=client,
            )
            if order_created:
                cons.log(f"{order} vytvoren", style="blue")
                order_count += 1
            else:
                cons.log(f"{order} jiz existuje", style="yellow")
                duplicit_count += 1
        #
        cons.log("-" * 35)
        cons.log(f"clientu vytvoreno: {client_count}", style="blue")
        cons.log(f"zakazek vytvoreno: {order_count}", style="blue")
        cons.log(f"Duplicitni zakazky: {duplicit_count}", style="red bold")
        cons.log("-" * 35)
