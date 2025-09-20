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
