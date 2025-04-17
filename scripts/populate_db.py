import os
import sys
from pathlib import Path

import django
from rich.console import Console

root_path = Path(__file__).resolve().parent.parent
sys.path.append(str(root_path))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AMS.settings")
django.setup()
from app_sprava_montazi import models

cons: Console = Console()


# def populate():
#     authors: list[str] = ["J.K. Rowling", "George Orwell", "J.R.R. Tolkien"]
#     for name in authors:
#         _, create = Author.objects.get_or_create(name=name)
#         if create:
#             cons.log(f"Author: {name} byl pridan do DB", style="blue")
#         else:
#             cons.log(f"Author: {name} uz je v DB", style="red")
#     print("Databáze byla naplněna!")


if __name__ == "__main__":
    ...
