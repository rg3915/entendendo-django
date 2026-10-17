"""Testes da API com o APIClient do DRF: sem servidor rodando."""
from datetime import date

from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase

from .models import ApiKey, Event, Tag, Talk

ABSTRACT = "A practical tour of Django REST framework: serializers, viewsets, auth, pagination, filters and tests."


class TalkApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.regis = User.objects.create_user("regis", password="x")
        cls.bruno = User.objects.create_user("bruno", password="x")
        ApiKey.objects.create(user=cls.regis, key="key-regis")
        cls.event = Event.objects.create(name="Noite #12", date=date(2026, 11, 19), city="Floripa")
        cls.tag = Tag.objects.create(name="Django")
        cls.talk = Talk.objects.create(event=cls.event, submitted_by=cls.bruno, title="DRF na prática", abstract=ABSTRACT)

    def payload(self, **extra):
        return {"title": "APIs com DRF", "abstract": ABSTRACT, "event_id": self.event.id, "tag_ids": [self.tag.id]} | extra

    def test_list_is_paginated(self):
        r = self.client.get("/drf/talks/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(r.data["results"][0]["speaker"], "bruno")

    def test_create_requires_auth(self):
        self.assertEqual(self.client.post("/drf/talks/", self.payload(), format="json").status_code, 401)

    def test_create_with_api_key(self):
        r = self.client.post("/drf/talks/", self.payload(), format="json", headers={"X-API-Key": "key-regis"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["speaker"], "regis")
        self.assertEqual(r.data["tags"], ["Django"])

    def test_invalid_payload_is_400(self):
        r = self.client.post(
            "/drf/talks/", self.payload(title="SHOUTING", abstract="short"), format="json", headers={"X-API-Key": "key-regis"}
        )
        self.assertEqual(r.status_code, 400)
        self.assertEqual(set(r.data), {"title", "abstract"})

    def test_patch_only_sent_fields(self):
        mine = Talk.objects.create(event=self.event, submitted_by=self.regis, title="Old", abstract=ABSTRACT, duration=40)
        r = self.client.patch(f"/drf/talks/{mine.id}/", {"title": "New"}, format="json", headers={"X-API-Key": "key-regis"})
        self.assertEqual(r.status_code, 200)
        mine.refresh_from_db()
        self.assertEqual((mine.title, mine.duration), ("New", 40))

    def test_patch_someone_elses_talk_is_403(self):
        r = self.client.patch(f"/drf/talks/{self.talk.id}/", {"title": "Mine now"}, format="json", headers={"X-API-Key": "key-regis"})
        self.assertEqual(r.status_code, 403)

    def test_me_uses_the_session(self):
        self.client.force_login(self.regis)
        self.assertEqual(self.client.get("/drf/me/").data, {"username": "regis"})

    def test_filter_by_title(self):
        r = self.client.get("/drf/talks/", {"q": "prática"})
        self.assertEqual([t["title"] for t in r.data["results"]], ["DRF na prática"])

    def test_stats_is_throttled(self):
        cache.clear()
        codes = [self.client.get("/drf/stats/").status_code for _ in range(4)]
        self.assertEqual(codes, [200, 200, 200, 429])
