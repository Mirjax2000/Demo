"""OOP pro datatables a filtrovani querysetu"""

from typing import TypedDict
from rich.console import Console

# --- django
from django.db.models import QuerySet
from django.http import JsonResponse
from django.urls import reverse

# --- models
from .models import Order


# --- type aliases
class FilterDict(TypedDict):
    status: str
    od: str
    start_date: str | None
    end_date: str | None


# ---
cons: Console = Console()


class Filter:
    def __init__(self, request) -> None:
        self.request = request
        self.json_orders = JsonOrders(self.request, self)

    def get_filters(self) -> FilterDict:
        return Utils.parse_order_filters(self.request)

    def return_queryset(self) -> QuerySet:
        filters = self.get_filters()
        return Utils.filter_orders(filters)


class JsonOrders:
    def __init__(self, request, parent: Filter) -> None:
        self.request = request
        self.parent: Filter = parent

    def get_json_data(self) -> JsonResponse:
        request = self.request
        draw = int(request.GET.get("draw", 1))
        start = int(request.GET.get("start", 0))
        length = int(request.GET.get("length", 15))

        queryset = self.parent.return_queryset()
        total_records = Order.objects.count()
        records_filtered = queryset.count()

        # --- ordering z DataTables ---
        order_column_index = request.GET.get("order[0][column]")
        order_dir = request.GET.get("order[0][dir]", "asc")

        if order_column_index is not None:
            # zjistíme název sloupce, podle kterého chceme řadit
            col_name = request.GET.get(f"columns[{order_column_index}][data]")
            if col_name:
                # složíme Django order string, podle směru
                order_prefix = "" if order_dir == "asc" else "-"
                queryset = queryset.order_by(f"{order_prefix}{col_name}")

        queryset = queryset[start : start + length]

        # ---
        data = []
        for order in queryset:
            order_link = reverse("order_detail", args=[order.pk])
            data.append(
                {
                    "order_number": (
                        f'<a href="{order_link}" class="L-table__link">'
                        f"{order.order_number}</a>"
                    ),
                    # ---
                    "distrib_hub": (
                        f"{order.distrib_hub.code} - {order.distrib_hub.city}"
                    ),
                    # ---
                    "mandant": order.mandant,
                }
            )

        response = {
            "draw": draw,
            "recordsTotal": total_records,
            "recordsFiltered": records_filtered,
            "data": data,
        }

        return JsonResponse(response)


class Utils:
    @staticmethod
    def parse_order_filters(request) -> FilterDict:
        """Vrací hodnoty z GET parametrů pro filtrování objednávek."""
        return {
            "status": request.GET.get("status", "").strip(),
            "od": request.GET.get("od", "").strip(),
            "start_date": request.GET.get("start_date", "").strip() or None,
            "end_date": request.GET.get("end_date", "").strip() or None,
        }

    @staticmethod
    def filter_orders(filters: FilterDict) -> QuerySet:
        """Vrátí queryset objednávek podle GET ale pres filters"""

        status = filters.get("status", "").strip()
        od_value = filters.get("od", "").strip()
        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        # --- dotaz na vsechno a postupne se pridavaji dalsi filtry
        orders = Order.objects.all()
        # --- status filtr
        # --- vsechny krome hidden
        if status == "all":
            orders = orders.exclude(status="Hidden")
        elif status == "closed":
            # --- Uzavrene
            orders = orders.filter(status__in=["Billed", "Canceled"])
        elif status:
            # --- jednotlive
            orders = orders.filter(status=status)
        else:
            # --- Otevrene - default filtr
            orders = orders.exclude(status__in=["Hidden", "Billed", "Canceled"])
        # --- casovy filtr
        if start_date:
            orders = orders.filter(evidence_termin__gte=start_date)

        if end_date:
            orders = orders.filter(evidence_termin__lte=end_date)
        # --- obchodni dum filtr
        if od_value:
            orders = orders.filter(order_number__startswith=od_value)

        return orders


if __name__ == "__main__":
    pass
