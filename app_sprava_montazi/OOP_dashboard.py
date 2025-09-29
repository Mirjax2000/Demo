from dataclasses import dataclass
from rich.console import Console

# --- django
from django.conf import settings
from django.shortcuts import redirect
from django.db.models import Q

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

    @staticmethod
    def no_montage_term_orders(qs=None) -> int:
        """Count orders (excluding HIDDEN) where montage_termin is not set.
        Respects provided queryset filtering (evidence_termin filter from form).
        """
        base = qs if qs is not None else Order.objects.all()
        base = base.exclude(status=Status.HIDDEN)
        count = base.filter(montage_termin__isnull=True).count()
        return count


    @staticmethod
    def new_orders_issues(qs=None):
        """Return queryset of NEW orders that are missing one of the required items:
        - delivery_termin (agreed delivery date)
        - assigned montage team when realization is by assembly crew
        - completed customer contact details (client.incomplete True or missing client)
        Respects provided queryset filtering (evidence_termin filter from form).
        """
        base = qs if qs is not None else Order.objects.all()
        base = base.filter(status=Status.NEW)

        cond_missing_delivery = Q(delivery_termin__isnull=True)
        cond_missing_team = Q(team__isnull=True, team_type=TeamType.BY_ASSEMBLY_CREW)
        cond_incomplete_client = Q(client__isnull=True) | Q(client__incomplete=True)

        queryset = (
            base.filter(
                cond_missing_delivery | cond_missing_team | cond_incomplete_client
            )
            .select_related("client", "team", "distrib_hub")
            .distinct()
        )
        return queryset

from dataclasses import dataclass
from rich.console import Console

# --- django
from django.conf import settings
from django.shortcuts import redirect
from django.db.models import Q

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

    @staticmethod
    def no_montage_term_orders(qs=None) -> int:
        """Count orders (excluding HIDDEN) where montage_termin is not set.
        Respects provided queryset filtering (evidence_termin filter from form).
        """
        base = qs if qs is not None else Order.objects.all()
        base = base.exclude(status=Status.HIDDEN)
        count = base.filter(montage_termin__isnull=True).count()
        return count


    @staticmethod
    def new_orders_issues(qs=None):
        """Return queryset of NEW orders that are missing one of the required items:
        - delivery_termin (agreed delivery date)
        - assigned montage team when realization is by assembly crew
        - completed customer contact details (client.incomplete True or missing client)
        Respects provided queryset filtering (evidence_termin filter from form).
        """
        base = qs if qs is not None else Order.objects.all()
        base = base.filter(status=Status.NEW)

        cond_missing_delivery = Q(delivery_termin__isnull=True)
        cond_missing_team = Q(team__isnull=True, team_type=TeamType.BY_ASSEMBLY_CREW)
        cond_incomplete_client = Q(client__isnull=True) | Q(client__incomplete=True)

        queryset = (
            base.filter(
                cond_missing_delivery | cond_missing_team | cond_incomplete_client
            )
            .select_related("client", "team", "distrib_hub")
            .distinct()
        )
        return queryset

    @staticmethod
    def customer_r_orders(qs=None):
        """Orders with order_number ending with '-R' (case-insensitive), realization by customer,
        and status NEW. Excludes HIDDEN. Respects provided queryset filtering.
        """
        base = qs if qs is not None else Order.objects.all()
        base = base.exclude(status=Status.HIDDEN)
        queryset = (
            base.filter(
                team_type=TeamType.BY_CUSTOMER,
                order_number__iendswith="-r",
                status=Status.NEW,
            )
            .select_related("client")
            .order_by("-evidence_termin")
        )
        return queryset
