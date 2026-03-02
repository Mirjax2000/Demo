"""
API v1 Views — ViewSets a speciální endpointy pro oddělený FE.
"""

import os
import time
import io
import zipfile
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import models
from django.db.models import QuerySet
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import viewsets, status, permissions, generics, serializers as drf_serializers
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from app_sprava_montazi.models import (
    Article,
    AppSetting,
    CallLog,
    Client,
    DistribHub,
    FinanceCostItem,
    FinanceRevenueItem,
    Order,
    OrderBackProtocol,
    OrderMontazImage,
    OrderPDFStorage,
    Status,
    Team,
    TeamType,
    Upload,
)
from app_sprava_montazi.OOP_protokols import SCCZPdfGenerator
from app_sprava_montazi.OOP_emails import CustomEmail
from app_sprava_montazi.OOP_dashboard import Dashboard
from app_sprava_montazi.OOP_back_protocol import ProtocolUploader
from app_sprava_montazi.utils import update_customers

from .serializers import (
    AppSettingSerializer,
    ArticleSerializer,
    CallLogSerializer,
    ClientDetailSerializer,
    ClientListSerializer,
    DashboardSerializer,
    DistribHubSerializer,
    FinanceCostItemSerializer,
    FinanceRevenueItemSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    OrderMontazImageSerializer,
    OrderWriteSerializer,
    RegisterSerializer,
    TeamDetailSerializer,
    TeamListSerializer,
    UploadSerializer,
    UserAdminSerializer,
    UserSerializer,
)
from .filters import (
    CallLogFilter,
    ClientFilter,
    FinanceCostItemFilter,
    FinanceRevenueItemFilter,
    OrderFilter,
    TeamFilter,
)
from .permissions import IsAdminRole, IsManagerOrAbove

User = get_user_model()


# ══════════════════════════════════════════
# Auth
# ══════════════════════════════════════════
# ══════════════════════════════════════════
# Auth helpers — httpOnly cookie JWT
# ══════════════════════════════════════════
def _set_jwt_cookies(response, access: str, refresh: str | None = None):
    """Nastaví httpOnly cookies s JWT tokeny."""
    from django.conf import settings as s

    response.set_cookie(
        s.JWT_COOKIE_NAME,
        access,
        max_age=int(s.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        httponly=s.JWT_COOKIE_HTTPONLY,
        secure=s.JWT_COOKIE_SECURE,
        samesite=s.JWT_COOKIE_SAMESITE,
        path=s.JWT_COOKIE_PATH,
    )
    if refresh:
        response.set_cookie(
            s.JWT_REFRESH_COOKIE_NAME,
            refresh,
            max_age=int(s.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
            httponly=s.JWT_COOKIE_HTTPONLY,
            secure=s.JWT_COOKIE_SECURE,
            samesite=s.JWT_COOKIE_SAMESITE,
            path=s.JWT_REFRESH_COOKIE_PATH,
        )
    return response


def _clear_jwt_cookies(response):
    """Smaže JWT cookies."""
    from django.conf import settings as s

    response.delete_cookie(s.JWT_COOKIE_NAME, path=s.JWT_COOKIE_PATH)
    response.delete_cookie(s.JWT_REFRESH_COOKIE_NAME, path=s.JWT_REFRESH_COOKIE_PATH)
    return response


class LoginView(TokenObtainPairView):
    """JWT login — vrací access + refresh token v httpOnly cookies."""

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        data = serializer.validated_data
        resp = Response({"detail": "Login OK."})
        _set_jwt_cookies(resp, data["access"], data["refresh"])
        return resp


class RefreshView(APIView):
    """JWT token refresh — čte refresh z httpOnly cookie."""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        from django.conf import settings as s

        raw_refresh = request.COOKIES.get(s.JWT_REFRESH_COOKIE_NAME)
        if not raw_refresh:
            return Response(
                {"detail": "Refresh token chybí."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        try:
            refresh = RefreshToken(raw_refresh)
            access = str(refresh.access_token)
            new_refresh = str(refresh) if s.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS") else None
            if s.SIMPLE_JWT.get("BLACKLIST_AFTER_ROTATION") and new_refresh:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass  # blacklist app not installed
        except TokenError:
            resp = Response(
                {"detail": "Refresh token neplatný."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            _clear_jwt_cookies(resp)
            return resp

        resp = Response({"detail": "Token refreshed."})
        _set_jwt_cookies(resp, access, new_refresh)
        return resp


class LogoutView(APIView):
    """Odstraní JWT cookies a blacklistne refresh token."""

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        from django.conf import settings as s

        raw_refresh = request.COOKIES.get(s.JWT_REFRESH_COOKIE_NAME)
        if raw_refresh:
            try:
                token = RefreshToken(raw_refresh)
                token.blacklist()
            except (TokenError, AttributeError):
                pass

        resp = Response({"detail": "Odhlášeno."})
        _clear_jwt_cookies(resp)
        return resp


class UserAdminViewSet(viewsets.ModelViewSet):
    """Admin správa uživatelů — seznam, detail, změna role/aktivace, vytvoření."""

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdminRole]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_serializer_class(self):
        if self.action == "create":
            from .serializers import UserAdminCreateSerializer
            return UserAdminCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        search = self.request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(
                models.Q(username__icontains=search)
                | models.Q(email__icontains=search)
                | models.Q(first_name__icontains=search)
                | models.Q(last_name__icontains=search)
            )
        return qs


class RegisterView(generics.CreateAPIView):
    """Registrace nového uživatele."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.IsAuthenticated]  # Jen přihlášení mohou registrovat


class MeView(APIView):
    """Vrátí info o aktuálně přihlášeném uživateli."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=UserSerializer)
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# ══════════════════════════════════════════
# DistribHub (read-only)
# ══════════════════════════════════════════
class DistribHubViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DistribHub.objects.all()
    serializer_class = DistribHubSerializer
    pagination_class = None  # malá tabulka, vracíme vše


# ══════════════════════════════════════════
# Teams
# ══════════════════════════════════════════
@extend_schema_view(
    list=extend_schema(summary="Seznam týmů"),
    retrieve=extend_schema(summary="Detail týmu"),
    create=extend_schema(summary="Vytvořit tým"),
    update=extend_schema(summary="Upravit tým"),
    destroy=extend_schema(summary="Smazat tým"),
)
class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    filterset_class = TeamFilter
    search_fields = ["name", "city", "region", "email"]
    ordering_fields = ["name", "city", "active"]
    ordering = ["name"]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "list":
            return TeamListSerializer
        return TeamDetailSerializer

    def destroy(self, request, *args, **kwargs):
        team = self.get_object()
        if team.active:
            return Response(
                {"detail": f"Tým '{team.name}' je stále aktivní. Smazat lze pouze neaktivní týmy."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)


# ══════════════════════════════════════════
# Clients
# ══════════════════════════════════════════
@extend_schema_view(
    list=extend_schema(summary="Seznam zákazníků"),
    retrieve=extend_schema(summary="Detail zákazníka"),
)
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    filterset_class = ClientFilter
    search_fields = ["name", "city", "street", "email", "zip_code"]
    ordering_fields = ["name", "city", "incomplete"]
    ordering = ["name"]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "list":
            return ClientListSerializer
        return ClientDetailSerializer

    @extend_schema(summary="Zakázky zákazníka")
    @action(detail=True, methods=["get"], url_path="orders")
    def orders(self, request, slug=None):
        client = self.get_object()
        orders = Order.objects.filter(client=client).select_related(
            "distrib_hub", "team"
        )
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Čísla zakázek s nekompletními zákazníky",
        description="Vrací seznam order_number zakázek, jejichž klient má incomplete=True (pro bot).",
    )
    @action(detail=False, methods=["get"], url_path="incomplete-orders")
    def incomplete_orders(self, request):
        """GET /api/v1/clients/incomplete-orders/ — bot endpoint."""
        qs = Order.objects.filter(client__incomplete=True).exclude(status="Hidden")
        order_numbers = [o.order_number.upper() for o in qs]
        return Response({"order_numbers": order_numbers})

    @extend_schema(
        summary="Batch aktualizace zákazníků",
        description="Přijímá seznam {order_number, details} a aktualizuje klientská data (pro bot).",
    )
    @action(detail=False, methods=["post"], url_path="batch-update")
    def batch_update(self, request):
        """POST /api/v1/clients/batch-update/ — bot endpoint."""
        updates = request.data.get("updates", [])
        if not updates or not isinstance(updates, list):
            return Response(
                {"detail": "Parametr 'updates' (seznam) je vyžadován."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        update_customers(updates)
        return Response({"message": "Zákazníci byli aktualizováni."})

    @extend_schema(
        summary="GDPR export osobních dat zákazníka",
        description="Strojově čitelný JSON se všemi osobními údaji zákazníka (čl. 20 GDPR).",
    )
    @action(detail=True, methods=["get"], url_path="export-data")
    def export_data(self, request, slug=None):
        """GET /api/v1/clients/{slug}/export-data/ — GDPR data portability."""
        client = self.get_object()

        # Kontaktní údaje
        personal = {
            "name": client.name,
            "street": client.street,
            "city": client.city,
            "zip_code": client.zip_code,
            "phone": client.phone,
            "email": client.email,
            "incomplete": client.incomplete,
        }

        # Historie zakázek
        orders_qs = Order.objects.filter(client=client).select_related(
            "distrib_hub", "team"
        )
        orders_data = [
            {
                "order_number": o.order_number,
                "mandant": o.mandant,
                "status": o.status,
                "team_type": o.team_type,
                "team": o.team.name if o.team else None,
                "distrib_hub": str(o.distrib_hub) if o.distrib_hub else None,
                "evidence_termin": str(o.evidence_termin) if o.evidence_termin else None,
                "delivery_termin": str(o.delivery_termin) if o.delivery_termin else None,
                "montage_termin": str(o.montage_termin) if o.montage_termin else None,
                "notes": o.notes,
            }
            for o in orders_qs
        ]

        # Call logy
        calls_qs = client.calls.select_related("user").all()
        calls_data = [
            {
                "called_at": c.called_at.isoformat(),
                "user": c.user.username,
                "note": c.note,
                "was_successful": c.was_successful,
            }
            for c in calls_qs
        ]

        return Response({
            "export_type": "GDPR_personal_data_export",
            "generated_at": __import__("django").utils.timezone.now().isoformat(),
            "client": personal,
            "orders": orders_data,
            "call_logs": calls_data,
        })


# ══════════════════════════════════════════
# Orders
# ══════════════════════════════════════════
@extend_schema_view(
    list=extend_schema(summary="Seznam zakázek"),
    retrieve=extend_schema(summary="Detail zakázky"),
    create=extend_schema(summary="Vytvořit zakázku"),
    update=extend_schema(summary="Upravit zakázku"),
    destroy=extend_schema(summary="Smazat zakázku"),
)
class OrderViewSet(viewsets.ModelViewSet):
    filterset_class = OrderFilter
    search_fields = [
        "order_number",
        "client__name",
        "team__name",
        "mandant",
        "distrib_hub__code",
        "distrib_hub__city",
        "notes",
    ]
    ordering_fields = [
        "evidence_termin",
        "delivery_termin",
        "montage_termin",
        "order_number",
        "status",
        "mandant",
        "client__name",
        "team__name",
    ]
    ordering = ["-evidence_termin"]

    def get_queryset(self) -> QuerySet:
        return (
            Order.objects.select_related("client", "team", "distrib_hub")
            .prefetch_related("articles", "montage_images")
            .all()
        )

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action in ("create", "update", "partial_update"):
            return OrderWriteSerializer
        return OrderDetailSerializer

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status != Status.HIDDEN:
            return Response(
                {"detail": "Smazat lze pouze skryté zakázky."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    # --- Custom actions ---

    @extend_schema(
        summary="Autocomplete zakázek dle delivery group",
        description="Vrací seznam order_number (max 10) filtrovaných dle 'term'. Pouze montážní zakázky (By_assembly_crew).",
    )
    @action(detail=False, methods=["get"], url_path="autocomplete-delivery")
    def autocomplete_delivery(self, request):
        term = request.query_params.get("term", "")
        qs = Order.objects.filter(
            order_number__icontains=term,
            team_type=TeamType.BY_ASSEMBLY_CREW,
        ).values_list("order_number", flat=True)[:10]
        return Response({"orders": [n.upper() for n in qs]})

    @extend_schema(summary="Skrýt zakázku")
    @action(detail=True, methods=["post"], url_path="hide")
    def hide(self, request, pk=None):
        order = self.get_object()
        if order.status != Status.NEW:
            return Response(
                {"detail": "Skrýt lze pouze zakázku ve stavu 'Nový'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = Status.HIDDEN
        order.save()
        return Response({"detail": f"Zakázka {order.order_number} skryta."})

    @extend_schema(summary="Přepnout: Zatermínováno/doručeno → Realizováno")
    @action(detail=True, methods=["post"], url_path="switch-to-realized")
    def switch_to_realized(self, request, pk=None):
        order = self.get_object()
        if order.status != Status.ADVICED or order.team_type != TeamType.BY_DELIVERY_CREW:
            return Response(
                {
                    "detail": "Jen zakázky ve stavu 'Zatermínováno' "
                    "s typem realizace 'Dopravcem' lze takto realizovat."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = Status.REALIZED
        order.save()
        return Response({"detail": f"Zakázka {order.order_number} realizována."})

    @extend_schema(summary="Přepnout typ realizace → Montážníky")
    @action(detail=True, methods=["post"], url_path="switch-to-assembly")
    def switch_to_assembly(self, request, pk=None):
        order = self.get_object()
        if order.status != Status.NEW or order.team_type != TeamType.BY_CUSTOMER:
            return Response(
                {
                    "detail": "Přepnout na montáž lze pouze nové zakázky "
                    "s typem realizace 'Zákazníkem'."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.team_type = TeamType.BY_ASSEMBLY_CREW
        order.save()
        return Response(
            {"detail": f"Zakázka {order.order_number} přepnuta na realizaci montážníky."}
        )

    @extend_schema(summary="Generovat PDF protokol")
    @action(detail=True, methods=["post"], url_path="generate-pdf")
    def generate_pdf(self, request, pk=None):
        order = self.get_object()
        try:
            from app_sprava_montazi.OOP_protokols import pdf_generator_classes

            mandant = order.mandant
            generator_class = pdf_generator_classes.get(
                mandant, pdf_generator_classes["default"]
            )
            generator = generator_class()
            pdf_io = generator.generate_pdf_protocol(model=order)
            generator.save_pdf_protocol_to_db(model=order, pdf=pdf_io)
            return Response({"detail": "PDF protokol vygenerován."})
        except Exception as e:
            return Response(
                {"detail": f"Chyba při generování PDF: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(summary="Stáhnout PDF protokol")
    @action(detail=True, methods=["get"], url_path="download-pdf")
    def download_pdf(self, request, pk=None):
        order = self.get_object()
        try:
            pdf = order.pdf
            return FileResponse(
                pdf.file.open("rb"),
                content_type="application/pdf",
                as_attachment=True,
                filename=f"protokol_{order.order_number}.pdf",
            )
        except OrderPDFStorage.DoesNotExist:
            return Response(
                {"detail": "PDF protokol neexistuje."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @extend_schema(summary="Zobrazit PDF inline (pro mandanty)")
    @action(detail=True, methods=["get"], url_path="view-pdf")
    def view_pdf(self, request, pk=None):
        order = self.get_object()
        try:
            pdf = order.pdf
            return FileResponse(
                pdf.file.open("rb"),
                content_type="application/pdf",
                as_attachment=False,
                filename=f"protokol_{order.order_number}.pdf",
            )
        except OrderPDFStorage.DoesNotExist:
            return Response(
                {"detail": "PDF protokol neexistuje."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @extend_schema(summary="Stáhnout montážní fotky jako ZIP")
    @action(detail=True, methods=["get"], url_path="download-montage-zip")
    def download_montage_zip(self, request, pk=None):
        order = self.get_object()
        images = order.montage_images.all()

        if not images.exists():
            return Response(
                {"detail": "Žádné montážní fotky k stažení."},
                status=status.HTTP_404_NOT_FOUND,
            )

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for img in images:
                if img.image:
                    filename = img.image.name.split("/")[-1]
                    zf.writestr(filename, img.image.read())

        buffer.seek(0)
        from django.http import HttpResponse as DjangoHttpResponse

        response = DjangoHttpResponse(buffer, content_type="application/zip")
        response["Content-Disposition"] = (
            f'attachment; filename="fotky_{order.order_number}.zip"'
        )
        return response

    @extend_schema(summary="Odeslat email s protokolem")
    @action(detail=True, methods=["post"], url_path="send-mail")
    def send_mail(self, request, pk=None):
        import secrets
        from django.utils import timezone
        from app_sprava_montazi.models import OrderBackProtocolToken

        order = self.get_object()

        OrderBackProtocolToken.objects.filter(order=order).delete()
        new_token = secrets.token_urlsafe(16)
        token_obj = OrderBackProtocolToken.objects.create(
            order=order, token=new_token
        )

        # URL pro zpětný protokol — FE URL (veřejná stránka)
        fe_base = request.build_absolute_uri("/")
        back_url = f"{fe_base}back-protocol?token={token_obj.token}"

        email = CustomEmail(pk=order.pk, back_url=back_url, user=request.user)
        try:
            email.send_email_with_encrypted_pdf()
            order.mail_datum_sended = timezone.now()
            order.mail_team_sended = order.team.name
            order.save()
            return Response(
                {
                    "detail": f"Email odeslán týmu {order.team} na {order.team.email}."
                }
            )
        except Exception as e:
            return Response(
                {"detail": f"Chyba odesílání: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Seznam zatermínovaných dopravních zakázek",
        description="Vrací order_number a evidence_termin pro Adviced + By_delivery_crew (pro bot).",
    )
    @action(detail=False, methods=["get"], url_path="adviced-delivery")
    def adviced_delivery(self, request):
        """GET /api/v1/orders/adviced-delivery/ — bot endpoint."""
        qs = Order.objects.filter(
            status=Status.ADVICED, team_type=TeamType.BY_DELIVERY_CREW
        )
        data = [
            {
                "order_number": o.order_number.upper(),
                "evidence_termin": o.evidence_termin,
            }
            for o in qs
        ]
        return Response({"orders": data})

    @extend_schema(
        summary="Batch realizace dopravních zakázek",
        description="Přijímá seznam order_number a přepne Adviced+Delivery na Realized (pro bot).",
    )
    @action(detail=False, methods=["post"], url_path="batch-realize")
    def batch_realize(self, request):
        """POST /api/v1/orders/batch-realize/ — bot endpoint."""
        order_numbers = request.data.get("orders", [])
        if not order_numbers or not isinstance(order_numbers, list):
            return Response(
                {"detail": "Parametr 'orders' (seznam) je vyžadován."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        qs = Order.objects.filter(order_number__in=order_numbers)
        found = set(qs.values_list("order_number", flat=True))
        not_found = list(set(order_numbers) - found)

        if not qs.exists():
            return Response(
                {"detail": "Žádné odpovídající objednávky nebyly nalezeny."},
                status=status.HTTP_404_NOT_FOUND,
            )

        updated, skipped = [], []
        for order in qs:
            if (
                order.status == Status.ADVICED
                and order.team_type == TeamType.BY_DELIVERY_CREW
            ):
                order.status = Status.REALIZED
                order.save(update_fields=["status"])
                updated.append(order.order_number)
            else:
                skipped.append(order.order_number)

        return Response(
            {"updated": updated, "not_found": not_found, "skipped": skipped}
        )

    @extend_schema(summary="Historie změn zakázky")
    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        from app_sprava_montazi.models import HistoricalArticle  # type: ignore

        order = self.get_object()
        order_history = list(order.history.all()[:50])

        try:
            article_history = list(
                HistoricalArticle.objects.filter(order=order)[:50]
            )
        except Exception:
            article_history = []

        all_history = order_history + article_history
        all_history.sort(key=lambda x: x.history_date, reverse=True)

        data = []
        for entry in all_history:
            is_article = isinstance(entry, HistoricalArticle)
            record = {
                "history_id": entry.history_id,
                "history_date": entry.history_date,
                "history_type": entry.get_history_type_display(),
                "history_user": str(entry.history_user) if entry.history_user else None,
                "model": "Article" if is_article else "Order",
                "status": entry.status if hasattr(entry, "status") else None,
                "notes": entry.notes if hasattr(entry, "notes") else None,
                "changes": [],
            }
            if is_article:
                record["article_name"] = str(getattr(entry, "name", ""))

            # Field-level diffs for changed records
            if entry.history_type == "~":
                prev = entry.prev_record
                if prev:
                    try:
                        delta = entry.diff_against(prev)
                        for change in delta.changes:
                            field_name = change.field
                            old_val = change.old
                            new_val = change.new

                            # Translate choice fields
                            choice_fields = {"team_type": TeamType, "status": Status}
                            if field_name in choice_fields:
                                choices_cls = choice_fields[field_name]
                                try:
                                    if old_val:
                                        old_val = getattr(choices_cls(old_val), "label", str(old_val))
                                    if new_val:
                                        new_val = getattr(choices_cls(new_val), "label", str(new_val))
                                except (ValueError, KeyError):
                                    pass

                            # Resolve FK names
                            try:
                                original_field = entry._meta.model._meta.get_field(field_name)
                                if original_field.is_relation and original_field.related_model:
                                    model_cls = original_field.related_model
                                    if old_val:
                                        try:
                                            old_val = str(model_cls.objects.get(pk=old_val))
                                        except model_cls.DoesNotExist:
                                            old_val = f"ID:{old_val} (smazáno)"
                                    if new_val:
                                        try:
                                            new_val = str(model_cls.objects.get(pk=new_val))
                                        except model_cls.DoesNotExist:
                                            new_val = f"ID:{new_val} (smazáno)"
                            except Exception:
                                pass

                            record["changes"].append({
                                "field": field_name,
                                "old": str(old_val) if old_val is not None else "-",
                                "new": str(new_val) if new_val is not None else "-",
                            })
                    except Exception:
                        pass

            data.append(record)
        return Response(data)

    @extend_schema(summary="Export zakázek do Excelu")
    @action(detail=False, methods=["get"], url_path="export-excel")
    def export_excel(self, request):
        from openpyxl import Workbook
        from django.http import HttpResponse

        qs = self.filter_queryset(self.get_queryset())
        wb = Workbook()
        ws = wb.active
        ws.title = "Zakázky"

        headers = [
            "Číslo zakázky",
            "Mandant",
            "Stav",
            "Typ realizace",
            "Zákazník",
            "Tým",
            "Místo určení",
            "Termín evidence",
            "Termín doručení",
            "Termín montáže",
            "Náklad",
            "Výnos",
            "Profit",
        ]
        ws.append(headers)

        for order in qs:
            ws.append(
                [
                    order.order_number,
                    order.mandant,
                    order.get_status_display(),
                    order.get_team_type_display(),
                    str(order.client) if order.client else "",
                    str(order.team) if order.team else "",
                    str(order.distrib_hub),
                    str(order.evidence_termin) if order.evidence_termin else "",
                    str(order.delivery_termin) if order.delivery_termin else "",
                    str(order.montage_termin) if order.montage_termin else "",
                    float(order.naklad) if order.naklad else 0,
                    float(order.vynos) if order.vynos else 0,
                    float(order.profit()),
                ]
            )

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename=zakazky_export.xlsx"
        wb.save(response)
        return response


# ══════════════════════════════════════════
# Articles (nested pod Order)
# ══════════════════════════════════════════
class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    pagination_class = None

    def get_queryset(self):
        return Article.objects.filter(order_id=self.kwargs["order_pk"])

    def perform_create(self, serializer):
        order = get_object_or_404(Order, pk=self.kwargs["order_pk"])
        serializer.save(order=order)


# ══════════════════════════════════════════
# Montáž Images (nested pod Order)
# ══════════════════════════════════════════
class OrderMontazImageViewSet(viewsets.ModelViewSet):
    serializer_class = OrderMontazImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = None

    def get_queryset(self):
        return OrderMontazImage.objects.filter(
            order_id=self.kwargs["order_pk"]
        ).order_by("position")

    def perform_create(self, serializer):
        from app_sprava_montazi.OOP_back_protocol import ProtocolUploader

        order = get_object_or_404(Order, pk=self.kwargs["order_pk"])
        image = self.request.FILES.get("image")
        if not image:
            raise drf_serializers.ValidationError({"image": "Soubor nevybrán."})

        # ------ auto-position
        last = (
            OrderMontazImage.objects.filter(order=order)
            .order_by("-position")
            .first()
        )
        position = (last.position + 1) if last else 1
        serializer.save(order=order, position=position)

        # ------ WebP konverze posledního obrázku
        try:
            uploader = ProtocolUploader(
                order=order, image=image, alt_text="", request=self.request
            )
            uploader.convert_and_save_webp_images()
        except Exception:
            pass  # best-effort, original image already saved


# ══════════════════════════════════════════
# Finance Items
# ══════════════════════════════════════════
class FinanceRevenueItemViewSet(viewsets.ModelViewSet):
    queryset = FinanceRevenueItem.objects.all()
    serializer_class = FinanceRevenueItemSerializer
    filterset_class = FinanceRevenueItemFilter
    ordering = ["-created"]


class FinanceCostItemViewSet(viewsets.ModelViewSet):
    queryset = FinanceCostItem.objects.all()
    serializer_class = FinanceCostItemSerializer
    filterset_class = FinanceCostItemFilter
    ordering = ["-created"]


# ══════════════════════════════════════════
# CallLog
# ══════════════════════════════════════════
class CallLogViewSet(viewsets.ModelViewSet):
    queryset = CallLog.objects.select_related("client", "user").all()
    serializer_class = CallLogSerializer
    filterset_class = CallLogFilter
    ordering = ["-called_at"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ══════════════════════════════════════════
# Dashboard
# ══════════════════════════════════════════
class DashboardView(APIView):
    """Agregované statistiky pro dashboard."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Dashboard statistiky",
        parameters=[
            OpenApiParameter("year", int, description="Rok (evidence_termin)"),
            OpenApiParameter("month", int, description="Měsíc (evidence_termin)"),
            OpenApiParameter("mandant", str, description="Filtr mandant"),
            OpenApiParameter("distrib_hub", int, description="ID distrib hubu"),
        ],
        responses=DashboardSerializer,
    )
    def get(self, request):
        qs = Order.objects.all()

        year = request.query_params.get("year")
        month = request.query_params.get("month")
        mandant = request.query_params.get("mandant")
        distrib_hub = request.query_params.get("distrib_hub")

        if year:
            qs = qs.filter(evidence_termin__year=int(year))
        if month:
            qs = qs.filter(evidence_termin__month=int(month))
        if mandant:
            qs = qs.filter(mandant=mandant)
        if distrib_hub:
            try:
                qs = qs.filter(distrib_hub_id=int(distrib_hub))
            except (TypeError, ValueError):
                pass

        dashboard = Dashboard()

        is_invalid, invalid_count = dashboard.invalid_orders(qs)
        new_issues = dashboard.new_orders_issues(qs)
        customer_r = dashboard.customer_r_orders(qs)

        # Dynamic filter options (from all orders, not filtered)
        all_orders = Order.objects.all()
        mandants = sorted(
            set(all_orders.values_list("mandant", flat=True))
        )
        years = sorted(
            {d.year for d in all_orders.dates("evidence_termin", "year")},
            reverse=True,
        )

        data = {
            "open_orders": dashboard.open_orders(qs),
            "closed_orders": dashboard.closed_orders(qs),
            "adviced_type_orders": dashboard.adviced_type_orders(qs),
            "count_all": dashboard.all_orders(qs),
            "hidden": dashboard.count_hidden(qs),
            "no_montage_term_count": dashboard.no_montage_term_orders(qs),
            "no_montage_total_count": dashboard.no_montage_total(qs),
            "has_no_montage_term": dashboard.no_montage_term_orders(qs) > 0,
            "is_invalid": is_invalid,
            "invalid_count": invalid_count,
            "finance_summary": dashboard.finance_summary(qs),
            "new_issues_count": new_issues.count(),
            "customer_r_count": customer_r.count(),
            # Detail tables (order lists for expandable sections)
            "new_issues_orders": OrderListSerializer(new_issues[:20], many=True).data,
            "customer_r_orders": OrderListSerializer(customer_r[:20], many=True).data,
            # Dynamic filter options
            "mandant_options": mandants,
            "year_options": years,
        }

        return Response(data)


# ══════════════════════════════════════════
# CSV Import
# ══════════════════════════════════════════
class CSVImportView(APIView):
    """Import zakázek z CSV souboru."""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Import CSV souboru",
        request=UploadSerializer,
    )
    def post(self, request):
        serializer = UploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        upload = serializer.save()

        # Zajistit distrib huby
        if not DistribHub.objects.exists():
            call_command("distrib_hub")

        try:
            db_count_old = Order.objects.count()
            call_command("import_data", upload.file.path)
            time.sleep(0.25)
            db_count_new = Order.objects.count()
            result = db_count_new - db_count_old
            return Response(
                {"detail": f"Import dokončen. {result} nových zakázek."},
                status=status.HTTP_201_CREATED,
            )
        except KeyError:
            return Response(
                {"detail": "Špatný soubor CSV."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DistribHub.DoesNotExist as e:
            return Response(
                {"detail": f"Chybné místo určení: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response(
                {"detail": f"Chyba hodnoty v souboru CSV: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"detail": f"Neznámá chyba: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ══════════════════════════════════════════
# AppSettings (read-only pro FE)
# ══════════════════════════════════════════
class AppSettingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AppSetting.objects.all()
    serializer_class = AppSettingSerializer
    pagination_class = None


# ══════════════════════════════════════════
# Health check
# ══════════════════════════════════════════
class HealthCheckView(APIView):
    """API Status — nevyžaduje autentizaci."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"status": "UP", "version": "2.0.0"})


# ══════════════════════════════════════════
# Back Protocol — externí (token-gated, bez auth)
# ══════════════════════════════════════════


def _is_back_protocol_token_expired(token_obj) -> bool:
    """Kontrola platnosti tokenu zpětného protokolu.

    Logika:
      1. Pokud má zakázka `montage_termin` → token platí do 24 h po termínu montáže.
      2. Pokud `montage_termin` chybí (null) → fallback: 48 h od vytvoření tokenu.
    """
    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    order = token_obj.order

    if order.montage_termin:
        return now > order.montage_termin + timedelta(hours=24)

    # fallback — montage_termin není nastaven
    return now - token_obj.created > timedelta(hours=48)

class BackProtocolTokenValidateView(APIView):
    """Ověří platnost tokenu pro zpětný protokol (GET).

    Veřejný endpoint — montážní tým nemá účet v systému.
    Vrací info o zakázce pokud je token platný.
    """

    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Ověřit token zpětného protokolu",
        parameters=[OpenApiParameter("token", str, required=True)],
    )
    def get(self, request):
        from app_sprava_montazi.models import OrderBackProtocolToken

        token = request.query_params.get("token")
        if not token:
            return Response(
                {"detail": "Token je povinný."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token_obj = OrderBackProtocolToken.objects.select_related(
                "order", "order__client", "order__team"
            ).get(token=token)
        except OrderBackProtocolToken.DoesNotExist:
            return Response(
                {"detail": "Neplatný nebo expirovaný token."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # TTL check — platnost do 24h po montage_termin (fallback 48h od vytvoření)
        if _is_back_protocol_token_expired(token_obj):
            token_obj.delete()
            return Response(
                {"detail": "Token vypršel."},
                status=status.HTTP_410_GONE,
            )

        order = token_obj.order
        return Response({
            "order_id": order.pk,
            "order_number": order.order_number,
            "client_name": order.client.name if order.client else None,
            "team_name": order.team.name if order.team else None,
            "has_back_protocol": hasattr(order, "back_protocol"),
        })


class BackProtocolUploadView(APIView):
    """Upload zpětného protokolu — token-gated (bez auth).

    POST s multipart/form-data:
      - token (str, povinný)
      - image (file, povinný)
      - alt_text (str, volitelný)

    Workflow: validace → uložení → QR validace → WebP konverze → status → smazání tokenu.
    """

    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(summary="Nahrát zpětný protokol (externí)")
    def post(self, request):
        from app_sprava_montazi.models import OrderBackProtocolToken

        token_str = request.data.get("token")
        image = request.FILES.get("image")
        alt_text = request.data.get("alt_text", "")

        if not token_str:
            return Response(
                {"detail": "Token je povinný."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not image:
            return Response(
                {"detail": "Soubor (image) je povinný."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token_obj = OrderBackProtocolToken.objects.select_related("order").get(
                token=token_str
            )
        except OrderBackProtocolToken.DoesNotExist:
            return Response(
                {"detail": "Neplatný nebo expirovaný token."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # TTL check — platnost do 24h po montage_termin (fallback 48h od vytvoření)
        if _is_back_protocol_token_expired(token_obj):
            token_obj.delete()
            return Response(
                {"detail": "Token vypršel."},
                status=status.HTTP_410_GONE,
            )

        order = token_obj.order
        uploader = ProtocolUploader(
            order=order, image=image, alt_text=alt_text, request=request
        )

        # 1) Validace obrázku
        if not uploader.validate_image():
            return Response(
                {"detail": uploader.error_message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2) Příprava souboru
        if not uploader.prepare_file_for_saving():
            return Response(
                {"detail": uploader.error_message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 3) Uložení
        if not uploader.save_protocol_object():
            return Response(
                {"detail": uploader.error_message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 4) QR validace
        if not uploader.validate_barcode():
            # Cleanup: smazat DB záznam protože soubor byl smazán v validate_barcode
            if uploader.protocol_obj:
                uploader.protocol_obj.delete()
            return Response(
                {"detail": uploader.error_message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 5) Konverze na WebP
        uploader.convert_and_save_webp()

        # 6) Update status → Realized
        uploader.update_order_status()

        # 7) Smazání tokenu
        uploader.delete_token()

        return Response(
            {"detail": "Protokol úspěšně přijat. Děkujeme!"},
            status=status.HTTP_201_CREATED,
        )


# ══════════════════════════════════════════
# Back Protocol — interní (autentizovaný upload)
# ══════════════════════════════════════════
class BackProtocolInternalUploadView(APIView):
    """Upload zpětného protokolu zevnitř aplikace (auth required).

    POST s multipart/form-data:
      - image (file, povinný)
      - alt_text (str, volitelný)

    Interní upload přeskakuje QR validaci — admin ví co nahrává.
    """

    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(summary="Nahrát zpětný protokol (interní)")
    def post(self, request, order_pk):
        order = get_object_or_404(Order, pk=order_pk)
        image = request.FILES.get("image")
        alt_text = request.data.get("alt_text", "")

        if not image:
            return Response(
                {"detail": "Soubor (image) je povinný."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        uploader = ProtocolUploader(
            order=order, image=image, alt_text=alt_text, request=request
        )

        if not uploader.validate_image():
            return Response(
                {"detail": uploader.error_message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not uploader.prepare_file_for_saving():
            return Response(
                {"detail": uploader.error_message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not uploader.save_protocol_object():
            return Response(
                {"detail": uploader.error_message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # QR validace přeskočena — interní upload (admin)

        # WebP konverze
        uploader.convert_and_save_webp()

        return Response(
            {"detail": "Zpětný protokol nahrán.", "order_id": order.pk},
            status=status.HTTP_201_CREATED,
        )


# ──────────────────────────────────────
# Bot Token Info (for Import page)
# ──────────────────────────────────────
class BotTokenInfoView(APIView):
    """Informace o bot účtu — bot se přihlašuje přes JWT (httpOnly cookies)."""

    permission_classes = [permissions.IsAuthenticated, IsManagerOrAbove]

    @extend_schema(summary="Stav bot účtu")
    def get(self, request):
        system_bot = os.getenv("SYSTEM_BOT")
        if not system_bot:
            return Response(
                {"configured": False, "message": "SYSTEM_BOT env variable není nastavena."},
            )
        try:
            user = User.objects.get(username=system_bot)
            jwt_lifetime = settings.SIMPLE_JWT.get(
                "ACCESS_TOKEN_LIFETIME", timedelta(minutes=60)
            )
            refresh_lifetime = settings.SIMPLE_JWT.get(
                "REFRESH_TOKEN_LIFETIME", timedelta(days=7)
            )
            return Response({
                "configured": True,
                "bot_user": system_bot,
                "is_active": user.is_active,
                "auth_method": "JWT httpOnly cookies",
                "access_lifetime_minutes": int(jwt_lifetime.total_seconds() / 60),
                "refresh_lifetime_days": int(refresh_lifetime.total_seconds() / 86400),
                "last_login": user.last_login.isoformat() if user.last_login else None,
            })
        except User.DoesNotExist:
            return Response({
                "configured": True,
                "bot_user": system_bot,
                "is_active": False,
                "message": f"Uživatel '{system_bot}' neexistuje v DB.",
            })
