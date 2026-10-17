from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import CreateView

from .forms import (
    AttachmentForm,
    GuestFormSet,
    SpeakerFormSet,
    SubscribeForm,
    SubscribeHelperForm,
    TalkForm,
)
from .models import Attachment, Event, Talk


def home(request):
    """Eventos com a chamada de palestras aberta."""
    events = Event.objects.filter(is_open=True).order_by("date")
    return render(request, "cfp/home.html", {"events": events})


def subscribe(request):
    """GET entrega a folha em branco; POST recebe a folha preenchida."""
    if request.method == "POST":
        form = SubscribeForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            messages.success(request, f"Thanks, {name}! We will let you know.")
            return redirect("cfp:thanks")
    else:
        form = SubscribeForm()
    return render(request, "cfp/subscribe.html", {"form": form})


def thanks(request):
    """O comprovante (destino do redirect)."""
    return render(request, "cfp/thanks.html")


def guests(request):
    """Formset: vários convidados de uma vez."""
    if request.method == "POST":
        formset = GuestFormSet(request.POST)
        if formset.is_valid():
            names = [f.cleaned_data["name"] for f in formset if f.has_changed() and not f.cleaned_data.get("DELETE")]
            messages.success(request, f"{len(names)} guest(s) on the list: {', '.join(names)}.")
            return redirect("cfp:guests")
    else:
        formset = GuestFormSet()
    return render(request, "cfp/guests.html", {"formset": formset})


@login_required
def my_talks(request):
    """Só as palestras de quem está logado."""
    talks = Talk.objects.filter(submitted_by=request.user).select_related("event")
    return render(request, "cfp/my_talks.html", {"talks": talks})


class TalkCreateView(LoginRequiredMixin, CreateView):
    """Nova proposta: o form, os co-palestrantes e os anexos no mesmo POST."""

    form_class = TalkForm
    template_name = "cfp/talk_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context["formset"] = SpeakerFormSet(self.request.POST, self.request.FILES)
            context["attachments_form"] = AttachmentForm(self.request.POST, self.request.FILES)
        else:
            context["formset"] = SpeakerFormSet()
            context["attachments_form"] = AttachmentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        formset = SpeakerFormSet(request.POST, request.FILES)
        attachments_form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid() and attachments_form.is_valid():
            with transaction.atomic():
                talk = form.save()
                formset.instance = talk
                formset.save()
                for f in attachments_form.cleaned_data["files"]:
                    Attachment.objects.create(talk=talk, file=f)
            messages.success(request, "Talk submitted!")
            return redirect("cfp:talk_detail", pk=talk.pk)
        return self.render_to_response(
            {"form": form, "formset": formset, "attachments_form": attachments_form}
        )


@login_required
def talk_create(request):
    """A mesma proposta numa função: commit=False e save_m2m()."""
    if request.method == "POST":
        form = TalkForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            talk = form.save(commit=False)
            talk.submitted_by = request.user
            talk.save()
            form.save_m2m()
            return redirect("cfp:talk_detail", pk=talk.pk)
    else:
        form = TalkForm(user=request.user)
    return render(request, "cfp/talk_form.html", {"form": form})


@login_required
def talk_edit(request, pk):
    """Edição: instance no form e no inline formset."""
    talk = get_object_or_404(Talk, pk=pk, submitted_by=request.user)
    if request.method == "POST":
        form = TalkForm(request.POST, request.FILES, instance=talk, user=request.user)
        formset = SpeakerFormSet(request.POST, request.FILES, instance=talk)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Talk updated!")
            return redirect("cfp:talk_detail", pk=talk.pk)
    else:
        form = TalkForm(instance=talk, user=request.user)
        formset = SpeakerFormSet(instance=talk)
    return render(request, "cfp/talk_form.html", {"form": form, "formset": formset, "talk": talk})


@login_required
def talk_detail(request, pk):
    """Slides, anexos e palestrantes de uma proposta."""
    talk = get_object_or_404(Talk, pk=pk, submitted_by=request.user)
    return render(request, "cfp/talk_detail.html", {"talk": talk})


@login_required
@require_POST
def check_title(request):
    """htmx: valida o título enquanto a pessoa digita e devolve só o partial."""
    form = TalkForm(request.POST, user=request.user)
    form.is_valid()
    return render(request, "cfp/talk_form.html#title-feedback", {"form": form})


def tw_crispy(request):
    """Tailwind: o filtro |crispy."""
    return render(request, "cfp/tw/subscribe_crispy.html", {"form": SubscribeForm()})


def tw_helper(request):
    """Tailwind: FormHelper e Layout."""
    return render(request, "cfp/tw/subscribe_helper.html", {"form": SubscribeHelperForm()})


def tw_tweaks(request):
    """Tailwind: widget-tweaks no template."""
    form = SubscribeForm(request.POST or None)
    if request.method == "POST":
        form.is_valid()
    return render(request, "cfp/tw/subscribe_tweaks.html", {"form": form})
