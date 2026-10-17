from django.contrib.auth.models import Group, Permission, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Talk


class PermissionTests(TestCase):
    """Quem pode fazer o quê na chamada de palestras."""

    @classmethod
    def setUpTestData(cls):
        call_command("seed", verbosity=0)
        cls.regis = User.objects.get(username="regis")
        cls.bruno = User.objects.get(username="bruno")
        cls.talk = Talk.objects.get(title="Django Forms na prática")
        cls.other = Talk.objects.get(title="Testes que dão sono")

    def test_speaker_cannot_open_review_queue(self):
        self.client.force_login(self.regis)
        self.assertEqual(self.client.get(reverse("cfp:review_list")).status_code, 403)

    def test_organizer_opens_review_queue(self):
        self.client.force_login(self.bruno)
        self.assertEqual(self.client.get(reverse("cfp:review_list")).status_code, 200)

    def test_owner_edits_own_talk(self):
        self.assertTrue(self.regis.has_perm("cfp.change_talk", self.talk))
        self.assertFalse(self.bruno.has_perm("cfp.change_talk", self.talk))

    def test_organizer_approves_only_own_event(self):
        self.assertTrue(self.bruno.has_perm("cfp.approve_talk", self.talk))
        self.assertFalse(self.bruno.has_perm("cfp.approve_talk", self.other))
        self.client.force_login(self.bruno)
        self.assertEqual(self.client.get(reverse("cfp:talk_approve", args=[self.other.pk])).status_code, 403)

    def test_permission_cache_needs_refetch(self):
        caio = User.objects.get(username="caio")
        self.assertFalse(caio.has_perm("cfp.approve_talk"))
        caio.groups.add(Group.objects.get(name="Organizers"))
        self.assertFalse(caio.has_perm("cfp.approve_talk"))      # cache antigo
        caio = User.objects.get(pk=caio.pk)
        self.assertTrue(caio.has_perm("cfp.approve_talk"))

    def test_inactive_superuser_has_nothing(self):
        admin = User.objects.get(username="admin")
        self.assertTrue(admin.has_perm("cfp.anything_at_all"))
        admin.is_active = False
        self.assertFalse(admin.has_perm("cfp.approve_talk"))

    def test_user_perm_str(self):
        perm = Permission.objects.get(codename="approve_talk")
        self.assertEqual(perm.user_perm_str, "cfp.approve_talk")
