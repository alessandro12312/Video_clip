"""Test aggiornamento rating e annotazione my_rating.

AC-3, AC-4, AC-5 della Story 2.5.
"""

from django.test import TestCase
from rest_framework.test import APIClient

from cs_clips.models import Rating
from cs_clips.tests.conftest import (
    create_api_client_authenticated,
    create_authenticated_user,
    create_sample_video,
)


class TestRatingPatch(TestCase):
    """PATCH value → 200, valore aggiornato."""

    def setUp(self):
        self.owner = create_authenticated_user(username="owner")
        self.rater = create_authenticated_user(username="rater")
        self.client = create_api_client_authenticated(self.rater)
        self.video = create_sample_video(uploader=self.owner)
        self.rating = Rating.objects.create(user=self.rater, video=self.video, value=3)

    def test_patch_updates_value(self):
        response = self.client.patch(
            f"/api/ratings/{self.rating.id}/",
            {"value": 5},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.rating.refresh_from_db()
        self.assertEqual(self.rating.value, 5)

    def test_patch_response_contains_updated_value(self):
        response = self.client.patch(
            f"/api/ratings/{self.rating.id}/",
            {"value": 1},
            format="json",
        )
        self.assertEqual(response.data["value"], 1)

    def test_patch_does_not_change_video_fk(self):
        """RatingUpdateSerializer espone solo 'value', video FK non è modificabile."""
        other_video = create_sample_video(uploader=self.owner, title="Altro Video")
        response = self.client.patch(
            f"/api/ratings/{self.rating.id}/",
            {"value": 4, "video": other_video.id},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.rating.refresh_from_db()
        self.assertEqual(self.rating.video_id, self.video.id)


class TestRatingPatchNonOwner(TestCase):
    """PATCH rating altrui → 403."""

    def setUp(self):
        self.owner = create_authenticated_user(username="owner")
        self.rater = create_authenticated_user(username="rater")
        self.other = create_authenticated_user(username="other")
        self.video = create_sample_video(uploader=self.owner)
        self.rating = Rating.objects.create(user=self.rater, video=self.video, value=3)
        self.client = create_api_client_authenticated(self.other)

    def test_non_owner_patch_returns_403(self):
        response = self.client.patch(
            f"/api/ratings/{self.rating.id}/",
            {"value": 5},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_non_owner_patch_preserves_original_value(self):
        self.client.patch(
            f"/api/ratings/{self.rating.id}/",
            {"value": 5},
            format="json",
        )
        self.rating.refresh_from_db()
        self.assertEqual(self.rating.value, 3)


class TestRatingMethodRestriction(TestCase):
    """PUT → 405, DELETE → 405."""

    def setUp(self):
        self.owner = create_authenticated_user(username="owner")
        self.rater = create_authenticated_user(username="rater")
        self.client = create_api_client_authenticated(self.rater)
        self.video = create_sample_video(uploader=self.owner)
        self.rating = Rating.objects.create(user=self.rater, video=self.video, value=3)

    def test_put_returns_405(self):
        response = self.client.put(
            f"/api/ratings/{self.rating.id}/",
            {"value": 5, "video": self.video.id},
            format="json",
        )
        self.assertEqual(response.status_code, 405)

    def test_delete_returns_405(self):
        response = self.client.delete(f"/api/ratings/{self.rating.id}/")
        self.assertEqual(response.status_code, 405)


class TestRatingPatchValidation(TestCase):
    """PATCH con valore fuori range (0, 6) → 400."""

    def setUp(self):
        self.owner = create_authenticated_user(username="owner")
        self.rater = create_authenticated_user(username="rater")
        self.client = create_api_client_authenticated(self.rater)
        self.video = create_sample_video(uploader=self.owner)
        self.rating = Rating.objects.create(user=self.rater, video=self.video, value=3)

    def test_patch_value_zero_returns_400(self):
        response = self.client.patch(
            f"/api/ratings/{self.rating.id}/",
            {"value": 0},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_patch_value_six_returns_400(self):
        response = self.client.patch(
            f"/api/ratings/{self.rating.id}/",
            {"value": 6},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_patch_value_negative_returns_400(self):
        response = self.client.patch(
            f"/api/ratings/{self.rating.id}/",
            {"value": -1},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_original_value_preserved_on_invalid_patch(self):
        self.client.patch(
            f"/api/ratings/{self.rating.id}/",
            {"value": 6},
            format="json",
        )
        self.rating.refresh_from_db()
        self.assertEqual(self.rating.value, 3)


class TestRatingPatchUnauthenticated(TestCase):
    """PATCH rating da utente non autenticato → 401."""

    def setUp(self):
        self.owner = create_authenticated_user(username="owner")
        self.rater = create_authenticated_user(username="rater")
        self.video = create_sample_video(uploader=self.owner)
        self.rating = Rating.objects.create(user=self.rater, video=self.video, value=3)
        self.client = APIClient()  # Non autenticato

    def test_unauthenticated_patch_returns_401(self):
        response = self.client.patch(
            f"/api/ratings/{self.rating.id}/",
            {"value": 5},
            format="json",
        )
        self.assertEqual(response.status_code, 401)


class TestMyRatingAnnotation(TestCase):
    """GET video include my_rating_id e my_rating_value corretti."""

    def setUp(self):
        self.owner = create_authenticated_user(username="owner")
        self.rater = create_authenticated_user(username="rater")
        self.video = create_sample_video(uploader=self.owner)

    def test_authenticated_with_rating(self):
        """Utente autenticato che ha votato → my_rating presenti."""
        rating = Rating.objects.create(user=self.rater, video=self.video, value=4)
        client = create_api_client_authenticated(self.rater)
        response = client.get(f"/api/videos/{self.video.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["my_rating_id"], rating.id)
        self.assertEqual(response.data["my_rating_value"], 4)

    def test_authenticated_without_rating(self):
        """Utente autenticato che NON ha votato → my_rating null."""
        client = create_api_client_authenticated(self.rater)
        response = client.get(f"/api/videos/{self.video.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["my_rating_id"])
        self.assertIsNone(response.data["my_rating_value"])

    def test_unauthenticated(self):
        """Utente non autenticato → my_rating null (retrieve è pubblico)."""
        client = APIClient()
        response = client.get(f"/api/videos/{self.video.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["my_rating_id"])
        self.assertIsNone(response.data["my_rating_value"])

    def test_my_rating_in_top_rated_action(self):
        """my_rating presente anche nell'action top-rated (usa get_queryset)."""
        Rating.objects.create(user=self.rater, video=self.video, value=5)
        client = create_api_client_authenticated(self.rater)
        response = client.get("/api/videos/top-rated/")
        self.assertEqual(response.status_code, 200)
        results = response.data["results"]
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["my_rating_value"], 5)

    def test_my_rating_in_list(self):
        """my_rating presente nella list dei video."""
        Rating.objects.create(user=self.rater, video=self.video, value=3)
        client = create_api_client_authenticated(self.rater)
        response = client.get("/api/videos/")
        self.assertEqual(response.status_code, 200)
        results = response.data["results"]
        self.assertTrue(len(results) > 0)
        video_data = next(v for v in results if v["id"] == self.video.id)
        self.assertEqual(video_data["my_rating_value"], 3)
