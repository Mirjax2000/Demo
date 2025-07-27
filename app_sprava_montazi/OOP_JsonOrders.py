"""OOP pro datatables a filtrovani querysetu"""

from typing import Tuple, TypedDict, TypeAlias
from rich.console import Console

# --- django
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.db.models.functions import Concat
from django.db.models import QuerySet, Q, F, Value

# --- models
from .models import Order, Client, Status, Team, TeamType

# --- utils
from .utils import check_order_error_adviced


# --- type aliases
class FilterDict(TypedDict):
    status: str
    od: str
    hub: str
    start_date: str | None
    end_date: str | None
    invalid: str | None
    mandant: str | None


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
ringing_bell_icon: str = (
    '<i class="fa-solid fa-bell fa-shake fa-sm u-txt-error-color me-1"></i>'
)


class JsonOrders:
    def __init__(self, request) -> None:
        self.request = request

    def get_filters(self) -> FilterDict:
        return Utils.parse_order_filters(self.request)

    def return_queryset(self) -> QuerySet:
        filters = self.get_filters()
        qs = Utils.filter_orders(filters)
        qs = qs.annotate(
            code_city=Concat("distrib_hub__code", Value("-"), "distrib_hub__city")
        )

        # Fulltext search z DataTables (globální vyhledávání)
        search_value = self.request.GET.get("search[value]", "").strip()
        if search_value:
            qs = qs.filter(
                Q(order_number__contains=search_value)
                | Q(code_city__icontains=search_value)
                | Q(mandant__icontains=search_value)
                | Q(client__name__icontains=search_value)
                | Q(team__name__icontains=search_value)
                | Q(evidence_termin__icontains=search_value)
                | Q(delivery_termin__icontains=search_value)
                | Q(montage_termin__icontains=search_value)
            )

        return qs

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
        error: bool = check_order_error_adviced(order.pk)
        name: str = "order-number"
        css: str = "L-table__link copy_link_order_number"
        content: str = str(order.order_number)
        order_link = reverse("order_detail", args=[order.pk])
        if error:
            css += " u-txt-error"
        result = f'<a href="{order_link}" name="{name}" class="{css}">{content}</a>'
        return result

    def distrib_hub_coll(self, order: Order) -> str:
        """Vraci __str__ z modelu"""
        name: str = "distrib-hub"
        content: str = str(order.distrib_hub)
        result: str = f'<span name="{name}">{content}</span>'
        return result

    def mandant_coll(self, order: Order) -> str:
        """Vraci mandant"""
        name: str = "mandant"
        content: str = str(order.mandant)
        result: str = f'<span name="{name}">{content}</span>'
        return result

    def evidence_termin_coll(self, order: Order) -> str:
        """Vraci evidence termin nebo -"""
        name: str = "evidence-termin"
        content: str = "-"
        css: str = "u-s-none"

        if order.evidence_termin:
            content = order.evidence_termin.strftime("%d.%m.%Y")

        result: str = f'<span name="{name}" class="{css}">{content}</span>'
        return result

    def deliver_termin_coll(self, order: Order) -> str:
        """Vraci delivery termin nebo -"""
        name: str = "delivery-termin"
        content: str = "-"
        css: str = "u-s-none"

        if order.delivery_termin:
            content = order.delivery_termin.strftime("%d.%m.%Y")

        result: str = f'<span name="{name}" class="{css}">{content}</span>'
        return result

    def client_coll(self, order: Order) -> str:
        """Vrací clienta complete nebo incomplete"""
        client: Client | None = order.client
        if not client:
            return '<span class="u-txt-error">Žádný klient</span>'

        name: str = "client"
        content: str = client.first_15()
        css: str = "u-txt-success"
        icon: str = success_icon
        title: str = str(client)

        if client.incomplete:
            css = "u-txt-warning"
            icon = exclamation_icon

        result: str = (
            f'<div title="{title}" name="{name}">{icon}'
            f'<span class="{css}">{content}</span></div>'
        )
        return result

    def team_type_coll(self, order: Order) -> str:
        """Vraci team type"""
        name: str = "team-type"
        css: str = "u-s-none"
        content: str = str(order.get_team_type_display())  # type: ignore

        if order.team_type == TeamType.BY_ASSEMBLY_CREW:
            css += " u-txt-success"
        elif order.team_type == TeamType.BY_DELIVERY_CREW:
            css += " u-txt-info"

        result: str = f'<span name="{name}" class="{css}">{content}</span>'
        return result

    def team_coll(self, order: Order) -> str:
        """Vrací tým a jeho stav jako HTML fragment"""
        name = "team"
        css = "u-s-none"
        content = "-"
        icon = ""
        title = ""

        team = order.team
        if team:
            title = team.name

        if order.is_missing_team():
            css += " u-txt-warning"
            icon = exclamation_icon
            content = "Nevybráno"

        elif team:
            css += " u-txt-success"
            icon = success_icon
            content = team.name_first_15()
            if not team.active:
                css = "u-s-none u-txt-error"
                icon = ringing_bell_icon

        result: str = f'<div title="{title}" name="{name}">{icon}<span class="{css}">{content}</span></div>'

        return result

    def montage_termin_coll(self, order: Order) -> str:
        """Vrací montage_termin jako HTML nebo varování."""
        name: str = "montage-termin"
        css: str = "u-s-none"
        content: str = "–"
        icon: str = ""
        time = timezone.localtime(order.montage_termin)

        if order.montage_termin:
            content = f"<strong>{time.strftime('%d.%m.%Y %H:%M')}</strong>"

        elif order.team_type == "By_assembly_crew":
            icon = exclamation_icon
            css += " u-txt-warning"
            content = "Nevybráno"

        result = f'<div name="{name}" class="{css}">{icon}<span>{content}</span></div>'
        return result

    def status_coll(self, order: Order) -> str:
        """Vrací status + případnou ikonu odkazu na protokol."""
        error = check_order_error_adviced(order.pk)
        content = order.get_status_display()[:8]  # type: ignore
        icon = ""

        if order.status == Status.ADVICED:
            icon_link = success_mail_icon
            if error:
                icon_link = warning_mail_icon

            if icon_link:
                icon = (
                    f'<a href="{reverse("protocol", kwargs={"pk": order.pk})}" '
                    f'title="Zobrazit protokol">{icon_link}</a>'
                )

        return f'<div name="status">{content} {icon}</div>'

    def articles_coll(self, order: Order) -> str:
        name: str = "articles"
        css = "u-s-none u-txt-center"
        article_count: str = str(order.articles.count())  # type: ignore

        if article_count == "0":
            css += " u-txt-error"
        result: str = f'<div name="{name}" "class="{css}">{article_count}</div>'

        return result

    def notes_coll(self, order: Order) -> str:
        name: str = "notes"
        title: str = order.notes
        content: str = order.notes_first_10()
        result: str = f'<span name="{name}" title="{title}">{content}</span>'

        return result


class Utils:
    @staticmethod
    def parse_order_filters(request) -> FilterDict:
        """Vrací hodnoty z GET parametrů pro filtrování objednávek."""
        return {
            "status": request.GET.get("status", "").strip(),
            "od": request.GET.get("od", "").strip(),
            "hub": request.GET.get("hub", "").strip(),
            "start_date": request.GET.get("start_date", "").strip() or None,
            "end_date": request.GET.get("end_date", "").strip() or None,
            "invalid": request.GET.get("invalid", "").strip() or None,
            "mandant": request.GET.get("mandant", "").strip() or None,
        }

    @staticmethod
    def filter_orders(filters: FilterDict) -> QuerySet:
        """Vrátí queryset objednávek podle GET parametrů."""
        if filters.get("invalid") == "true":
            return Utils.get_invalid_orders()
        # --- jinak normalni filtr
        return Utils.get_filtered_orders(filters)

    @staticmethod
    def get_invalid_orders() -> QuerySet:
        """Vrátí objednávky se statusem ADVICED, které mají chybu."""
        filtr: QuerySet = Order.objects.filter(status=Status.ADVICED).filter(
            Q(mail_datum_sended__isnull=True)
            | (
                Q(mail_datum_sended__isnull=False)
                & Q(team__name__isnull=False)
                & ~Q(team__name=F("mail_team_sended"))
            )
            | Q(team__active=False)
        )

        return filtr

    # --- stara verze
    # @staticmethod
    # def get_filtered_orders(filters: FilterDict) -> QuerySet:
    #     """Vrátí objednávky podle statusu, datumu a obchodního domu."""
    #     status = filters.get("status", "").strip()
    #     od_value = filters.get("od", "").strip()
    #     start_date = filters.get("start_date")
    #     end_date = filters.get("end_date")

    #     orders = Order.objects.all()

    #     if status == "all":
    #         orders = orders.exclude(status="Hidden")
    #     elif status == "closed":
    #         orders = orders.filter(status__in=["Billed", "Canceled"])
    #     elif status:
    #         orders = orders.filter(status=status)
    #     else:
    #         orders = orders.exclude(status__in=["Hidden", "Billed", "Canceled"])

    #     if start_date:
    #         orders = orders.filter(evidence_termin__gte=start_date)

    #     if end_date:
    #         orders = orders.filter(evidence_termin__lte=end_date)

    #     if od_value:
    #         orders = orders.filter(order_number__startswith=od_value)

    #     return orders

    @staticmethod
    def get_filtered_orders(filters: FilterDict) -> QuerySet:
        """Vrátí objednávky podle statusu, datumu a obchodního domu."""

        filter_cond: dict = {}
        exclude_cond: dict = {}

        status = filters.get("status", "")
        od_value = filters.get("od", "")
        hub_value = filters.get("hub", "")
        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        mandant = filters.get("mandant")

        # --- Status logika
        if status == "all":
            exclude_cond["status"] = "Hidden"
        elif status == "closed":
            filter_cond["status__in"] = ["Billed", "Canceled"]
        elif status:
            filter_cond["status"] = status
        else:
            exclude_cond["status__in"] = ["Hidden", "Billed", "Canceled"]

        # --- mandant
        if mandant:
            filter_cond["mandant"] = mandant

        # --- Datum od-do
        if start_date:
            filter_cond["evidence_termin__gte"] = start_date
        if end_date:
            filter_cond["evidence_termin__lte"] = end_date

        # --- Obchodní dům
        if od_value:
            filter_cond["order_number__startswith"] = od_value

        # --- Distrib Hub
        if hub_value:
            filter_cond["distrib_hub__slug"] = hub_value

        # --- Dotaz
        orders = Order.objects.filter(**filter_cond)

        if exclude_cond:
            orders = orders.exclude(**exclude_cond)

        return orders

    # --- verze filtru 2
    # @staticmethod
    # def get_filtered_orders_verze_2(filters: FilterDict) -> QuerySet:
    #     """Vrátí objednávky podle statusu, datumu a obchodního domu."""

    #     status = filters.get("status", "")
    #     od_value = filters.get("od", "")
    #     start_date = filters.get("start_date")
    #     end_date = filters.get("end_date")

    #     query = Q()

    #     # --- Status logika
    #     if status == "all":
    #         query &= ~Q(status="Hidden")  # vyřadit "Hidden"
    #     elif status == "closed":
    #         query &= Q(status__in=["Billed", "Canceled"])
    #     elif status:
    #         query &= Q(status=status)
    #     else:
    #         query &= ~Q(status__in=["Hidden", "Billed", "Canceled"])

    #     # --- Datum od-do
    #     if start_date:
    #         query &= Q(evidence_termin__gte=start_date)
    #     if end_date:
    #         query &= Q(evidence_termin__lte=end_date)

    #     # --- Obchodní dům
    #     if od_value:
    #         query &= Q(order_number__startswith=od_value)

    #     orders = Order.objects.filter(query)
    #     return orders


if __name__ == "__main__":
    ...
