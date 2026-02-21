"""Test per validazione upload video (Story 2-1)."""
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()


class VideoUploadValidationTest(APITestCase):
    """Test per endpoint POST /api/videos/ con validazione (Story 2-1)."""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/videos/'
        self.user = User.objects.create_user(
            username='uploader', email='uploader@test.com', password='SecurePass123!'
        )
        group, _ = Group.objects.get_or_create(name='user')
        self.user.groups.add(group)
        self.client.force_authenticate(user=self.user)

    def _make_video_file(self, name='test.mp4', size=1024, content_type='video/mp4'):
        """Crea un SimpleUploadedFile per i test."""
        return SimpleUploadedFile(name, b'\x00' * size, content_type=content_type)

    @patch('cs_clips.serializers.VideoFileClip')
    def test_upload_valid_file_returns_201(self, mock_clip_class):
        """Upload con file MP4 valido, 30s, < 500MB → 201 (AC #1, #2)."""
        mock_clip = MagicMock()
        mock_clip.duration = 30
        mock_clip.__enter__ = MagicMock(return_value=mock_clip)
        mock_clip.__exit__ = MagicMock(return_value=False)
        mock_clip_class.return_value = mock_clip

        video_file = self._make_video_file()
        response = self.client.post(self.url, {
            'file': video_file,
            'title': 'Clutch test',
            'tag': 'clutch',
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Clutch test')
        self.assertEqual(response.data['duration'], 30)

    @patch('cs_clips.serializers.VideoFileClip')
    def test_upload_duration_too_short_returns_400(self, mock_clip_class):
        """Upload con durata < 10s → 400 con messaggio specifico (AC #2)."""
        mock_clip = MagicMock()
        mock_clip.duration = 5
        mock_clip.__enter__ = MagicMock(return_value=mock_clip)
        mock_clip.__exit__ = MagicMock(return_value=False)
        mock_clip_class.return_value = mock_clip

        video_file = self._make_video_file()
        response = self.client.post(self.url, {
            'file': video_file,
            'title': 'Clip corta',
            'tag': 'clutch',
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Il video deve durare tra 10 secondi e 1 minuto')

    @patch('cs_clips.serializers.VideoFileClip')
    def test_upload_duration_too_long_returns_400(self, mock_clip_class):
        """Upload con durata > 60s → 400 con messaggio specifico (AC #2)."""
        mock_clip = MagicMock()
        mock_clip.duration = 120
        mock_clip.__enter__ = MagicMock(return_value=mock_clip)
        mock_clip.__exit__ = MagicMock(return_value=False)
        mock_clip_class.return_value = mock_clip

        video_file = self._make_video_file()
        response = self.client.post(self.url, {
            'file': video_file,
            'title': 'Clip lunga',
            'tag': 'funny',
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Il video deve durare tra 10 secondi e 1 minuto')

    def test_upload_unsupported_format_returns_400(self):
        """Upload con formato non supportato (.txt) → 400 con messaggio specifico (AC #3)."""
        txt_file = SimpleUploadedFile('document.txt', b'not a video', content_type='text/plain')
        response = self.client.post(self.url, {
            'file': txt_file,
            'title': 'Non video',
            'tag': 'clutch',
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Formato non supportato. Formati accettati: MP4, MOV, AVI, MKV, WebM')

    def test_upload_pdf_format_returns_400(self):
        """Upload con formato .pdf → 400 con messaggio specifico (AC #3)."""
        pdf_file = SimpleUploadedFile('doc.pdf', b'%PDF-1.4', content_type='application/pdf')
        response = self.client.post(self.url, {
            'file': pdf_file,
            'title': 'PDF test',
            'tag': 'clutch',
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('cs_clips.serializers.MAX_VIDEO_FILE_SIZE', 512)
    def test_upload_oversized_file_returns_400(self):
        """Upload con file > limite dimensione → 400 con messaggio specifico (AC #4)."""
        # File da 1024 bytes supera il limite mockato di 512 bytes
        big_file = self._make_video_file(size=1024)
        response = self.client.post(self.url, {
            'file': big_file,
            'title': 'File enorme',
            'tag': 'fail',
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Il file supera la dimensione massima di 500MB')

    def test_upload_unauthenticated_returns_401(self):
        """Upload senza autenticazione → 401."""
        unauthenticated_client = APIClient()
        video_file = self._make_video_file()
        response = unauthenticated_client.post(self.url, {
            'file': video_file,
            'title': 'Unauthorized',
            'tag': 'clutch',
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_toconfirm_user_returns_403(self):
        """Upload con utente toconfirm (read-only) → 403."""
        toconfirm_user = User.objects.create_user(
            username='pending', email='pending@test.com', password='SecurePass123!'
        )
        toconfirm_group, _ = Group.objects.get_or_create(name='toconfirm')
        toconfirm_user.groups.add(toconfirm_group)

        self.client.force_authenticate(user=toconfirm_user)
        video_file = self._make_video_file()
        response = self.client.post(self.url, {
            'file': video_file,
            'title': 'Pending user',
            'tag': 'clutch',
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('cs_clips.serializers.VideoFileClip')
    def test_upload_allow_download_false_saved(self, mock_clip_class):
        """Upload con allow_download=false → campo salvato correttamente (AC #5)."""
        mock_clip = MagicMock()
        mock_clip.duration = 30
        mock_clip.__enter__ = MagicMock(return_value=mock_clip)
        mock_clip.__exit__ = MagicMock(return_value=False)
        mock_clip_class.return_value = mock_clip

        video_file = self._make_video_file()
        response = self.client.post(self.url, {
            'file': video_file,
            'title': 'No download',
            'tag': 'clutch',
            'allow_download': 'false',
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['allow_download'])
