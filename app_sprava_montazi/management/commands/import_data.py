"""Custom commands"""

from pathlib import Path
import pandas as pd
from django.core.management.base import BaseCommand
from rich.console import Console
from django.utils.text import slugify
from app_sprava_montazi.models import DistribHub, Order


cons: Console = Console()


class Command(BaseCommand):
    def handle(self, *args, **kwargs) -> None:
        directory: Path = Path("./files")
        file: str = "dataset.csv"
        file_path: Path = directory / file
        #
        dataset: pd.DataFrame = pd.read_csv(file_path, encoding="cp1250", delimiter=";")
        dataset.columns = dataset.columns.str.strip()
        dataset.columns = [slugify(col) for col in dataset.columns]

        dataset = dataset[["misto-urceni", "cislo-zakazky", "mandant"]]
        cons.print(dataset.head)
        dataset_dict: list = dataset.to_dict(orient="records")

        for item in dataset_dict:
            distrib_hub_obj = DistribHub.objects.get(code=item["misto-urceni"])
            #
            order, created = Order.objects.get_or_create(
                order_number=item["cislo-zakazky"],
                distrib_hub=distrib_hub_obj,
                mandant=item["mandant"],
            )
            if created:
                cons.log(f"{order} vytvoren")
            else:
                cons.log(f"{order} jiz existuje")
