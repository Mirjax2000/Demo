"""servisni views"""

from __future__ import annotations
import secrets
import io
import zipfile
from rich.console import Console
from dataclasses import dataclass
from typing import Any


# --- Django
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.db.models import Count, Q, QuerySet
from django.core.cache import cache


# --- modely z DB
from .models import Order, OrderBackProtocolToken, TeamType
from . import models

# --- OOP classes
from .OOP_emails import CustomEmail

cons: Console = Console()
# ---
APP_URL = "app_sprava_montazi"

# --- Konfigurace cache pro dashboard ---
CACHE_TTL = 60  # sekundy


# --- Emails ---
class SendMailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        order: Order = get_object_or_404(Order, pk=pk)

        # --- vždy vytvoříme nový token (smažeme starý)
        OrderBackProtocolToken.objects.filter(order=order).delete()
        new_token = secrets.token_urlsafe(16)
        token_obj = OrderBackProtocolToken.objects.create(order=order, token=new_token)

        # --- vygenerujeme URL s tokenem
        back_url = request.build_absolute_uri(
            reverse("back_protocol", kwargs={"pk": pk}) + f"?token={token_obj.token}"
        )

        # --- odeslání e-mailu
        email: CustomEmail = CustomEmail(pk=pk, back_url=back_url, user=request.user)
        try:
            email.send_email_with_encrypted_pdf()
            order.mail_datum_sended = timezone.now()
            order.mail_team_sended = order.team.name
            order.save()
            messages.success(
                request,
                (
                    f"Email pro montazni tym: <strong>{order.team}</strong> "
                    f"na adresu <strong>{order.team.email}</strong> byl odeslan."  # type: ignore
                ),
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            messages.error(
                request,
                (
                    f"Email pro montazni tym: <strong>{order.team}</strong> "
                    f"na adresu <strong>{order.team.email}</strong> "
                    f"nebyl odeslan, Chyba: {str(e)}"
                ),
            )

        return redirect("protocol", pk=pk)


# --- Autocomplete ---


class AutocompleteOrdersByDeliveryGroupView(LoginRequiredMixin, View):
    def get(self, request):
        term = request.GET.get("term", "")
        zakazky = Order.objects.filter(
            order_number__icontains=term, team_type=TeamType.BY_ASSEMBLY_CREW
        ).values_list("order_number", flat=True)[:10]

        send_to_autocomplete: list[str] = []
        for zakazka in zakazky:
            send_to_autocomplete.append(zakazka.upper())
        return JsonResponse({"orders": send_to_autocomplete})


class OrderStatusView(LoginRequiredMixin, View):
    def get(self, request):
        number = request.GET.get("order_number", "")
        try:
            order = Order.objects.get(order_number=number)
            status = order.get_status_display()  # type:ignore
            if order.team_type != TeamType.BY_ASSEMBLY_CREW:
                return JsonResponse(
                    {"status": "Toto není montážní zakázka"}, status=409
                )
            return JsonResponse({"status": status}, status=200)

        except Order.DoesNotExist:
            return JsonResponse({"status": "Neznámé číslo zakázky"}, status=404)


# --- Download image zip ---


class DownloadMontageImagesZipView(View, LoginRequiredMixin):
    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number)
        images = order.montage_images.all()  # type:ignore

        # Vytvoření dočasného ZIP archivu v paměti
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for img in images:
                if img.image:
                    filename = f"{img.image.name.split('/')[-1]}"
                    zip_file.writestr(filename, img.image.read())

        buffer.seek(0)
        response = HttpResponse(buffer, content_type="application/zip")
        response["Content-Disposition"] = (
            f"attachment; filename=fotky_{order.order_number}.zip"
        )
        return response


@dataclass(frozen=True)
class DashboardFilters:
    date_from: str | None = None
    date_to: str | None = None
    status: str | None = None
    team: str | None = None
    q: str | None = None


def _to_filters_dict(filters: dict[str, Any]) -> DashboardFilters:
    return DashboardFilters(
        date_from=filters.get("date_from") or None,
        date_to=filters.get("date_to") or None,
        status=filters.get("status") or None,
        team=filters.get("team") or None,
        q=filters.get("q") or None,
    )


def _base_orders_qs(user) -> QuerySet:
    qs = models.Order.objects.all()
    # TODO: omezení podle role/mandanta (pokud je potřeba): např. qs.filter(mandant=user.profile.mandant)
    return qs


def _not_finalized_qs(qs: QuerySet) -> QuerySet:
    """Zakázky, které nejsou ve finálních stavech."""
    return qs.exclude(
        status__in=[
            models.Status.REALIZED,
            models.Status.BILLED,
            models.Status.CANCELED,
            models.Status.HIDDEN,
        ]
    )


def _apply_filters(qs: QuerySet, f: DashboardFilters) -> QuerySet:
    # Datumový rozsah – počítáme s polem montage_termin
    if f.date_from:
        try:
            df = timezone.datetime.fromisoformat(f.date_from)
            qs = qs.filter(montage_termin__date__gte=df.date())
        except Exception:
            pass
    if f.date_to:
        try:
            dt = timezone.datetime.fromisoformat(f.date_to)
            qs = qs.filter(montage_termin__date__lte=dt.date())
        except Exception:
            pass

    # Stavové presety mapované na reálná pole/relace
    today = timezone.localdate()
    if f.status == "open":
        qs = _not_finalized_qs(qs)
    elif f.status == "overdue":
        qs = _not_finalized_qs(qs).filter(montage_termin__date__lt=today)
    elif f.status == "pending_protocol":
        # Po termínu montáže (nebo dnes) a chybí zpětný protokol
        qs = qs.filter(montage_termin__date__lte=today, back_protocol__isnull=True)
    elif f.status == "pending_pdf_check":
        # Existuje vygenerované PDF a zakázka není finálně uzavřená
        qs = _not_finalized_qs(qs).filter(pdf__isnull=False)
    elif f.status == "hidden":
        qs = qs.filter(status=models.Status.HIDDEN)

    # Filtrování týmu podle názvu
    if f.team:
        qs = qs.filter(team__name__icontains=f.team)

    # Fulltext – jednoduché OR přes vybraná pole
    if f.q:
        qs = qs.filter(
            Q(order_number__icontains=f.q)
            | Q(client__name__icontains=f.q)
            | Q(team__name__icontains=f.q)
        )

    return qs


def _cache_key(prefix: str, filters: DashboardFilters, user_id: int | None) -> str:
    return f"dash:{prefix}:{user_id}:{filters.date_from}:{filters.date_to}:{filters.status}:{filters.team}:{filters.q}"


def get_dashboard_kpi(filters: dict[str, Any], user) -> dict[str, int]:
    f = _to_filters_dict(filters)
    key = _cache_key("kpi", f, getattr(user, "id", None))
    cached = cache.get(key)
    if cached is not None:
        return cached

    base = _apply_filters(_base_orders_qs(user), f)
    today = timezone.localdate()
    week_start = today - timezone.timedelta(days=today.weekday())
    week_end = week_start + timezone.timedelta(days=6)

    # KPI výpočty s reálnými statusy/relacemi
    open_orders = _not_finalized_qs(base).count()
    overdue_orders = _not_finalized_qs(base).filter(montage_termin__date__lt=today).count()
    today_orders = base.filter(montage_termin__date=today).count()
    week_orders = base.filter(montage_termin__date__range=(week_start, week_end)).count()
    pending_protocol = base.filter(montage_termin__date__lte=today, back_protocol__isnull=True).count()
    pending_pdf_check = _not_finalized_qs(base).filter(pdf__isnull=False).count()

    # Neúplní zákazníci – dle flagu u modelu Client
    incomplete_customers = models.Client.objects.filter(incomplete=True).count()

    data = {
        "open_orders": open_orders,
        "overdue_orders": overdue_orders,
        "today_orders": today_orders,
        "week_orders": week_orders,
        "pending_protocol": pending_protocol,
        "pending_pdf_check": pending_pdf_check,
        "incomplete_customers": incomplete_customers,
    }
    cache.set(key, data, CACHE_TTL)
    return data


def get_dashboard_hot_orders(filters: dict[str, Any], user, limit: int = 10) -> list[dict[str, Any]]:
    f = _to_filters_dict(filters)
    key = _cache_key(f"hot:{limit}", f, getattr(user, "id", None))
    cached = cache.get(key)
    if cached is not None:
        return cached

    qs = _apply_filters(_base_orders_qs(user), f)
    qs = (
        _not_finalized_qs(qs)
        .only("pk", "order_number", "status", "montage_termin", "team__name", "client__name")
        .select_related("team", "client")
        .order_by("montage_termin", "pk")
    )
    items: list[dict[str, Any]] = []
    for o in qs[:limit]:
        items.append(
            {
                "pk": o.pk,
                "order_number": getattr(o, "order_number", ""),
                "client": getattr(getattr(o, "client", None), "name", "") or "",
                "team": getattr(getattr(o, "team", None), "name", "") or "",
                "planned_at": getattr(o, "montage_termin", None),
                "status": getattr(o, "status", ""),
            }
        )
    cache.set(key, items, CACHE_TTL)
    return items


def get_dashboard_teams_load(filters: dict[str, Any], user) -> list[dict[str, Any]]:
    f = _to_filters_dict(filters)
    key = _cache_key("teams_load", f, getattr(user, "id", None))
    cached = cache.get(key)
    if cached is not None:
        return cached

    today = timezone.localdate()
    week_start = today - timezone.timedelta(days=today.weekday())
    week_end = week_start + timezone.timedelta(days=6)

    base = _apply_filters(_base_orders_qs(user), f)
    orders = _not_finalized_qs(base).filter(montage_termin__date__range=(week_start, week_end))

    agg = (
        orders.values("team__slug", "team__name")
        .annotate(this_week_count=Count("id"))
        .order_by("-this_week_count", "team__name")
    )

    items: list[dict[str, Any]] = []
    for row in agg:
        items.append(
            {
                "team_name": row.get("team__name") or "Neznámý tým",
                "this_week_count": row.get("this_week_count") or 0,
                "detail_slug": row.get("team__slug") or "",
            }
        )
    cache.set(key, items, CACHE_TTL)
    return items


def get_dashboard_alerts(filters: dict[str, Any], user) -> dict[str, list[dict[str, Any]]]:
    f = _to_filters_dict(filters)
    key = _cache_key("alerts", f, getattr(user, "id", None))
    cached = cache.get(key)
    if cached is not None:
        return cached

    base = _apply_filters(_base_orders_qs(user), f)
    today = timezone.localdate()

    # Čeká na protokol – po termínu montáže (nebo dnes) a bez zpětného protokolu
    prot_qs = (
        base.filter(montage_termin__date__lte=today, back_protocol__isnull=True)
        .only("pk", "order_number", "montage_termin")
        .order_by("montage_termin")[:10]
    )
    pending_protocol = [{"pk": o.pk, "order_number": getattr(o, "order_number", "")} for o in prot_qs]

    # K revizi PDF – PDF existuje, ale zakázka není finálně uzavřená
    pdf_qs = (
        _not_finalized_qs(base).filter(pdf__isnull=False)
        .only("pk", "order_number")
        .order_by("-pk")[:10]
    )
    pending_pdf_check = [{"pk": o.pk, "order_number": getattr(o, "order_number", "")} for o in pdf_qs]

    # Neúplní zákazníci – dle flagu
    inc_qs = models.Client.objects.filter(incomplete=True).only("id", "name")[:10]
    incomplete_customers = [{"client_name": getattr(c, "name", ""), "pk": getattr(c, "id", None)} for c in inc_qs]

    data = {
        "pending_protocol": pending_protocol,
        "pending_pdf_check": pending_pdf_check,
        "incomplete_customers": incomplete_customers,
    }
    cache.set(key, data, CACHE_TTL)
    return data
