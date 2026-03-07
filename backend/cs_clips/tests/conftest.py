"""Utilita' condivise per test — helper function riusabili."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

User = get_user_model()


def create_authenticated_user(username="testuser", password="testpass123"):
    """Crea utente con gruppo 'user'.

    Requisito: ogni utente DEVE avere almeno un gruppo.
    """
    user = User.objects.create_user(
        username=username,
        password=password,
        email=f"{username}@test.com",
    )
    group, _ = Group.objects.get_or_create(name="user")
    user.groups.add(group)
    return user


def create_toconfirm_user(username="pendinguser", password="testpass123"):
    """Crea utente con gruppo 'toconfirm' (sola lettura)."""
    user = User.objects.create_user(
        username=username,
        password=password,
        email=f"{username}@test.com",
    )
    group, _ = Group.objects.get_or_create(name="toconfirm")
    user.groups.add(group)
    return user


def create_admin_user(username="adminuser", password="adminpass123"):
    """Crea utente admin con gruppo 'admin' e is_staff=True."""
    user = User.objects.create_user(
        username=username,
        password=password,
        email=f"{username}@test.com",
        is_staff=True,
    )
    group, _ = Group.objects.get_or_create(name="admin")
    user.groups.add(group)
    return user


def create_sample_video(uploader, title="Test Video", tag="clutch"):
    """Crea video con file mock (MinIO attivo richiesto).

    NOTA IMPORTANTE: Usa Video.objects.create() diretto, NON il serializer.
    Il VideoInputSerializer.create() chiama MoviePy per estrarre la durata
    dal file reale — qui passiamo un file finto (SimpleUploadedFile) e la
    durata hardcoded a 30s, bypassando MoviePy.
    Il file viene comunque salvato sul Django storage backend (MinIO),
    quindi MinIO deve essere attivo per usare questa helper.
    """
    from cs_clips.models import Video

    video_file = SimpleUploadedFile(
        "test_video.mp4",
        b"fake-video-content",
        content_type="video/mp4",
    )
    return Video.objects.create(
        uploader=uploader,
        title=title,
        tag=tag,
        file=video_file,
        duration=30,  # Hardcoded — bypassa MoviePy intenzionalmente
    )


def create_api_client_authenticated(user=None):
    """Ritorna APIClient con force_authenticate."""
    if user is None:
        user = create_authenticated_user()
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def create_sample_contest(tag="clutch"):
    """Crea contest attivo per la settimana corrente."""
    from datetime import date, timedelta

    from cs_clips.models import Contest

    today = date.today()
    # Lunedi della settimana corrente
    monday = today - timedelta(days=today.weekday())
    # Sabato della settimana corrente
    saturday = monday + timedelta(days=5)

    return Contest.objects.create(
        name=f"Contest {tag} settimanale",
        tag=tag,
        start_date=monday,
        end_date=saturday,
        is_closed=False,
    )
