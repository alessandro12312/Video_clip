"""Test per upload video con validazione completa (Story 2.1).

Copre: AC-1 (allow_download), AC-2 (durata), AC-3 (formato),
AC-4 (dimensione), AC-5 (file corrotto), AC-6 (permessi), AC-8 (shape risposta).
"""

import shutil
import tempfile
from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from cs_clips.tests.conftest import (
    create_api_client_authenticated,
    create_authenticated_user,
    create_toconfirm_user,
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


def _mock_moviepy(duration=30):
    """Crea mock di VideoFileClip con durata specifica (context manager)."""
    mock_clip = MagicMock()
    mock_clip.duration = duration
    mock_clip.__enter__ = MagicMock(return_value=mock_clip)
    mock_clip.__exit__ = MagicMock(return_value=False)
    return mock_clip


def _valid_video_file(name="test.mp4", content_type="video/mp4", size=1024):
    """Crea SimpleUploadedFile valido per test upload."""
    content = b"x" * size
    return SimpleUploadedFile(name, content, content_type=content_type)


MOCK_FILE_URL = "http://mock-minio/video/test.mp4"


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
    MEDIA_ROOT=TEMP_MEDIA_ROOT,
)
class TestUploadValidation(APITestCase):
    """Test validazione upload video (AC-1 → AC-8)."""

    def setUp(self):
        self.user = create_authenticated_user()
        self.client = create_api_client_authenticated(self.user)
        self.url = "/api/videos/"

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def _upload_data(self, **overrides):
        """Dati base per upload video valido."""
        data = {
            "title": "Test Clip",
            "tag": "clutch",
            "file": _valid_video_file(),
        }
        data.update(overrides)
        return data

    # ------------------------------------------------------------------ #
    #  AC-1: Upload video valido con campo allow_download                 #
    # ------------------------------------------------------------------ #

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer.get_file_url",
        return_value=MOCK_FILE_URL,
    )
    @patch("cs_clips.api.videos.video_serializers.VideoFileClip")
    def test_upload_valid_video_201(self, mock_vfc, _mock_url):
        """Upload video valido → 201, con allow_download, views, duration."""
        mock_vfc.return_value = _mock_moviepy(30)
        data = self._upload_data(allow_download=True)
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["allow_download"])
        self.assertEqual(response.data["views"], 0)
        self.assertEqual(response.data["duration"], 30)

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer.get_file_url",
        return_value=MOCK_FILE_URL,
    )
    @patch("cs_clips.api.videos.video_serializers.VideoFileClip")
    def test_upload_allow_download_false(self, mock_vfc, _mock_url):
        """allow_download=false → campo salvato correttamente."""
        mock_vfc.return_value = _mock_moviepy(30)
        data = self._upload_data(allow_download=False)
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data["allow_download"])

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer.get_file_url",
        return_value=MOCK_FILE_URL,
    )
    @patch("cs_clips.api.videos.video_serializers.VideoFileClip")
    def test_upload_allow_download_default_true(self, mock_vfc, _mock_url):
        """allow_download non specificato → default True dal modello."""
        mock_vfc.return_value = _mock_moviepy(30)
        data = self._upload_data()
        # Non invio allow_download → default True
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["allow_download"])

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer.get_file_url",
        return_value=MOCK_FILE_URL,
    )
    @patch("cs_clips.api.videos.video_serializers.VideoFileClip")
    def test_upload_associates_contest(self, mock_vfc, _mock_url):
        """Upload video auto-associa al contest corrente per quel tag (AC-1)."""
        mock_vfc.return_value = _mock_moviepy(30)
        data = self._upload_data()
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data["contest"])
        self.assertIsInstance(response.data["contest"], int)

    # ------------------------------------------------------------------ #
    #  AC-2: Validazione durata — reject automatico                       #
    # ------------------------------------------------------------------ #

    @patch("cs_clips.api.videos.video_serializers.VideoFileClip")
    def test_duration_too_short_400(self, mock_vfc):
        """Durata < 10s → 400 con messaggio specifico."""
        mock_vfc.return_value = _mock_moviepy(5)
        data = self._upload_data()
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "La durata del video deve essere tra 10 secondi e 1 minuto",
        )

    @patch("cs_clips.api.videos.video_serializers.VideoFileClip")
    def test_duration_too_long_400(self, mock_vfc):
        """Durata > 60s → 400 con messaggio specifico."""
        mock_vfc.return_value = _mock_moviepy(90)
        data = self._upload_data()
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "La durata del video deve essere tra 10 secondi e 1 minuto",
        )

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer.get_file_url",
        return_value=MOCK_FILE_URL,
    )
    @patch("cs_clips.api.videos.video_serializers.VideoFileClip")
    def test_duration_boundary_10s_accepted(self, mock_vfc, _mock_url):
        """Durata esattamente 10s → 201 (limite inferiore)."""
        mock_vfc.return_value = _mock_moviepy(10)
        data = self._upload_data()
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer.get_file_url",
        return_value=MOCK_FILE_URL,
    )
    @patch("cs_clips.api.videos.video_serializers.VideoFileClip")
    def test_duration_boundary_60s_accepted(self, mock_vfc, _mock_url):
        """Durata esattamente 60s → 201 (limite superiore)."""
        mock_vfc.return_value = _mock_moviepy(60)
        data = self._upload_data()
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # ------------------------------------------------------------------ #
    #  AC-3: Validazione formato — reject automatico                      #
    # ------------------------------------------------------------------ #

    def test_format_unsupported_extension_400(self):
        """File con estensione non supportata (.gif) → 400."""
        data = self._upload_data(
            file=SimpleUploadedFile("test.gif", b"fake", content_type="image/gif")
        )
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Formato non supportato. Formati accettati: MP4, MOV, AVI, MKV, WebM",
        )

    def test_format_wrong_content_type_400(self):
        """File con content_type non video (image/png rinominato .mp4) → 400."""
        data = self._upload_data(
            file=SimpleUploadedFile("test.mp4", b"fake", content_type="image/png")
        )
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Formato non supportato. Formati accettati: MP4, MOV, AVI, MKV, WebM",
        )

    # ------------------------------------------------------------------ #
    #  AC-4: Validazione dimensione file                                  #
    # ------------------------------------------------------------------ #

    @patch(
        "cs_clips.api.videos.video_serializers.VideoInputSerializer.MAX_FILE_SIZE",
        10,
    )
    def test_file_too_large_400(self):
        """File > MAX_FILE_SIZE → 400 con messaggio specifico."""
        # 20 byte > MAX_FILE_SIZE (patchato a 10)
        big_file = SimpleUploadedFile("test.mp4", b"x" * 20, content_type="video/mp4")
        data = self._upload_data(file=big_file)
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Il file supera la dimensione massima di 500MB",
        )

    # ------------------------------------------------------------------ #
    #  AC-5: File corrotto o codec non supportato                         #
    # ------------------------------------------------------------------ #

    @patch("cs_clips.api.videos.video_serializers.VideoFileClip")
    def test_corrupt_file_moviepy_exception_400(self, mock_vfc):
        """File corrotto — MoviePy non riesce a leggere → 400."""
        mock_vfc.side_effect = Exception("Codec not found")
        data = self._upload_data()
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["detail"],
            "Impossibile leggere i metadati del video. "
            "Verifica che il file non sia corrotto",
        )

    # ------------------------------------------------------------------ #
    #  AC-6: Permessi — solo utenti confermati possono caricare           #
    # ------------------------------------------------------------------ #

    def test_toconfirm_user_forbidden_403(self):
        """Utente toconfirm tenta upload → 403."""
        toconfirm = create_toconfirm_user()
        client = create_api_client_authenticated(toconfirm)
        data = {
            "title": "Test",
            "tag": "clutch",
            "file": _valid_video_file(),
        }
        response = client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_unauthorized_401(self):
        """Utente non autenticato tenta upload → 401."""
        anon_client = APIClient()
        data = {
            "title": "Test",
            "tag": "clutch",
            "file": _valid_video_file(),
        }
        response = anon_client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------------------------------------------------ #
    #  AC-8: Shape risposta — tutti i campi del tipo Video frontend       #
    # ------------------------------------------------------------------ #

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer.get_file_url",
        return_value=MOCK_FILE_URL,
    )
    @patch("cs_clips.api.videos.video_serializers.VideoFileClip")
    def test_response_shape_all_frontend_fields(self, mock_vfc, _mock_url):
        """Risposta 201 contiene tutti i campi del tipo Video frontend."""
        mock_vfc.return_value = _mock_moviepy(30)
        data = self._upload_data()
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        expected_fields = {
            "id",
            "title",
            "file",
            "file_url",
            "uploader",
            "average_rating",
            "views",
            "tag",
            "duration",
            "allow_download",
            "contest",
            "created_at",
            "updated_at",
        }
        self.assertEqual(set(response.data.keys()), expected_fields)

        # Verifica tipi specifici
        self.assertIsInstance(response.data["allow_download"], bool)
        self.assertIsInstance(response.data["views"], int)
        self.assertEqual(response.data["views"], 0)
        self.assertIsInstance(response.data["average_rating"], float)
        self.assertEqual(response.data["average_rating"], 0.0)
        self.assertEqual(response.data["uploader"], self.user.username)
