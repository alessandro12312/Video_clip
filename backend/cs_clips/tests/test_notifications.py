"""Test suite per Story 5.1: Modello Notification e API backend."""

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from cs_clips.models import Notification
from cs_clips.tests.conftest import (
    create_api_client_authenticated,
    create_authenticated_user,
    create_sample_video,
)


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class NotificationModelTest(TestCase):
    """Test modello Notification (AC #1)."""

    def setUp(self):
        self.user = create_authenticated_user(username="recipient")
        self.sender = create_authenticated_user(username="sender")

    def test_create_notification_all_fields(self):
        """Notification può essere creata con tutti i campi."""
        notif = Notification.objects.create(
            recipient=self.user,
            sender=self.sender,
            type=Notification.Type.COMMENT_RECEIVED,
            is_read=False,
        )
        self.assertEqual(notif.recipient, self.user)
        self.assertEqual(notif.sender, self.sender)
        self.assertEqual(notif.type, "comment_received")
        self.assertFalse(notif.is_read)
        self.assertIsNotNone(notif.created_at)

    def test_str_representation(self):
        """__str__ mostra tipo display e username destinatario."""
        notif = Notification.objects.create(
            recipient=self.user,
            sender=self.sender,
            type=Notification.Type.LIKE_RECEIVED,
        )
        self.assertIn("Like ricevuto", str(notif))
        self.assertIn(self.user.username, str(notif))

    def test_ordering_by_created_at_desc(self):
        """Notifiche ordinate per -created_at (più recente prima)."""
        n1 = Notification.objects.create(
            recipient=self.user,
            type=Notification.Type.CONTEST_OPENED,
        )
        n2 = Notification.objects.create(
            recipient=self.user,
            type=Notification.Type.LIKE_RECEIVED,
        )
        notifs = list(Notification.objects.filter(recipient=self.user))
        self.assertEqual(notifs[0].pk, n2.pk)
        self.assertEqual(notifs[1].pk, n1.pk)

    def test_notification_types_all_seven(self):
        """Verifica che ci siano 7 tipi di notifica."""
        self.assertEqual(len(Notification.Type.choices), 7)


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class NotificationAPIListTest(TestCase):
    """Test API GET /api/notifications/ (AC #2)."""

    def setUp(self):
        self.user = create_authenticated_user(username="user1")
        self.other = create_authenticated_user(username="user2")
        self.client = create_api_client_authenticated(self.user)

        # Notifiche per user1
        Notification.objects.create(
            recipient=self.user,
            sender=self.other,
            type=Notification.Type.LIKE_RECEIVED,
        )
        Notification.objects.create(
            recipient=self.user,
            type=Notification.Type.CONTEST_OPENED,
        )
        # Notifica per user2 (non deve apparire)
        Notification.objects.create(
            recipient=self.other,
            sender=self.user,
            type=Notification.Type.COMMENT_RECEIVED,
        )

    def test_list_returns_only_own_notifications(self):
        """GET /api/notifications/ ritorna solo le notifiche del richiedente."""
        resp = self.client.get("/api/notifications/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        results = resp.data["results"]
        self.assertEqual(len(results), 2)
        for notif in results:
            self.assertEqual(notif["recipient"], self.user.pk)

    def test_list_paginated_and_ordered(self):
        """GET /api/notifications/ è paginato e ordinato per -created_at."""
        resp = self.client.get("/api/notifications/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("count", resp.data)
        self.assertIn("results", resp.data)
        results = resp.data["results"]
        if len(results) > 1:
            self.assertGreaterEqual(results[0]["created_at"], results[1]["created_at"])


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class NotificationUnreadCountTest(TestCase):
    """Test API GET /api/notifications/unread-count/ (AC #3)."""

    def setUp(self):
        self.user = create_authenticated_user(username="user1")
        self.client = create_api_client_authenticated(self.user)
        Notification.objects.create(
            recipient=self.user,
            type=Notification.Type.LIKE_RECEIVED,
            is_read=False,
        )
        Notification.objects.create(
            recipient=self.user,
            type=Notification.Type.CONTEST_OPENED,
            is_read=False,
        )
        Notification.objects.create(
            recipient=self.user,
            type=Notification.Type.COMMENT_RECEIVED,
            is_read=True,
        )

    def test_unread_count_returns_correct_number(self):
        """GET /api/notifications/unread-count/ ritorna conteggio corretto."""
        resp = self.client.get("/api/notifications/unread-count/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["count"], 2)


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class NotificationMarkReadTest(TestCase):
    """Test API POST /api/notifications/{id}/mark-read/ (AC #4)."""

    def setUp(self):
        self.user = create_authenticated_user(username="user1")
        self.other = create_authenticated_user(username="user2")
        self.client = create_api_client_authenticated(self.user)
        self.notif = Notification.objects.create(
            recipient=self.user,
            type=Notification.Type.LIKE_RECEIVED,
            is_read=False,
        )
        self.other_notif = Notification.objects.create(
            recipient=self.other,
            type=Notification.Type.LIKE_RECEIVED,
            is_read=False,
        )

    def test_mark_read_own_notification(self):
        """POST /api/notifications/{id}/mark-read/ marca come letta."""
        resp = self.client.post(f"/api/notifications/{self.notif.pk}/mark-read/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.notif.refresh_from_db()
        self.assertTrue(self.notif.is_read)

    def test_mark_read_other_user_notification_returns_404(self):
        """POST /api/notifications/{id}/mark-read/ su notifica altrui ritorna 404."""
        resp = self.client.post(f"/api/notifications/{self.other_notif.pk}/mark-read/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class NotificationMarkAllReadTest(TestCase):
    """Test API POST /api/notifications/mark-all-read/ (AC #5)."""

    def setUp(self):
        self.user = create_authenticated_user(username="user1")
        self.client = create_api_client_authenticated(self.user)
        Notification.objects.create(
            recipient=self.user,
            type=Notification.Type.LIKE_RECEIVED,
            is_read=False,
        )
        Notification.objects.create(
            recipient=self.user,
            type=Notification.Type.CONTEST_OPENED,
            is_read=False,
        )

    def test_mark_all_read(self):
        """POST /api/notifications/mark-all-read/ marca tutte come lette."""
        resp = self.client.post("/api/notifications/mark-all-read/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        unread = Notification.objects.filter(recipient=self.user, is_read=False).count()
        self.assertEqual(unread, 0)


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class NotificationAutoCreationTest(TestCase):
    """Test creazione automatica notifiche (AC #6)."""

    def setUp(self):
        self.owner = create_authenticated_user(username="owner")
        self.actor = create_authenticated_user(username="actor")
        self.video = create_sample_video(self.owner, title="Test Video")
        self.owner_client = create_api_client_authenticated(self.owner)
        self.actor_client = create_api_client_authenticated(self.actor)

    def test_comment_on_other_video_creates_notification(self):
        """Commento su video di altro utente crea notifica comment_received."""
        self.actor_client.post(
            "/api/comments/",
            {"video": self.video.pk, "content": "Bel video!", "timestamp_second": 5},
        )
        notif = Notification.objects.filter(
            recipient=self.owner,
            type=Notification.Type.COMMENT_RECEIVED,
        )
        self.assertEqual(notif.count(), 1)
        self.assertEqual(notif.first().sender, self.actor)
        self.assertEqual(notif.first().video, self.video)

    def test_like_on_other_video_creates_notification(self):
        """Like su video di altro utente crea notifica like_received."""
        self.actor_client.post(f"/api/videos/{self.video.pk}/like/")
        notif = Notification.objects.filter(
            recipient=self.owner,
            type=Notification.Type.LIKE_RECEIVED,
            video=self.video,
        )
        self.assertEqual(notif.count(), 1)
        self.assertEqual(notif.first().sender, self.actor)

    def test_comment_on_own_video_no_notification(self):
        """Commento su PROPRIO video NON crea notifica (self-skip)."""
        self.owner_client.post(
            "/api/comments/",
            {"video": self.video.pk, "content": "Mio!", "timestamp_second": 3},
        )
        notif = Notification.objects.filter(
            recipient=self.owner,
            type=Notification.Type.COMMENT_RECEIVED,
        )
        self.assertEqual(notif.count(), 0)

    def test_like_on_own_video_no_notification(self):
        """Like su PROPRIO video NON crea notifica (self-skip)."""
        self.owner_client.post(f"/api/videos/{self.video.pk}/like/")
        notif = Notification.objects.filter(
            recipient=self.owner,
            type=Notification.Type.LIKE_RECEIVED,
        )
        self.assertEqual(notif.count(), 0)


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class NotificationAuthTest(TestCase):
    """Test utente non autenticato riceve 401 (AC: tutti)."""

    def test_unauthenticated_user_gets_401(self):
        """Utente non autenticato riceve 401 su tutti gli endpoint."""
        client = APIClient()
        endpoints = [
            ("/api/notifications/", "get"),
            ("/api/notifications/unread-count/", "get"),
            ("/api/notifications/mark-all-read/", "post"),
        ]
        for url, method in endpoints:
            resp = getattr(client, method)(url)
            self.assertEqual(
                resp.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f"{method.upper()} {url} should return 401",
            )


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class NotificationCommentLikeTest(TestCase):
    """Test notifica like_received su commento (AC #6 — Task 3.4)."""

    def setUp(self):
        self.owner = create_authenticated_user(username="commenter")
        self.actor = create_authenticated_user(username="liker")
        self.video = create_sample_video(self.owner, title="Test Video")
        self.actor_client = create_api_client_authenticated(self.actor)
        self.owner_client = create_api_client_authenticated(self.owner)

        # Creo un commento del proprietario sul video
        from cs_clips.models import Comment

        self.comment = Comment.objects.create(
            user=self.owner,
            video=self.video,
            content="Grande clip!",
            timestamp_second=5,
        )

    def test_like_on_other_comment_creates_notification(self):
        """Like su commento di altro utente crea notifica like_received."""
        self.actor_client.post(f"/api/comments/{self.comment.pk}/like/")
        notif = Notification.objects.filter(
            recipient=self.owner,
            type=Notification.Type.LIKE_RECEIVED,
            comment=self.comment,
        )
        self.assertEqual(notif.count(), 1)
        self.assertEqual(notif.first().sender, self.actor)
        self.assertEqual(notif.first().video, self.video)

    def test_like_on_own_comment_no_notification(self):
        """Like su PROPRIO commento NON crea notifica (self-skip)."""
        self.owner_client.post(f"/api/comments/{self.comment.pk}/like/")
        notif = Notification.objects.filter(
            recipient=self.owner,
            type=Notification.Type.LIKE_RECEIVED,
            comment=self.comment,
        )
        self.assertEqual(notif.count(), 0)


@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class NotificationContestOpenedTest(TestCase):
    """Test notifica contest_opened via bulk_create (AC #6 — Task 3.5)."""

    def setUp(self):
        self.user1 = create_authenticated_user(username="user1")
        self.user2 = create_authenticated_user(username="user2")
        # Entrambi nel gruppo 'user' (create_authenticated_user lo fa gia)

    def test_new_contest_creates_notifications_for_all_users(self):
        """Creazione contest genera notifiche contest_opened per tutti gli utenti."""
        from cs_clips.utils.get_date_util import get_or_create_current_contest

        contest = get_or_create_current_contest("clutch")
        notifs = Notification.objects.filter(
            type=Notification.Type.CONTEST_OPENED,
            contest=contest,
        )
        self.assertEqual(notifs.count(), 2)
        recipients = set(notifs.values_list("recipient_id", flat=True))
        self.assertIn(self.user1.pk, recipients)
        self.assertIn(self.user2.pk, recipients)

    def test_existing_contest_no_duplicate_notifications(self):
        """Richiamare get_or_create su contest esistente NON duplica notifiche."""
        from cs_clips.utils.get_date_util import get_or_create_current_contest

        contest1 = get_or_create_current_contest("clutch")
        contest2 = get_or_create_current_contest("clutch")
        self.assertEqual(contest1.pk, contest2.pk)
        notifs = Notification.objects.filter(
            type=Notification.Type.CONTEST_OPENED,
        )
        # Solo 2 notifiche (dalla prima creazione), non 4
        self.assertEqual(notifs.count(), 2)
