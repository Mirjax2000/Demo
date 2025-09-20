from dataclasses import dataclass
from rich.console import Console

# --- django
from django.conf import settings
from django.shortcuts import redirect

# --- models
from .models import Order, OrderBackProtocol, OrderBackProtocolToken, Status
from .models import OrderMontazImage, TeamType

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
    def closed_orders() -> dict[str, int]:
        status_billed = Order.objects.filter(status=Status.BILLED).count()
        status_canceled = Order.objects.filter(status=Status.CANCELED).count()
        return {
            "vyuctovane": status_billed,
            "zrusene": status_canceled,
        }

    @staticmethod
    def adviced_type_orders() -> dict[str, int]:
        status_adviced_by_assembly = Order.objects.filter(
            status=Status.ADVICED, team_type=TeamType.BY_ASSEMBLY_CREW
        ).count()
        status_adviced_by_delivery = Order.objects.filter(
            status=Status.ADVICED, team_type=TeamType.BY_DELIVERY_CREW
        ).count()
        return {
            "montazni": status_adviced_by_assembly,
            "dopravni": status_adviced_by_delivery,
        }

    @staticmethod
    def invalid_orders() -> tuple[bool, int]:
        return call_errors_adviced()

    @staticmethod
    def all_orders() -> int:
        count = Order.objects.exclude(status=Status.HIDDEN).count()
        return count

    @staticmethod
    def count_hidden() -> int:
        count = Order.objects.filter(status=Status.HIDDEN).count()
        return count
