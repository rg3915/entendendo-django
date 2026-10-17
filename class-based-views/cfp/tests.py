import io
from contextlib import redirect_stdout
from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Event, Talk
from .views import TalkUpdateView

ABSTRACT = "A practical tour of Django: forms, class-based views and the flow behind them, with real code."


class CBVTests(TestCase):
    """Uma regra por teste: tudo que o vídeo afirma sobre as CBVs."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.regis = User.objects.create_user("regis", password="x")
        cls.bruno = User.objects.create_user("bruno", password="x")
        cls.event = Event.objects.create(name="Open", date=date(2026, 11, 19), city="Floripa", is_open=True)
        cls.other = Event.objects.create(name="Open 2", date=date(2026, 12, 10), city="Curitiba", is_open=True)
        for k in range(4):
            Talk.objects.create(submitted_by=cls.regis, event=cls.event if k < 3 else cls.other, title=f"Talk {k}",
                                abstract=ABSTRACT, level="beginner", duration=40)
        cls.alheia = Talk.objects.create(submitted_by=cls.bruno, event=cls.event, title="Bruno's", abstract=ABSTRACT,
                                         level="beginner", duration=40)

    def setUp(self):
        self.client.force_login(self.regis)

    def data(self, **extra):
        return {"event": self.other.pk, "title": "New talk", "abstract": ABSTRACT, "level": "beginner", "duration": 40, **extra}

    def test_list_only_mine_and_paginated(self):
        r = self.client.get(reverse("cfp:talk_list"))
        self.assertEqual(r.template_name, ["cfp/talk_list.html"])
        self.assertEqual(len(r.context["talks"]), 3)
        self.assertEqual(r.context["paginator"].count, 4)
        self.assertNotContains(r, "Bruno's")

    def test_detail_of_someone_else_is_404(self):
        self.assertEqual(self.client.get(self.alheia.get_absolute_url()).status_code, 404)

    def test_create_goes_to_get_absolute_url(self):
        r = self.client.post(reverse("cfp:talk_new"), self.data())
        talk = Talk.objects.get(title="New talk")
        self.assertRedirects(r, talk.get_absolute_url())
        self.assertEqual(talk.submitted_by, self.regis)

    def test_invalid_post_renders_form_again(self):
        r = self.client.post(reverse("cfp:talk_new"), self.data(title=""))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context["form"].errors)

    def test_update_someone_else_is_404(self):
        self.assertEqual(self.client.get(reverse("cfp:talk_edit", args=[self.alheia.pk])).status_code, 404)

    def test_delete_confirms_on_get_and_deletes_on_post(self):
        talk = Talk.objects.get(title="Talk 0")
        self.assertContains(self.client.get(reverse("cfp:talk_delete", args=[talk.pk])), "Yes, delete it")
        self.assertRedirects(self.client.post(reverse("cfp:talk_delete", args=[talk.pk])), reverse("cfp:talk_list"))
        self.assertFalse(Talk.objects.filter(pk=talk.pk).exists())

    def test_ping_405_with_allow_header(self):
        r = self.client.post(reverse("cfp:ping"))
        self.assertEqual((r.status_code, r["Allow"]), (405, "GET, HEAD, OPTIONS"))

    def test_redirect_view_302_and_preserve_request_307(self):
        self.assertEqual(self.client.get(reverse("cfp:old_talks")).status_code, 302)
        self.assertEqual(self.client.post(reverse("cfp:old_submit")).status_code, 307)

    def test_check_title_returns_only_the_partial(self):
        r = self.client.post(reverse("cfp:check_title"), {"title": "Talk 0", "event": self.event.pk})
        self.assertContains(r, "already submitted")
        self.assertNotContains(r, "<html")

    def test_check_title_refuses_get(self):
        self.assertEqual(self.client.get(reverse("cfp:check_title")).status_code, 405)

    def test_login_required_mixin_comes_first(self):
        self.assertIs(TalkUpdateView.__mro__[1], LoginRequiredMixin)
        self.client.logout()
        self.assertRedirects(self.client.get(reverse("cfp:talk_list")), "/accounts/login/?next=/talks/")

    def test_trace_prints_the_flow(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.client.get(reverse("cfp:talk_new_traced"))
        flow = out.getvalue()
        self.assertLess(flow.index("dispatch"), flow.index("get()"))
        # no GET o form nasce dentro do get_context_data
        self.assertLess(flow.index("get_context_data"), flow.index("get_form_kwargs"))


@override_settings(MIDDLEWARE=[*settings.MIDDLEWARE, "django.contrib.auth.middleware.LoginRequiredMiddleware"])
class LoginRequiredMiddlewareTests(TestCase):
    """Django 5.1: tudo fechado por padrão; login_not_required abre a porta."""

    def test_everything_is_private_by_default(self):
        self.assertRedirects(self.client.get("/ping/"), "/accounts/login/?next=/ping/")

    def test_login_not_required_opens_the_home(self):
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_login_page_is_open(self):
        self.assertEqual(self.client.get("/accounts/login/").status_code, 200)
