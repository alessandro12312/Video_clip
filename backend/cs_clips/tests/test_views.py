from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from cs_clips.models import Video, Comment, VideoLike, CommentLike

User = get_user_model()


class VideoLikeEndpointTest(APITestCase):
    """Test per endpoint like/unlike video (AC #3)."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='pass123')
        self.user2 = User.objects.create_user(username='testuser2', email='test2@test.com', password='pass123')
        group, _ = Group.objects.get_or_create(name='user')
        self.user.groups.add(group)
        self.user2.groups.add(group)
        self.video = Video.objects.create(title='Test Video', uploader=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_like_video(self):
        """POST /api/videos/{id}/like/ — crea VideoLike, ritorna like_count."""
        response = self.client.post(f'/api/videos/{self.video.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['like_count'], 1)
        self.assertTrue(VideoLike.objects.filter(user=self.user, video=self.video).exists())

    def test_double_like_video_returns_400(self):
        """like su video già likato → 400 con messaggio."""
        VideoLike.objects.create(user=self.user, video=self.video)
        response = self.client.post(f'/api/videos/{self.video.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Hai già messo like')

    def test_unlike_video(self):
        """POST /api/videos/{id}/unlike/ — rimuove VideoLike, ritorna like_count."""
        VideoLike.objects.create(user=self.user, video=self.video)
        response = self.client.post(f'/api/videos/{self.video.id}/unlike/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['like_count'], 0)
        self.assertFalse(VideoLike.objects.filter(user=self.user, video=self.video).exists())

    def test_unlike_video_not_liked_returns_400(self):
        """unlike su video non likato → 400 con messaggio."""
        response = self.client.post(f'/api/videos/{self.video.id}/unlike/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Non hai messo like a questo video')

    def test_like_count_multiple_users(self):
        """Verifica conteggio like con più utenti."""
        VideoLike.objects.create(user=self.user, video=self.video)
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(f'/api/videos/{self.video.id}/like/')
        self.assertEqual(response.data['like_count'], 2)


class CommentLikeEndpointTest(APITestCase):
    """Test per endpoint like/unlike commento (AC #4)."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='pass123')
        group, _ = Group.objects.get_or_create(name='user')
        self.user.groups.add(group)
        self.video = Video.objects.create(title='Test Video', uploader=self.user)
        self.comment = Comment.objects.create(user=self.user, video=self.video, content='Test comment')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_like_comment(self):
        """POST /api/comments/{id}/like/ — crea CommentLike, ritorna like_count."""
        response = self.client.post(f'/api/comments/{self.comment.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['like_count'], 1)

    def test_double_like_comment_returns_400(self):
        """like su commento già likato → 400."""
        CommentLike.objects.create(user=self.user, comment=self.comment)
        response = self.client.post(f'/api/comments/{self.comment.id}/like/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Hai già messo like')

    def test_unlike_comment(self):
        """POST /api/comments/{id}/unlike/ — rimuove CommentLike."""
        CommentLike.objects.create(user=self.user, comment=self.comment)
        response = self.client.post(f'/api/comments/{self.comment.id}/unlike/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['like_count'], 0)

    def test_unlike_comment_not_liked_returns_400(self):
        """unlike su commento non likato → 400."""
        response = self.client.post(f'/api/comments/{self.comment.id}/unlike/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PopupCommentsEndpointTest(APITestCase):
    """Test per endpoint popup-comments (AC #2)."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='pass123')
        self.user2 = User.objects.create_user(username='marco', email='marco@test.com', password='pass123')
        group, _ = Group.objects.get_or_create(name='user')
        self.user.groups.add(group)
        self.user2.groups.add(group)
        self.video = Video.objects.create(title='Test Video', uploader=self.user, duration=60)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_popup_comments_empty(self):
        """Nessun commento con like → lista vuota."""
        response = self.client.get(f'/api/videos/{self.video.id}/popup-comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_popup_comments_filters_disabled(self):
        """Commenti con is_disabled=True sono esclusi."""
        comment = Comment.objects.create(
            user=self.user2, video=self.video, content='Disabled', timestamp_second=10, is_disabled=True
        )
        CommentLike.objects.create(user=self.user, comment=comment)
        response = self.client.get(f'/api/videos/{self.video.id}/popup-comments/')
        self.assertEqual(len(response.data), 0)

    def test_popup_comments_filters_zero_timestamp(self):
        """Commenti con timestamp_second=0 sono esclusi."""
        comment = Comment.objects.create(
            user=self.user2, video=self.video, content='At zero', timestamp_second=0
        )
        CommentLike.objects.create(user=self.user, comment=comment)
        response = self.client.get(f'/api/videos/{self.video.id}/popup-comments/')
        self.assertEqual(len(response.data), 0)

    def test_popup_comments_requires_min_one_like(self):
        """Solo commenti con almeno 1 like sono inclusi."""
        Comment.objects.create(
            user=self.user2, video=self.video, content='No likes', timestamp_second=10
        )
        response = self.client.get(f'/api/videos/{self.video.id}/popup-comments/')
        self.assertEqual(len(response.data), 0)

    def test_popup_comments_returns_top_comment_per_timestamp(self):
        """Per ogni timestamp unico, restituisce solo il commento con più like."""
        comment1 = Comment.objects.create(
            user=self.user2, video=self.video, content='Primo', timestamp_second=18
        )
        comment2 = Comment.objects.create(
            user=self.user, video=self.video, content='Secondo', timestamp_second=18
        )
        # comment1 ha 2 like, comment2 ha 1 like
        CommentLike.objects.create(user=self.user, comment=comment1)
        CommentLike.objects.create(user=self.user2, comment=comment1)
        CommentLike.objects.create(user=self.user, comment=comment2)

        response = self.client.get(f'/api/videos/{self.video.id}/popup-comments/')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['comment_id'], comment1.id)
        self.assertEqual(response.data[0]['like_count'], 2)

    def test_popup_comments_ordered_by_timestamp(self):
        """I risultati sono ordinati per timestamp crescente."""
        c1 = Comment.objects.create(user=self.user2, video=self.video, content='A', timestamp_second=30)
        c2 = Comment.objects.create(user=self.user2, video=self.video, content='B', timestamp_second=10)
        CommentLike.objects.create(user=self.user, comment=c1)
        CommentLike.objects.create(user=self.user, comment=c2)

        response = self.client.get(f'/api/videos/{self.video.id}/popup-comments/')
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['timestamp'], 10)
        self.assertEqual(response.data[1]['timestamp'], 30)

    def test_popup_comments_response_format(self):
        """Verifica formato risposta: timestamp, comment_id, text, author, like_count."""
        comment = Comment.objects.create(
            user=self.user2, video=self.video, content='quel flick!', timestamp_second=18
        )
        CommentLike.objects.create(user=self.user, comment=comment)

        response = self.client.get(f'/api/videos/{self.video.id}/popup-comments/')
        self.assertEqual(len(response.data), 1)
        item = response.data[0]
        self.assertEqual(item['timestamp'], 18)
        self.assertEqual(item['comment_id'], comment.id)
        self.assertEqual(item['text'], 'quel flick!')
        self.assertEqual(item['author'], 'marco')
        self.assertEqual(item['like_count'], 1)


class CommentDisabledFilterTest(APITestCase):
    """Test per filtro commenti disabilitati (AC #7)."""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='pass123')
        group, _ = Group.objects.get_or_create(name='user')
        self.user.groups.add(group)
        self.video = Video.objects.create(title='Test Video', uploader=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_disabled_comments_excluded(self):
        """Commenti con is_disabled=True sono esclusi dalle query pubbliche."""
        Comment.objects.create(user=self.user, video=self.video, content='Visible')
        Comment.objects.create(user=self.user, video=self.video, content='Hidden', is_disabled=True)

        response = self.client.get('/api/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Solo il commento visibile deve apparire
        comment_contents = [c['content'] for c in response.data['results']]
        self.assertIn('Visible', comment_contents)
        self.assertNotIn('Hidden', comment_contents)


class VideoSerializerFieldsTest(APITestCase):
    """Test per campi VideoSerializer aggiornati (AC #6)."""

    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', email='admin@test.com', password='pass123')
        group, _ = Group.objects.get_or_create(name='user')
        self.user.groups.add(group)
        self.video = Video.objects.create(title='Test Video', uploader=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_video_detail_has_allow_download(self):
        """allow_download è visibile nel VideoSerializer."""
        response = self.client.get(f'/api/videos/{self.video.id}/')
        self.assertIn('allow_download', response.data)
        self.assertTrue(response.data['allow_download'])

    def test_video_detail_has_like_count(self):
        """like_count è visibile nel VideoSerializer."""
        response = self.client.get(f'/api/videos/{self.video.id}/')
        self.assertIn('like_count', response.data)
        self.assertEqual(response.data['like_count'], 0)


class ModeratorGroupMigrationTest(TestCase):
    """Test per la data migration del gruppo moderator (AC #5)."""

    def test_moderator_group_exists(self):
        """Verifica che il gruppo moderator è stato creato dalla migration."""
        self.assertTrue(Group.objects.filter(name='moderator').exists())


class UserSearchEndpointTest(APITestCase):
    """Test per ricerca utenti via SearchFilter (Story 1-9, AC #3)."""

    def setUp(self):
        self.user = User.objects.create_user(username='alice', email='alice@test.com', password='pass123')
        self.user2 = User.objects.create_user(username='bob', email='bob@test.com', password='pass123')
        self.user3 = User.objects.create_user(username='alex', email='alex@test.com', password='pass123')
        group, _ = Group.objects.get_or_create(name='user')
        self.user.groups.add(group)
        self.user2.groups.add(group)
        self.user3.groups.add(group)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_search_users_by_username(self):
        """GET /api/users/?search=al → restituisce alice e alex."""
        response = self.client.get('/api/users/', {'search': 'al'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [u['username'] for u in response.data['results']]
        self.assertIn('alice', usernames)
        self.assertIn('alex', usernames)
        self.assertNotIn('bob', usernames)

    def test_search_users_no_results(self):
        """GET /api/users/?search=zzz → lista vuota."""
        response = self.client.get('/api/users/', {'search': 'zzz'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_search_users_case_insensitive(self):
        """La ricerca è case-insensitive."""
        response = self.client.get('/api/users/', {'search': 'AL'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [u['username'] for u in response.data['results']]
        self.assertIn('alice', usernames)
        self.assertIn('alex', usernames)

    def test_search_empty_returns_all(self):
        """GET /api/users/ senza search → restituisce tutti gli utenti."""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
