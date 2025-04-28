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
    order_create,
    order_detail,
    order_update,
)

urlpatterns: list = [
    path("admin/", admin.site.urls),
]

app_sprava_montazi: list = [
    path("", IndexView.as_view(), name="index"),
    path("homepage/", HomePageView.as_view(), name="homepage"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    # orders
    path("orders/", OrdersView.as_view(), name="orders"),
    path("order/create/", order_create, name="order_create"),
    path("order/update/<int:order_id>/", order_update, name="order_update"),
    path("order/detail/<int:order_id>/", order_detail, name="order_detail"),
    # teams
    path("teams/", TeamsView.as_view(), name="teams"),
    path("teams/create", TeamCreateView.as_view(), name="team_create"),
    path("teams/<slug:slug>/update", TeamUpdateView.as_view(), name="team_update"),
]

app_accounts_urls: list = [
    path("accounts/register/", RegisterView.as_view(), name="signup"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/", include("django.contrib.auth.urls")),
]

api_urls: list = []
#
urlpatterns += app_sprava_montazi
urlpatterns += app_accounts_urls
urlpatterns += api_urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
