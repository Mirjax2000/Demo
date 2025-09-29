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
    def open_orders(qs=None) -> dict[str, int]:
        base = qs if qs is not None else Order.objects.all()
        status_new = base.filter(status=Status.NEW).count()
        status_adviced = base.filter(status=Status.ADVICED).count()
        status_realized = base.filter(status=Status.REALIZED).count()
        return {
            "nove": status_new,
            "zaterminovane": status_adviced,
            "realizovane": status_realized,
        }

    @staticmethod
    def closed_orders(qs=None) -> dict[str, int]:
        base = qs if qs is not None else Order.objects.all()
        status_billed = base.filter(status=Status.BILLED).count()
        status_canceled = base.filter(status=Status.CANCELED).count()
        return {
            "vyuctovane": status_billed,
            "zrusene": status_canceled,
        }

    @staticmethod
    def adviced_type_orders(qs=None) -> dict[str, int]:
        base = qs if qs is not None else Order.objects.all()
        status_adviced_by_assembly = base.filter(
            status=Status.ADVICED, team_type=TeamType.BY_ASSEMBLY_CREW
        ).count()
        status_adviced_by_delivery = base.filter(
            status=Status.ADVICED, team_type=TeamType.BY_DELIVERY_CREW
        ).count()
        return {
            "montazni": status_adviced_by_assembly,
            "dopravni": status_adviced_by_delivery,
        }

    @staticmethod
    def invalid_orders(qs=None) -> tuple[bool, int]:
        base = qs if qs is not None else None
        return call_errors_adviced(base)

    @staticmethod
    def all_orders(qs=None) -> int:
        base = qs if qs is not None else Order.objects.all()
        count = base.exclude(status=Status.HIDDEN).count()
        return count

    @staticmethod
    def count_hidden(qs=None) -> int:
        base = qs if qs is not None else Order.objects.all()
        count = base.filter(status=Status.HIDDEN).count()
        return count
