"""Custom commands"""

from pathlib import Path
import pandas as pd
from django.core.management.base import BaseCommand
from rich.console import Console
from app_sprava_montazi.models import DistribHub, Order


cons: Console = Console()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        directory: Path = Path("./files")
        file: str = "dataset.csv"
        file_path: Path = directory / file
        dataset: pd.DataFrame = pd.read_csv(file_path, encoding="cp1250", delimiter=";")
        dataset.columns = dataset.columns.str.strip()
        dataset = dataset[["Místo urcení", "Císlo zakázky", "Mandant"]]
        dataset_dict: list = dataset.to_dict(orient="records")
        for item in dataset_dict:
            distrib_hub_obj = DistribHub.objects.get(code=item["Místo urcení"])
            order, created = Order.objects.get_or_create(
                order_number=item["Císlo zakázky"],
                distrib_hub=distrib_hub_obj,
                mandant=item["Mandant"],
            )
            if created:
                cons.log(f"{order} vytvoren")
            else:
                cons.log(f"{order} jiz existuje")
