"""Custom commands"""

from pathlib import Path
from datetime import datetime
from rich.console import Console
from pandas import DataFrame, read_csv
from django.core.management.base import BaseCommand, CommandParser
from django.utils.text import slugify
from app_sprava_montazi.models import DistribHub, Order, Client, TeamType

cons: Console = Console()


def create_datetime(source):
    """Format pro delivery/evidence termin"""
    if source:
        return datetime.strptime(str(source), "%d.%m.%Y").date()
    return None


def create_client(item: dict) -> tuple[Client, bool]:
    """Vytvoreni clienta"""
    name: str = f"{item['prijmeni']} {item['krestni-jmeno']}"
    client, client_created = Client.objects.get_or_create(
        name=name.strip(), zip_code=item["psc"]
    )
    if client_created:
        cons.log(f"🆗 {client} vytvoren", style="blue")
    else:
        cons.log(f"{client} jiz existuje", style="yellow")

    return client, client_created


def create_order(
    item: dict, distrib_hub_obj: DistribHub, client: Client, team_type
) -> tuple[Order, bool]:
    """vytvarim Order"""

    delivery_termin = create_datetime(item["avizovany-termin"])
    evidence_termin = create_datetime(item["erfassungstermin"])
    #
    order, order_created = Order.objects.get_or_create(
        order_number=item["cislo-zakazky"],
        distrib_hub=distrib_hub_obj,
        mandant=item["mandant"],
        client=client,
        delivery_termin=delivery_termin,
        evidence_termin=evidence_termin,
        team_type=team_type,
        notes=item["poznamka-mandanta"],
    )
    if order_created:
        cons.log(f"🆗 {order}: vytvoren", style="blue")
    else:
        cons.log(f"⚠️ {order}: jiz existuje ", style="red")
    cons.log("...")

    return order, order_created


def create_dataset(file_path) -> DataFrame:
    dataset: DataFrame = read_csv(
        file_path,
        encoding="cp1250",
        delimiter=";",
    ).dropna(how="all")
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
            "poznamka-mandanta",
        ]
    ]
    dataset["krestni-jmeno"] = dataset["krestni-jmeno"].fillna("")
    dataset["avizovany-termin"] = dataset["avizovany-termin"].fillna(False)
    dataset["poznamka-mandanta"] = dataset["poznamka-mandanta"].fillna("")
    dataset["cislo-zakazky"] = dataset["cislo-zakazky"].apply(slugify)
    return dataset


def create_log(
    dataset: DataFrame,
    client_count: int,
    basic_order_count: int,
    extend_order_count: int,
    duplicit_count: int,
) -> None:
    """Vypis logu"""
    cons.log("-" * 35)
    cons.log(f"celkovy pocet zaznamu v datasetu je: {len(dataset)}")
    cons.log(f"clientu vytvoreno: {client_count}", style="blue")
    cons.log("---")
    cons.log(f"zakazek basic vytvoreno: {basic_order_count}", style="blue")
    cons.log(f"zakazek extend vytvoreno: {extend_order_count}", style="blue")
    cons.log("---")
    cons.log(f"Duplicitni zakazky: {duplicit_count}", style="red bold")
    cons.log("-" * 35)


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("file", type=str, help="pridej soubor csv")

    def handle(self, *args, **kwargs) -> None:
        file_path: Path = Path("./files") / kwargs["file"]
        #
        dataset = create_dataset(file_path)
        # filtr datasetu
        # (montaz == 1) nebo (montaz == 0 a cislo_zakazky končí na -R)
        basic_dataset = dataset[dataset["montaz"] == 1]
        extend_dataset = dataset[
            (dataset["montaz"] == 0) & (dataset["cislo-zakazky"].str.endswith("-r"))
        ]

        #
        basic_order_count, extend_order_count, client_count, duplicit_count = 0, 0, 0, 0
        # -------------------------------
        for item in basic_dataset.to_dict(orient="records"):
            # ziskavam FK DistribHubu
            distrib_hub = DistribHub.objects.get(code=item["misto-urceni"])
            #
            # vytvarim FK clienta
            client, client_created = create_client(item)
            if client_created:
                client_count += 1
            #
            _, order_created = create_order(
                item, distrib_hub, client, TeamType.BY_ASSEMBLY_CREW
            )
            if order_created:
                basic_order_count += 1
            else:
                duplicit_count += 1

        for item in extend_dataset.to_dict(orient="records"):
            # ziskavam FK DistribHubu
            distrib_hub = DistribHub.objects.get(code=item["misto-urceni"])
            #
            # vytvarim FK clienta
            client, client_created = create_client(item)
            if client_created:
                client_count += 1
            #
            _, order_created = create_order(
                item, distrib_hub, client, TeamType.BY_CUSTOMER
            )
            if order_created:
                extend_order_count += 1
            else:
                duplicit_count += 1
        # -------------------------------
        create_log(
            dataset,
            client_count,
            basic_order_count,
            extend_order_count,
            duplicit_count,
        )
