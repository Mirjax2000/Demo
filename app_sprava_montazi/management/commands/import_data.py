"""Custom commands"""

from pathlib import Path
from datetime import datetime
from django.conf.locale import da
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


def create_client(prijmeni: str, krestni_jmeno: str, psc: str) -> tuple[Client, bool]:
    """Vytvoreni clienta"""
    name: str = f"{prijmeni} {krestni_jmeno}"
    client, client_created = Client.objects.get_or_create(
        name=name.strip(), zip_code=psc
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


def dataset_filter(dataset) -> tuple[DataFrame, DataFrame]:
    basic_dataset = dataset[dataset["montaz"] == 1]
    extend_dataset = dataset[
        (dataset["montaz"] == 0) & (dataset["cislo-zakazky"].str.endswith("-r"))
    ]
    return basic_dataset, extend_dataset


def create_orders_from_dataset(
    dataset: DataFrame,
    team_type,
    counter: str,
    basic_order_count: int = 0,
    extend_order_count: int = 0,
    client_count: int = 0,
    duplicit_count: int = 0,
):
    for item in dataset.to_dict(orient="records"):
        # ziskavam FK DistribHubu
        distrib_hub = DistribHub.objects.get(code=item["misto-urceni"])
        #
        # vytvarim FK clienta
        client, client_created = create_client(
            item["prijmeni"], item["krestni-jmeno"], item["psc"]
        )
        if client_created:
            client_count += 1
        #
        _, order_created = create_order(item, distrib_hub, client, team_type)
        if order_created:
            if counter == "basic":
                basic_order_count += 1
            elif counter == "extend":
                extend_order_count += 1

        else:
            duplicit_count += 1
    return basic_order_count, extend_order_count, client_count, duplicit_count


def logs(
    dataset: DataFrame,
    client_count: int,
    basic_order_count: int,
    extend_order_count: int,
    duplicit_count: int,
) -> None:
    """Vypis logu"""
    small_break: str = "------\n"
    big_break: str = "-" * 40
    cons.log(
        big_break
        + "\n"
        + f"celkovy pocet zaznamu v datasetu je: {len(dataset)}\n"
        + f"clientu vytvoreno: {client_count}\n"
        + small_break
        + f"zakazek basic vytvoreno: {basic_order_count}\n"
        + f"zakazek extend vytvoreno: {extend_order_count}\n"
        + small_break
        + f"zakazek celkem vytvoreno: {extend_order_count + basic_order_count}\n"
        + small_break
        + f"Duplicitni zakazky: {duplicit_count}\n"
        + big_break
        + "\n",
        style="blue",
    )


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("file", type=str, help="pridej soubor csv")

    def handle(self, *args, **kwargs) -> None:
        file_path: Path = Path("./files") / kwargs["file"]
        # ---
        dataset = create_dataset(file_path)
        basic_dataset, extend_dataset = dataset_filter(dataset)
        # ---
        datasets = [
            (basic_dataset, TeamType.BY_ASSEMBLY_CREW, "basic"),
            (extend_dataset, TeamType.BY_CUSTOMER, "extend"),
        ]
        # Inicializace počítadel
        basic_order_count = 0
        extend_order_count = 0
        client_count = 0
        duplicit_count = 0
        # spusteni create funkce v cyklu
        # -------------------------------
        for _dataset, team_type, counter in datasets:
            basic_order_count, extend_order_count, client_count, duplicit_count = (
                create_orders_from_dataset(
                    _dataset,
                    team_type,
                    counter,
                    basic_order_count,
                    extend_order_count,
                    client_count,
                    duplicit_count,
                )
            )
        # -------------------------------
        logs(
            dataset,
            client_count,
            basic_order_count,
            extend_order_count,
            duplicit_count,
        )
