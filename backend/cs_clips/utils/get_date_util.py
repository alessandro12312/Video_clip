# classe utility per gestire le date dei contest settimanali

import datetime

from django.utils import timezone

from cs_clips.models import Contest

# Lista dei mesi
MESI_ITALIANO = [
    "gennaio",
    "febbraio",
    "marzo",
    "aprile",
    "maggio",
    "giugno",
    "luglio",
    "agosto",
    "settembre",
    "ottobre",
    "novembre",
    "dicembre",
]


def get_or_create_current_contest(tag):
    """
    Restituisce il contest settimanale attivo, o lo crea
    se non esiste o è stato già chiuso.
    La settimana inizia di lunedì e finisce di sabato
    (chiusura prevista il sabato).
    Il nome è generato come: anno, mese, numero settimana, tag.
    Esempio: 2025giugno2clutch
    Se c'è più di un contest per la stessa settimana (chiusura anticipata),
    aggiunge un suffisso progressivo
    (es: 2025giugno2clutch).
    """

    today = timezone.now().date()
    # Calcola il lunedì della settimana corrente
    start_of_week = today - datetime.timedelta(days=today.weekday())
    # Contest disponibili fino a sabato incluso (5 giorni dopo lunedì)
    end_of_week = start_of_week + datetime.timedelta(days=5)

    # Calcola anno e mese
    anno = start_of_week.year
    mese_idx = start_of_week.month - 1  # indice per lista MESI_ITALIANO
    mese_nome = MESI_ITALIANO[mese_idx]

    # Calcola il numero della settimana del mese
    # La settimana parte da lunedì
    first_day_month = start_of_week.replace(day=1)
    first_day_weekday = first_day_month.weekday()
    delta_days = (start_of_week - first_day_month).days
    week_number = (delta_days + first_day_weekday) // 7

    base_nome = f"{anno}{mese_nome}{week_number}{tag}"

    # Cerchiamo tutti i contest della stessa settimana
    contest_settimanali = Contest.objects.filter(
        start_date=start_of_week, end_date=end_of_week, tag=tag
    ).order_by("id")

    # Prendiamo l'ultimo contest (se c'è)
    contest_corrente = (
        contest_settimanali.last() if contest_settimanali.exists() else None
    )

    if contest_corrente and not contest_corrente.is_closed:
        # Esiste ed è ancora aperto → ritorna questo
        return contest_corrente

    # Se non c'è nessun contest, o quello esistente è chiuso,
    # calcoliamo il suffisso numerico
    count = contest_settimanali.count() + 1 if contest_settimanali.exists() else 1
    nome_contest = base_nome if count == 1 else f"{base_nome}({count})"

    contest = Contest.objects.create(
        start_date=start_of_week, end_date=end_of_week, name=nome_contest, tag=tag
    )
    return contest
