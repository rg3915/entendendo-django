from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from cfp.api import me, router, stats

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/me/", me),
    path("api/stats/", stats),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("cfp.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
