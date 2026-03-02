"""Test per endpoint commenti (Story 2.4).

Copre: AC-1 (commento con/senza timestamp), AC-3 (eliminazione commento),
AC-4 (filtro per video), AC-5 (permessi toconfirm), AC-6 (non-regressione).
"""

import shutil
import tempfile

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from cs_clips.models import Comment
from cs_clips.tests.conftest import (
    create_api_client_authenticated,
    create_authenticated_user,
    create_sample_video,
    create_toconfirm_user,
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
    MINIO_STORAGE_MEDIA_BUCKET_NAME="test-bucket",
)
class TestCommentCreate(APITestCase):
    """Test creazione commenti con e senza timestamp (AC-1)."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = create_authenticated_user("commenter")
        self.client_auth = create_api_client_authenticated(self.user)
        self.video = create_sample_video(self.user, title="Video Test")
        self.url = "/api/comments/"

    def test_create_comment_with_valid_timestamp(self):
        """Commento con timestamp valido → 201 + timestamp_second salvato."""
        data = {
            "video": self.video.id,
            "content": "Bel momento!",
            "timestamp_second": 15,
        }
        response = self.client_auth.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["timestamp_second"], 15)
        self.assertEqual(response.data["content"], "Bel momento!")
        self.assertEqual(response.data["user"], "commenter")

    def test_create_comment_without_timestamp(self):
        """Commento senza timestamp (default 0) → 201 + commento normale."""
        data = {
            "video": self.video.id,
            "content": "Bel video!",
        }
        response = self.client_auth.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["timestamp_second"], 0)

    def test_create_comment_with_timestamp_zero(self):
        """Commento con timestamp_second=0 → 201 + commento normale."""
        data = {
            "video": self.video.id,
            "content": "Commento generico",
            "timestamp_second": 0,
        }
        response = self.client_auth.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["timestamp_second"], 0)

    def test_create_comment_timestamp_exceeds_duration(self):
        """Commento con timestamp > durata video → 400 + messaggio errore."""
        data = {
            "video": self.video.id,
            "content": "Troppo avanti",
            "timestamp_second": 999,
        }
        response = self.client_auth.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "ValidationError")
        self.assertIn("timestamp_second", response.data["detail"])
        self.assertIn("durata", response.data["detail"].lower())

    def test_create_comment_timestamp_at_duration(self):
        """Commento con timestamp = durata video (30s) → 201."""
        data = {
            "video": self.video.id,
            "content": "Alla fine!",
            "timestamp_second": 30,
        }
        response = self.client_auth.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["timestamp_second"], 30)


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
    MINIO_STORAGE_MEDIA_BUCKET_NAME="test-bucket",
)
class TestCommentFilter(APITestCase):
    """Test filtro commenti per video (AC-4)."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = create_authenticated_user("viewer")
        self.client_auth = create_api_client_authenticated(self.user)
        self.video_a = create_sample_video(self.user, title="Video A")
        self.video_b = create_sample_video(self.user, title="Video B")
        self.url = "/api/comments/"

        # Crea commenti per video A
        for i in range(3):
            Comment.objects.create(
                user=self.user,
                video=self.video_a,
                content=f"Commento A-{i}",
            )
        # Crea commenti per video B
        for i in range(2):
            Comment.objects.create(
                user=self.user,
                video=self.video_b,
                content=f"Commento B-{i}",
            )

    def test_filter_by_video_id(self):
        """GET /api/comments/?video={id} → solo commenti del video specificato."""
        response = self.client_auth.get(self.url, {"video": self.video_a.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        for comment in response.data["results"]:
            self.assertEqual(comment["video"], self.video_a.id)

    def test_filter_by_other_video(self):
        """GET /api/comments/?video={id} per video B → solo 2 commenti."""
        response = self.client_auth.get(self.url, {"video": self.video_b.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_no_filter_returns_all(self):
        """GET /api/comments/ senza filtro → tutti i commenti non disabilitati."""
        response = self.client_auth.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)

    def test_paginated_response_format(self):
        """Risposta paginata con count, next, previous, results."""
        response = self.client_auth.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
    MINIO_STORAGE_MEDIA_BUCKET_NAME="test-bucket",
)
class TestCommentDelete(APITestCase):
    """Test eliminazione commento (AC-3)."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.owner = create_authenticated_user("owner")
        self.other_user = create_authenticated_user("other")
        self.video = create_sample_video(self.owner, title="Video Delete")

        self.comment = Comment.objects.create(
            user=self.owner,
            video=self.video,
            content="Commento da eliminare",
        )

    def test_delete_own_comment(self):
        """Autore elimina il proprio commento → 204 No Content."""
        client = create_api_client_authenticated(self.owner)
        url = f"/api/comments/{self.comment.id}/"
        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_other_user_comment(self):
        """Non-autore tenta eliminazione → 403 Forbidden."""
        client = create_api_client_authenticated(self.other_user)
        url = f"/api/comments/{self.comment.id}/"
        response = client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())

    def test_update_comment_not_allowed(self):
        """PUT/PATCH non consentiti sui commenti → 405 Method Not Allowed."""
        client = create_api_client_authenticated(self.owner)
        url = f"/api/comments/{self.comment.id}/"

        response_put = client.put(url, {"content": "Modificato"}, format="json")
        self.assertEqual(response_put.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response_patch = client.patch(url, {"content": "Modificato"}, format="json")
        self.assertEqual(response_patch.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
    MINIO_STORAGE_MEDIA_BUCKET_NAME="test-bucket",
)
class TestCommentAuth(APITestCase):
    """Test autenticazione e permessi commenti (AC-5)."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = create_authenticated_user("authuser")
        self.video = create_sample_video(self.user, title="Video Auth")
        Comment.objects.create(
            user=self.user,
            video=self.video,
            content="Commento esistente",
        )
        self.url = "/api/comments/"

    def test_unauthenticated_post(self):
        """Utente non autenticato → 401 su POST."""
        data = {
            "video": self.video.id,
            "content": "Non autorizzato",
        }
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_delete(self):
        """Utente non autenticato → 401 su DELETE."""
        comment = Comment.objects.first()
        response = self.client.delete(f"/api/comments/{comment.id}/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_toconfirm_can_read(self):
        """Utente toconfirm può leggere commenti (GET) → 200."""
        tc_user = create_toconfirm_user("pending")
        client = create_api_client_authenticated(tc_user)
        response = client.get(self.url, {"video": self.video.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_toconfirm_cannot_create(self):
        """Utente toconfirm non può creare commenti (POST) → 403."""
        tc_user = create_toconfirm_user("pending2")
        client = create_api_client_authenticated(tc_user)
        data = {
            "video": self.video.id,
            "content": "Non dovrei poter commentare",
        }
        response = client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
    MINIO_STORAGE_MEDIA_BUCKET_NAME="test-bucket",
)
class TestCommentDisabled(APITestCase):
    """Test filtro commenti disabilitati."""

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = create_authenticated_user("disabletest")
        self.client_auth = create_api_client_authenticated(self.user)
        self.video = create_sample_video(self.user, title="Video Disabled")

        Comment.objects.create(
            user=self.user,
            video=self.video,
            content="Visibile",
        )
        Comment.objects.create(
            user=self.user,
            video=self.video,
            content="Nascosto",
            is_disabled=True,
        )

    def test_disabled_comments_not_in_list(self):
        """Commenti con is_disabled=True non appaiono nella lista."""
        response = self.client_auth.get("/api/comments/", {"video": self.video.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["content"], "Visibile")
