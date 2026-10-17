"""API da Noite do Código com Django Ninja: eventos e propostas de palestra."""
from typing import Annotated, Literal

from django.shortcuts import get_object_or_404
from ninja import Field, FilterLookup, FilterSchema, ModelSchema, NinjaAPI, PatchDict, Query, Router, Schema, Status
from ninja.pagination import PageNumberPagination, paginate
from ninja.security import APIKeyHeader, django_auth
from ninja.throttling import AnonRateThrottle
from pydantic import field_validator

from .models import ApiKey, Event, Talk


class ApiKeyAuth(APIKeyHeader):
    """Autentica pela chave enviada no cabeçalho X-API-Key."""

    param_name = "X-API-Key"

    def authenticate(self, request, key):
        token = ApiKey.objects.select_related("user").filter(key=key).first()
        return token.user if token else None


class EventOut(ModelSchema):
    """Evento como sai na API: os campos vêm do model."""

    class Meta:
        model = Event
        fields = ["id", "name", "date", "city", "is_open"]


class TalkOut(ModelSchema):
    """Palestra como sai na API, com o evento, o palestrante e as tags."""

    event: str = Field(alias="event.name")
    speaker: str = Field(alias="submitted_by.username")
    tags: list[str]

    class Meta:
        model = Talk
        fields = ["id", "title", "level", "duration"]

    @staticmethod
    def resolve_tags(talk):
        return [tag.name for tag in talk.tags.all()]


class TalkIn(Schema):
    """O que o cliente manda para criar uma palestra (validado pelo Pydantic)."""

    title: str = Field(max_length=120)
    abstract: str = Field(min_length=80)
    event_id: int
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    duration: Literal[20, 40] = 40
    tags: list[int] = []

    @field_validator("title")
    @classmethod
    def not_shouting(cls, title):
        if title.isupper():
            raise ValueError("Please don't shout: use lowercase letters too.")
        return title


class TalkFilter(FilterSchema):
    """Filtros da listagem: ?level=…&event_id=…&q=…"""

    level: str | None = None
    event_id: int | None = None
    q: Annotated[str | None, FilterLookup("title__icontains")] = None


class Message(Schema):
    detail: str


api = NinjaAPI(title="Noite do Código API", version="1.0.0")
events = Router(tags=["events"])
talks = Router(tags=["talks"])


@events.get("/", response=list[EventOut])
def list_events(request):
    """Eventos com a chamada de palestras aberta."""
    return Event.objects.filter(is_open=True).order_by("date")


@talks.get("/", response=list[TalkOut])
@paginate(PageNumberPagination, page_size=2)
def list_talks(request, filters: Query[TalkFilter]):
    """Lista as palestras, filtrada e paginada."""
    qs = Talk.objects.select_related("event", "submitted_by").prefetch_related("tags").order_by("id")
    return filters.filter(qs)


@talks.get("/{talk_id}", response=TalkOut)
def get_talk(request, talk_id: int):
    return get_object_or_404(Talk, id=talk_id)


@talks.post("/", response={201: TalkOut}, auth=ApiKeyAuth())
def create_talk(request, payload: TalkIn):
    """Cria a palestra em nome de quem está autenticado (request.auth)."""
    talk = Talk.objects.create(submitted_by=request.auth, **payload.dict(exclude={"tags"}))
    talk.tags.set(payload.tags)
    return Status(201, talk)


@talks.patch("/{talk_id}", response={200: TalkOut, 403: Message}, auth=ApiKeyAuth())
def update_talk(request, talk_id: int, payload: PatchDict[TalkIn]):
    """Atualiza só os campos enviados; só quem enviou a palestra pode editar."""
    talk = get_object_or_404(Talk, id=talk_id)
    if talk.submitted_by != request.auth:
        return Status(403, {"detail": "Only the speaker can edit this talk."})
    tags = payload.pop("tags", None)
    for attr, value in payload.items():
        setattr(talk, attr, value)
    talk.save()
    if tags is not None:
        talk.tags.set(tags)
    return talk


@api.get("/me", auth=django_auth)
def me(request):
    """Quem está logado pela sessão do Django (o mesmo login do site)."""
    return {"username": request.auth.username}


@api.get("/stats", throttle=[AnonRateThrottle("3/10s")])
async def stats(request):
    """Números da chamada, com consultas assíncronas do ORM."""
    return {
        "talks": await Talk.objects.acount(),
        "open_events": await Event.objects.filter(is_open=True).acount(),
    }


api.add_router("/events", events)
api.add_router("/talks", talks)
