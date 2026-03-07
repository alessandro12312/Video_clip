"""Test eliminazione video — AC-1 e AC-2 della Story 2.5."""

from django.test import TestCase
from rest_framework.test import APIClient

from cs_clips.models import Comment, Rating, Video
from cs_clips.tests.conftest import (
    create_api_client_authenticated,
    create_authenticated_user,
    create_sample_video,
    create_toconfirm_user,
)


class TestVideoDeleteOwner(TestCase):
    """Proprietario elimina il proprio video → 204, video non esiste più in DB."""

    def setUp(self):
        self.user = create_authenticated_user(username="owner")
        self.client = create_api_client_authenticated(self.user)
        self.video = create_sample_video(uploader=self.user)

    def test_owner_delete_returns_204(self):
        response = self.client.delete(f"/api/videos/{self.video.id}/")
        self.assertEqual(response.status_code, 204)

    def test_owner_delete_removes_video_from_db(self):
        self.client.delete(f"/api/videos/{self.video.id}/")
        self.assertFalse(Video.objects.filter(id=self.video.id).exists())

    def test_owner_delete_twice_returns_404(self):
        self.client.delete(f"/api/videos/{self.video.id}/")
        response = self.client.delete(f"/api/videos/{self.video.id}/")
        self.assertEqual(response.status_code, 404)


class TestVideoDeleteCascade(TestCase):
    """Commenti e rating associati vengono eliminati a cascata."""

    def setUp(self):
        self.owner = create_authenticated_user(username="owner")
        self.other = create_authenticated_user(username="rater")
        self.client = create_api_client_authenticated(self.owner)
        self.video = create_sample_video(uploader=self.owner)

        # Crea rating e commento associati al video
        self.rating = Rating.objects.create(user=self.other, video=self.video, value=4)
        self.comment = Comment.objects.create(
            user=self.other,
            video=self.video,
            content="Bel video!",
            timestamp_second=5,
        )

    def test_delete_cascades_ratings(self):
        self.client.delete(f"/api/videos/{self.video.id}/")
        self.assertFalse(Rating.objects.filter(id=self.rating.id).exists())

    def test_delete_cascades_comments(self):
        self.client.delete(f"/api/videos/{self.video.id}/")
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())


class TestVideoDeleteNonOwner(TestCase):
    """Non-proprietario tenta di eliminare un video → 403."""

    def setUp(self):
        self.owner = create_authenticated_user(username="owner")
        self.other = create_authenticated_user(username="other")
        self.client = create_api_client_authenticated(self.other)
        self.video = create_sample_video(uploader=self.owner)

    def test_non_owner_delete_returns_403(self):
        response = self.client.delete(f"/api/videos/{self.video.id}/")
        self.assertEqual(response.status_code, 403)

    def test_non_owner_delete_preserves_video(self):
        self.client.delete(f"/api/videos/{self.video.id}/")
        self.assertTrue(Video.objects.filter(id=self.video.id).exists())


class TestVideoDeleteToconfirm(TestCase):
    """Utente toconfirm non può eliminare video → 403."""

    def setUp(self):
        self.owner = create_authenticated_user(username="owner")
        self.toconfirm = create_toconfirm_user(username="pending")
        self.client = create_api_client_authenticated(self.toconfirm)
        self.video = create_sample_video(uploader=self.owner)

    def test_toconfirm_delete_returns_403(self):
        response = self.client.delete(f"/api/videos/{self.video.id}/")
        self.assertEqual(response.status_code, 403)


class TestVideoDeleteUnauthenticated(TestCase):
    """Utente non autenticato non può eliminare video → 401."""

    def setUp(self):
        self.owner = create_authenticated_user(username="owner")
        self.video = create_sample_video(uploader=self.owner)
        self.client = APIClient()  # Non autenticato

    def test_unauthenticated_delete_returns_401(self):
        response = self.client.delete(f"/api/videos/{self.video.id}/")
        self.assertEqual(response.status_code, 401)
