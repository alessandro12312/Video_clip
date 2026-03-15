"""Test per API Bracket e Matchup (Story 6.2)."""

from unittest.mock import patch

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from cs_clips.models import (
    Bracket,
    ContestEntry,
    Matchup,
    MatchupVote,
    Notification,
)
from cs_clips.tests.conftest import (
    create_admin_user,
    create_api_client_authenticated,
    create_authenticated_user,
    create_sample_video,
)
from cs_clips.utils.bracket_logic import generate_bracket


class BracketListTest(TestCase):
    """Test GET /api/brackets/ (AC #4)."""

    def setUp(self):
        self.creator = create_authenticated_user(username="list_creator")
        self.b1 = Bracket.objects.create(
            name="Bracket Uno",
            max_participants=8,
            created_by=self.creator,
        )
        self.b2 = Bracket.objects.create(
            name="Bracket Due",
            max_participants=16,
            created_by=self.creator,
            status=Bracket.Status.ACTIVE,
        )

    def test_list_brackets_200(self):
        """Lista bracket restituisce 200 con paginazione."""
        client = APIClient()
        resp = client.get("/api/brackets/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("results", resp.data)
        self.assertEqual(len(resp.data["results"]), 2)

    def test_list_brackets_entries_count(self):
        """entries_count annotato correttamente."""
        user = create_authenticated_user(username="list_player")
        video = create_sample_video(uploader=user, title="List Video")
        ContestEntry.objects.create(bracket=self.b1, user=user, video=video)

        client = APIClient()
        resp = client.get("/api/brackets/")
        results = resp.data["results"]
        # b2 prima (piu' recente), b1 seconda
        b1_data = next(r for r in results if r["id"] == self.b1.id)
        b2_data = next(r for r in results if r["id"] == self.b2.id)
        self.assertEqual(b1_data["entries_count"], 1)
        self.assertEqual(b2_data["entries_count"], 0)

    def test_list_filter_status(self):
        """Filtro ?status= funziona."""
        client = APIClient()
        resp = client.get("/api/brackets/", {"status": "registration"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 1)
        self.assertEqual(resp.data["results"][0]["name"], "Bracket Uno")

    def test_list_brackets_fields(self):
        """Verifica che i campi richiesti siano presenti."""
        client = APIClient()
        resp = client.get("/api/brackets/")
        item = resp.data["results"][0]
        expected_fields = [
            "id",
            "name",
            "description",
            "status",
            "max_participants",
            "current_round",
            "entries_count",
            "created_by",
            "created_by_username",
            "created_at",
            "prize_description",
        ]
        for field in expected_fields:
            self.assertIn(field, item, f"Campo mancante: {field}")


class BracketDetailTest(TestCase):
    """Test GET /api/brackets/{id}/ (AC #5)."""

    def setUp(self):
        self.creator = create_authenticated_user(username="detail_creator")
        self.bracket = Bracket.objects.create(
            name="Detail Bracket",
            max_participants=8,
            created_by=self.creator,
        )
        # Crea 4 entry e genera bracket
        self.entries = []
        for i in range(4):
            user = create_authenticated_user(username=f"detail_player{i}")
            video = create_sample_video(uploader=user, title=f"Detail Video {i}")
            entry = ContestEntry.objects.create(
                bracket=self.bracket, user=user, video=video
            )
            self.entries.append(entry)

        with patch("cs_clips.utils.bracket_logic.random.shuffle"):
            generate_bracket(self.bracket)

    def test_detail_bracket_200(self):
        """Dettaglio bracket restituisce 200 con matchups_by_round."""
        client = APIClient()
        resp = client.get(f"/api/brackets/{self.bracket.id}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("matchups_by_round", resp.data)
        # 2 turni: round 1 (2 matchup) + round 2 (1 matchup)
        self.assertIn(1, resp.data["matchups_by_round"])
        self.assertIn(2, resp.data["matchups_by_round"])

    def test_detail_matchups_have_entries(self):
        """Matchup nel dettaglio hanno entry nested con user e video."""
        client = APIClient()
        resp = client.get(f"/api/brackets/{self.bracket.id}/")
        round_1 = resp.data["matchups_by_round"][1]
        matchup = round_1[0]
        self.assertIn("entry_1", matchup)
        self.assertIn("entry_2", matchup)
        self.assertIn("avg_rating_1", matchup)
        self.assertIn("avg_rating_2", matchup)

        # Entry nested ha user e video info
        entry_data = matchup["entry_1"]
        self.assertIn("user_id", entry_data)
        self.assertIn("username", entry_data)
        self.assertIn("video_id", entry_data)
        self.assertIn("video_title", entry_data)

    def test_detail_my_entry_authenticated(self):
        """my_entry presente per utente iscritto."""
        user = self.entries[0].user
        client = create_api_client_authenticated(user)
        resp = client.get(f"/api/brackets/{self.bracket.id}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data["my_entry"])
        self.assertEqual(resp.data["my_entry"]["user_id"], user.id)

    def test_detail_my_entry_not_enrolled(self):
        """my_entry null per utente non iscritto."""
        outsider = create_authenticated_user(username="outsider")
        client = create_api_client_authenticated(outsider)
        resp = client.get(f"/api/brackets/{self.bracket.id}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNone(resp.data["my_entry"])

    def test_detail_unauthenticated(self):
        """Dettaglio accessibile senza autenticazione, my_entry=null."""
        client = APIClient()
        resp = client.get(f"/api/brackets/{self.bracket.id}/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNone(resp.data["my_entry"])


class EnterBracketTest(TestCase):
    """Test POST /api/brackets/{id}/enter/ (AC #1)."""

    def setUp(self):
        self.creator = create_authenticated_user(username="enter_creator")
        self.bracket = Bracket.objects.create(
            name="Enter Bracket",
            max_participants=4,
            created_by=self.creator,
        )
        self.user = create_authenticated_user(username="enter_user")
        self.video = create_sample_video(uploader=self.user, title="Enter Video")

    def test_enter_bracket_201(self):
        """Iscrizione crea ContestEntry e risponde 201."""
        client = create_api_client_authenticated(self.user)
        resp = client.post(
            f"/api/brackets/{self.bracket.id}/enter/",
            {"video_id": self.video.id},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            ContestEntry.objects.filter(bracket=self.bracket, user=self.user).exists()
        )

    def test_enter_bracket_creates_notification(self):
        """Iscrizione crea notifica bracket_invite."""
        client = create_api_client_authenticated(self.user)
        client.post(
            f"/api/brackets/{self.bracket.id}/enter/",
            {"video_id": self.video.id},
            format="json",
        )
        notif = Notification.objects.filter(recipient=self.user, type="bracket_invite")
        self.assertEqual(notif.count(), 1)

    def test_enter_bracket_duplicate_409(self):
        """Iscrizione duplicata ritorna 409."""
        ContestEntry.objects.create(
            bracket=self.bracket, user=self.user, video=self.video
        )
        client = create_api_client_authenticated(self.user)
        resp = client.post(
            f"/api/brackets/{self.bracket.id}/enter/",
            {"video_id": self.video.id},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_enter_bracket_not_registration_400(self):
        """Iscrizione a bracket non in registration ritorna 400."""
        self.bracket.status = Bracket.Status.ACTIVE
        self.bracket.save()

        client = create_api_client_authenticated(self.user)
        resp = client.post(
            f"/api/brackets/{self.bracket.id}/enter/",
            {"video_id": self.video.id},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enter_bracket_full_400(self):
        """Iscrizione a bracket pieno ritorna 400."""
        # Riempi il bracket (max_participants=4)
        for i in range(4):
            u = create_authenticated_user(username=f"filler{i}")
            v = create_sample_video(uploader=u, title=f"Fill Video {i}")
            ContestEntry.objects.create(bracket=self.bracket, user=u, video=v)

        client = create_api_client_authenticated(self.user)
        resp = client.post(
            f"/api/brackets/{self.bracket.id}/enter/",
            {"video_id": self.video.id},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enter_bracket_unauthenticated_401(self):
        """Iscrizione senza autenticazione ritorna 401."""
        client = APIClient()
        resp = client.post(
            f"/api/brackets/{self.bracket.id}/enter/",
            {"video_id": self.video.id},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_enter_bracket_invalid_video_400(self):
        """Iscrizione con video_id inesistente ritorna 400."""
        client = create_api_client_authenticated(self.user)
        resp = client.post(
            f"/api/brackets/{self.bracket.id}/enter/",
            {"video_id": 99999},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Video non trovato", resp.data["detail"])


class VoteMatchupTest(TestCase):
    """Test POST /api/matchups/{id}/vote/ (AC #2)."""

    def setUp(self):
        self.creator = create_authenticated_user(username="vote_creator")
        self.bracket = Bracket.objects.create(
            name="Vote Bracket",
            max_participants=8,
            created_by=self.creator,
        )
        # Crea 4 entry e genera bracket
        self.entries = []
        for i in range(4):
            user = create_authenticated_user(username=f"vote_player{i}")
            video = create_sample_video(uploader=user, title=f"Vote Video {i}")
            entry = ContestEntry.objects.create(
                bracket=self.bracket, user=user, video=video
            )
            self.entries.append(entry)

        with patch("cs_clips.utils.bracket_logic.random.shuffle"):
            generate_bracket(self.bracket)

        self.matchup = Matchup.objects.filter(
            bracket=self.bracket, round_number=1, is_completed=False
        ).first()
        self.voter = create_authenticated_user(username="voter")

    def test_vote_matchup_201(self):
        """Voto valido crea MatchupVote e risponde 201."""
        client = create_api_client_authenticated(self.voter)
        resp = client.post(
            f"/api/matchups/{self.matchup.id}/vote/",
            {"entry": self.matchup.entry_1.id, "value": 4},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            MatchupVote.objects.filter(matchup=self.matchup, user=self.voter).exists()
        )

    def test_vote_matchup_duplicate_409(self):
        """Voto duplicato ritorna 409."""
        MatchupVote.objects.create(
            matchup=self.matchup,
            user=self.voter,
            entry=self.matchup.entry_1,
            value=3,
        )
        client = create_api_client_authenticated(self.voter)
        resp = client.post(
            f"/api/matchups/{self.matchup.id}/vote/",
            {"entry": self.matchup.entry_1.id, "value": 5},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_vote_completed_matchup_400(self):
        """Voto su matchup completato ritorna 400."""
        self.matchup.is_completed = True
        self.matchup.winner = self.matchup.entry_1
        self.matchup.save()

        client = create_api_client_authenticated(self.voter)
        resp = client.post(
            f"/api/matchups/{self.matchup.id}/vote/",
            {"entry": self.matchup.entry_1.id, "value": 3},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_vote_wrong_entry_400(self):
        """Voto per entry non appartenente al matchup ritorna 400."""
        # Prendi un'entry da un altro matchup
        other_matchup = (
            Matchup.objects.filter(
                bracket=self.bracket, round_number=1, is_completed=False
            )
            .exclude(id=self.matchup.id)
            .first()
        )
        wrong_entry = other_matchup.entry_1

        client = create_api_client_authenticated(self.voter)
        resp = client.post(
            f"/api/matchups/{self.matchup.id}/vote/",
            {"entry": wrong_entry.id, "value": 3},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_vote_value_out_of_range_400(self):
        """Voto fuori range 1-5 ritorna 400."""
        client = create_api_client_authenticated(self.voter)

        resp = client.post(
            f"/api/matchups/{self.matchup.id}/vote/",
            {"entry": self.matchup.entry_1.id, "value": 0},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        resp = client.post(
            f"/api/matchups/{self.matchup.id}/vote/",
            {"entry": self.matchup.entry_1.id, "value": 6},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_vote_unauthenticated_401(self):
        """Voto senza autenticazione ritorna 401."""
        client = APIClient()
        resp = client.post(
            f"/api/matchups/{self.matchup.id}/vote/",
            {"entry": self.matchup.entry_1.id, "value": 3},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class CloseMatchupTest(TestCase):
    """Test POST /api/matchups/{id}/close/ (AC #3)."""

    def setUp(self):
        self.admin = create_admin_user(username="close_admin")
        self.bracket = Bracket.objects.create(
            name="Close Bracket",
            max_participants=8,
            created_by=self.admin,
        )
        self.entries = []
        for i in range(4):
            user = create_authenticated_user(username=f"close_player{i}")
            video = create_sample_video(uploader=user, title=f"Close Video {i}")
            entry = ContestEntry.objects.create(
                bracket=self.bracket, user=user, video=video
            )
            self.entries.append(entry)

        with patch("cs_clips.utils.bracket_logic.random.shuffle"):
            generate_bracket(self.bracket)

        self.matchup = Matchup.objects.filter(
            bracket=self.bracket, round_number=1, is_completed=False
        ).first()

    def test_close_matchup_admin_200(self):
        """Admin chiude matchup: 200, vincitore assegnato."""
        # Aggiungi voti
        voter1 = create_authenticated_user(username="close_voter1")
        voter2 = create_authenticated_user(username="close_voter2")
        MatchupVote.objects.create(
            matchup=self.matchup,
            user=voter1,
            entry=self.matchup.entry_1,
            value=5,
        )
        MatchupVote.objects.create(
            matchup=self.matchup,
            user=voter2,
            entry=self.matchup.entry_2,
            value=3,
        )

        client = create_api_client_authenticated(self.admin)
        resp = client.post(f"/api/matchups/{self.matchup.id}/close/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("winner_entry_id", resp.data)
        self.assertEqual(resp.data["winner_entry_id"], self.matchup.entry_1.id)

        self.matchup.refresh_from_db()
        self.assertTrue(self.matchup.is_completed)
        self.assertEqual(self.matchup.winner, self.matchup.entry_1)

    def test_close_matchup_advances_winner(self):
        """Vincitore avanza al turno successivo."""
        voter = create_authenticated_user(username="adv_voter")
        MatchupVote.objects.create(
            matchup=self.matchup,
            user=voter,
            entry=self.matchup.entry_1,
            value=5,
        )

        client = create_api_client_authenticated(self.admin)
        client.post(f"/api/matchups/{self.matchup.id}/close/")

        # Verifica avanzamento al turno 2
        next_matchup = Matchup.objects.get(
            bracket=self.bracket,
            round_number=2,
            position=self.matchup.position // 2,
        )
        if self.matchup.position % 2 == 0:
            self.assertEqual(next_matchup.entry_1, self.matchup.entry_1)
        else:
            self.assertEqual(next_matchup.entry_2, self.matchup.entry_1)

    def test_close_matchup_non_admin_403(self):
        """Utente non admin riceve 403."""
        user = create_authenticated_user(username="non_admin_closer")
        client = create_api_client_authenticated(user)
        resp = client.post(f"/api/matchups/{self.matchup.id}/close/")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_close_matchup_tie_entry1_wins(self):
        """In caso di parita', entry_1 vince (FR43b)."""
        voter1 = create_authenticated_user(username="tie_voter1")
        voter2 = create_authenticated_user(username="tie_voter2")
        MatchupVote.objects.create(
            matchup=self.matchup,
            user=voter1,
            entry=self.matchup.entry_1,
            value=4,
        )
        MatchupVote.objects.create(
            matchup=self.matchup,
            user=voter2,
            entry=self.matchup.entry_2,
            value=4,
        )

        client = create_api_client_authenticated(self.admin)
        resp = client.post(f"/api/matchups/{self.matchup.id}/close/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["winner_entry_id"], self.matchup.entry_1.id)

    def test_close_final_matchup_bracket_completed(self):
        """Chiusura ultimo matchup → bracket diventa 'completed'."""
        # Chiudi tutti i matchup del turno 1
        r1_matchups = Matchup.objects.filter(
            bracket=self.bracket, round_number=1, is_completed=False
        )
        client = create_api_client_authenticated(self.admin)

        for m in r1_matchups:
            voter = create_authenticated_user(username=f"final_voter_{m.id}")
            MatchupVote.objects.create(
                matchup=m,
                user=voter,
                entry=m.entry_1,
                value=5,
            )
            client.post(f"/api/matchups/{m.id}/close/")

        # Ora chiudi il matchup del turno 2 (finale)
        finale = Matchup.objects.get(bracket=self.bracket, round_number=2, position=0)
        voter = create_authenticated_user(username="finale_voter")
        MatchupVote.objects.create(
            matchup=finale,
            user=voter,
            entry=finale.entry_1,
            value=5,
        )
        resp = client.post(f"/api/matchups/{finale.id}/close/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.bracket.refresh_from_db()
        self.assertEqual(self.bracket.status, Bracket.Status.COMPLETED)

    def test_close_matchup_creates_bracket_turn_notification(self):
        """Chiusura matchup crea notifica bracket_turn per prossimo matchup."""
        # Chiudi primo matchup del turno 1
        voter = create_authenticated_user(username="notif_voter")
        MatchupVote.objects.create(
            matchup=self.matchup,
            user=voter,
            entry=self.matchup.entry_1,
            value=5,
        )
        client = create_api_client_authenticated(self.admin)
        client.post(f"/api/matchups/{self.matchup.id}/close/")

        # Chiudi anche l'altro matchup del turno 1 per popolare il prossimo matchup
        other_matchup = Matchup.objects.filter(
            bracket=self.bracket, round_number=1, is_completed=False
        ).first()
        if other_matchup:
            voter2 = create_authenticated_user(username="notif_voter2")
            MatchupVote.objects.create(
                matchup=other_matchup,
                user=voter2,
                entry=other_matchup.entry_1,
                value=5,
            )
            client.post(f"/api/matchups/{other_matchup.id}/close/")

            # Verifica notifica bracket_turn
            notifs = Notification.objects.filter(type="bracket_turn")
            self.assertTrue(notifs.exists())

    def test_close_matchup_no_votes_400(self):
        """Chiusura matchup senza voti ritorna 400."""
        client = create_api_client_authenticated(self.admin)
        resp = client.post(f"/api/matchups/{self.matchup.id}/close/")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nessun voto", resp.data["detail"])


class MatchupVoteModelTest(TestCase):
    """Test per il modello MatchupVote."""

    def setUp(self):
        self.creator = create_authenticated_user(username="mv_creator")
        self.bracket = Bracket.objects.create(
            name="MV Bracket",
            max_participants=8,
            created_by=self.creator,
        )
        self.user1 = create_authenticated_user(username="mv_p1")
        self.user2 = create_authenticated_user(username="mv_p2")
        self.video1 = create_sample_video(uploader=self.user1, title="MV V1")
        self.video2 = create_sample_video(uploader=self.user2, title="MV V2")
        self.entry1 = ContestEntry.objects.create(
            bracket=self.bracket, user=self.user1, video=self.video1
        )
        self.entry2 = ContestEntry.objects.create(
            bracket=self.bracket, user=self.user2, video=self.video2
        )
        self.matchup = Matchup.objects.create(
            bracket=self.bracket,
            round_number=1,
            position=0,
            entry_1=self.entry1,
            entry_2=self.entry2,
        )
        self.voter = create_authenticated_user(username="mv_voter")

    def test_create_matchup_vote(self):
        """Crea MatchupVote e verifica campi."""
        vote = MatchupVote.objects.create(
            matchup=self.matchup,
            user=self.voter,
            entry=self.entry1,
            value=4,
        )
        self.assertEqual(vote.matchup, self.matchup)
        self.assertEqual(vote.user, self.voter)
        self.assertEqual(vote.entry, self.entry1)
        self.assertEqual(vote.value, 4)
        self.assertIsNotNone(vote.created_at)

    def test_unique_together_matchup_user(self):
        """Un utente puo' votare solo una volta per matchup."""
        MatchupVote.objects.create(
            matchup=self.matchup, user=self.voter, entry=self.entry1, value=3
        )
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            MatchupVote.objects.create(
                matchup=self.matchup, user=self.voter, entry=self.entry2, value=5
            )

    def test_str(self):
        """__str__ include valore, utente e matchup ID."""
        vote = MatchupVote.objects.create(
            matchup=self.matchup, user=self.voter, entry=self.entry1, value=5
        )
        self.assertIn("5", str(vote))
        self.assertIn(str(self.voter), str(vote))
