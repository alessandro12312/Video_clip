"""Test per profilo utente: by-username, bio, campi calcolati, permessi."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from cs_clips.tests.conftest import (
    create_api_client_authenticated,
    create_authenticated_user,
)

User = get_user_model()


class TestByUsername(APITestCase):
    """Test per l'endpoint GET /api/users/by-username/{username}/."""

    def setUp(self):
        self.user = create_authenticated_user(username="mario")
        self.other = create_authenticated_user(username="luigi")
        self.client = create_api_client_authenticated(self.user)

    def test_get_by_username_valid(self):
        """GET by-username con username valido ritorna 200 con tutti i campi."""
        response = self.client.get("/api/users/by-username/luigi/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["username"], "luigi")
        self.assertIn("bio", data)
        self.assertIn("followers_count", data)
        self.assertIn("following_count", data)
        self.assertIn("is_followed_by_me", data)
        self.assertIn("id", data)
        self.assertIn("email", data)
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)
        self.assertIn("followers", data)
        self.assertIn("following", data)

    def test_get_by_username_not_found(self):
        """GET by-username con username inesistente → 404 {code, detail}."""
        response = self.client.get("/api/users/by-username/fantasma/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # AC-1: formato errore {code, detail}
        self.assertIn("code", response.data)
        self.assertIn("detail", response.data)

    def test_get_by_username_unauthenticated(self):
        """GET by-username senza autenticazione ritorna 401."""
        client = APIClient()
        response = client.get("/api/users/by-username/mario/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestBioUpdate(APITestCase):
    """Test per PATCH bio nel profilo utente."""

    def setUp(self):
        self.user = create_authenticated_user(username="mario")
        self.other = create_authenticated_user(username="luigi")
        self.client = create_api_client_authenticated(self.user)

    def test_patch_bio_valid(self):
        """PATCH bio con valore valido ritorna 200 e bio aggiornata."""
        response = self.client.patch(
            f"/api/users/{self.user.id}/",
            {"bio": "Ciao, amo i video!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], "Ciao, amo i video!")
        # Verifica che i campi calcolati siano presenti
        self.assertIn("followers_count", response.data)
        self.assertIn("following_count", response.data)
        self.assertIn("is_followed_by_me", response.data)

    def test_patch_bio_too_long(self):
        """PATCH bio oltre 500 caratteri ritorna 400 con messaggio in italiano."""
        long_bio = "x" * 501
        response = self.client.patch(
            f"/api/users/{self.user.id}/",
            {"bio": long_bio},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # AC-2: messaggio di validazione in italiano (non il default inglese)
        self.assertNotIn("Ensure this", str(response.data))

    def test_patch_bio_empty(self):
        """PATCH bio vuota (reset) ritorna 200 e bio svuotata."""
        # Prima imposta una bio
        self.user.bio = "Bio iniziale"
        self.user.save()

        response = self.client.patch(
            f"/api/users/{self.user.id}/",
            {"bio": ""},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["bio"], "")


class TestProfilePermissions(APITestCase):
    """Test per i permessi PATCH sul profilo."""

    def setUp(self):
        self.user = create_authenticated_user(username="mario")
        self.other = create_authenticated_user(username="luigi")

        # toconfirm user — il helper conftest crea solo gruppo "user"
        self.toconfirm_user = User.objects.create_user(
            username="peach", password="testpass123", email="peach@test.com"
        )
        toconfirm_group, _ = Group.objects.get_or_create(name="toconfirm")
        self.toconfirm_user.groups.add(toconfirm_group)

    def test_patch_own_profile(self):
        """Utente 'user' può modificare il proprio profilo."""
        client = create_api_client_authenticated(self.user)
        response = client.patch(
            f"/api/users/{self.user.id}/",
            {"bio": "Nuova bio"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_other_profile_forbidden(self):
        """Utente 'user' NON può modificare il profilo altrui → 403."""
        client = create_api_client_authenticated(self.user)
        response = client.patch(
            f"/api/users/{self.other.id}/",
            {"bio": "Hacked"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_as_toconfirm_forbidden(self):
        """Utente 'toconfirm' NON può modificare il profilo → 403."""
        client = create_api_client_authenticated(self.toconfirm_user)
        response = client.patch(
            f"/api/users/{self.toconfirm_user.id}/",
            {"bio": "Test"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestIsFollowedByMe(APITestCase):
    """Test per il campo calcolato is_followed_by_me."""

    def setUp(self):
        self.user_a = create_authenticated_user(username="mario")
        self.user_b = create_authenticated_user(username="luigi")
        self.user_c = create_authenticated_user(username="peach")
        self.client = create_api_client_authenticated(self.user_a)

    def test_is_followed_by_me_true(self):
        """is_followed_by_me è True quando seguo l'utente."""
        self.user_a.following.add(self.user_b)

        response = self.client.get(f"/api/users/{self.user_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_followed_by_me"])

    def test_is_followed_by_me_false(self):
        """is_followed_by_me è False quando NON seguo l'utente."""
        response = self.client.get(f"/api/users/{self.user_c.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_followed_by_me"])

    def test_is_followed_by_me_self(self):
        """is_followed_by_me è False per il proprio profilo."""
        response = self.client.get(f"/api/users/{self.user_a.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_followed_by_me"])


class TestFollowersCounts(APITestCase):
    """Test per followers_count e following_count."""

    def setUp(self):
        self.user_a = create_authenticated_user(username="mario")
        self.user_b = create_authenticated_user(username="luigi")
        self.user_c = create_authenticated_user(username="peach")
        self.client = create_api_client_authenticated(self.user_a)

    def test_followers_and_following_count(self):
        """followers_count e following_count corretti dopo follow."""
        # A segue B e C
        self.user_a.following.add(self.user_b)
        self.user_a.following.add(self.user_c)
        # B segue A
        self.user_b.following.add(self.user_a)

        # Profilo di A: 1 follower (B), 2 following (B, C)
        response = self.client.get(f"/api/users/{self.user_a.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["followers_count"], 1)
        self.assertEqual(response.data["following_count"], 2)

        # Profilo di B: 1 follower (A), 1 following (A)
        response = self.client.get(f"/api/users/{self.user_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["followers_count"], 1)
        self.assertEqual(response.data["following_count"], 1)

        # Profilo di C: 1 follower (A), 0 following
        response = self.client.get(f"/api/users/{self.user_c.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["followers_count"], 1)
        self.assertEqual(response.data["following_count"], 0)

    def test_counts_after_unfollow(self):
        """Contatori aggiornati dopo unfollow."""
        self.user_a.following.add(self.user_b)
        self.user_a.following.remove(self.user_b)

        response = self.client.get(f"/api/users/{self.user_b.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["followers_count"], 0)
