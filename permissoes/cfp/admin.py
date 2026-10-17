from django.contrib import admin

from .models import Event, Talk


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["name", "date", "organizer", "is_open"]


@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    list_display = ["title", "event", "submitted_by", "status"]
    list_filter = ["status", "event"]
