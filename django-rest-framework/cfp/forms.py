from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row
from crispy_tailwind.layout import Submit
from django import forms
from django.urls import reverse_lazy

from .models import Event, Speaker, Talk


class SubscribeForm(forms.Form):
    """Avise-me quando abrir a inscrição (forms.Form puro, sem banco)."""

    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    city = forms.CharField(required=False, help_text="We only use it to pick the next city.")
    phone = forms.CharField(required=False, widget=forms.TelInput)


class SubscribeHelperForm(SubscribeForm):
    """O mesmo formulário, com o layout descrito no Python pelo crispy."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row("name", "email"),
            "city",
            Submit("submit", "Notify me"),
        )


class GuestForm(forms.Form):
    """Um amigo que vai junto."""

    name = forms.CharField(max_length=80)
    email = forms.EmailField()


GuestFormSet = forms.formset_factory(GuestForm, extra=2, max_num=5, can_delete=True)


class TalkForm(forms.ModelForm):
    """Proposta de palestra: FK para evento, M2M com tags e o usuário logado."""

    class Meta:
        model = Talk
        fields = ["event", "title", "abstract", "level", "duration", "tags", "slides"]
        widgets = {
            "title": forms.TextInput(attrs={
                "hx-post": reverse_lazy("cfp:check_title"),
                "hx-trigger": "input changed delay:500ms",
                "hx-target": "closest div",
                "hx-swap": "outerHTML",
                "hx-include": "[name=event]",
            }),
            "abstract": forms.Textarea(attrs={"rows": 4}),
            "level": forms.RadioSelect,
            "tags": forms.CheckboxSelectMultiple,
        }
        error_messages = {
            "title": {"max_length": "Keep the title under 120 characters."},
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        event = self.fields["event"]
        event.queryset = Event.objects.filter(is_open=True)
        event.empty_label = "Pick an event"
        event.label_from_instance = lambda e: f"{e.name} · {e.date:%d/%m}"

    def clean_title(self):
        """Título repetido no mesmo evento não passa."""
        title = self.cleaned_data["title"]
        event = self.cleaned_data.get("event")
        same = Talk.objects.filter(event=event, title__iexact=title).exclude(pk=self.instance.pk)
        if event and same.exists():
            raise forms.ValidationError(
                "A talk with this title was already submitted to this event.",
                code="duplicate",
            )
        return title

    def clean(self):
        """Regras que envolvem mais de um campo (e o usuário)."""
        cleaned = super().clean()
        level, duration = cleaned.get("level"), cleaned.get("duration")
        if level == Talk.Level.ADVANCED and duration == Talk.Duration.SHORT:
            raise forms.ValidationError(
                "An advanced talk needs 40 minutes.", code="too_short"
            )
        event = cleaned.get("event")
        if self.user and event and not self.instance.pk:
            sent = Talk.objects.filter(submitted_by=self.user, event=event).count()
            if sent >= 3:
                raise forms.ValidationError(
                    "You can submit at most 3 talks per event.", code="limit"
                )
        return cleaned

    def save(self, commit=True):
        """Grava quem enviou a proposta."""
        talk = super().save(commit=False)
        if self.user:
            talk.submitted_by = self.user
        if commit:
            talk.save()
            self.save_m2m()
        return talk


SpeakerFormSet = forms.inlineformset_factory(
    Talk, Speaker, fields=["name", "email", "photo"], extra=1, can_delete=True
)


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class AttachmentForm(forms.Form):
    """Vários anexos de uma vez (receita da documentação)."""

    files = MultipleFileField(required=False)
