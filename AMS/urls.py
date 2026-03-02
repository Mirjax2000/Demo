"""URLs config — API-only (React frontend)"""

from drf_spectacular.views import SpectacularAPIView as APIs
from drf_spectacular.views import SpectacularSwaggerView as Swagger
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.urls.conf import include


urlpatterns: list = [
    path("admin/", admin.site.urls),
]

# API v1 — REST API pro React frontend
api_v1_urls: list = [
    path("api/v1/", include("api_v1.urls", namespace="api_v1")),
    path("api/v1/schema/", APIs.as_view(), name="schema-v1"),
    path("api/v1/docs/", Swagger.as_view(url_name="schema-v1"), name="api-docs-v1"),
]

urlpatterns += api_v1_urls
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
