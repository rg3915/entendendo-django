from django.conf import settings
from django.core.validators import FileExtensionValidator, MinLengthValidator
from django.db import models
from django.urls import reverse

from .validators import validate_not_shouting


class Event(models.Model):
    """Uma edição do meetup Noite do Código."""

    name = models.CharField(max_length=80)
    date = models.DateField()
    city = models.CharField(max_length=60)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Assunto da palestra (Django, Python, testes...)."""

    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Talk(models.Model):
    """Proposta de palestra enviada para um evento."""

    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    class Duration(models.IntegerChoices):
        SHORT = 20, "20 min"
        LONG = 40, "40 min"

    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="talks")
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=120, validators=[validate_not_shouting])
    abstract = models.TextField(validators=[MinLengthValidator(80)])
    level = models.CharField(max_length=12, choices=Level, default=Level.BEGINNER)
    duration = models.IntegerField(choices=Duration, default=Duration.LONG)
    tags = models.ManyToManyField(Tag, blank=True)
    slides = models.FileField(
        upload_to="slides/%Y/",
        validators=[FileExtensionValidator(["pdf"])],
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Para onde a CreateView e a UpdateView mandam depois de salvar (sem success_url)."""
        return reverse("cfp:talk_detail", kwargs={"pk": self.pk})


class Speaker(models.Model):
    """Co-palestrante de uma proposta (o inline formset)."""

    talk = models.ForeignKey(Talk, on_delete=models.CASCADE, related_name="speakers")
    name = models.CharField(max_length=80)
    email = models.EmailField()
    photo = models.ImageField(upload_to="speakers/", blank=True)

    def __str__(self):
        return self.name


class Attachment(models.Model):
    """Um arquivo anexado à proposta (um registro por arquivo)."""

    talk = models.ForeignKey(Talk, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="attachments/")

    def __str__(self):
        return self.file.name
