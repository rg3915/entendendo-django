from django.contrib import messages
from django.contrib.auth.decorators import login_not_required, login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import SubscribeForm, TalkForm
from .mixins import OwnerQuerysetMixin, UserFormKwargsMixin
from .models import Event, Talk
from .trace import TraceMixin


# ------------------------------------------------------------------ funções (FBV): o "antes"

def subscribe_fbv(request):
    """GET entrega a folha em branco; POST recebe a folha preenchida."""
    if request.method == "POST":
        form = SubscribeForm(request.POST)
        if form.is_valid():
            messages.success(request, f"Thanks, {form.cleaned_data['name']}!")
            return redirect("cfp:thanks")
    else:
        form = SubscribeForm()
    return render(request, "cfp/subscribe.html", {"form": form})


@login_required
def my_talks_fbv(request):
    """Só as palestras de quem está logado."""
    talks = Talk.objects.filter(submitted_by=request.user)
    return render(request, "cfp/talk_list.html", {"talks": talks})


# ------------------------------------------------------------------ classes (CBV)

class PingView(View):
    """A CBV mínima: um método para cada verbo HTTP."""

    def get(self, request):
        return HttpResponse("pong")


@method_decorator(login_not_required, name="dispatch")
class HomeView(TemplateView):
    """Página inicial: só um template e um pouco de contexto."""

    template_name = "cfp/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["events"] = Event.objects.filter(is_open=True).order_by("date")
        return context


@method_decorator(login_not_required, name="dispatch")
class SubscribeView(FormView):
    """O mesmo avise-me da função, agora numa FormView."""

    form_class = SubscribeForm
    template_name = "cfp/subscribe.html"
    success_url = reverse_lazy("cfp:thanks")

    def form_valid(self, form):
        messages.success(self.request, f"Thanks, {form.cleaned_data['name']}!")
        return super().form_valid(form)


@method_decorator(login_not_required, name="dispatch")
class ThanksView(TemplateView):
    """O comprovante (destino do redirect)."""

    template_name = "cfp/thanks.html"


class TalkListView(LoginRequiredMixin, OwnerQuerysetMixin, ListView):
    """Minhas palestras, 3 por página."""

    model = Talk
    paginate_by = 3
    ordering = ["-created_at"]
    context_object_name = "talks"


class TalkDetailView(LoginRequiredMixin, OwnerQuerysetMixin, DetailView):
    """Uma palestra minha (a dos outros dá 404)."""

    model = Talk


class TalkCreateView(LoginRequiredMixin, UserFormKwargsMixin, CreateView):
    """Nova proposta: sem success_url, vai para o get_absolute_url."""

    model = Talk
    form_class = TalkForm

    def form_valid(self, form):
        messages.success(self.request, "Talk submitted!")
        return super().form_valid(form)


class TracedTalkCreateView(TraceMixin, TalkCreateView):
    """A mesma CreateView, contando no terminal cada método que o Django chama."""


class TalkUpdateView(LoginRequiredMixin, OwnerQuerysetMixin, UserFormKwargsMixin, UpdateView):
    """Edição: mesmo form e mesmo template da criação."""

    model = Talk
    form_class = TalkForm

    def form_valid(self, form):
        messages.success(self.request, "Talk updated!")
        return super().form_valid(form)


class TalkDeleteView(LoginRequiredMixin, OwnerQuerysetMixin, DeleteView):
    """GET mostra a confirmação; POST apaga."""

    model = Talk
    success_url = reverse_lazy("cfp:talk_list")

    def form_valid(self, form):
        messages.success(self.request, f"“{self.object}” deleted.")
        return super().form_valid(form)


class CheckTitleView(LoginRequiredMixin, UserFormKwargsMixin, FormView):
    """htmx: valida o título e devolve só o partial (template_name com #, Django 6.0)."""

    form_class = TalkForm
    template_name = "cfp/talk_form.html#title-feedback"
    http_method_names = ["post"]

    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
