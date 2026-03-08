"""Test per endpoint listing, detail e videos contest (Story 4.1, 4.2)."""

from datetime import date, timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from cs_clips.models import Contest, Rating, Video
from cs_clips.tests.conftest import (
    create_admin_user,
    create_api_client_authenticated,
    create_authenticated_user,
)

CONTESTS_URL = "/api/contests/"


def _create_contest(tag="clutch", is_closed=False, winner=None, name=None):
    """Helper: crea contest con date settimana corrente."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    saturday = monday + timedelta(days=5)
    return Contest.objects.create(
        name=name or f"Contest {tag}",
        tag=tag,
        start_date=monday,
        end_date=saturday,
        is_closed=is_closed,
        closed_at=timezone.now() if is_closed else None,
        winner=winner,
    )


def _create_contest_past(tag="clutch", is_closed=False, winner=None, weeks_ago=1):
    """Helper: crea contest con date di settimane passate."""
    today = date.today()
    monday = today - timedelta(weeks=weeks_ago, days=today.weekday())
    saturday = monday + timedelta(days=5)
    return Contest.objects.create(
        name=f"Contest {tag} W-{weeks_ago}",
        tag=tag,
        start_date=monday,
        end_date=saturday,
        is_closed=is_closed,
        closed_at=timezone.now() if is_closed else None,
        winner=winner,
    )


class ContestListTests(APITestCase):
    """Test GET /api/contests/ (AC #1)."""

    def setUp(self):
        self.user = create_authenticated_user()
        self.client = create_api_client_authenticated(self.user)

    def test_list_returns_paginated_response(self):
        """Lista contest ritorna formato paginato {count, next, previous, results}."""
        _create_contest(tag="clutch")
        _create_contest_past(tag="funny", weeks_ago=2)

        response = self.client.get(CONTESTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)

    def test_list_fields_present(self):
        """Ogni contest nella lista ha tutti i campi richiesti."""
        _create_contest(tag="clutch")

        response = self.client.get(CONTESTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contest = response.data["results"][0]
        expected_fields = {
            "id",
            "name",
            "tag",
            "start_date",
            "end_date",
            "is_closed",
            "closed_at",
            "winner",
            "winner_title",
            "video_count",
        }
        self.assertEqual(set(contest.keys()), expected_fields)

    def test_list_ordered_by_start_date_desc(self):
        """Contest ordinati per -start_date (piu recenti prima)."""
        c_old = _create_contest_past(tag="clutch", weeks_ago=3)
        c_new = _create_contest(tag="funny")

        response = self.client.get(CONTESTS_URL)
        results = response.data["results"]
        self.assertEqual(results[0]["id"], c_new.id)
        self.assertEqual(results[1]["id"], c_old.id)

    def test_list_includes_video_count(self):
        """video_count conta i video associati al contest."""
        contest = _create_contest(tag="clutch")
        Video.objects.create(
            title="V1",
            uploader=self.user,
            contest=contest,
            file="v1.mp4",
            duration=30,
        )
        Video.objects.create(
            title="V2",
            uploader=self.user,
            contest=contest,
            file="v2.mp4",
            duration=30,
        )

        response = self.client.get(CONTESTS_URL)
        self.assertEqual(response.data["results"][0]["video_count"], 2)

    def test_list_video_count_zero(self):
        """Contest senza video ha video_count=0."""
        _create_contest(tag="clutch")

        response = self.client.get(CONTESTS_URL)
        self.assertEqual(response.data["results"][0]["video_count"], 0)

    def test_list_empty_returns_zero_count(self):
        """Lista vuota ritorna {count: 0, results: []}."""
        response = self.client.get(CONTESTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])


class ContestDetailTests(APITestCase):
    """Test GET /api/contests/{id}/ (AC #2)."""

    def setUp(self):
        self.user = create_authenticated_user()
        self.client = create_api_client_authenticated(self.user)

    def test_retrieve_returns_contest_detail(self):
        """Detail ritorna contest con video_count."""
        contest = _create_contest(tag="clutch")
        Video.objects.create(
            title="V1",
            uploader=self.user,
            contest=contest,
            file="v1.mp4",
            duration=30,
        )

        response = self.client.get(f"{CONTESTS_URL}{contest.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], contest.id)
        self.assertEqual(response.data["video_count"], 1)

    def test_retrieve_closed_contest_has_winner_detail(self):
        """Contest chiuso include winner_detail nested."""
        winner = Video.objects.create(
            title="Winner Video",
            uploader=self.user,
            file="winner.mp4",
            duration=30,
        )
        contest = _create_contest(tag="clutch", is_closed=True, winner=winner)

        response = self.client.get(f"{CONTESTS_URL}{contest.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["winner_detail"])
        self.assertEqual(response.data["winner_detail"]["title"], "Winner Video")
        self.assertEqual(response.data["winner"], winner.id)

    def test_retrieve_open_contest_winner_detail_null(self):
        """Contest attivo ha winner=null e winner_detail=null."""
        contest = _create_contest(tag="clutch")

        response = self.client.get(f"{CONTESTS_URL}{contest.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["winner"])
        self.assertIsNone(response.data["winner_detail"])

    def test_retrieve_404_for_nonexistent(self):
        """Detail per ID inesistente ritorna 404."""
        response = self.client.get(f"{CONTESTS_URL}99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ContestFilterTests(APITestCase):
    """Test filtri ?tag= e ?is_closed= (AC #6, #7)."""

    def setUp(self):
        self.user = create_authenticated_user()
        self.client = create_api_client_authenticated(self.user)

    def test_filter_by_tag(self):
        """Filtro ?tag=funny ritorna solo contest con quel tag."""
        _create_contest(tag="clutch")
        funny = _create_contest_past(tag="funny", weeks_ago=1)

        response = self.client.get(CONTESTS_URL, {"tag": "funny"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], funny.id)

    def test_filter_by_is_closed_true(self):
        """Filtro ?is_closed=true ritorna solo contest chiusi."""
        _create_contest(tag="clutch", is_closed=False)
        closed = _create_contest_past(tag="funny", is_closed=True, weeks_ago=2)

        response = self.client.get(CONTESTS_URL, {"is_closed": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], closed.id)

    def test_filter_by_is_closed_false(self):
        """Filtro ?is_closed=false ritorna solo contest attivi."""
        active = _create_contest(tag="clutch", is_closed=False)
        _create_contest_past(tag="funny", is_closed=True, weeks_ago=2)

        response = self.client.get(CONTESTS_URL, {"is_closed": "false"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], active.id)

    def test_filter_combined_tag_and_is_closed(self):
        """Filtri combinati ?tag=clutch&is_closed=true."""
        _create_contest(tag="clutch", is_closed=False)
        closed_clutch = _create_contest_past(tag="clutch", is_closed=True, weeks_ago=2)
        _create_contest_past(tag="funny", is_closed=True, weeks_ago=3)

        response = self.client.get(CONTESTS_URL, {"tag": "clutch", "is_closed": "true"})
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], closed_clutch.id)


class ContestActionRoutingTests(APITestCase):
    """Smoke test per routing @action winners e end (migrati da APIView standalone)."""

    def setUp(self):
        self.user = create_authenticated_user()
        self.client = create_api_client_authenticated(self.user)

    def test_winners_action_accessible(self):
        """GET /api/contests/winners/ e raggiungibile e ritorna 200."""
        response = self.client.get(f"{CONTESTS_URL}winners/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_end_action_requires_admin(self):
        """POST /api/contests/end/ richiede admin — 403 per utente normale."""
        response = self.client.post(f"{CONTESTS_URL}end/", {"tag": "clutch"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_end_action_accessible_by_admin(self):
        """POST /api/contests/end/ da admin — 404 se nessun contest attivo."""
        admin = create_admin_user()
        admin_client = create_api_client_authenticated(admin)
        response = admin_client.post(f"{CONTESTS_URL}end/", {"tag": "clutch"})
        # 404 perche nessun contest attivo — ma routing funziona
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ContestAuthTests(APITestCase):
    """Test autenticazione — 401 per utenti non autenticati (IsAuthenticated)."""

    def test_unauthenticated_list_returns_401(self):
        """Utente non autenticato riceve 401 su lista."""
        response = self.client.get(CONTESTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_detail_returns_401(self):
        """Utente non autenticato riceve 401 su detail."""
        response = self.client.get(f"{CONTESTS_URL}1/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ContestVideosActionTests(APITestCase):
    """Test GET /api/contests/{id}/videos/ (Story 4.2 — AC #1, #4)."""

    def setUp(self):
        self.user = create_authenticated_user()
        self.client = create_api_client_authenticated(self.user)
        self.contest = _create_contest(tag="clutch")

    def test_videos_returns_paginated_response(self):
        """Videos action ritorna formato paginato."""
        Video.objects.create(
            title="V1",
            uploader=self.user,
            contest=self.contest,
            file="v1.mp4",
            duration=30,
            tag="clutch",
        )

        response = self.client.get(f"{CONTESTS_URL}{self.contest.id}/videos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 1)

    def test_videos_includes_rating_annotations(self):
        """Video include average_rating, my_rating_id, my_rating_value."""
        video = Video.objects.create(
            title="V1",
            uploader=self.user,
            contest=self.contest,
            file="v1.mp4",
            duration=30,
            tag="clutch",
        )
        Rating.objects.create(user=self.user, video=video, value=4)

        response = self.client.get(f"{CONTESTS_URL}{self.contest.id}/videos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        v = response.data["results"][0]
        self.assertEqual(v["average_rating"], 4.0)
        self.assertIsNotNone(v["my_rating_id"])
        self.assertEqual(v["my_rating_value"], 4)
        self.assertIn("like_count", v)
        self.assertEqual(v["like_count"], 0)
        self.assertIn("is_liked_by_me", v)
        self.assertFalse(v["is_liked_by_me"])

    def test_videos_ordered_by_avg_rating_desc(self):
        """Video ordinati per media voti decrescente (classifica)."""
        user2 = create_authenticated_user(username="voter2")
        v1 = Video.objects.create(
            title="Low",
            uploader=self.user,
            contest=self.contest,
            file="v1.mp4",
            duration=30,
            tag="clutch",
        )
        v2 = Video.objects.create(
            title="High",
            uploader=self.user,
            contest=self.contest,
            file="v2.mp4",
            duration=30,
            tag="clutch",
        )
        Rating.objects.create(user=self.user, video=v1, value=2)
        Rating.objects.create(user=self.user, video=v2, value=5)
        Rating.objects.create(user=user2, video=v2, value=4)

        response = self.client.get(f"{CONTESTS_URL}{self.contest.id}/videos/")
        results = response.data["results"]
        self.assertEqual(results[0]["id"], v2.id)
        self.assertEqual(results[1]["id"], v1.id)

    def test_videos_unrated_appear_last(self):
        """Video senza voti appaiono dopo quelli con voti (NULLS LAST)."""
        v_rated = Video.objects.create(
            title="Rated",
            uploader=self.user,
            contest=self.contest,
            file="v1.mp4",
            duration=30,
            tag="clutch",
        )
        v_unrated = Video.objects.create(
            title="Unrated",
            uploader=self.user,
            contest=self.contest,
            file="v2.mp4",
            duration=30,
            tag="clutch",
        )
        Rating.objects.create(user=self.user, video=v_rated, value=3)

        response = self.client.get(f"{CONTESTS_URL}{self.contest.id}/videos/")
        results = response.data["results"]
        self.assertEqual(results[0]["id"], v_rated.id)
        self.assertEqual(results[1]["id"], v_unrated.id)

    def test_videos_empty_contest(self):
        """Contest senza video ritorna lista vuota."""
        response = self.client.get(f"{CONTESTS_URL}{self.contest.id}/videos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    def test_videos_my_rating_null_if_not_voted(self):
        """my_rating_id e my_rating_value sono null se l'utente non ha votato."""
        Video.objects.create(
            title="V1",
            uploader=self.user,
            contest=self.contest,
            file="v1.mp4",
            duration=30,
            tag="clutch",
        )

        response = self.client.get(f"{CONTESTS_URL}{self.contest.id}/videos/")
        v = response.data["results"][0]
        self.assertIsNone(v["my_rating_id"])
        self.assertIsNone(v["my_rating_value"])

    def test_videos_unauthenticated_returns_401(self):
        """Utente non autenticato riceve 401."""
        response = self.client.get(f"{CONTESTS_URL}{self.contest.id}/videos/")
        # Logged in, so reset client to unauthenticated
        from rest_framework.test import APIClient

        anon_client = APIClient()
        response = anon_client.get(f"{CONTESTS_URL}{self.contest.id}/videos/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
