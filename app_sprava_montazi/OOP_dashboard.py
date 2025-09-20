from dataclasses import dataclass
from rich.console import Console

# --- django
from django.conf import settings
from django.shortcuts import redirect

# --- models
from .models import Order, OrderBackProtocol, OrderBackProtocolToken, Status
from .models import OrderMontazImage

# utils
from .utils import call_errors_adviced

# ---
cons: Console = Console()
# ---


class Dashboard:
    @staticmethod
    def open_orders() -> dict[str, int]:
        status_new = Order.objects.filter(status=Status.NEW).count()
        status_adviced = Order.objects.filter(status=Status.ADVICED).count()
        status_realized = Order.objects.filter(status=Status.REALIZED).count()
        return {
            "nove": status_new,
            "zaterminovane": status_adviced,
            "realizovane": status_realized,
        }

    @staticmethod
    def invalid_orders() -> tuple[bool, int]:
        return call_errors_adviced()
