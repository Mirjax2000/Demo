"""
URLs config
"""

from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls.conf import include

from accounts.views import RegisterView
from app_sprava_montazi.views import (
    DashboardView,
    IndexView,
    HomePageView,
    OrdersView,
    TeamsView,
    TeamCreateView,
    TeamUpdateView,
    TeamDetailView,
    OrderDetailView,
    OrderCreateView,
    ClientUpdateView,
    CreatePageView,
    OrderUpdateView,
)

urlpatterns: list = [
    path("admin/", admin.site.urls),
]

app_sprava_montazi: list = [
    path("", IndexView.as_view(), name="index"),
    path("homepage/", HomePageView.as_view(), name="homepage"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    # --- orders ---
    path("orders/", OrdersView.as_view(), name="orders"),
    path("order/create/", OrderCreateView.as_view(), name="order_create"),
    path(
        "order/order_update/<int:pk>/",
        OrderUpdateView.as_view(),
        name="order_update",
    ),
    path(
        "order/client_update/<slug:slug>/<int:order_pk>/",
        ClientUpdateView.as_view(),
        name="client_update",
    ),
    path("order/detail/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    # --- create ---
    path("createpage/", CreatePageView.as_view(), name="createpage"),
    # --- teams ---
    path("teams/", TeamsView.as_view(), name="teams"),
    path("teams/create/", TeamCreateView.as_view(), name="team_create"),
    path("teams/detail/<slug:slug>/", TeamDetailView.as_view(), name="team_detail"),
    path("teams/update/<slug:slug>/", TeamUpdateView.as_view(), name="team_update"),
]

app_accounts_urls: list = [
    path("accounts/register/", RegisterView.as_view(), name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),
]

api_urls: list = []
#
urlpatterns += app_sprava_montazi
urlpatterns += app_accounts_urls
urlpatterns += api_urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
