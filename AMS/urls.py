"""URLs config"""

from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.urls.conf import include
from accounts.views import RegisterView, CustomLoginView
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
    TeamDeleteView as TeamDelete,
    OrderDetailView as OrderDetail,
    OrderDeleteView as OrderDelete,
    OrderCreateView as OrderCreate,
    OrderUpdateView as OrderUpdate,
    GeneratePDFView as GeneratePDF,
    OrderHiddenView as OrderHidden,
    OrderHistoryView as OrderHistory,
    BackProtocolView as BackProtocol,
    ClientUpdateSecondaryView as CUS,
    AssemblyDocsView as AssemblyDocs,
    UploadOneImageView as UploadOneImg,
    OrderProtocolView as OrderProtocol,
    ClientsOrdersView as ClientsOrders,
    ProtocolUploadView as ProtocolUpload,
    UploadBackProtocolView as UplBckPrtcl,
    CheckPDFProtocolView as CheckPDFProtocol,
    MontageImgUploadView as MontageImgUpload,
    ExportOrdersExcelView as ExportOrdersExcel,
    SwitchAdvicedWithDeliveryToRealizedView as SwtchAdvcdDlrToRlzd,
)

from app_sprava_montazi.views_services import (
    AutocompleteOrdersByDeliveryGroupView as AtcompByDlivryOrders,
    OrderStatusView as OrderStatus,
    SendMailView as SendMail,
    DownloadMontageImagesZipView as DownMontZip,
)

from API.views import (
    CustomerUpdateView as CustomerUpdate,
    IncompleteCustomersView as IncmpCstmrs,
    RealizujZakazkyView as RealizujZakazky,
)
from API.views import (
    ApiStatusView as ApiStatus,
    ZaterminovanoDopravouView as ZatermDoprav,
)


# --- typove zkratky
PK = "<int:pk>"
OPK = "<int:order_pk>"
ONMB = "<str:order_number>"
SLUG = "<slug:slug>"
MANDANT = "<str:mandant>"
SWTCH1 = "switch/adviced_delivery_to_realized"
SWTCH1NAME = "order_switch_delivery_realized"
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
    path(f"order/{PK}/hidden/", OrderHidden.as_view(), name="order_hidden"),
    path(f"order/{PK}/{SWTCH1}", SwtchAdvcdDlrToRlzd.as_view(), name=f"{SWTCH1NAME}"),
    path(f"order/{PK}/order_update/", OrderUpdate.as_view(), name="order_update"),
    path(f"order/{PK}/delete_order/", OrderDelete.as_view(), name="delete_order"),
    path(f"order/{PK}/detail/", OrderDetail.as_view(), name="order_detail"),
    path("order/export/", ExportOrdersExcel.as_view(), name="order_export"),
    path(f"order/{PK}/assembly_docs/", AssemblyDocs.as_view(), name="assembly_docs"),
    # --- client
    path(f"order/{PK}/client_update/", CUV.as_view(), name="client_update"),
    path(f"order/{SLUG}/client_update_sec/", CUS.as_view(), name="client_update_sec"),
    path(f"order/{SLUG}/client_orders/", ClientsOrders.as_view(), name="client_orders"),
    # ---
    path(f"order/{PK}/history/", OrderHistory.as_view(), name="order_history"),
    # ---
    path(f"order/{PK}/protocol/", OrderProtocol.as_view(), name="protocol"),
    path(f"order/{PK}/generate-pdf/", GeneratePDF.as_view(), name="generate_pdf"),
    path(f"order/{PK}/back_protocol/", BackProtocol.as_view(), name="back_protocol"),
    path(f"order/{PK}/upload_protocol/", UplBckPrtcl.as_view(), name="upload_protocol"),
    path(f"order/{PK}/upload_one_img/", UploadOneImg.as_view(), name="upload_one_img"),
    # ---
    # --- create ---
    path("createpage/", CreatePage.as_view(), name="createpage"),
    path("createpage/upload/", ProtocolUpload.as_view(), name="create_upload_protocol"),
    path("createpage/imgupload/", MontageImgUpload.as_view(), name="create_upload_img"),
    #
    # --- teams ---
    path("teams/", Teams.as_view(), name="teams"),
    path("teams/create/", TeamCreate.as_view(), name="team_create"),
    path(f"teams/{PK}/delete/", TeamDelete.as_view(), name="team_delete"),
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
    path(
        "autocomp-orders/", AtcompByDlivryOrders.as_view(), name="autocomplete_orders"
    ),
    path("order-status/", OrderStatus.as_view(), name="order_status"),
    # --- download image zip ---
    path(f"order/{ONMB}/dwn-imgs/", DownMontZip.as_view(), name="dwn_mont_imgs_zip"),
]


app_accounts_urls: list = [
    path("accounts/login/", CustomLoginView.as_view(), name="login"),
    path("accounts/register/", RegisterView.as_view(), name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),
]

api_urls: list = [
    path(
        "api/incomplete-customers/", IncmpCstmrs.as_view(), name="incomplete-customers"
    ),
    path(
        "api/inc-dopravni-zakazka/", ZatermDoprav.as_view(), name="inc-dopravni-zakazka"
    ),
    path("api/update-customers/", CustomerUpdate.as_view(), name="update-customers"),
    path("api/update-dopzak/", RealizujZakazky.as_view(), name="update-dopzak"),
    path("api/status/", ApiStatus.as_view(), name="api-status"),
    path("api-token-auth/", obtain_auth_token),
    # --- swagger
    path("api/schema/", login_required(SpectacularAPIView.as_view()), name="schema"),
    path(
        "api/docs/",
        login_required(SpectacularSwaggerView.as_view(url_name="schema")),
        name="api-docs",
    ),
]

#
urlpatterns += app_sprava_montazi
urlpatterns += app_accounts_urls
urlpatterns += api_urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
