from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from cs_clips.permissions import RoleBasedPermission

User = get_user_model()


class RoleBasedPermissionTests(TestCase):
    """Test per RoleBasedPermission — verifica DELETE su Video (campo uploader)
    e su Comment (campo user)."""

    def setUp(self):
        self.permission = RoleBasedPermission()
        self.user_group, _ = Group.objects.get_or_create(name='user')

        self.owner = User.objects.create_user(
            username='owner', password='testpass', email='owner@test.com'
        )
        self.owner.groups.add(self.user_group)

        self.other_user = User.objects.create_user(
            username='other', password='testpass', email='other@test.com'
        )
        self.other_user.groups.add(self.user_group)

        self.superuser = User.objects.create_superuser(
            username='admin', password='testpass', email='admin@test.com'
        )

    def _make_request(self, user, method='DELETE'):
        request = Mock()
        request.user = user
        request.method = method
        return request

    def test_owner_can_delete_video(self):
        """Utente 'user' puo' eliminare il proprio Video (campo uploader)."""
        video = Mock()
        video.uploader = self.owner
        # Video non ha attributo 'user'
        del video.user

        request = self._make_request(self.owner)
        self.assertTrue(
            self.permission.has_object_permission(request, None, video)
        )

    def test_other_user_cannot_delete_video(self):
        """Utente 'user' NON puo' eliminare Video di un altro utente."""
        video = Mock()
        video.uploader = self.owner
        del video.user

        request = self._make_request(self.other_user)
        self.assertFalse(
            self.permission.has_object_permission(request, None, video)
        )

    def test_owner_can_delete_comment(self):
        """Utente 'user' puo' eliminare il proprio Comment (campo user)."""
        comment = Mock(spec=['user'])
        comment.user = self.owner

        request = self._make_request(self.owner)
        self.assertTrue(
            self.permission.has_object_permission(request, None, comment)
        )

    def test_other_user_cannot_delete_comment(self):
        """Utente 'user' NON puo' eliminare Comment di un altro utente."""
        comment = Mock(spec=['user'])
        comment.user = self.owner

        request = self._make_request(self.other_user)
        self.assertFalse(
            self.permission.has_object_permission(request, None, comment)
        )

    def test_superuser_can_delete_anything(self):
        """Superuser puo' eliminare qualsiasi oggetto."""
        video = Mock()
        video.uploader = self.owner

        request = self._make_request(self.superuser)
        self.assertTrue(
            self.permission.has_object_permission(request, None, video)
        )
