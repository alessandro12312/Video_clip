"""Logica generazione bracket e avanzamento vincitori."""

import math
import random

from django.core.exceptions import ValidationError
from django.db import transaction


def generate_bracket(bracket):
    """Genera i matchup per un torneo a eliminazione diretta.

    - Verifica che il bracket sia in stato "registration" con almeno 2 iscritti.
    - Verifica che il numero di iscritti non superi max_participants.
    - Calcola bye per partecipanti non potenza di 2.
    - Crea matchup per tutti i turni con posizioni pre-calcolate.
    - Aggiorna lo stato del bracket a "active".
    """
    from cs_clips.models import Bracket, Matchup

    if bracket.status != Bracket.Status.REGISTRATION:
        raise ValidationError(
            "Il bracket deve essere in stato 'registration' per avviare il torneo."
        )

    entries = list(bracket.entries.all())
    n = len(entries)

    if n < 2:
        raise ValidationError("Servono almeno 2 partecipanti per avviare il torneo.")

    if n > bracket.max_participants:
        raise ValidationError(
            f"Troppi partecipanti: {n} iscritti, massimo {bracket.max_participants}."
        )

    # Calcola struttura bracket
    num_rounds = math.ceil(math.log2(n))
    bracket_size = 2**num_rounds
    num_byes = bracket_size - n

    # Shuffle casuale dei partecipanti
    random.shuffle(entries)

    # Numero matchup per turno 1
    num_matchups_round1 = bracket_size // 2

    with transaction.atomic():
        # Crea matchup turno 1
        entry_index = 0
        for pos in range(num_matchups_round1):
            if pos < num_byes:
                # Bye: solo entry_1, auto-completato
                Matchup.objects.create(
                    bracket=bracket,
                    round_number=1,
                    position=pos,
                    entry_1=entries[entry_index],
                    entry_2=None,
                    winner=entries[entry_index],
                    is_completed=True,
                )
                entry_index += 1
            else:
                # Matchup normale con 2 partecipanti
                Matchup.objects.create(
                    bracket=bracket,
                    round_number=1,
                    position=pos,
                    entry_1=entries[entry_index],
                    entry_2=entries[entry_index + 1],
                )
                entry_index += 2

        # Crea matchup vuoti per turni successivi
        for round_num in range(2, num_rounds + 1):
            num_matchups = bracket_size // (2**round_num)
            for pos in range(num_matchups):
                Matchup.objects.create(
                    bracket=bracket,
                    round_number=round_num,
                    position=pos,
                )

        # Avanza automaticamente i vincitori dei bye al turno 2
        bye_matchups = bracket.matchups.filter(round_number=1, is_completed=True)
        for matchup in bye_matchups:
            advance_winner(matchup)

        # Aggiorna stato bracket
        bracket.status = Bracket.Status.ACTIVE
        bracket.current_round = 1
        bracket.save()


def advance_winner(matchup):
    """Avanza il vincitore di un matchup al turno successivo.

    - Calcola posizione nel turno successivo: position // 2
    - Assegna a entry_1 (posizione pari) o entry_2 (posizione dispari)
    - Aggiorna current_round del bracket se tutti i matchup del turno sono completati
    - Se e' l'ultimo matchup (turno finale), marca il bracket come completato.
    """
    from cs_clips.models import Bracket

    if not matchup.winner:
        raise ValidationError("Il matchup non ha un vincitore assegnato.")

    bracket = matchup.bracket

    # Controlla se e' il turno finale
    next_round = matchup.round_number + 1
    next_matchup = bracket.matchups.filter(
        round_number=next_round,
        position=matchup.position // 2,
    ).first()

    if next_matchup is None:
        # Turno finale completato — bracket completato
        bracket.status = Bracket.Status.COMPLETED
        bracket.save()
        return

    # Assegna vincitore al matchup successivo
    if matchup.position % 2 == 0:
        next_matchup.entry_1 = matchup.winner
    else:
        next_matchup.entry_2 = matchup.winner
    next_matchup.save()

    # Aggiorna current_round se tutti i matchup del turno corrente sono completati
    round_matchups = bracket.matchups.filter(round_number=matchup.round_number)
    if not round_matchups.filter(is_completed=False).exists():
        bracket.current_round = next_round
        bracket.save()


def close_matchup(matchup, winner_entry):
    """Chiude un matchup assegnando il vincitore e propagando l'avanzamento.

    - Valida che winner_entry sia entry_1 o entry_2 del matchup
    - Imposta winner e is_completed
    - Chiama advance_winner per propagare
    """
    if winner_entry not in (matchup.entry_1, matchup.entry_2):
        raise ValidationError(
            "Il vincitore deve essere uno dei partecipanti del matchup."
        )

    with transaction.atomic():
        matchup.winner = winner_entry
        matchup.is_completed = True
        matchup.save()
        advance_winner(matchup)
