"""utilitky"""

from django.db.models import QuerySet
from .models import Order


def parse_order_filters(request) -> dict:
    """Vrací hodnoty z GET parametrů pro filtrování objednávek."""
    return {
        "status": request.GET.get("status", "").strip(),
        "od": request.GET.get("od", "").strip(),
        "start_date": request.GET.get("start_date"),
        "end_date": request.GET.get("end_date"),
    }


def filter_orders(filters: dict) -> QuerySet:
    """Vrátí queryset objednávek podle GET ale pres filters"""
    orders = Order.objects.exclude(status="Hidden")

    status = filters.get("status", "").strip()
    od_value = filters.get("od", "").strip()
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")

    if status:
        orders = orders.filter(status=status)

    if start_date:
        orders = orders.filter(evidence_termin__gte=start_date)

    if end_date:
        orders = orders.filter(evidence_termin__lte=end_date)

    if od_value:
        orders = orders.filter(order_number__startswith=od_value)

    return orders
