"""Test per l'algoritmo di spareggio ponderato con like (Story 3.4)."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from cs_clips.models import Comment, Contest, Rating, Video, VideoLike
from cs_clips.tests.conftest import (
    create_admin_user,
    create_api_client_authenticated,
    create_authenticated_user,
)
from cs_clips.utils.desempate import desempate_ponderato

User = get_user_model()


class DesempatePonderatoTest(TestCase):
    """Test unitari per desempate_ponderato() con like."""

    def setUp(self):
        self.user1 = create_authenticated_user("user1")
        self.user2 = create_authenticated_user("user2")
        self.user3 = create_authenticated_user("user3")
        self.user4 = create_authenticated_user("user4")

        self.contest = Contest.objects.create(
            name="Test Contest",
            tag="clutch",
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            is_closed=False,
        )

        # Crea video con path fittizio (non serve file reale per test algoritmo)
        self.video1 = Video.objects.create(
            title="Video Uno",
            uploader=self.user1,
            contest=self.contest,
            file="test_video_1.mp4",
            duration=30,
        )
        self.video2 = Video.objects.create(
            title="Video Due",
            uploader=self.user2,
            contest=self.contest,
            file="test_video_2.mp4",
            duration=30,
        )

    def test_winner_with_more_likes_wins_on_tiebreak(self):
        """Video con più like vince a parità di voti e views (AC #1)."""
        # Stessi voti
        Rating.objects.create(user=self.user1, video=self.video1, value=8)
        Rating.objects.create(user=self.user2, video=self.video2, value=8)

        # Stesse views
        self.video1.views = 10
        self.video2.views = 10
        self.video1.save()
        self.video2.save()

        # Video2 ha più like → deve vincere
        VideoLike.objects.create(user=self.user1, video=self.video2)
        VideoLike.objects.create(user=self.user3, video=self.video2)
        VideoLike.objects.create(user=self.user1, video=self.video1)  # solo 1 like

        winner = desempate_ponderato([self.video1, self.video2])
        self.assertEqual(winner.title, "Video Due")

    def test_zero_likes_no_error(self):
        """Video con 0 like non causa errori, contribuisce 0 al punteggio (AC #2)."""
        # Diversi voti per avere un vincitore chiaro
        Rating.objects.create(user=self.user1, video=self.video1, value=9)
        Rating.objects.create(user=self.user2, video=self.video2, value=5)

        self.video1.views = 20
        self.video2.views = 5
        self.video1.save()
        self.video2.save()

        # Zero like su entrambi
        winner = desempate_ponderato([self.video1, self.video2])
        self.assertEqual(winner.title, "Video Uno")

    def test_all_same_likes_normalize_returns_ones(self):
        """Tutti i video con stesso numero like → normalize() ritorna tutti 1."""
        # Stessi like
        VideoLike.objects.create(user=self.user1, video=self.video1)
        VideoLike.objects.create(user=self.user1, video=self.video2)

        # Video1 vince per più voti
        Rating.objects.create(user=self.user1, video=self.video1, value=9)
        Rating.objects.create(user=self.user2, video=self.video1, value=9)
        Rating.objects.create(user=self.user1, video=self.video2, value=5)

        self.video1.views = 10
        self.video2.views = 10
        self.video1.save()
        self.video2.save()

        winner = desempate_ponderato([self.video1, self.video2])
        # Con like uguali (normalizzati a 1), vince chi ha più voti
        self.assertEqual(winner.title, "Video Uno")

    def test_algorithm_uses_likes_not_comments(self):
        """L'algoritmo usa likes, non commenti (AC #1 — verifica sostituzione)."""
        # Stesse views e rating
        Rating.objects.create(user=self.user1, video=self.video1, value=8)
        Rating.objects.create(user=self.user1, video=self.video2, value=8)
        self.video1.views = 10
        self.video2.views = 10
        self.video1.save()
        self.video2.save()

        # Video1 ha più commenti
        Comment.objects.create(user=self.user1, video=self.video1, content="A")
        Comment.objects.create(user=self.user2, video=self.video1, content="B")
        Comment.objects.create(user=self.user3, video=self.video1, content="C")

        # Video2 ha più like
        VideoLike.objects.create(user=self.user1, video=self.video2)
        VideoLike.objects.create(user=self.user2, video=self.video2)
        VideoLike.objects.create(user=self.user3, video=self.video2)

        winner = desempate_ponderato([self.video1, self.video2])
        # Deve vincere video2 (più like), NON video1 (più commenti)
        self.assertEqual(winner.title, "Video Due")

    def test_empty_list_returns_none(self):
        """Lista vuota ritorna None senza errori (edge case)."""
        result = desempate_ponderato([])
        self.assertIsNone(result)

    def test_single_video_returns_that_video(self):
        """Lista con un solo video ritorna quel video direttamente."""
        winner = desempate_ponderato([self.video1])
        self.assertEqual(winner.title, "Video Uno")


class EndContestWithLikesTest(APITestCase):
    """Test integrazione EndContestView con like reali (Task 3.4)."""

    def setUp(self):
        self.admin = create_admin_user()
        self.client = create_api_client_authenticated(self.admin)
        self.user1 = create_authenticated_user("user1")
        self.user2 = create_authenticated_user("user2")
        self.user3 = create_authenticated_user("user3")

        today = timezone.now().date()
        self.contest = Contest.objects.create(
            name="Contest Like Test",
            tag="clutch",
            start_date=today,
            end_date=today,
            is_closed=False,
        )

        self.video1 = Video.objects.create(
            title="Video A",
            uploader=self.user1,
            contest=self.contest,
            file="test_video_a.mp4",
            duration=30,
        )
        self.video2 = Video.objects.create(
            title="Video B",
            uploader=self.user2,
            contest=self.contest,
            file="test_video_b.mp4",
            duration=30,
        )

    def test_end_contest_tiebreak_uses_likes(self):
        """EndContestView: spareggio usa like reali (Task 3.4, AC #1)."""
        # Stessa media voto → scatta spareggio
        Rating.objects.create(user=self.user1, video=self.video1, value=8)
        Rating.objects.create(user=self.user1, video=self.video2, value=8)

        # Stesse views
        self.video1.views = 10
        self.video2.views = 10
        self.video1.save()
        self.video2.save()

        # Video2 ha più like → vince
        VideoLike.objects.create(user=self.user1, video=self.video2)
        VideoLike.objects.create(user=self.user2, video=self.video2)
        VideoLike.objects.create(user=self.user3, video=self.video2)
        VideoLike.objects.create(user=self.user1, video=self.video1)

        response = self.client.post("/api/contests/end/", {"tag": "clutch"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["winner"]["title"], "Video B")
        self.assertEqual(len(response.data["finalists"]), 2)
        finalist_titles = {f["title"] for f in response.data["finalists"]}
        self.assertEqual(finalist_titles, {"Video A", "Video B"})


class CloseContestsCommandWithLikesTest(TestCase):
    """Test integrazione close_contests management command con like reali."""

    def test_close_contests_tiebreak_uses_likes(self):
        """close_contests: spareggio usa like reali (Task 3.5)."""
        from datetime import timedelta

        from django.core.management import call_command

        user1 = create_authenticated_user("cmd_user1")
        user2 = create_authenticated_user("cmd_user2")
        user3 = create_authenticated_user("cmd_user3")

        yesterday = timezone.now().date() - timedelta(days=1)
        contest = Contest.objects.create(
            name="Contest Scaduto",
            tag="clutch",
            start_date=yesterday - timedelta(days=7),
            end_date=yesterday,
            is_closed=False,
        )

        video1 = Video.objects.create(
            title="Cmd Video A",
            uploader=user1,
            contest=contest,
            file="test_cmd_video_a.mp4",
            duration=30,
        )
        video2 = Video.objects.create(
            title="Cmd Video B",
            uploader=user2,
            contest=contest,
            file="test_cmd_video_b.mp4",
            duration=30,
        )

        # Stessa media voto
        Rating.objects.create(user=user1, video=video1, value=7)
        Rating.objects.create(user=user1, video=video2, value=7)

        # Stesse views
        video1.views = 10
        video2.views = 10
        video1.save()
        video2.save()

        # Video2 ha più like → vince
        VideoLike.objects.create(user=user1, video=video2)
        VideoLike.objects.create(user=user2, video=video2)
        VideoLike.objects.create(user=user3, video=video2)

        call_command("close_contests")

        contest.refresh_from_db()
        self.assertTrue(contest.is_closed)
        self.assertEqual(contest.winner.title, "Cmd Video B")
