"""Test per endpoint download video (Story 2.2).

Copre: AC-1 (download propria clip), AC-2 (download altrui),
AC-3 (permessi toconfirm e non autenticati), AC-6 (presigned URL fresca).
"""

import tempfile
from unittest.mock import patch

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from cs_clips.tests.conftest import (
    create_api_client_authenticated,
    create_authenticated_user,
    create_toconfirm_user,
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

MOCK_DOWNLOAD_URL = "http://minio:9000/bucket/video.mp4?presigned=download"
MOCK_FILE_URL = "http://minio:9000/bucket/video.mp4?presigned=view"


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
    MINIO_STORAGE_MEDIA_BUCKET_NAME="test-bucket",
)
class TestDownloadEndpoint(APITestCase):
    """Test endpoint GET /api/videos/{id}/download/ (AC-1, AC-2, AC-3)."""

    def setUp(self):
        from cs_clips.tests.conftest import create_sample_video

        self.owner = create_authenticated_user("owner")
        self.other_user = create_authenticated_user("other")
        self.video = create_sample_video(self.owner, title="La mia clip", tag="clutch")
        self.url = f"/api/videos/{self.video.id}/download/"

    # --- AC-1: Download propria clip ---

    @patch("cs_clips.api.videos.video_views.VideoOutputSerializer._get_minio_client")
    def test_owner_download_own_clip_returns_200(self, mock_minio):
        """Proprietario scarica la propria clip → 200 con download_url."""
        mock_minio.return_value.presigned_get_object.return_value = MOCK_DOWNLOAD_URL
        client = create_api_client_authenticated(self.owner)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("download_url", response.data)
        self.assertEqual(response.data["download_url"], MOCK_DOWNLOAD_URL)

    @patch("cs_clips.api.videos.video_views.VideoOutputSerializer._get_minio_client")
    def test_owner_download_with_allow_download_false(self, mock_minio):
        """Proprietario scarica clip con allow_download=False → 200."""
        mock_minio.return_value.presigned_get_object.return_value = MOCK_DOWNLOAD_URL
        self.video.allow_download = False
        self.video.save()

        client = create_api_client_authenticated(self.owner)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("download_url", response.data)

    # --- AC-2: Download clip altrui ---

    @patch("cs_clips.api.videos.video_views.VideoOutputSerializer._get_minio_client")
    def test_other_user_download_with_allow_download_true(self, mock_minio):
        """Altro utente scarica clip con allow_download=True → 200."""
        mock_minio.return_value.presigned_get_object.return_value = MOCK_DOWNLOAD_URL
        client = create_api_client_authenticated(self.other_user)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("download_url", response.data)

    @patch("cs_clips.api.videos.video_views.VideoOutputSerializer._get_minio_client")
    def test_other_user_download_with_allow_download_false(self, mock_minio):
        """Altro utente scarica clip con allow_download=False → 403."""
        self.video.allow_download = False
        self.video.save()

        client = create_api_client_authenticated(self.other_user)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["detail"],
            "Il download non è abilitato per questa clip",
        )
        # MinIO non deve essere chiamato
        mock_minio.return_value.presigned_get_object.assert_not_called()

    # --- AC-3: Permessi download ---

    def test_unauthenticated_user_download_returns_401(self):
        """Utente non autenticato → 401."""
        client = APIClient()
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_toconfirm_user_download_returns_403(self):
        """Utente toconfirm → 403 (download è azione privilegiata)."""
        toconfirm = create_toconfirm_user()
        client = create_api_client_authenticated(toconfirm)
        response = client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Casi limite ---

    def test_download_nonexistent_video_returns_404(self):
        """Download video inesistente → 404."""
        client = create_api_client_authenticated(self.owner)
        response = client.get("/api/videos/99999/download/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("cs_clips.api.videos.video_views.VideoOutputSerializer._get_minio_client")
    def test_presigned_url_has_content_disposition(self, mock_minio):
        """Verifica che la presigned URL viene richiesta con Content-Disposition."""
        mock_minio.return_value.presigned_get_object.return_value = MOCK_DOWNLOAD_URL
        client = create_api_client_authenticated(self.owner)
        client.get(self.url)

        call_kwargs = mock_minio.return_value.presigned_get_object.call_args
        response_headers = call_kwargs.kwargs.get("response_headers", {})
        disposition = response_headers.get("response-content-disposition", "")
        self.assertIn("attachment", disposition)
        self.assertIn("filename=", disposition)

    # --- AC-6: Non-regressione presigned URL ---

    @patch(
        "cs_clips.api.videos.video_serializers.VideoOutputSerializer._get_minio_client"
    )
    def test_video_detail_returns_file_url(self, mock_minio):
        """GET /api/videos/{id}/ ritorna file_url valida (non-regressione)."""
        mock_minio.return_value.presigned_get_object.return_value = MOCK_FILE_URL
        client = create_api_client_authenticated(self.owner)
        response = client.get(f"/api/videos/{self.video.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("file_url", response.data)
