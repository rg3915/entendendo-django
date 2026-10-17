"""Testes da API com o TestClient do Django Ninja: sem servidor rodando."""
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from ninja.testing import TestClient

from .api import api
from .models import ApiKey, Event, Tag, Talk

ABSTRACT = "A practical tour of Django Ninja: schemas, routers, auth, pagination, filters and tests."


class TalkApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.regis = User.objects.create_user("regis", password="x")
        cls.bruno = User.objects.create_user("bruno", password="x")
        ApiKey.objects.create(user=cls.regis, key="key-regis")
        cls.event = Event.objects.create(name="Noite #12", date=date(2026, 11, 19), city="Floripa")
        cls.tag = Tag.objects.create(name="Django")
        cls.talk = Talk.objects.create(event=cls.event, submitted_by=cls.bruno, title="Ninja na prática", abstract=ABSTRACT)

    def setUp(self):
        self.client = TestClient(api)

    def payload(self, **extra):
        return {"title": "APIs com Ninja", "abstract": ABSTRACT, "event_id": self.event.id, "tags": [self.tag.id]} | extra

    def test_list_is_paginated(self):
        r = self.client.get("/talks/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["count"], 1)
        self.assertEqual(r.json()["items"][0]["speaker"], "bruno")

    def test_create_requires_auth(self):
        self.assertEqual(self.client.post("/talks/", json=self.payload()).status_code, 401)

    def test_create_with_api_key(self):
        r = self.client.post("/talks/", json=self.payload(), headers={"X-API-Key": "key-regis"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["speaker"], "regis")
        self.assertEqual(r.json()["tags"], ["Django"])

    def test_invalid_payload_is_422(self):
        r = self.client.post("/talks/", json=self.payload(title="SHOUTING", abstract="short"), headers={"X-API-Key": "key-regis"})
        self.assertEqual(r.status_code, 422)
        self.assertEqual({e["loc"][-1] for e in r.json()["detail"]}, {"title", "abstract"})

    def test_patch_only_sent_fields(self):
        mine = Talk.objects.create(event=self.event, submitted_by=self.regis, title="Old", abstract=ABSTRACT, duration=40)
        r = self.client.patch(f"/talks/{mine.id}", json={"title": "New"}, headers={"X-API-Key": "key-regis"})
        self.assertEqual(r.status_code, 200)
        mine.refresh_from_db()
        self.assertEqual((mine.title, mine.duration), ("New", 40))

    def test_patch_someone_elses_talk_is_403(self):
        r = self.client.patch(f"/talks/{self.talk.id}", json={"title": "Mine now"}, headers={"X-API-Key": "key-regis"})
        self.assertEqual(r.status_code, 403)

    def test_me_uses_django_session(self):
        self.assertEqual(self.client.get("/me").status_code, 401)
        self.assertEqual(self.client.get("/me", user=self.regis).json(), {"username": "regis"})

    def test_filter_by_title(self):
        self.assertEqual(self.client.get("/talks/", query_params={"q": "ninja"}).json()["count"], 1)
        self.assertEqual(self.client.get("/talks/", query_params={"q": "celery"}).json()["count"], 0)
