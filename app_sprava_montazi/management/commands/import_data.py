"""Custom commands"""

from datetime import datetime
from pathlib import Path
from typing import TypedDict

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.utils.text import slugify
from pandas import DataFrame, read_csv
from rich.console import Console

from app_sprava_montazi.models import Client, DistribHub, Order


class ClientRecord(TypedDict):
    """Typova anotace"""

    client: Client
    client_created: bool


class OrderRecord(TypedDict):
    """Typova anotace"""

    order: Order
    order_created: bool


# ---
cons: Console = Console()
# ---


class Command(BaseCommand):
    """Custom command"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter: dict[str, int] = {
            "by_assembly_crew_count": 0,
            "by_customer_count": 0,
            "client_count": 0,
            "duplicit_count": 0,
        }

    def update_counters(self, client: ClientRecord, order: OrderRecord) -> None:
        """Updating self.counter"""
        client_created = client["client_created"]
        order_instance = order["order"]
        order_created = order["order_created"]

        if client_created:
            self.counter["client_count"] += 1

        if order_created:
            if order_instance.team_type == "By_assembly_crew":
                self.counter["by_assembly_crew_count"] += 1
            elif order_instance.team_type == "By_customer":
                self.counter["by_customer_count"] += 1

        else:
            self.counter["duplicit_count"] += 1

    def create_orders_from_dataset(self, dataset: DataFrame) -> None:
        """create orders form dataset with progress bar"""

        for item in dataset.to_dict(orient="records"):
            try:
                # ziskavam FK DistribHubu
                distrib_hub: DistribHub = DistribHub.objects.get(
                    code=item["misto-urceni"]
                )
                # vytvarim FK clienta
                client: ClientRecord = CreateRecords.create_client(
                    item["prijmeni"], item["krestni-jmeno"], item["psc"]
                )
                # vytvarim Order
                order: OrderRecord = CreateRecords.create_order(
                    item, distrib_hub, client["client"]
                )

                self.update_counters(client, order)

            except DistribHub.DoesNotExist:
                cons.log(
                    f"Chybi DistribHub pro objednavku: \n"
                    f"{item.get('cislo-zakazky', 'N/A')}",
                    style="red",
                )
                raise

            except ValueError as e:
                cons.log(
                    f"spatna data ve sloupcich CSV souboru \n"
                    f"'{item.get('cislo-zakazky', 'N/A')}': {e}",
                    style="red",
                )
                raise

            except Exception as e:
                cons.log(
                    f"Neocekavana chyba u objednavky: \n"
                    f"{item.get('cislo-zakazky', 'N/A')} {str(e)}",
                    style="red",
                )
                raise

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("file", type=str, help="pridej soubor csv")

    def handle(self, *args, **kwargs):
        # cesta k souboru
        file_path: Path = Path("./files") / kwargs["file"]

        # nacteni datasetu
        dataset = DatasetTools.create_dataset(file_path)
        filtered_dataset: DataFrame = DatasetTools.dataset_filter(dataset)

        try:
            with transaction.atomic():
                self.create_orders_from_dataset(filtered_dataset)
                Utility.logs(dataset, self.counter)

        except Exception as e:
            cons.log(f"Dataset se nezpracoval kvuli chybe: {str(e)}", style="red bold")
            cons.log("Zadna data z tohoto souboru nebyla ulozena.", style="red")
            raise


class DatasetTools:
    """Utility class"""

    @staticmethod
    def create_dataset(file_path) -> DataFrame:
        """Create dataset"""
        expected_cols: list[str] = [
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
        dataset: DataFrame = read_csv(file_path, encoding="cp1250", delimiter=";")
        dataset.columns = dataset.columns.str.strip()
        dataset.columns = [slugify(col) for col in dataset.columns]
        # kontrola sloupcu
        missing = set(expected_cols) - set(dataset.columns)
        if missing:
            cons.log(f"chybi pozadovane sloupce: {missing}")
            raise KeyError(f"CSV soubor postrádá požadované sloupce: {missing}")
        # tvorba datasetu s pozadovanyma sloupcema
        dataset = dataset[expected_cols]
        # cisteni datasetu
        dataset["krestni-jmeno"] = dataset["krestni-jmeno"].fillna("")
        dataset["avizovany-termin"] = dataset["avizovany-termin"].fillna("").astype(str)
        dataset["erfassungstermin"] = dataset["erfassungstermin"].fillna("").astype(str)
        dataset["poznamka-mandanta"] = dataset["poznamka-mandanta"].fillna("")
        dataset["cislo-zakazky"] = dataset["cislo-zakazky"].apply(slugify)

        return dataset

    @staticmethod
    def create_datetime(source: str):
        if not source or source.strip().lower() == "nan":
            return None
        try:
            return datetime.strptime(source.strip(), "%d.%m.%Y").date()
        except ValueError:
            cons.log(f"Chybný formát data: '{source}'", style="yellow")
            return None

    @staticmethod
    def dataset_filter(dataset: DataFrame) -> DataFrame:
        """dataset filter"""

        filtered_dataset = dataset[
            (dataset["montaz"] == 1)
            | ((dataset["montaz"] == 0) & (dataset["cislo-zakazky"].str.endswith("-r")))
        ].copy()

        filtered_dataset["team_type"] = "By_customer"
        filtered_dataset.loc[filtered_dataset["montaz"] == 1, "team_type"] = (
            "By_assembly_crew"
        )

        return filtered_dataset


class CreateRecords:
    """Vytvareni zaznamu v DB"""

    @staticmethod
    def create_client(
        prijmeni: str,
        krestni_jmeno: str,
        psc: str,
    ) -> ClientRecord:
        """Vytvoreni zaznam clienta"""

        name: str = f"{prijmeni} {krestni_jmeno}"
        client, client_created = Client.objects.get_or_create(
            name=name.strip(), zip_code=psc
        )

        result: ClientRecord = {
            "client": client,
            "client_created": client_created,
        }

        return result

    @staticmethod
    def create_order(
        item: dict, distrib_hub_obj: DistribHub, client: Client
    ) -> OrderRecord:
        """vytvarim Order zaznam"""

        delivery_termin = DatasetTools.create_datetime(item["avizovany-termin"])
        evidence_termin = DatasetTools.create_datetime(item["erfassungstermin"])
        # ---
        order, order_created = Order.objects.get_or_create(
            order_number=item["cislo-zakazky"],
            defaults={
                "distrib_hub": distrib_hub_obj,
                "mandant": item["mandant"],
                "client": client,
                "delivery_termin": delivery_termin,
                "evidence_termin": evidence_termin,
                "team_type": item["team_type"],
                "notes": item["poznamka-mandanta"],
            },
        )
        result: OrderRecord = {
            "order": order,
            "order_created": order_created,
        }

        return result


class Utility:
    """Utility"""

    @staticmethod
    def logs(dataset: DataFrame, counter: dict[str, int]) -> None:
        """Vypis logu"""

        small_break: str = "------\n"
        big_break: str = "-" * 40 + "\n"
        order_sum = counter["by_assembly_crew_count"] + counter["by_customer_count"]
        cons.log(
            big_break
            + f"celkovy pocet zaznamu v datasetu je: {len(dataset)}\n"
            + f"clientu vytvoreno: {counter['client_count']}\n"
            + small_break
            + f"zakazek pro montaz vytvoreno: {counter['by_assembly_crew_count']}\n"
            + f"zakazek nerozhodnuto vytvoreno: {counter['by_customer_count']}\n"
            + small_break
            + f"zakazek celkem vytvoreno: {order_sum}\n"
            + small_break
            + f"Duplicitni zakazky: {counter['duplicit_count']}\n"
            + big_break,
            style="blue",
        )
