from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from cfp import api_drf, api_ninja

urlpatterns = [
    path("admin/", admin.site.urls),
    # a mesma API duas vezes, no mesmo processo e no mesmo banco
    path("drf/", include(api_drf.router.urls)),
    path("drf/me/", api_drf.me),
    path("drf/stats/", api_drf.stats),
    path("drf/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("drf/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("ninja/", api_ninja.api.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("cfp.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
