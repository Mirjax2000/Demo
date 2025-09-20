from dataclasses import dataclass
from rich.console import Console

# --- django
from django.conf import settings
from django.shortcuts import redirect

# --- models
from .models import Order, OrderBackProtocol, OrderBackProtocolToken, Status
from .models import OrderMontazImage

# ---
cons: Console = Console()
# ---


class Dashboard:
    def __init__(self) -> None:
        pass

    def open_orders(self):
        open_count = 10
        closed_count = 20
        return {"open_orders": open_count, "closed_orders": closed_count}
