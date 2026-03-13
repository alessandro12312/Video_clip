"""Test per modelli Bracket, ContestEntry, Matchup e logica bracket."""

from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from cs_clips.models import Bracket, ContestEntry, Matchup
from cs_clips.tests.conftest import (
    create_authenticated_user,
    create_sample_video,
)
from cs_clips.utils.bracket_logic import (
    advance_winner,
    close_matchup,
    generate_bracket,
)


class BracketModelTest(TestCase):
    """Test per il modello Bracket (AC #1)."""

    def setUp(self):
        self.user = create_authenticated_user(
            username="bracket_creator",
        )

    def test_create_bracket_with_all_fields(self):
        """Crea un bracket con tutti i campi e verifica valori."""
        bracket = Bracket.objects.create(
            name="Torneo Primavera",
            description="Torneo di primavera 2026",
            status=Bracket.Status.REGISTRATION,
            max_participants=16,
            created_by=self.user,
            prize_description="Medaglia d'oro",
        )
        self.assertEqual(bracket.name, "Torneo Primavera")
        self.assertEqual(bracket.description, "Torneo di primavera 2026")
        self.assertEqual(bracket.status, Bracket.Status.REGISTRATION)
        self.assertEqual(bracket.max_participants, 16)
        self.assertEqual(bracket.current_round, 1)
        self.assertEqual(bracket.created_by, self.user)
        self.assertIsNotNone(bracket.created_at)
        self.assertEqual(bracket.prize_description, "Medaglia d'oro")

    def test_bracket_str(self):
        """__str__ ritorna il nome del bracket."""
        bracket = Bracket.objects.create(
            name="Torneo Test",
            max_participants=8,
            created_by=self.user,
        )
        self.assertEqual(str(bracket), "Torneo Test")

    def test_bracket_status_choices(self):
        """Verifica che Status TextChoices contenga i 3 valori."""
        choices = [c[0] for c in Bracket.Status.choices]
        self.assertIn("registration", choices)
        self.assertIn("active", choices)
        self.assertIn("completed", choices)

    def test_bracket_ordering(self):
        """Bracket ordinati per -created_at."""
        b1 = Bracket.objects.create(
            name="Primo",
            max_participants=4,
            created_by=self.user,
        )
        b2 = Bracket.objects.create(
            name="Secondo",
            max_participants=4,
            created_by=self.user,
        )
        brackets = list(Bracket.objects.all())
        self.assertEqual(brackets[0], b2)
        self.assertEqual(brackets[1], b1)

    def test_bracket_default_status(self):
        """Status di default e' 'registration'."""
        bracket = Bracket.objects.create(
            name="Default Test",
            max_participants=4,
            created_by=self.user,
        )
        self.assertEqual(bracket.status, Bracket.Status.REGISTRATION)


class ContestEntryModelTest(TestCase):
    """Test per il modello ContestEntry (AC #2)."""

    def setUp(self):
        self.creator = create_authenticated_user(username="creator")
        self.participant = create_authenticated_user(
            username="participant",
        )
        self.bracket = Bracket.objects.create(
            name="Torneo Entry Test",
            max_participants=8,
            created_by=self.creator,
        )
        self.video = create_sample_video(
            uploader=self.participant,
        )

    def test_create_contest_entry(self):
        """Crea una ContestEntry e verifica campi."""
        entry = ContestEntry.objects.create(
            bracket=self.bracket,
            user=self.participant,
            video=self.video,
        )
        self.assertEqual(entry.bracket, self.bracket)
        self.assertEqual(entry.user, self.participant)
        self.assertEqual(entry.video, self.video)
        self.assertIsNotNone(entry.created_at)

    def test_unique_together_bracket_user(self):
        """Un utente non puo' iscriversi due volte."""
        ContestEntry.objects.create(
            bracket=self.bracket,
            user=self.participant,
            video=self.video,
        )
        video2 = create_sample_video(uploader=self.participant, title="Video 2")
        with self.assertRaises(IntegrityError):
            ContestEntry.objects.create(
                bracket=self.bracket,
                user=self.participant,
                video=video2,
            )


class MatchupModelTest(TestCase):
    """Test per il modello Matchup (AC #3)."""

    def setUp(self):
        self.creator = create_authenticated_user(
            username="mcreator",
        )
        self.bracket = Bracket.objects.create(
            name="Torneo Matchup Test",
            max_participants=8,
            created_by=self.creator,
        )

    def test_create_matchup(self):
        """Crea un matchup e verifica campi."""
        matchup = Matchup.objects.create(
            bracket=self.bracket,
            round_number=1,
            position=0,
        )
        self.assertEqual(matchup.bracket, self.bracket)
        self.assertEqual(matchup.round_number, 1)
        self.assertEqual(matchup.position, 0)
        self.assertIsNone(matchup.entry_1)
        self.assertIsNone(matchup.entry_2)
        self.assertIsNone(matchup.winner)
        self.assertFalse(matchup.is_completed)

    def test_unique_together_bracket_round_position(self):
        """Stessa posizione nello stesso turno non consentita."""
        Matchup.objects.create(bracket=self.bracket, round_number=1, position=0)
        with self.assertRaises(IntegrityError):
            Matchup.objects.create(
                bracket=self.bracket,
                round_number=1,
                position=0,
            )


class GenerateBracketTest(TestCase):
    """Test per generate_bracket (AC #4)."""

    def _create_entries(self, bracket, count):
        """Helper: crea N partecipanti con entry."""
        entries = []
        for i in range(count):
            user = create_authenticated_user(
                username=f"player{i}_{bracket.pk}",
            )
            video = create_sample_video(uploader=user, title=f"Video {i}")
            entry = ContestEntry.objects.create(bracket=bracket, user=user, video=video)
            entries.append(entry)
        return entries

    def test_4_participants(self):
        """4 partecipanti: 2 matchup R1 + 1 matchup R2."""
        creator = create_authenticated_user(
            username="gen4_creator",
        )
        bracket = Bracket.objects.create(
            name="T4",
            max_participants=8,
            created_by=creator,
        )
        self._create_entries(bracket, 4)

        with patch("cs_clips.utils.bracket_logic.random.shuffle"):
            generate_bracket(bracket)

        bracket.refresh_from_db()
        self.assertEqual(bracket.status, Bracket.Status.ACTIVE)
        self.assertEqual(bracket.current_round, 1)

        r1 = Matchup.objects.filter(bracket=bracket, round_number=1)
        r2 = Matchup.objects.filter(bracket=bracket, round_number=2)
        self.assertEqual(r1.count(), 2)
        self.assertEqual(r2.count(), 1)

        # Nessun bye
        for m in r1:
            self.assertIsNotNone(m.entry_1)
            self.assertIsNotNone(m.entry_2)
            self.assertFalse(m.is_completed)

        # Turno 2 vuoto
        finale = r2.first()
        self.assertIsNone(finale.entry_1)
        self.assertIsNone(finale.entry_2)

    def test_3_participants_with_bye(self):
        """3 partecipanti: 1 bye + 2 matchup R1 + 1 R2."""
        creator = create_authenticated_user(
            username="gen3_creator",
        )
        bracket = Bracket.objects.create(
            name="T3",
            max_participants=8,
            created_by=creator,
        )
        self._create_entries(bracket, 3)

        with patch("cs_clips.utils.bracket_logic.random.shuffle"):
            generate_bracket(bracket)

        bracket.refresh_from_db()
        self.assertEqual(bracket.status, Bracket.Status.ACTIVE)

        r1 = Matchup.objects.filter(bracket=bracket, round_number=1)
        r2 = Matchup.objects.filter(bracket=bracket, round_number=2)
        self.assertEqual(r1.count(), 2)
        self.assertEqual(r2.count(), 1)

        # 1 bye nel turno 1
        bye_matchups = r1.filter(is_completed=True, entry_2__isnull=True)
        self.assertEqual(bye_matchups.count(), 1)

        # Bye ha avanzato vincitore al turno 2
        finale = r2.first()
        self.assertIsNotNone(finale.entry_1)

    def test_8_participants(self):
        """8 partecipanti: 4 R1 + 2 R2 + 1 finale."""
        creator = create_authenticated_user(
            username="gen8_creator",
        )
        bracket = Bracket.objects.create(
            name="T8",
            max_participants=16,
            created_by=creator,
        )
        self._create_entries(bracket, 8)

        with patch("cs_clips.utils.bracket_logic.random.shuffle"):
            generate_bracket(bracket)

        r1 = Matchup.objects.filter(bracket=bracket, round_number=1)
        r2 = Matchup.objects.filter(bracket=bracket, round_number=2)
        r3 = Matchup.objects.filter(bracket=bracket, round_number=3)
        self.assertEqual(r1.count(), 4)
        self.assertEqual(r2.count(), 2)
        self.assertEqual(r3.count(), 1)

        # Nessun bye con 8 partecipanti (potenza di 2)
        bye_count = r1.filter(is_completed=True).count()
        self.assertEqual(bye_count, 0)

    def test_less_than_2_participants_raises_error(self):
        """Meno di 2 partecipanti → ValidationError."""
        creator = create_authenticated_user(
            username="gen1_creator",
        )
        bracket = Bracket.objects.create(
            name="T1",
            max_participants=8,
            created_by=creator,
        )
        self._create_entries(bracket, 1)

        with self.assertRaises(ValidationError) as ctx:
            generate_bracket(bracket)
        self.assertIn("almeno 2", str(ctx.exception))

    def test_bracket_not_in_registration_raises_error(self):
        """Bracket non in 'registration' → ValidationError."""
        creator = create_authenticated_user(
            username="genactive_creator",
        )
        bracket = Bracket.objects.create(
            name="T_active",
            max_participants=8,
            created_by=creator,
            status=Bracket.Status.ACTIVE,
        )
        self._create_entries(bracket, 4)

        with self.assertRaises(ValidationError) as ctx:
            generate_bracket(bracket)
        self.assertIn("registration", str(ctx.exception))


class AdvanceWinnerTest(TestCase):
    """Test per advance_winner (AC #5)."""

    def test_winner_advances_to_correct_matchup(self):
        """Vincitore avanza al matchup corretto."""
        creator = create_authenticated_user(
            username="adv_creator",
        )
        bracket = Bracket.objects.create(
            name="T_adv",
            max_participants=8,
            created_by=creator,
        )

        # Crea 4 entry
        entries = []
        for i in range(4):
            user = create_authenticated_user(
                username=f"adv_player{i}",
            )
            video = create_sample_video(uploader=user, title=f"Adv Video {i}")
            entry = ContestEntry.objects.create(bracket=bracket, user=user, video=video)
            entries.append(entry)

        with patch("cs_clips.utils.bracket_logic.random.shuffle"):
            generate_bracket(bracket)

        # Chiudi matchup pos 0 turno 1 — entry_1 vince
        m0 = Matchup.objects.get(bracket=bracket, round_number=1, position=0)
        close_matchup(m0, m0.entry_1)

        # 0 % 2 == 0 → entry_1
        finale = Matchup.objects.get(bracket=bracket, round_number=2, position=0)
        self.assertEqual(finale.entry_1, m0.entry_1)

        # Chiudi matchup pos 1 turno 1 — entry_2 vince
        m1 = Matchup.objects.get(bracket=bracket, round_number=1, position=1)
        close_matchup(m1, m1.entry_2)

        # 1 % 2 == 1 → entry_2
        finale.refresh_from_db()
        self.assertEqual(finale.entry_2, m1.entry_2)


class CloseMatchupTest(TestCase):
    """Test per close_matchup e completamento bracket."""

    def test_last_matchup_completes_bracket(self):
        """Ultimo matchup → bracket 'completed'."""
        creator = create_authenticated_user(
            username="close_creator",
        )
        bracket = Bracket.objects.create(
            name="T_close",
            max_participants=4,
            created_by=creator,
        )

        entries = []
        for i in range(2):
            user = create_authenticated_user(
                username=f"close_player{i}",
            )
            video = create_sample_video(uploader=user, title=f"Close Video {i}")
            entry = ContestEntry.objects.create(bracket=bracket, user=user, video=video)
            entries.append(entry)

        with patch("cs_clips.utils.bracket_logic.random.shuffle"):
            generate_bracket(bracket)

        m = Matchup.objects.get(bracket=bracket, round_number=1, position=0)
        close_matchup(m, m.entry_1)

        bracket.refresh_from_db()
        self.assertEqual(bracket.status, Bracket.Status.COMPLETED)


class AdvanceWinnerNoWinnerTest(TestCase):
    """Test per advance_winner senza vincitore."""

    def test_advance_winner_without_winner_raises_error(self):
        """advance_winner senza winner → ValidationError."""
        creator = create_authenticated_user(username="nw_creator")
        bracket = Bracket.objects.create(
            name="T_no_winner",
            max_participants=8,
            created_by=creator,
        )
        matchup = Matchup.objects.create(
            bracket=bracket,
            round_number=1,
            position=0,
        )
        with self.assertRaises(ValidationError) as ctx:
            advance_winner(matchup)
        self.assertIn("vincitore", str(ctx.exception))


class CloseMatchupInvalidWinnerTest(TestCase):
    """Test per close_matchup con vincitore non valido."""

    def test_close_matchup_with_invalid_winner_raises_error(self):
        """close_matchup con winner non appartenente al matchup → ValidationError."""
        creator = create_authenticated_user(username="inv_creator")
        bracket = Bracket.objects.create(
            name="T_invalid",
            max_participants=8,
            created_by=creator,
        )

        users = [create_authenticated_user(username=f"inv_player{i}") for i in range(3)]
        videos = [
            create_sample_video(uploader=u, title=f"Inv Video {i}")
            for i, u in enumerate(users)
        ]
        entries = [
            ContestEntry.objects.create(bracket=bracket, user=u, video=v)
            for u, v in zip(users, videos)
        ]

        matchup = Matchup.objects.create(
            bracket=bracket,
            round_number=1,
            position=0,
            entry_1=entries[0],
            entry_2=entries[1],
        )
        # entries[2] non partecipa a questo matchup
        with self.assertRaises(ValidationError) as ctx:
            close_matchup(matchup, entries[2])
        self.assertIn("partecipanti", str(ctx.exception))


class MaxParticipantsTest(TestCase):
    """Test per verifica max_participants."""

    def test_too_many_participants_raises_error(self):
        """Piu' iscritti di max_participants → ValidationError."""
        creator = create_authenticated_user(username="max_creator")
        bracket = Bracket.objects.create(
            name="T_max",
            max_participants=2,
            created_by=creator,
        )
        for i in range(4):
            user = create_authenticated_user(username=f"max_player{i}")
            video = create_sample_video(uploader=user, title=f"Max Video {i}")
            ContestEntry.objects.create(bracket=bracket, user=user, video=video)

        with self.assertRaises(ValidationError) as ctx:
            generate_bracket(bracket)
        self.assertIn("Troppi partecipanti", str(ctx.exception))


class CurrentRoundProgressionTest(TestCase):
    """Test per aggiornamento current_round durante il torneo."""

    def test_current_round_updates_when_round_complete(self):
        """current_round avanza quando tutti i matchup del turno sono completati."""
        creator = create_authenticated_user(username="round_creator")
        bracket = Bracket.objects.create(
            name="T_round",
            max_participants=8,
            created_by=creator,
        )
        for i in range(4):
            user = create_authenticated_user(username=f"round_player{i}")
            video = create_sample_video(uploader=user, title=f"Round Video {i}")
            ContestEntry.objects.create(bracket=bracket, user=user, video=video)

        with patch("cs_clips.utils.bracket_logic.random.shuffle"):
            generate_bracket(bracket)

        bracket.refresh_from_db()
        self.assertEqual(bracket.current_round, 1)

        # Chiudi tutti i matchup del turno 1
        r1_matchups = Matchup.objects.filter(bracket=bracket, round_number=1)
        for m in r1_matchups:
            close_matchup(m, m.entry_1)

        bracket.refresh_from_db()
        self.assertEqual(bracket.current_round, 2)


class AdminActionTest(TestCase):
    """Test per admin action start_bracket (AC #7)."""

    def test_start_bracket_admin_action(self):
        """Admin action avvia il torneo."""
        from django.contrib.admin.sites import AdminSite
        from django.contrib.messages.storage.fallback import (
            FallbackStorage,
        )
        from django.test import RequestFactory

        from cs_clips.admin import BracketAdmin

        creator = create_authenticated_user(
            username="admin_action_creator",
        )
        bracket = Bracket.objects.create(
            name="T_admin",
            max_participants=8,
            created_by=creator,
        )

        for i in range(4):
            user = create_authenticated_user(
                username=f"admin_player{i}",
            )
            video = create_sample_video(uploader=user, title=f"Admin Video {i}")
            ContestEntry.objects.create(bracket=bracket, user=user, video=video)

        site = AdminSite()
        admin_obj = BracketAdmin(Bracket, site)
        factory = RequestFactory()
        request = factory.post("/admin/")
        request.user = creator
        setattr(request, "session", "session")
        setattr(
            request,
            "_messages",
            FallbackStorage(request),
        )

        with patch("cs_clips.utils.bracket_logic.random.shuffle"):
            admin_obj.start_bracket(
                request,
                Bracket.objects.filter(pk=bracket.pk),
            )

        bracket.refresh_from_db()
        self.assertEqual(bracket.status, Bracket.Status.ACTIVE)
        self.assertTrue(Matchup.objects.filter(bracket=bracket).exists())
