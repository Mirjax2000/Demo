"""
API v1 URL routing — /api/v1/ namespace.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# ── DRF Router pro ViewSety ──
router = DefaultRouter()
router.register(r"orders", views.OrderViewSet, basename="order")
router.register(r"teams", views.TeamViewSet, basename="team")
router.register(r"clients", views.ClientViewSet, basename="client")
router.register(r"distrib-hubs", views.DistribHubViewSet, basename="distrib-hub")
router.register(r"finance/revenue", views.FinanceRevenueItemViewSet, basename="finance-revenue")
router.register(r"finance/costs", views.FinanceCostItemViewSet, basename="finance-cost")
router.register(r"call-logs", views.CallLogViewSet, basename="call-log")
router.register(r"settings", views.AppSettingViewSet, basename="app-setting")
router.register(r"users", views.UserAdminViewSet, basename="user-admin")

app_name = "api_v1"

urlpatterns = [
    # ── Auth (JWT — httpOnly cookies) ──
    path("auth/login/", views.LoginView.as_view(), name="jwt-login"),
    path("auth/refresh/", views.RefreshView.as_view(), name="jwt-refresh"),
    path("auth/logout/", views.LogoutView.as_view(), name="jwt-logout"),
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/me/", views.MeView.as_view(), name="me"),
    # ── Dashboard ──
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    # ── CSV Import ──
    path("import/", views.CSVImportView.as_view(), name="csv-import"),
    # ── Bot Token Info ──
    path("bot-token-info/", views.BotTokenInfoView.as_view(), name="bot-token-info"),
    # ── Health check ──
    path("health/", views.HealthCheckView.as_view(), name="health"),
    # ── Nested: Order → Articles ──
    path(
        "orders/<int:order_pk>/articles/",
        views.ArticleViewSet.as_view({"get": "list", "post": "create"}),
        name="order-articles-list",
    ),
    path(
        "orders/<int:order_pk>/articles/<int:pk>/",
        views.ArticleViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="order-articles-detail",
    ),
    # ── Nested: Order → Montáž Images ──
    path(
        "orders/<int:order_pk>/images/",
        views.OrderMontazImageViewSet.as_view({"get": "list", "post": "create"}),
        name="order-images-list",
    ),
    path(
        "orders/<int:order_pk>/images/<int:pk>/",
        views.OrderMontazImageViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
        name="order-images-detail",
    ),
    # ── Back Protocol (externí — token, bez auth) ──
    path(
        "back-protocol/validate/",
        views.BackProtocolTokenValidateView.as_view(),
        name="back-protocol-validate",
    ),
    path(
        "back-protocol/upload/",
        views.BackProtocolUploadView.as_view(),
        name="back-protocol-upload",
    ),
    # ── Back Protocol (interní — auth) ──
    path(
        "orders/<int:order_pk>/back-protocol/",
        views.BackProtocolInternalUploadView.as_view(),
        name="back-protocol-internal",
    ),
    # ── Router URLs (orders, teams, clients, ...) ──
    path("", include(router.urls)),
]
