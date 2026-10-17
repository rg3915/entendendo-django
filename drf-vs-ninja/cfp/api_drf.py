"""API da Noite do Código com Django REST framework (em /drf/): eventos e propostas de palestra."""
import django_filters
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import authentication, exceptions, permissions, routers, serializers, viewsets
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .models import ApiKey, Event, Talk
from .serializers import EventSerializer, TalkSerializer


class ApiKeyAuthentication(authentication.BaseAuthentication):
    """Autentica pela chave enviada no cabeçalho X-API-Key."""

    def authenticate(self, request):
        key = request.headers.get("X-API-Key")
        if not key:
            return None
        token = ApiKey.objects.select_related("user").filter(key=key).first()
        if token is None:
            raise exceptions.AuthenticationFailed("Invalid API key.")
        return (token.user, token)

    def authenticate_header(self, request):
        return "X-API-Key"


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Qualquer um lê; só quem enviou a palestra pode editar."""

    message = "Only the speaker can edit this talk."

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or obj.submitted_by == request.user


class TalkFilter(django_filters.FilterSet):
    """Filtros da listagem: ?level=…&event_id=…&q=…"""

    event_id = django_filters.NumberFilter(field_name="event_id")
    q = django_filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = Talk
        fields = ["level"]


class TwoPerPage(PageNumberPagination):
    page_size = 2


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """Eventos com a chamada de palestras aberta."""

    queryset = Event.objects.filter(is_open=True).order_by("date")
    serializer_class = EventSerializer
    pagination_class = None


class TalkViewSet(viewsets.ModelViewSet):
    """Palestras: lista filtrada e paginada, detalhe, criação e PATCH só do dono."""

    queryset = Talk.objects.select_related("event", "submitted_by").prefetch_related("tags").order_by("id")
    serializer_class = TalkSerializer
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    pagination_class = TwoPerPage
    filterset_class = TalkFilter
    http_method_names = ["get", "post", "patch"]

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)


@extend_schema(responses=inline_serializer("Me", {"username": serializers.CharField()}))
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    """Quem está logado pela sessão do Django (o mesmo login do site)."""
    return Response({"username": request.user.username})


class StatsThrottle(AnonRateThrottle):
    rate = "3/min"  # o DRF só aceita período em s, m, h ou d
    scope = "drf_stats"  # o throttle do Ninja usa a mesma chave de cache "throttle_anon_<ip>": sem isso, as duas dividem a contagem


@extend_schema(responses=inline_serializer("Stats", {"talks": serializers.IntegerField(), "open_events": serializers.IntegerField()}))
@api_view(["GET"])
@throttle_classes([StatsThrottle])
def stats(request):
    """Números da chamada (o DRF não tem view assíncrona: esta é síncrona)."""
    return Response({"talks": Talk.objects.count(), "open_events": Event.objects.filter(is_open=True).count()})


router = routers.DefaultRouter()
router.register("events", EventViewSet)
router.register("talks", TalkViewSet)
