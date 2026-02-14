from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from cs_clips.models import Video, Comment, VideoLike, CommentLike, Notification, Contest

User = get_user_model()


class VideoLikeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='pass123')
        from django.contrib.auth.models import Group
        group, _ = Group.objects.get_or_create(name='user')
        self.user.groups.add(group)
        self.video = Video.objects.create(title='Test Video', uploader=self.user)

    def test_create_video_like(self):
        """Verifica creazione VideoLike con FK user + video."""
        like = VideoLike.objects.create(user=self.user, video=self.video)
        self.assertEqual(like.user, self.user)
        self.assertEqual(like.video, self.video)
        self.assertIsNotNone(like.created_at)

    def test_unique_together_video_like(self):
        """Verifica vincolo unique_together su VideoLike."""
        VideoLike.objects.create(user=self.user, video=self.video)
        with self.assertRaises(IntegrityError):
            VideoLike.objects.create(user=self.user, video=self.video)

    def test_cascade_delete_user(self):
        """Verifica CASCADE su eliminazione utente."""
        VideoLike.objects.create(user=self.user, video=self.video)
        self.user.delete()
        self.assertEqual(VideoLike.objects.count(), 0)

    def test_cascade_delete_video(self):
        """Verifica CASCADE su eliminazione video."""
        VideoLike.objects.create(user=self.user, video=self.video)
        self.video.delete()
        self.assertEqual(VideoLike.objects.count(), 0)


class CommentLikeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='pass123')
        from django.contrib.auth.models import Group
        group, _ = Group.objects.get_or_create(name='user')
        self.user.groups.add(group)
        self.video = Video.objects.create(title='Test Video', uploader=self.user)
        self.comment = Comment.objects.create(user=self.user, video=self.video, content='Test comment')

    def test_create_comment_like(self):
        """Verifica creazione CommentLike con FK user + comment."""
        like = CommentLike.objects.create(user=self.user, comment=self.comment)
        self.assertEqual(like.user, self.user)
        self.assertEqual(like.comment, self.comment)
        self.assertIsNotNone(like.created_at)

    def test_unique_together_comment_like(self):
        """Verifica vincolo unique_together su CommentLike."""
        CommentLike.objects.create(user=self.user, comment=self.comment)
        with self.assertRaises(IntegrityError):
            CommentLike.objects.create(user=self.user, comment=self.comment)

    def test_cascade_delete_comment(self):
        """Verifica CASCADE su eliminazione commento."""
        CommentLike.objects.create(user=self.user, comment=self.comment)
        self.comment.delete()
        self.assertEqual(CommentLike.objects.count(), 0)


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='pass123')
        from django.contrib.auth.models import Group
        group, _ = Group.objects.get_or_create(name='user')
        self.user.groups.add(group)

    def test_create_notification(self):
        """Verifica creazione Notification con tutti i campi."""
        notif = Notification.objects.create(
            recipient=self.user,
            type=Notification.NotificationType.VIDEO_LIKE,
            content='Test notifica',
            related_object_id=1
        )
        self.assertEqual(notif.recipient, self.user)
        self.assertEqual(notif.type, 'video_like')
        self.assertFalse(notif.read)
        self.assertIsNotNone(notif.created_at)

    def test_notification_type_choices(self):
        """Verifica tutti i tipi di notifica nel TextChoices enum."""
        expected_types = ['comment', 'comment_like', 'video_like', 'popup_promoted', 'contest_invite', 'contest_turn']
        actual_types = [choice[0] for choice in Notification.NotificationType.choices]
        self.assertEqual(actual_types, expected_types)

    def test_cascade_delete_recipient(self):
        """Verifica CASCADE su eliminazione utente destinatario."""
        Notification.objects.create(
            recipient=self.user,
            type=Notification.NotificationType.COMMENT,
            content='Test',
            related_object_id=1
        )
        self.user.delete()
        self.assertEqual(Notification.objects.count(), 0)


class VideoAllowDownloadTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='pass123')
        from django.contrib.auth.models import Group
        group, _ = Group.objects.get_or_create(name='user')
        self.user.groups.add(group)

    def test_allow_download_default_true(self):
        """Verifica che allow_download ha default=True."""
        video = Video.objects.create(title='Test Video', uploader=self.user)
        self.assertTrue(video.allow_download)

    def test_allow_download_false(self):
        """Verifica che allow_download può essere impostato a False."""
        video = Video.objects.create(title='Test Video', uploader=self.user, allow_download=False)
        self.assertFalse(video.allow_download)


class CommentIsDisabledTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='pass123')
        from django.contrib.auth.models import Group
        group, _ = Group.objects.get_or_create(name='user')
        self.user.groups.add(group)
        self.video = Video.objects.create(title='Test Video', uploader=self.user)

    def test_is_disabled_default_false(self):
        """Verifica che is_disabled ha default=False."""
        comment = Comment.objects.create(user=self.user, video=self.video, content='Test')
        self.assertFalse(comment.is_disabled)

    def test_is_disabled_true(self):
        """Verifica che is_disabled può essere impostato a True."""
        comment = Comment.objects.create(user=self.user, video=self.video, content='Test', is_disabled=True)
        self.assertTrue(comment.is_disabled)
