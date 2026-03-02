"""
API v1 Filters — filtrovací třídy pro DRF.
"""

from django_filters import rest_framework as filters

from django.db.models import Q, F

from app_sprava_montazi.models import (
    Order,
    Client,
    Team,
    Status,
    TeamType,
    DistribHub,
    FinanceCostItem,
    FinanceRevenueItem,
    CallLog,
)


class OrderFilter(filters.FilterSet):
    """Filtrování zakázek pro DataTables i obecné API."""

    status = filters.ChoiceFilter(choices=Status.choices)
    team_type = filters.ChoiceFilter(choices=TeamType.choices)
    mandant = filters.CharFilter(lookup_expr="exact")
    distrib_hub = filters.NumberFilter(field_name="distrib_hub_id")

    # --- nevalidní zakázky (ADVICED + BY_ASSEMBLY_CREW s problémy)
    invalid = filters.BooleanFilter(method="filter_invalid")

    # --- bez termínu montáže (exclude HIDDEN + closed)
    no_montage_term = filters.BooleanFilter(method="filter_no_montage_term")

    # --- časové rozsahy
    evidence_from = filters.DateFilter(
        field_name="evidence_termin", lookup_expr="gte"
    )
    evidence_to = filters.DateFilter(
        field_name="evidence_termin", lookup_expr="lte"
    )
    delivery_from = filters.DateFilter(
        field_name="delivery_termin", lookup_expr="gte"
    )
    delivery_to = filters.DateFilter(
        field_name="delivery_termin", lookup_expr="lte"
    )
    montage_from = filters.DateTimeFilter(
        field_name="montage_termin", lookup_expr="gte"
    )
    montage_to = filters.DateTimeFilter(
        field_name="montage_termin", lookup_expr="lte"
    )

    # --- rok/měsíc pro dashboard
    year = filters.NumberFilter(field_name="evidence_termin", lookup_expr="year")
    month = filters.NumberFilter(field_name="evidence_termin", lookup_expr="month")

    # --- zakázky podle prefix čísla (OD)
    order_number_prefix = filters.CharFilter(
        field_name="order_number", lookup_expr="istartswith"
    )

    # --- neúplný klient
    client_incomplete = filters.BooleanFilter(field_name="client__incomplete")

    # --- stav skupiny (otevřené = bez hidden/billed/canceled)
    status_group = filters.CharFilter(method="filter_status_group")

    # --- klient slug
    client_slug = filters.CharFilter(field_name="client__slug")

    # --- tým
    team_id = filters.NumberFilter(field_name="team_id")

    class Meta:
        model = Order
        fields = [
            "status",
            "team_type",
            "mandant",
            "distrib_hub",
            "team_id",
        ]

    def filter_status_group(self, queryset, name, value):
        """
        Skupiny:
         - 'open': vše kromě Hidden, Billed, Canceled
         - 'closed': Billed + Canceled
         - 'all': vše kromě Hidden
        """
        if value == "open":
            return queryset.exclude(
                status__in=[Status.HIDDEN, Status.BILLED, Status.CANCELED]
            )
        elif value == "closed":
            return queryset.filter(status__in=[Status.BILLED, Status.CANCELED])
        elif value == "all":
            return queryset.exclude(status=Status.HIDDEN)
        return queryset

    def filter_invalid(self, queryset, name, value):
        """Nevalidní = ADVICED + BY_ASSEMBLY_CREW s: mail neodeslaný ||
        tým nesouhlasí || tým neaktivní."""
        if not value:
            return queryset
        base = queryset.filter(
            status=Status.ADVICED, team_type=TeamType.BY_ASSEMBLY_CREW
        )
        cond_mail = Q(mail_datum_sended__isnull=True)
        cond_soulad = Q(
            mail_datum_sended__isnull=False, team__name__isnull=False
        ) & ~Q(team__name=F("mail_team_sended"))
        cond_inactive = Q(team__active=False)
        return base.filter(cond_mail | cond_soulad | cond_inactive)

    def filter_no_montage_term(self, queryset, name, value):
        """Zakázky bez termínu montáže (exclude hidden + closed)."""
        if not value:
            return queryset
        return queryset.exclude(
            status__in=[Status.HIDDEN, Status.BILLED, Status.CANCELED]
        ).filter(montage_termin__isnull=True)


class ClientFilter(filters.FilterSet):
    incomplete = filters.BooleanFilter()
    name = filters.CharFilter(lookup_expr="icontains")
    city = filters.CharFilter(lookup_expr="icontains")
    zip_code = filters.CharFilter(lookup_expr="exact")

    class Meta:
        model = Client
        fields = ["incomplete", "name", "city", "zip_code"]


class TeamFilter(filters.FilterSet):
    active = filters.BooleanFilter()
    name = filters.CharFilter(lookup_expr="icontains")
    city = filters.CharFilter(lookup_expr="icontains")
    region = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Team
        fields = ["active", "name", "city", "region"]


class FinanceRevenueItemFilter(filters.FilterSet):
    order = filters.NumberFilter(field_name="order_id")

    class Meta:
        model = FinanceRevenueItem
        fields = ["order"]


class FinanceCostItemFilter(filters.FilterSet):
    order = filters.NumberFilter(field_name="order_id")
    team = filters.NumberFilter(field_name="team_id")
    carrier_confirmed = filters.BooleanFilter()

    class Meta:
        model = FinanceCostItem
        fields = ["order", "team", "carrier_confirmed"]


class CallLogFilter(filters.FilterSet):
    client = filters.NumberFilter(field_name="client_id")
    was_successful = filters.CharFilter()

    class Meta:
        model = CallLog
        fields = ["client", "was_successful"]
