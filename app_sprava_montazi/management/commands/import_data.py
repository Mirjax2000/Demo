"""Custom commands"""

from pathlib import Path
from datetime import datetime
from typing import TypedDict
from django.db import transaction
from rich.console import Console
from pandas import DataFrame, read_csv
from django.core.management.base import BaseCommand, CommandParser
from django.utils.text import slugify
from app_sprava_montazi.models import DistribHub, Order, Client, TeamType


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
        # ---
        self.counter: dict[str, int] = {
            "basic_order_count": 0,
            "extend_order_count": 0,
            "client_count": 0,
            "duplicit_count": 0,
        }

    def create_orders_from_dataset(
        self,
        dataset: DataFrame,
        team_type: TeamType,
        counter_type: str,
    ) -> None:
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
                if client["client_created"]:
                    self.counter["client_count"] += 1
                # vytvarim Order
                order: OrderRecord = CreateRecords.create_order(
                    item, distrib_hub, client["client"], team_type
                )
                # =========================================
                if order["order_created"]:
                    if counter_type == "basic":
                        self.counter["basic_order_count"] += 1
                    elif counter_type == "extend":
                        self.counter["extend_order_count"] += 1
                else:
                    self.counter["duplicit_count"] += 1
                # =========================================
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
                    f"{item.get('cislo-zakazky', 'N/A')} {e}",
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
        all_datasets: dict[str, DataFrame] = DatasetTools.dataset_filter(dataset)

        # rozdeleni datasetu podle typu montaze
        datasets: list[tuple] = [
            (all_datasets["basic_dataset"], TeamType.BY_ASSEMBLY_CREW, "basic"),
            (all_datasets["extend_dataset"], TeamType.BY_CUSTOMER, "extend"),
        ]

        try:
            with transaction.atomic():
                for df, team_type, counter_type in datasets:
                    self.create_orders_from_dataset(df, team_type, counter_type)

                # pokud vse probehlo bez chyby, vypiseme logy
                Utility.logs(dataset, self.counter)

        except Exception as e:
            cons.log(f"Dataset se nezpracoval kvuli chybe: {e}", style="red bold")
            cons.log("Zadna data z tohoto souboru nebyla ulozena.", style="red")
            raise

        finally:
            self.counter.clear()


class DatasetTools:
    """Utility class"""

    @staticmethod
    def create_dataset(file_path) -> DataFrame:
        """Create dataset"""
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
        # cisteni datasetu
        dataset["krestni-jmeno"] = dataset["krestni-jmeno"].fillna("")
        dataset["avizovany-termin"] = dataset["avizovany-termin"].fillna(False)
        dataset["poznamka-mandanta"] = dataset["poznamka-mandanta"].fillna("")
        dataset["cislo-zakazky"] = dataset["cislo-zakazky"].apply(slugify)

        return dataset

    @staticmethod
    def create_datetime(source):
        """Format pro delivery/evidence termin"""
        if source:
            return datetime.strptime(str(source), "%d.%m.%Y").date()
        return None

    @staticmethod
    def dataset_filter(dataset: DataFrame) -> DataFrame:
        """dataset filter"""

        dataset = dataset[
            (dataset["montaz"] == 1)
            | ((dataset["montaz"] == 0) & (dataset["cislo-zakazky"].str.endswith("-r")))
        ].copy()

        dataset["team_type"] = "By_customer"
        dataset.loc[dataset["montaz"] == 1, "team_type"] = "By_assembly_crew"

        return dataset


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
        item: dict,
        distrib_hub_obj: DistribHub,
        client: Client,
        team_type: TeamType,
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
                "team_type": team_type,
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
        order_sum = counter["extend_order_count"] + counter["basic_order_count"]
        cons.log(
            big_break
            + f"celkovy pocet zaznamu v datasetu je: {len(dataset)}\n"
            + f"clientu vytvoreno: {counter['client_count']}\n"
            + small_break
            + f"zakazek basic vytvoreno: {counter['basic_order_count']}\n"
            + f"zakazek extend vytvoreno: {counter['extend_order_count']}\n"
            + small_break
            + f"zakazek celkem vytvoreno: {order_sum}\n"
            + small_break
            + f"Duplicitni zakazky: {counter['duplicit_count']}\n"
            + big_break,
            style="blue",
        )
