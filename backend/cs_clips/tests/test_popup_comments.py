"""Test per l'endpoint GET /api/videos/{id}/popup-comments/."""

from rest_framework import status
from rest_framework.test import APITestCase

from cs_clips.models import Comment, CommentLike
from cs_clips.tests.conftest import (
    create_api_client_authenticated,
    create_authenticated_user,
    create_sample_video,
)


class PopupCommentsTests(APITestCase):
    """Test endpoint popup-comments su VideoViewSet."""

    def setUp(self):
        self.user = create_authenticated_user(username="author")
        self.liker = create_authenticated_user(username="liker")
        self.client_auth = create_api_client_authenticated(self.user)
        self.video = create_sample_video(self.user, title="Popup Video")
        self.url = f"/api/videos/{self.video.id}/popup-comments/"

    # --- Helper ---
    def _create_comment(self, timestamp=5, content="test", user=None, disabled=False):
        return Comment.objects.create(
            user=user or self.user,
            video=self.video,
            content=content,
            timestamp_second=timestamp,
            is_disabled=disabled,
        )

    def _like_comment(self, comment, user=None):
        CommentLike.objects.create(user=user or self.liker, comment=comment)

    # --- Test ---
    def test_empty_when_no_liked_comments(self):
        """Nessun commento con like → lista vuota."""
        self._create_comment(timestamp=5, content="no like")
        resp = self.client_auth.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

    def test_threshold_one_like(self):
        """Commento con 1 like appare, commento con 0 like no."""
        c_liked = self._create_comment(timestamp=5, content="liked")
        self._create_comment(timestamp=10, content="not liked")
        self._like_comment(c_liked)

        resp = self.client_auth.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["id"], c_liked.id)
        self.assertEqual(resp.data[0]["content"], "liked")
        self.assertGreaterEqual(resp.data[0]["like_count"], 1)

    def test_disabled_comment_excluded(self):
        """Commento disabilitato con like non appare."""
        c_disabled = self._create_comment(
            timestamp=5, content="disabled", disabled=True
        )
        self._like_comment(c_disabled)

        resp = self.client_auth.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

    def test_top_liked_per_timestamp(self):
        """Per stesso timestamp, ritorna il commento con più like."""
        c1 = self._create_comment(timestamp=5, content="few likes")
        c2 = self._create_comment(timestamp=5, content="many likes")

        # c1: 1 like
        self._like_comment(c1, user=self.liker)
        # c2: 2 like
        liker2 = create_authenticated_user(username="liker2")
        self._like_comment(c2, user=self.liker)
        self._like_comment(c2, user=liker2)

        resp = self.client_auth.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["id"], c2.id)
        self.assertEqual(resp.data[0]["content"], "many likes")

    def test_ordered_by_timestamp(self):
        """I popup sono ordinati per timestamp crescente."""
        c10 = self._create_comment(timestamp=10, content="at 10s")
        c3 = self._create_comment(timestamp=3, content="at 3s")
        c20 = self._create_comment(timestamp=20, content="at 20s")
        self._like_comment(c10)
        self._like_comment(c3)
        self._like_comment(c20)

        resp = self.client_auth.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 3)
        timestamps = [c["timestamp_second"] for c in resp.data]
        self.assertEqual(timestamps, [3, 10, 20])

    def test_timestamp_zero_excluded(self):
        """Commenti con timestamp_second=0 (generici) non diventano popup."""
        c_generic = self._create_comment(timestamp=0, content="generic")
        self._like_comment(c_generic)

        resp = self.client_auth.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

    def test_not_paginated(self):
        """La risposta è una lista piatta, non paginata."""
        c = self._create_comment(timestamp=5)
        self._like_comment(c)

        resp = self.client_auth.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)
        # Non deve avere struttura paginata
        self.assertNotIn("results", resp.data if isinstance(resp.data, dict) else {})

    def test_is_liked_by_me_annotation(self):
        """Il campo is_liked_by_me è annotato correttamente per l'utente."""
        c = self._create_comment(timestamp=5)
        self._like_comment(c, user=self.user)

        resp = self.client_auth.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertTrue(resp.data[0]["is_liked_by_me"])

    def test_nonexistent_video_returns_404(self):
        """Popup-comments per video inesistente → 404."""
        resp = self.client_auth.get("/api/videos/99999/popup-comments/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
