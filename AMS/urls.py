"""
URLs configuration
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls.conf import include

from accounts.views import RegisterView

urlpatterns: list = [
    path("admin/", admin.site.urls),
]

app_accounts_urls: list = [
    path("accounts/register/", RegisterView.as_view(), name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),
]

app_sprava_montazi: list = []
api_urls: list = []
#
urlpatterns += app_sprava_montazi
urlpatterns += app_accounts_urls
urlpatterns += api_urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
