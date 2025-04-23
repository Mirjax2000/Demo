"""Custom commands"""

from pathlib import Path
import pandas as pd
from django.core.management.base import BaseCommand, CommandParser
from rich.console import Console
from django.utils.text import slugify
from app_sprava_montazi.models import DistribHub, Order, Client


cons: Console = Console()


def create_client(item) -> tuple[Client, bool]:
    name: str = f"{item['prijmeni']} {item['krestni-jmeno']}"
    client, client_created = Client.objects.get_or_create(
        name=name.strip(), zip_code=item["psc"]
    )
    if client_created:
        cons.log(f"🆗 {client} vytvoren", style="blue")
    else:
        cons.log(f"{client} jiz existuje", style="yellow")
    return client, client_created


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("file", type=str, help="pridej soubor csv")

    def handle(self, *args, **kwargs) -> None:
        directory: Path = Path("./files")
        file: str = kwargs["file"]
        file_path: Path = directory / file
        #
        dataset: pd.DataFrame = pd.read_csv(
            file_path,
            encoding="cp1250",
            delimiter=";",
        )
        #
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
                "avizovany-termin",
                "erfassungstermin",
            ]
        ]
        dataset["krestni-jmeno"] = dataset["krestni-jmeno"].fillna("")
        dataset["cislo-zakazky"] = dataset["cislo-zakazky"].apply(slugify)
        # filtr datasetu
        # montaz == 1
        # montaz == 0 a cislo_zakazky končí na -R
        filtered_dataset = dataset[
            (dataset["montaz"] == 1)
            | ((dataset["montaz"] == 0) & (dataset["cislo-zakazky"].str.endswith("-r")))
        ]

        cons.print(dataset.head())

        dataset_dict: list = filtered_dataset.to_dict(orient="records")
        #
        order_count, client_count, duplicit_count = 0, 0, 0
        #
        for item in dataset_dict:
            # ziskavam FK DistribHubu
            distrib_hub_obj = DistribHub.objects.get(code=item["misto-urceni"])

            #
            # vytvarim FK clienta
            client, client_created = create_client(item)
            if client_created:
                client_count += 1
            #
            # vytvarim Order
            # order, order_created = Order.objects.get_or_create(
            #     order_number=item["cislo-zakazky"],
            #     distrib_hub=distrib_hub_obj,
            #     mandant=item["mandant"],
            #     client=client,
            #     delivery_termin="",
            #     evidence_termin="",
            # )
            # if order_created:
            #     cons.log(f"🆗 {order}: vytvoren", style="blue")
            #     cons.log("...")
            #     order_count += 1

            # else:
            #     cons.log(f"⚠️ {order}: jiz existuje ", style="yellow")
            #     cons.log("...")
            #     duplicit_count += 1
        #
        cons.log("-" * 35)
        cons.log(f"celkovy pocet zaznamu v datasetu je: {len(dataset)}")
        cons.log(f"clientu vytvoreno: {client_count}", style="blue")
        cons.log(f"zakazek vytvoreno: {order_count}", style="blue")
        cons.log(f"Duplicitni zakazky: {duplicit_count}", style="red bold")
        cons.log("-" * 35)
