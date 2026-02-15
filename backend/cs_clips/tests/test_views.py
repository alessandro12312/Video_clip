from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from cs_clips.models import Video, Comment, VideoLike, CommentLike

User = get_user_model()


class UserRegistrationEndpointTest(APITestCase):
    """Test per endpoint registrazione utente (Story 1-2)."""

    def setUp(self):
        self.client = APIClient()
        self.url = '/api/users/'
        self.valid_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!'
        }

    def test_registration_success_creates_user_and_assigns_group(self):
        """POST /api/users/ con dati validi → 201, crea utente con gruppo 'toconfirm' (AC #1)."""
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('SecurePass123!'))
        self.assertTrue(user.groups.filter(name='toconfirm').exists())
        self.assertFalse(user.groups.filter(name='user').exists())

    def test_registration_duplicate_username_returns_400(self):
        """POST /api/users/ con username duplicato → 400 con messaggio specifico (AC #2)."""
        User.objects.create_user(username='existing', email='old@example.com', password='OldPass123!')
        data = {
            'username': 'existing',
            'email': 'new@example.com',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Username già in uso', response.data['detail'])

    def test_registration_duplicate_email_returns_400(self):
        """POST /api/users/ con email duplicata → 400 con messaggio specifico (AC #2)."""
        User.objects.create_user(username='existing', email='taken@example.com', password='OldPass123!')
        data = {
            'username': 'differentuser',
            'email': 'taken@example.com',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email già registrata', response.data['detail'])

    def test_registration_weak_password_returns_400(self):
        """POST /api/users/ con password troppo corta → 400 con requisiti minimi (AC #3)."""
        data = {
            'username': 'shortpw',
            'email': 'shortpw@example.com',
            'password': 'abc'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data['detail'])

    def test_registration_numeric_password_returns_400(self):
        """POST /api/users/ con password interamente numerica → 400 (AC #3)."""
        data = {
            'username': 'numericpw',
            'email': 'numericpw@example.com',
            'password': '12345678'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data['detail'])

    def test_registration_missing_username_returns_400(self):
        """POST /api/users/ senza username → 400."""
        data = {'email': 'no@user.com', 'password': 'SecurePass123!'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data['detail'])

    def test_registration_missing_email_returns_400(self):
        """POST /api/users/ senza email → 400."""
        data = {'username': 'noemail', 'password': 'SecurePass123!'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['detail'])

    def test_registration_missing_password_returns_400(self):
        """POST /api/users/ senza password → 400."""
        data = {'username': 'nopw', 'email': 'nopw@example.com'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data['detail'])

    def test_registration_password_not_in_response(self):
        """La password non è visibile nella risposta (write_only)."""
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)

    def test_registration_duplicate_username_case_insensitive(self):
        """Username duplicato è case-insensitive (AC #2)."""
        User.objects.create_user(username='CaseUser', email='case@test.com', password='OldPass123!')
        data = {
            'username': 'caseuser',
            'email': 'other@test.com',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_email_case_insensitive(self):
        """Email duplicata è case-insensitive (AC #2)."""
        User.objects.create_user(username='original', email='Taken@Example.com', password='OldPass123!')
        data = {
            'username': 'newuser',
            'email': 'taken@example.com',
            'password': 'SecurePass123!'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserRegistrationIntegrationTest(APITestCase):
    """Test integrazione: registrazione → JWT → refresh (Story 1-2, AC #1, Task 5)."""

    def test_full_flow_register_then_login_jwt(self):
        """Flusso completo: registrazione → login JWT → token valido (AC #1)."""
        client = APIClient()
        # 1. Registrazione
        reg_data = {
            'username': 'integration_user',
            'email': 'integration@example.com',
            'password': 'SecurePass123!'
        }
        reg_response = client.post('/api/users/', reg_data, format='json')
        self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)

        # 2. Login JWT
        token_response = client.post('/api/token/', {
            'username': 'integration_user',
            'password': 'SecurePass123!'
        }, format='json')
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', token_response.data)
        self.assertIn('refresh', token_response.data)

        # 3. Accesso autenticato con access token
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_response.data["access"]}')
        me_response = client.get(f'/api/users/{User.objects.get(username="integration_user").id}/')
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data['username'], 'integration_user')

    def test_token_refresh_after_registration(self):
        """Token refresh funziona dopo registrazione (AC #1, Subtask 5.2)."""
        client = APIClient()
        # Registrazione + Login
        client.post('/api/users/', {
            'username': 'refresh_user',
            'email': 'refresh@example.com',
            'password': 'SecurePass123!'
        }, format='json')
        token_response = client.post('/api/token/', {
            'username': 'refresh_user',
            'password': 'SecurePass123!'
        }, format='json')

        # Refresh token
        refresh_response = client.post('/api/token/refresh/', {
            'refresh': token_response.data['refresh']
        }, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)


class LoginAndJWTEndpointTest(APITestCase):
    """Test per login JWT e refresh token (Story 1-3)."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='loginuser', email='login@example.com', password='SecurePass123!'
        )
        group, _ = Group.objects.get_or_create(name='user')
        self.user.groups.add(group)
        self.login_url = '/api/token/'
        self.refresh_url = '/api/token/refresh/'

    def test_login_success_returns_access_and_refresh(self):
        """POST /api/token/ con credenziali valide → 200 + access + refresh (AC #1, Task 7.1)."""
        response = self.client.post(self.login_url, {
            'username': 'loginuser',
            'password': 'SecurePass123!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password_returns_401(self):
        """POST /api/token/ con password errata → 401 (AC #1, Task 7.2)."""
        response = self.client.post(self.login_url, {
            'username': 'loginuser',
            'password': 'WrongPassword!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user_returns_401(self):
        """POST /api/token/ con utente inesistente → 401 (AC #1, Task 7.3)."""
        response = self.client.post(self.login_url, {
            'username': 'ghostuser',
            'password': 'SecurePass123!'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_returns_new_access(self):
        """POST /api/token/refresh/ con refresh valido → nuovo access token (AC #2, Task 7.4)."""
        login_response = self.client.post(self.login_url, {
            'username': 'loginuser',
            'password': 'SecurePass123!'
        }, format='json')
        refresh = login_response.data['refresh']
        response = self.client.post(self.refresh_url, {
            'refresh': refresh
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_refresh_token_expired_returns_401(self):
        """POST /api/token/refresh/ con refresh scaduto/invalido → 401 (AC #4, Task 7.5)."""
        response = self.client.post(self.refresh_url, {
            'refresh': 'invalid-token-value'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_rotation_returns_new_refresh(self):
        """POST /api/token/refresh/ con ROTATE_REFRESH_TOKENS=True → restituisce nuovo refresh (AC #4, Task 7.6)."""
        login_response = self.client.post(self.login_url, {
            'username': 'loginuser',
            'password': 'SecurePass123!'
        }, format='json')
        old_refresh = login_response.data['refresh']
        response = self.client.post(self.refresh_url, {
            'refresh': old_refresh
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertNotEqual(response.data['refresh'], old_refresh)

    def test_login_updates_last_login(self):
        """POST /api/token/ aggiorna last_login dell'utente (Task 7.7)."""
        self.assertIsNone(self.user.last_login)
        self.client.post(self.login_url, {
            'username': 'loginuser',
            'password': 'SecurePass123!'
        }, format='json')
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)

    def test_protected_endpoint_without_jwt_returns_401(self):
        """GET /api/users/ senza JWT → 401 (Task 7.8)."""
        unauthenticated_client = APIClient()
        response = unauthenticated_client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_valid_jwt_returns_200(self):
        """GET /api/users/ con JWT valido → 200 (Task 7.9)."""
        login_response = self.client.post(self.login_url, {
            'username': 'loginuser',
            'password': 'SecurePass123!'
        }, format='json')
        access = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_protected_endpoint_with_invalid_jwt_returns_401(self):
        """GET /api/users/ con JWT invalido → 401 (Task 7.10)."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid-token-here')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


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
