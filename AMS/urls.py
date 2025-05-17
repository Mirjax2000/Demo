"""URLs config"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from accounts.views import RegisterView
from app_sprava_montazi.views import (
    DashboardView as Dashboard,
    IndexView as Index,
    HomePageView as HomePage,
    OrdersView as Orders,
    TeamsView as Teams,
    TeamCreateView as TeamCreate,
    TeamUpdateView as TeamUpdate,
    TeamDetailView as TeamDetail,
    OrderDetailView as OrderDetail,
    OrderCreateView as OrderCreate,
    ClientUpdateView as CUV,
    CreatePageView as CreatePage,
    OrderUpdateView as OrderUpdate,
    ClientsOrdersView as ClientsOrders,
    OrderHistoryView as OrderHistory,
    ClientUpdateSecondaryView as CUS,
)

# --- typove zkratky
SLUG = "<slug:slug>"
OPK = "<int:order_pk>"
PK = "<int:pk>"
# ---
urlpatterns: list = [
    path("admin/", admin.site.urls),
]

app_sprava_montazi: list = [
    path("", Index.as_view(), name="index"),
    path("homepage/", HomePage.as_view(), name="homepage"),
    path("dashboard/", Dashboard.as_view(), name="dashboard"),
    #
    # --- orders ---
    path("orders/", Orders.as_view(), name="orders"),
    path("order/create/", OrderCreate.as_view(), name="order_create"),
    path(f"order/order_update/{PK}/", OrderUpdate.as_view(), name="order_update"),
    path(f"order/client_update/{SLUG}/{OPK}/", CUV.as_view(), name="client_update"),
    path(f"order/client_update_sec/{SLUG}/", CUS.as_view(), name="client_update_sec"),
    path(f"order/detail/{PK}/", OrderDetail.as_view(), name="order_detail"),
    path(f"order/client_orders/{SLUG}/", ClientsOrders.as_view(), name="client_orders"),
    path(f"order/history/{PK}/", OrderHistory.as_view(), name="order_history"),
    #
    # --- create ---
    path("createpage/", CreatePage.as_view(), name="createpage"),
    #
    # --- teams ---
    path("teams/", Teams.as_view(), name="teams"),
    path("teams/create/", TeamCreate.as_view(), name="team_create"),
    path(f"teams/detail/{SLUG}/", TeamDetail.as_view(), name="team_detail"),
    path(f"teams/update/{SLUG}/", TeamUpdate.as_view(), name="team_update"),
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
