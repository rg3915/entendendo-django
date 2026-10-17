from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from cfp.api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("cfp.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
