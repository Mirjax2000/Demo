"""URLs config"""

from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from accounts.views import RegisterView
from app_sprava_montazi.views import (
    PdfView as Pdf,
    IndexView as Index,
    TeamsView as Teams,
    OrdersView as Orders,
    ClientUpdateView as CUV,
    OrderPdfView as OrderPdf,
    HomePageView as HomePage,
    DashboardView as Dashboard,
    CreatePageView as CreatePage,
    TeamCreateView as TeamCreate,
    TeamUpdateView as TeamUpdate,
    TeamDetailView as TeamDetail,
    OrderDetailView as OrderDetail,
    OrderCreateView as OrderCreate,
    OrderUpdateView as OrderUpdate,
    GeneratePDFView as GeneratePDF,
    OrderHistoryView as OrderHistory,
    BackProtocolView as BackProtocol,
    ClientUpdateSecondaryView as CUS,
    OrderProtocolView as OrderProtocol,
    ClientsOrdersView as ClientsOrders,
    CustomerUpdateView as CustomerUpdate,
    CheckPDFProtocolView as CheckPDFProtocol,
    ExportOrdersExcelView as ExportOrdersExcel,
    UploadBackProtocolView as UploadBackProtocol,
    IncompleteCustomersView as IncompleteCustomers,
)
from app_sprava_montazi.views_services import (
    AutocompleteOrdersView as AutocompleteOrders,
    OrderStatusView as OrderStatus,
    SendMailView as SendMail,
)

# --- typove zkratky
PK = "<int:pk>"
OPK = "<int:order_pk>"
SLUG = "<slug:slug>"
MANDANT = "<str:mandant>"
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
    path("order/export/", ExportOrdersExcel.as_view(), name="order_export"),
    path(f"order/{SLUG}/{OPK}/client_update/", CUV.as_view(), name="client_update"),
    path(f"order/{SLUG}/client_update_sec/", CUS.as_view(), name="client_update_sec"),
    path(f"order/{SLUG}/client_orders/", ClientsOrders.as_view(), name="client_orders"),
    path(f"order/{PK}/order_update/", OrderUpdate.as_view(), name="order_update"),
    path(f"order/{PK}/detail/", OrderDetail.as_view(), name="order_detail"),
    path(f"order/{PK}/history/", OrderHistory.as_view(), name="order_history"),
    path(f"order/{PK}/protocol/", OrderProtocol.as_view(), name="protocol"),
    path(f"order/{PK}/generate-pdf/", GeneratePDF.as_view(), name="generate_pdf"),
    path(f"order/{PK}/back_protocol/", BackProtocol.as_view(), name="back_protocol"),
    path(
        f"order/{PK}/upload_protocol/",
        UploadBackProtocol.as_view(),
        name="upload_protocol",
    ),
    #
    # --- create ---
    path("createpage/", CreatePage.as_view(), name="createpage"),
    #
    # --- teams ---
    path("teams/", Teams.as_view(), name="teams"),
    path("teams/create/", TeamCreate.as_view(), name="team_create"),
    path(f"teams/{SLUG}/detail/", TeamDetail.as_view(), name="team_detail"),
    path(f"teams/{SLUG}/update/", TeamUpdate.as_view(), name="team_update"),
    #
    # --- pdf ---
    path(f"pdf/{MANDANT}/mandant/", Pdf.as_view(), name="mandant_pdf"),
    path(f"pdf/{PK}/order/", OrderPdf.as_view(), name="protocol_pdf"),
    path(f"pdf/{PK}/check/", CheckPDFProtocol.as_view(), name="check_pdf"),
    #
    # --- email ---
    path(f"send/{PK}/order/", SendMail.as_view(), name="send_mail"),
    #
    # --- autocomplete ---
    path("autocomp-orders/", AutocompleteOrders.as_view(), name="autocomplete_orders"),
    path("order-status/", OrderStatus.as_view(), name="order_status"),
]


app_accounts_urls: list = [
    path("accounts/register/", RegisterView.as_view(), name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),
]

api_urls: list = [
    path(
        "api/incomplete-customers/",
        IncompleteCustomers.as_view(),
        name="incomplete-customers",
    ),
    path("api/update-customers/", CustomerUpdate.as_view(), name="update-customers"),
    path("api-token-auth/", obtain_auth_token),
]
#
urlpatterns += app_sprava_montazi
urlpatterns += app_accounts_urls
urlpatterns += api_urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
