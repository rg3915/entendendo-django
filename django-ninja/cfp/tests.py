from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .forms import GuestFormSet, SubscribeForm, TalkForm
from .models import Attachment, Event, Tag, Talk

ABSTRACT = "A practical tour of Django forms: what as_p renders, GET and POST, validation and formsets."


@override_settings(MEDIA_ROOT="/tmp/django_forms_test_media")
class FormsTests(TestCase):
    """Uma regra por teste: tudo que o vídeo afirma."""

    @classmethod
    def setUpTestData(cls):
        cls.regis = get_user_model().objects.create_user("regis", password="x")
        cls.open = Event.objects.create(name="Open", date=date(2026, 11, 19), city="Floripa", is_open=True)
        cls.closed = Event.objects.create(name="Closed", date=date(2026, 9, 24), city="POA", is_open=False)
        cls.tags = [Tag.objects.create(name="Django"), Tag.objects.create(name="Forms")]

    def data(self, **extra):
        d = {"event": self.open.pk, "title": "Forms", "abstract": ABSTRACT, "level": "beginner", "duration": 40}
        d.update(extra)
        return d

    def test_get_renders_unbound_form(self):
        response = self.client.get(reverse("cfp:subscribe"))
        self.assertFalse(response.context["form"].is_bound)

    def test_invalid_post_returns_200_with_aria_invalid(self):
        response = self.client.post(reverse("cfp:subscribe"), {"name": "", "email": "regis@"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'aria-invalid="true"')
        self.assertContains(response, 'value="regis@"')

    def test_valid_post_redirects(self):
        response = self.client.post(reverse("cfp:subscribe"), {"name": "Regis", "email": "regis@example.com"})
        self.assertRedirects(response, reverse("cfp:thanks"))

    def test_cleaned_data_has_empty_optional(self):
        form = SubscribeForm({"name": "Regis", "email": "regis@example.com"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["city"], "")

    def test_shouting_title(self):
        form = TalkForm(self.data(title="DJANGO FORMS"), user=self.regis)
        self.assertTrue(form.has_error("title", "shouting"))

    def test_duplicate_title(self):
        Talk.objects.create(submitted_by=self.regis, event=self.open, title="Forms", abstract=ABSTRACT, level="beginner", duration=40)
        form = TalkForm(self.data(), user=self.regis)
        self.assertTrue(form.has_error("title", "duplicate"))

    def test_advanced_short_is_non_field_error(self):
        form = TalkForm(self.data(level="advanced", duration=20), user=self.regis)
        self.assertTrue(form.has_error("__all__", "too_short"))

    def test_limit_of_three_per_user(self):
        for n in range(3):
            Talk.objects.create(submitted_by=self.regis, event=self.open, title=f"T{n}", abstract=ABSTRACT, level="beginner", duration=40)
        form = TalkForm(self.data(), user=self.regis)
        self.assertTrue(form.has_error("__all__", "limit"))

    def test_closed_event_is_refused(self):
        form = TalkForm(self.data(event=self.closed.pk), user=self.regis)
        self.assertTrue(form.has_error("event", "invalid_choice"))

    def test_commit_false_needs_save_m2m(self):
        form = TalkForm(self.data(tags=[t.pk for t in self.tags]), user=self.regis)
        self.assertTrue(form.is_valid())
        talk = form.save(commit=False)
        talk.save()
        self.assertEqual(talk.tags.count(), 0)
        form.save_m2m()
        self.assertEqual(talk.tags.count(), 2)

    def test_txt_slides_refused(self):
        txt = SimpleUploadedFile("notes.txt", b"hello")
        form = TalkForm(self.data(), {"slides": txt}, user=self.regis)
        self.assertTrue(form.has_error("slides", "invalid_extension"))

    def test_three_attachments_three_records(self):
        self.client.force_login(self.regis)
        files = [SimpleUploadedFile(f"f{n}.pdf", b"%PDF-1.4") for n in range(3)]
        data = self.data(**{"speakers-TOTAL_FORMS": 0, "speakers-INITIAL_FORMS": 0, "files": files})
        response = self.client.post(reverse("cfp:talk_new"), data)
        talk = Talk.objects.get()
        self.assertRedirects(response, reverse("cfp:talk_detail", args=[talk.pk]))
        self.assertEqual(Attachment.objects.filter(talk=talk).count(), 3)

    def test_formset_without_management_form_is_invalid(self):
        formset = GuestFormSet({})
        self.assertFalse(formset.is_valid())
        self.assertIn("ManagementForm data is missing", str(formset.non_form_errors()))

    def test_formset_ignores_blank_extra(self):
        data = {"form-TOTAL_FORMS": 2, "form-INITIAL_FORMS": 0, "form-0-name": "Bia", "form-0-email": "bia@example.com"}
        formset = GuestFormSet(data)
        self.assertTrue(formset.is_valid())
        self.assertFalse(formset.forms[1].has_changed())

    def test_check_title_returns_only_the_partial(self):
        Talk.objects.create(submitted_by=self.regis, event=self.open, title="Forms", abstract=ABSTRACT, level="beginner", duration=40)
        self.client.force_login(self.regis)
        response = self.client.post(reverse("cfp:check_title"), {"title": "Forms", "event": self.open.pk})
        self.assertContains(response, "already submitted")
        self.assertNotContains(response, "<html")
