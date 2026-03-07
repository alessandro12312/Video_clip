"""Test per moderazione admin — Story 0-4.

Verifica il comportamento del campo is_disabled su Comment,
la cascata DELETE su Video, le admin actions Django,
la sospensione utente e le restrizioni di accesso.
"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from cs_clips.models import Comment, Rating
from cs_clips.tests.conftest import (
    create_admin_user,
    create_api_client_authenticated,
    create_authenticated_user,
    create_sample_contest,
    create_sample_video,
)

User = get_user_model()


class CommentModerationTests(APITestCase):
    """Test per AC-1: commenti disabilitati nascosti dalle API."""

    def setUp(self):
        self.admin = create_admin_user()
        self.user = create_authenticated_user()
        self.video = create_sample_video(uploader=self.user)
        # Commento visibile
        self.visible_comment = Comment.objects.create(
            user=self.user,
            video=self.video,
            content="Commento visibile",
            timestamp_second=5,
        )
        # Commento disabilitato
        self.disabled_comment = Comment.objects.create(
            user=self.user,
            video=self.video,
            content="Commento disabilitato",
            timestamp_second=10,
            is_disabled=True,
        )

    def test_disabled_comment_hidden_from_api(self):
        """Commento con is_disabled=True NON appare in GET /api/comments/."""
        client = create_api_client_authenticated(self.user)
        response = client.get("/api/comments/")
        self.assertEqual(response.status_code, 200)
        comment_ids = [c["id"] for c in response.data["results"]]
        self.assertNotIn(self.disabled_comment.pk, comment_ids)

    def test_enabled_comment_visible_in_api(self):
        """Commento con is_disabled=False appare normalmente in GET /api/comments/."""
        client = create_api_client_authenticated(self.user)
        response = client.get("/api/comments/")
        self.assertEqual(response.status_code, 200)
        comment_ids = [c["id"] for c in response.data["results"]]
        self.assertIn(self.visible_comment.pk, comment_ids)

    def test_disabled_comment_detail_returns_404(self):
        """GET /api/comments/{id}/ restituisce 404 per commento disabilitato."""
        client = create_api_client_authenticated(self.user)
        response = client.get(f"/api/comments/{self.disabled_comment.pk}/")
        self.assertEqual(response.status_code, 404)

    def test_is_disabled_not_exposed_via_api_serializer(self):
        """is_disabled non modificabile via API: PATCH bloccato (405).
        La moderazione avviene solo via Django Admin."""
        superuser = User.objects.create_superuser(
            username="superadmin",
            password="superpass123",
            email="super@test.com",
        )
        client = create_api_client_authenticated(superuser)
        response = client.patch(
            f"/api/comments/{self.visible_comment.pk}/",
            {
                "content": self.visible_comment.content,
                "video": self.visible_comment.video.pk,
                "timestamp_second": self.visible_comment.timestamp_second,
                "is_disabled": True,
            },
            format="json",
        )
        # PATCH non consentito su commenti (http_method_names restrittivo)
        self.assertEqual(response.status_code, 405)
        self.visible_comment.refresh_from_db()
        self.assertFalse(self.visible_comment.is_disabled)


class VideoCascadeDeleteTests(APITestCase):
    """Test per AC-2: eliminazione video con CASCADE su commenti e rating."""

    def setUp(self):
        self.user = create_authenticated_user()
        self.video = create_sample_video(uploader=self.user)
        # Crea commento e rating associati al video
        self.comment = Comment.objects.create(
            user=self.user,
            video=self.video,
            content="Commento da cancellare",
            timestamp_second=0,
        )
        self.rating = Rating.objects.create(
            user=self.user,
            video=self.video,
            value=4,
        )

    def test_video_delete_cascades_comments(self):
        """Eliminazione video cancella commenti e rating associati per CASCADE."""
        comment_pk = self.comment.pk
        rating_pk = self.rating.pk

        self.video.delete()

        self.assertFalse(Comment.objects.filter(pk=comment_pk).exists())
        self.assertFalse(Rating.objects.filter(pk=rating_pk).exists())


class AdminActionTests(APITestCase):
    """Test per admin actions: disabilita/abilita commenti, chiudi contest."""

    def setUp(self):
        self.admin = create_admin_user()
        self.admin.is_superuser = True
        self.admin.save()
        self.user = create_authenticated_user()
        self.video = create_sample_video(uploader=self.user)

    def test_admin_disabilita_commenti_action(self):
        """Admin action 'disabilita_commenti' imposta is_disabled=True."""
        comment = Comment.objects.create(
            user=self.user,
            video=self.video,
            content="Da disabilitare",
            timestamp_second=0,
        )
        self.client.login(username="adminuser", password="adminpass123")
        url = reverse("admin:cs_clips_comment_changelist")
        self.client.post(
            url,
            {
                "action": "disabilita_commenti",
                "_selected_action": [comment.pk],
            },
        )
        comment.refresh_from_db()
        self.assertTrue(comment.is_disabled)

    def test_admin_abilita_commenti_action(self):
        """Admin action 'abilita_commenti' imposta is_disabled=False."""
        comment = Comment.objects.create(
            user=self.user,
            video=self.video,
            content="Da riabilitare",
            timestamp_second=0,
            is_disabled=True,
        )
        self.client.login(username="adminuser", password="adminpass123")
        url = reverse("admin:cs_clips_comment_changelist")
        self.client.post(
            url,
            {
                "action": "abilita_commenti",
                "_selected_action": [comment.pk],
            },
        )
        comment.refresh_from_db()
        self.assertFalse(comment.is_disabled)

    def test_admin_chiudi_contest_action(self):
        """Admin action 'chiudi_contest' chiude un contest aperto."""
        contest = create_sample_contest()
        self.assertFalse(contest.is_closed)
        self.client.login(username="adminuser", password="adminpass123")
        url = reverse("admin:cs_clips_contest_changelist")
        self.client.post(
            url,
            {
                "action": "chiudi_contest",
                "_selected_action": [contest.pk],
            },
        )
        contest.refresh_from_db()
        self.assertTrue(contest.is_closed)
        self.assertIsNotNone(contest.closed_at)


class UserSuspensionTests(APITestCase):
    """Test per AC-3: utente sospeso non puo' autenticarsi."""

    def test_inactive_user_jwt_rejected(self):
        """Utente con is_active=False riceve 401 su richiesta JWT."""
        user = create_authenticated_user(username="suspended_user")
        user.is_active = False
        user.save()
        response = self.client.post(
            "/api/token/",
            {"username": "suspended_user", "password": "testpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
