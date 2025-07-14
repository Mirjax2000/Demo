"""OOP pro datatables a filtrovani querysetu"""

from typing import Tuple, TypedDict, TypeAlias
from rich.console import Console

# --- django
from django.db.models import QuerySet
from django.http import JsonResponse
from django.urls import reverse

# --- models
from .models import Order, Client, Article


# --- type aliases
class FilterDict(TypedDict):
    status: str
    od: str
    start_date: str | None
    end_date: str | None


JsonHeader: TypeAlias = Tuple[int, int, int, str | None, str]

# ---
cons: Console = Console()
# ---

exclamation_icon: str = (
    '<i class="fa-solid fa-triangle-exclamation me-1 u-txt-warning-color"></i>'
)
success_icon: str = '<i class="fa-solid fa-check me-1 u-txt-success-color"></i>'
warning_mail_icon: str = (
    '<i class="fa-solid fa-envelope fa-beat u-txt-warning-color"></i>'
)
success_mail_icon: str = (
    '<i class="fa-solid fa-envelope-circle-check u-txt-success-light-color"></i>'
)


class JsonOrders:
    def __init__(self, request) -> None:
        self.request = request

    def get_filters(self) -> FilterDict:
        return Utils.parse_order_filters(self.request)

    def return_queryset(self) -> QuerySet:
        filters = self.get_filters()
        return Utils.filter_orders(filters)

    def get_datatebles_params(self) -> JsonHeader:
        request = self.request
        draw = int(request.GET.get("draw", 1))
        start = int(request.GET.get("start", 0))
        length = int(request.GET.get("length", 15))
        order_coll_index: str = request.GET.get("order[0][column]")
        order_dir = request.GET.get("order[0][dir]", "asc")
        return draw, start, length, order_coll_index, order_dir

    def get_json_data(self) -> JsonResponse:
        request = self.request
        draw, start, length, order_coll_index, order_dir = self.get_datatebles_params()
        qs: QuerySet = self.return_queryset()
        records_total: int = Order.objects.count()
        records_filtered: int = qs.count()

        if order_coll_index is not None:
            # zjistíme název sloupce, podle kterého chceme řadit
            col_name = request.GET.get(f"columns[{order_coll_index}][data]")
            if col_name:
                # složíme Django order string, podle směru
                order_prefix = "" if order_dir == "asc" else "-"
                qs = qs.order_by(f"{order_prefix}{col_name}")

        qs = qs[start : start + length]

        # ---
        data = []
        for order in qs:
            data.append(
                {
                    "order_number": self.order_number_coll(order),
                    "distrib_hub": self.distrib_hub_coll(order),
                    "mandant": self.mandant_coll(order),
                    "evidence_termin": self.evidence_termin_coll(order),
                    "delivery_termin": self.deliver_termin_coll(order),
                    "client": self.client_coll(order),
                    "team_type": self.team_type_coll(order),
                    "team": self.team_coll(order),
                    "montage_termin": self.montage_termin_coll(order),
                    "status": self.status_coll(order),
                    "articles": self.articles_coll(order),
                    "notes": self.notes_coll(order),
                }
            )

        response = {
            "draw": draw,
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered,
            "data": data,
        }

        return JsonResponse(response)

    def order_number_coll(self, order: Order) -> str:
        """vraci i s linkem na order"""
        order_link = reverse("order_detail", args=[order.pk])
        result = (
            f'<a href="{order_link}" class="L-table__link">{order.order_number}</a>'
        )
        return result

    def distrib_hub_coll(self, order: Order) -> str:
        """Vraci __str__ z modelu"""
        result: str = str(order.distrib_hub)
        return result

    def mandant_coll(self, order: Order) -> str:
        """Vraci mandant"""
        result: str = str(order.mandant)
        return result

    def evidence_termin_coll(self, order: Order) -> str:
        """Vraci evidence termin nebo -"""
        result: str = "-"
        if order.evidence_termin:
            result = order.evidence_termin.strftime("%d.%m.%Y")
        return result

    def deliver_termin_coll(self, order: Order) -> str:
        """Vraci delivery termin nebo -"""
        result: str = "-"
        if order.delivery_termin:
            result = order.delivery_termin.strftime("%d.%m.%Y")
        return result

    def client_coll(self, order: Order) -> str:
        """Vrací clienta complete nebo incomplete"""
        client: Client | None = order.client
        if not client:
            return '<span class="u-txt-error">Žádný klient</span>'

        css: str = "u-txt-success"
        icon: str = success_icon
        title: str = str(client)

        if client.incomplete:
            css = "u-txt-warning"
            icon = exclamation_icon

        result: str = (
            f'<span title="{title}">{icon}'
            f'<span class="{css}">{client.first_15()}</span></span>'
        )
        return result

    def team_type_coll(self, order: Order) -> str:
        """Vraci team type"""
        css: str = "u-s-none"
        if order.team_type == "By_assembly_crew":
            css += " u-txt-success"
        result: str = f'<span class="{css}">{order.get_team_type_display()}</span>'  # type: ignore
        return result

    def team_coll(self, order: Order) -> str:
        """Vraci team type"""

        css: str = "u-s-none"
        content: str = "-"
        icon: str = ""

        if order.is_missing_team():
            css += " u-txt-warning"
            icon = exclamation_icon
            content = "Nevybráno"

        elif order.team:
            css += " u-txt-success"
            icon = success_icon
            content = f"{order.team}"

        result: str = f'<span>{icon}<span class="{css}">{content}</span></span>'

        return result

    def montage_termin_coll(self, order: Order) -> str:
        """Vrací montage_termin jako HTML nebo varování."""

        css: str = "u-s-none"
        content: str = "–"
        icon: str = ""

        if order.montage_termin:
            content = (
                f"<strong>{order.montage_termin.strftime('%d.%m.%Y %H:%M')}</strong>"
            )
        elif order.team_type == "By_assembly_crew":
            icon = exclamation_icon
            css += " u-txt-warning"
            content = "Nevybráno"

        result = f'<span>{icon}<span class="{css}">{content}</span></span>'
        return result

    def status_coll(self, order: Order) -> str:
        """Vrací status + případnou ikonu odkazu na protokol."""

        content = order.get_status_display()[:8]  # type: ignore
        icon: str = ""

        if order.status == "Adviced":
            icon_link: str = warning_mail_icon
            if order.mail_datum_sended:
                icon_link = success_mail_icon

            icon = (
                f'<a href="{reverse("protocol", kwargs={"pk": order.pk})}"'
                f'title="Zobrazit protokol">'
                f"{icon_link}</a>"
            )

        result = f"{content} {icon}"
        return result

    def articles_coll(self, order: Order) -> str:
        css = "u-s-none u-txt-center"
        article_count: str = str(order.articles.count())  # type: ignore
        if article_count == "0":
            css += " u-txt-error"
        result: str = f'<div class="{css}">{article_count}</div>'

        return result

    def notes_coll(self, order: Order) -> str:
        title: str = order.notes
        content: str = order.notes_first_10()
        result: str = f'<span title="{title}">{content}</span>'

        return result


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
    ...
