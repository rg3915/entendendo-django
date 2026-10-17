from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from cfp.models import Event, Tag, Talk


class Command(BaseCommand):
    help = "Cria eventos, tags e as usuárias de exemplo (dados fictícios)."

    def handle(self, *args, **options):
        User = get_user_model()
        for username in ["regis", "bruno"]:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username, password="noite-do-codigo")
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
        abstract = "A practical tour of Django: forms, class-based views and the flow behind them, with real code."
        nov, dec = Event.objects.get(name="Noite do Código #12"), Event.objects.get(name="Noite do Código #13")
        talks = [
            (nov, regis, "Django Forms na prática"), (nov, regis, "Formsets sem medo"), (nov, regis, "Validação sem segredo"),
            (dec, regis, "Class-Based Views sem mistério"), (dec, regis, "Mixins na vida real"),
            (dec, User.objects.get(username="bruno"), "Testes com pytest"),
        ]
        for event, user, title in talks:
            Talk.objects.get_or_create(
                title=title, event=event,
                defaults={"submitted_by": user, "abstract": abstract, "level": "beginner", "duration": 40},
            )
        self.stdout.write(self.style.SUCCESS("Seed ok: 3 events, 6 tags, 6 talks, users regis and bruno."))
