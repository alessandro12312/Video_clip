"""Test per VideoLike e CommentLike — modelli, endpoint, annotazioni."""

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from cs_clips.models import Comment, CommentLike, VideoLike
from cs_clips.tests.conftest import (
    create_api_client_authenticated,
    create_authenticated_user,
    create_sample_video,
    create_toconfirm_user,
)


class VideoLikeModelTest(TestCase):
    """Test sul modello VideoLike."""

    def setUp(self):
        self.user = create_authenticated_user()
        self.video = create_sample_video(self.user)

    def test_create_video_like(self):
        """Creazione di un VideoLike."""
        like = VideoLike.objects.create(user=self.user, video=self.video)
        self.assertEqual(like.user, self.user)
        self.assertEqual(like.video, self.video)
        self.assertIsNotNone(like.created_at)

    def test_unique_together_video_like(self):
        """unique_together impedisce like duplicato."""
        VideoLike.objects.create(user=self.user, video=self.video)
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            VideoLike.objects.create(user=self.user, video=self.video)

    def test_cascade_delete_video(self):
        """Eliminazione video rimuove i like associati."""
        VideoLike.objects.create(user=self.user, video=self.video)
        self.video.delete()
        self.assertEqual(VideoLike.objects.count(), 0)


class CommentLikeModelTest(TestCase):
    """Test sul modello CommentLike."""

    def setUp(self):
        self.user = create_authenticated_user()
        self.video = create_sample_video(self.user)
        self.comment = Comment.objects.create(
            user=self.user, video=self.video, content="Test comment", timestamp_second=0
        )

    def test_create_comment_like(self):
        """Creazione di un CommentLike."""
        like = CommentLike.objects.create(user=self.user, comment=self.comment)
        self.assertEqual(like.user, self.user)
        self.assertEqual(like.comment, self.comment)

    def test_unique_together_comment_like(self):
        """unique_together impedisce like duplicato."""
        CommentLike.objects.create(user=self.user, comment=self.comment)
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            CommentLike.objects.create(user=self.user, comment=self.comment)

    def test_cascade_delete_comment(self):
        """Eliminazione commento rimuove i like associati."""
        CommentLike.objects.create(user=self.user, comment=self.comment)
        self.comment.delete()
        self.assertEqual(CommentLike.objects.count(), 0)


class VideoLikeEndpointTest(APITestCase):
    """Test endpoint POST/DELETE /api/videos/{id}/like/."""

    def setUp(self):
        self.user = create_authenticated_user()
        self.client = create_api_client_authenticated(self.user)
        self.video = create_sample_video(self.user)

    def test_like_video_201(self):
        """POST /api/videos/{id}/like/ → 201."""
        response = self.client.post(f"/api/videos/{self.video.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "Like aggiunto.")
        self.assertTrue(
            VideoLike.objects.filter(user=self.user, video=self.video).exists()
        )

    def test_like_video_duplicate_409(self):
        """POST duplicato → 409 (IntegrityError gestita dall'error handler)."""
        self.client.post(f"/api/videos/{self.video.id}/like/")
        response = self.client.post(f"/api/videos/{self.video.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["code"], "Conflict")
        self.assertIn("detail", response.data)

    def test_unlike_video_204(self):
        """DELETE /api/videos/{id}/like/ → 204."""
        VideoLike.objects.create(user=self.user, video=self.video)
        response = self.client.delete(f"/api/videos/{self.video.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            VideoLike.objects.filter(user=self.user, video=self.video).exists()
        )

    def test_unlike_video_not_found_404(self):
        """DELETE senza like esistente → 404."""
        response = self.client.delete(f"/api/videos/{self.video.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_like_nonexistent_video_404(self):
        """POST su video inesistente → 404."""
        response = self.client.post("/api/videos/99999/like/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CommentLikeEndpointTest(APITestCase):
    """Test endpoint POST/DELETE /api/comments/{id}/like/."""

    def setUp(self):
        self.user = create_authenticated_user()
        self.client = create_api_client_authenticated(self.user)
        self.video = create_sample_video(self.user)
        self.comment = Comment.objects.create(
            user=self.user, video=self.video, content="Test", timestamp_second=0
        )

    def test_like_comment_201(self):
        """POST /api/comments/{id}/like/ → 201."""
        response = self.client.post(f"/api/comments/{self.comment.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "Like aggiunto.")
        self.assertTrue(
            CommentLike.objects.filter(user=self.user, comment=self.comment).exists()
        )

    def test_like_comment_duplicate_409(self):
        """POST duplicato → 409."""
        self.client.post(f"/api/comments/{self.comment.id}/like/")
        response = self.client.post(f"/api/comments/{self.comment.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data["code"], "Conflict")
        self.assertIn("detail", response.data)

    def test_unlike_comment_204(self):
        """DELETE /api/comments/{id}/like/ → 204."""
        CommentLike.objects.create(user=self.user, comment=self.comment)
        response = self.client.delete(f"/api/comments/{self.comment.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unlike_comment_not_found_404(self):
        """DELETE senza like → 404."""
        response = self.client.delete(f"/api/comments/{self.comment.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_like_nonexistent_comment_404(self):
        """POST su commento inesistente → 404."""
        response = self.client.post("/api/comments/99999/like/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class VideoLikeAnnotationTest(APITestCase):
    """Test annotazioni like_count e is_liked_by_me su video detail."""

    def setUp(self):
        self.user = create_authenticated_user()
        self.user2 = create_authenticated_user(username="user2")
        self.client = create_api_client_authenticated(self.user)
        self.video = create_sample_video(self.user)

    def test_like_count_and_is_liked_by_me_on_video_detail(self):
        """Video detail include like_count e is_liked_by_me."""
        # Nessun like
        response = self.client.get(f"/api/videos/{self.video.id}/")
        self.assertEqual(response.data["like_count"], 0)
        self.assertFalse(response.data["is_liked_by_me"])

        # Utente corrente mette like
        VideoLike.objects.create(user=self.user, video=self.video)
        response = self.client.get(f"/api/videos/{self.video.id}/")
        self.assertEqual(response.data["like_count"], 1)
        self.assertTrue(response.data["is_liked_by_me"])

        # Secondo utente mette like
        VideoLike.objects.create(user=self.user2, video=self.video)
        response = self.client.get(f"/api/videos/{self.video.id}/")
        self.assertEqual(response.data["like_count"], 2)
        self.assertTrue(response.data["is_liked_by_me"])

    def test_is_liked_by_me_false_for_other_user(self):
        """is_liked_by_me è False se l'utente corrente non ha messo like."""
        VideoLike.objects.create(user=self.user2, video=self.video)
        response = self.client.get(f"/api/videos/{self.video.id}/")
        self.assertEqual(response.data["like_count"], 1)
        self.assertFalse(response.data["is_liked_by_me"])


class CommentLikeAnnotationTest(APITestCase):
    """Test annotazioni like_count e is_liked_by_me su comment list."""

    def setUp(self):
        self.user = create_authenticated_user()
        self.user2 = create_authenticated_user(username="user2")
        self.client = create_api_client_authenticated(self.user)
        self.video = create_sample_video(self.user)
        self.comment = Comment.objects.create(
            user=self.user, video=self.video, content="Bel video!", timestamp_second=5
        )

    def test_like_count_and_is_liked_by_me_on_comment_list(self):
        """Comment list include like_count e is_liked_by_me."""
        response = self.client.get(f"/api/comments/?video={self.video.id}")
        comment_data = response.data["results"][0]
        self.assertEqual(comment_data["like_count"], 0)
        self.assertFalse(comment_data["is_liked_by_me"])

        # Mette like
        CommentLike.objects.create(user=self.user, comment=self.comment)
        response = self.client.get(f"/api/comments/?video={self.video.id}")
        comment_data = response.data["results"][0]
        self.assertEqual(comment_data["like_count"], 1)
        self.assertTrue(comment_data["is_liked_by_me"])

    def test_is_liked_by_me_false_for_other_user(self):
        """is_liked_by_me è False se l'utente corrente non ha messo like."""
        CommentLike.objects.create(user=self.user2, comment=self.comment)
        response = self.client.get(f"/api/comments/?video={self.video.id}")
        comment_data = response.data["results"][0]
        self.assertEqual(comment_data["like_count"], 1)
        self.assertFalse(comment_data["is_liked_by_me"])


class AnonymousUserAnnotationTest(APITestCase):
    """Test annotazioni like per utente anonimo (SSR retrieve AllowAny)."""

    def setUp(self):
        self.user = create_authenticated_user()
        self.video = create_sample_video(self.user)
        VideoLike.objects.create(user=self.user, video=self.video)

    def test_anonymous_user_sees_like_count_and_is_liked_false(self):
        """Utente non autenticato vede like_count ma is_liked_by_me=False."""
        # Client senza autenticazione
        response = self.client.get(f"/api/videos/{self.video.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["like_count"], 1)
        self.assertFalse(response.data["is_liked_by_me"])


class LikePermissionTest(APITestCase):
    """Test permessi: utente toconfirm non può fare like."""

    def test_toconfirm_user_cannot_like_video(self):
        """Utente toconfirm → 403 su POST like video."""
        user = create_authenticated_user()
        video = create_sample_video(user)
        toconfirm = create_toconfirm_user()
        client = create_api_client_authenticated(toconfirm)
        response = client.post(f"/api/videos/{video.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_toconfirm_user_cannot_like_comment(self):
        """Utente toconfirm → 403 su POST like commento."""
        user = create_authenticated_user()
        video = create_sample_video(user)
        comment = Comment.objects.create(
            user=user, video=video, content="Test", timestamp_second=0
        )
        toconfirm = create_toconfirm_user()
        client = create_api_client_authenticated(toconfirm)
        response = client.post(f"/api/comments/{comment.id}/like/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
