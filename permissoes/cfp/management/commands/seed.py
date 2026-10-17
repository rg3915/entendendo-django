from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from cfp.models import Event, Tag, Talk


class Command(BaseCommand):
    help = "Cria eventos, tags e as usuárias de exemplo (dados fictícios)."

    def handle(self, *args, **options):
        User = get_user_model()
        for username in ["regis", "bruno", "caio"]:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username, password="noite-do-codigo")
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", password="noite-do-codigo")
        User.objects.filter(username="caio").update(is_staff=True)
        events = [
            ("Noite do Código #12", date(2026, 11, 19), "Florianópolis", True),
            ("Noite do Código #13", date(2026, 12, 10), "Curitiba", True),
            ("Noite do Código #11", date(2026, 9, 24), "Porto Alegre", False),
        ]
        for name, day, city, is_open in events:
            Event.objects.update_or_create(name=name, defaults={"date": day, "city": city, "is_open": is_open})
        for name in ["Django", "Python", "Forms", "Testing", "htmx", "Career"]:
            Tag.objects.get_or_create(name=name)
        regis = User.objects.get(username="regis")
        bruno = User.objects.get(username="bruno")
        Event.objects.filter(name="Noite do Código #12").update(organizer=bruno)
        organizers, _ = Group.objects.get_or_create(name="Organizers")
        organizers.permissions.set(Permission.objects.filter(codename__in=["view_talk", "approve_talk"]))
        bruno.groups.add(organizers)
        event = Event.objects.get(name="Noite do Código #12")
        abstract = "A practical tour of Django forms: what as_p renders, GET and POST, validation and formsets."
        for title in ["Django Forms na prática", "Formsets sem medo", "Permissões sem susto"]:
            Talk.objects.get_or_create(
                title=title, event=event,
                defaults={"submitted_by": regis, "abstract": abstract, "level": "beginner", "duration": 40},
            )
        other = Event.objects.get(name="Noite do Código #13")
        Talk.objects.get_or_create(
            title="Testes que dão sono", event=other,
            defaults={"submitted_by": regis, "abstract": abstract, "level": "intermediate", "duration": 20},
        )
        self.stdout.write(self.style.SUCCESS("Seed ok: users regis, bruno (Organizers), caio (staff) and admin."))
