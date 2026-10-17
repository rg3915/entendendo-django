"""Serializers da API: traduzem os models para JSON e validam o que chega."""
from rest_framework import serializers

from .models import Event, Tag, Talk


class EventSerializer(serializers.ModelSerializer):
    """Evento como sai na API: os campos vêm do model."""

    class Meta:
        model = Event
        fields = ["id", "name", "date", "city", "is_open"]


class TalkSerializer(serializers.ModelSerializer):
    """Palestra: lê com o evento, o palestrante e as tags; escreve pelos ids."""

    event = serializers.CharField(source="event.name", read_only=True)
    speaker = serializers.CharField(source="submitted_by.username", read_only=True)
    tags = serializers.SlugRelatedField(slug_field="name", many=True, read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(source="event", queryset=Event.objects.all(), write_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        source="tags", queryset=Tag.objects.all(), many=True, write_only=True, required=False
    )

    class Meta:
        model = Talk
        fields = ["id", "title", "abstract", "level", "duration", "event", "speaker", "tags", "event_id", "tag_ids"]
        extra_kwargs = {"abstract": {"write_only": True}}
