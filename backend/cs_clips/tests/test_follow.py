"""Test per follow, unfollow e liste followers/following paginate."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from cs_clips.tests.conftest import (
    create_api_client_authenticated,
    create_authenticated_user,
    create_toconfirm_user,
)

User = get_user_model()


class TestFollow(APITestCase):
    """Test per POST /api/users/{id}/follow/."""

    def setUp(self):
        self.user_a = create_authenticated_user(username="alice")
        self.user_b = create_authenticated_user(username="bob")
        self.client_a = create_api_client_authenticated(self.user_a)

    def test_follow_success(self):
        """Follow riuscito → 200, risposta con detail, is_followed, followers_count."""
        response = self.client_a.post(f"/api/users/{self.user_b.id}/follow/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["detail"], "Ora segui bob.")
        self.assertTrue(data["is_followed"])
        self.assertEqual(data["followers_count"], 1)
        # Verifica relazione M2M
        self.assertTrue(self.user_a.following.filter(id=self.user_b.id).exists())

    def test_follow_self_returns_400(self):
        """Follow sé stesso → 400 con messaggio 'Non puoi seguire te stesso.'."""
        response = self.client_a.post(f"/api/users/{self.user_a.id}/follow/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "Non puoi seguire te stesso.")

    def test_follow_as_toconfirm_returns_403(self):
        """Follow come utente 'toconfirm' → 403 con formato {code, detail}."""
        toconfirm_user = create_toconfirm_user(username="pending")
        client = create_api_client_authenticated(toconfirm_user)

        response = client.post(f"/api/users/{self.user_b.id}/follow/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)

    def test_follow_nonexistent_user_returns_404(self):
        """Follow utente inesistente → 404 con formato {code, detail}."""
        response = self.client_a.post("/api/users/99999/follow/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)

    def test_follow_idempotent(self):
        """Follow doppio non genera errore (M2M .add() idempotente)."""
        self.client_a.post(f"/api/users/{self.user_b.id}/follow/")
        response = self.client_a.post(f"/api/users/{self.user_b.id}/follow/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["followers_count"], 1)

    def test_follow_updates_count_correctly(self):
        """followers_count aggiornato dopo follow da più utenti."""
        user_c = create_authenticated_user(username="carol")
        client_c = create_api_client_authenticated(user_c)

        self.client_a.post(f"/api/users/{self.user_b.id}/follow/")
        response = client_c.post(f"/api/users/{self.user_b.id}/follow/")
        self.assertEqual(response.data["followers_count"], 2)


class TestUnfollow(APITestCase):
    """Test per POST /api/users/{id}/unfollow/."""

    def setUp(self):
        self.user_a = create_authenticated_user(username="alice")
        self.user_b = create_authenticated_user(username="bob")
        self.client_a = create_api_client_authenticated(self.user_a)

    def test_unfollow_success(self):
        """Unfollow riuscito → 200, risposta arricchita."""
        self.user_a.following.add(self.user_b)
        response = self.client_a.post(f"/api/users/{self.user_b.id}/unfollow/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["detail"], "Hai smesso di seguire bob.")
        self.assertFalse(data["is_followed"])
        self.assertEqual(data["followers_count"], 0)
        # Verifica relazione M2M rimossa
        self.assertFalse(self.user_a.following.filter(id=self.user_b.id).exists())

    def test_unfollow_not_followed_is_idempotent(self):
        """Unfollow utente non seguito → 200, idempotente."""
        response = self.client_a.post(f"/api/users/{self.user_b.id}/unfollow/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["detail"], "Hai smesso di seguire bob.")
        self.assertFalse(data["is_followed"])
        self.assertEqual(data["followers_count"], 0)

    def test_unfollow_decrements_count(self):
        """followers_count decrementato correttamente dopo unfollow."""
        user_c = create_authenticated_user(username="carol")
        # Due utenti seguono bob
        self.user_a.following.add(self.user_b)
        user_c.following.add(self.user_b)

        response = self.client_a.post(f"/api/users/{self.user_b.id}/unfollow/")
        self.assertEqual(response.data["followers_count"], 1)


class TestGetFollowersPaginated(APITestCase):
    """Test per GET /api/users/{id}/followers/ (paginato)."""

    def setUp(self):
        self.user = create_authenticated_user(username="target")
        self.client = create_api_client_authenticated(self.user)

    def test_followers_paginated_format(self):
        """GET followers → 200, formato paginato {count, next, previous, results}."""
        follower = create_authenticated_user(username="follower1")
        follower.following.add(self.user)

        response = self.client.get(f"/api/users/{self.user.id}/followers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn("count", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)
        self.assertIn("results", data)
        self.assertEqual(data["count"], 1)
        self.assertEqual(len(data["results"]), 1)

    def test_followers_contain_user_fields(self):
        """Results contengono User con campi calcolati e valori corretti."""
        follower = create_authenticated_user(username="follower1")
        follower.bio = "La mia bio"
        follower.save()
        follower.following.add(self.user)

        response = self.client.get(f"/api/users/{self.user.id}/followers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.data["results"][0]
        self.assertEqual(user_data["username"], "follower1")
        self.assertEqual(user_data["bio"], "La mia bio")
        self.assertEqual(user_data["followers_count"], 0)
        self.assertEqual(user_data["following_count"], 1)
        self.assertFalse(user_data["is_followed_by_me"])
        self.assertIn("id", user_data)

    def test_followers_page_2(self):
        """GET followers pagina 2 con >10 follower → paginazione corretta."""
        # Crea 15 follower
        for i in range(15):
            f = create_authenticated_user(username=f"follower{i}")
            f.following.add(self.user)

        # Pagina 1: 10 risultati
        response = self.client.get(f"/api/users/{self.user.id}/followers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 15)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

        # Pagina 2: 5 risultati
        response = self.client.get(f"/api/users/{self.user.id}/followers/?page=2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 15)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNone(response.data["next"])
        self.assertIsNotNone(response.data["previous"])

    def test_followers_empty(self):
        """GET followers vuoti → {count: 0, next: null, previous: null, results: []}."""
        response = self.client.get(f"/api/users/{self.user.id}/followers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["count"], 0)
        self.assertIsNone(data["next"])
        self.assertIsNone(data["previous"])
        self.assertEqual(data["results"], [])

    def test_followers_nonexistent_user_returns_404(self):
        """GET followers utente inesistente → 404 con formato {code, detail}."""
        response = self.client.get("/api/users/99999/followers/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)


class TestGetFollowingPaginated(APITestCase):
    """Test per GET /api/users/{id}/following/ (paginato)."""

    def setUp(self):
        self.user = create_authenticated_user(username="target")
        self.client = create_api_client_authenticated(self.user)

    def test_following_paginated_format(self):
        """GET following → 200, formato paginato {count, next, previous, results}."""
        followed = create_authenticated_user(username="followed1")
        self.user.following.add(followed)

        response = self.client.get(f"/api/users/{self.user.id}/following/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn("count", data)
        self.assertIn("next", data)
        self.assertIn("previous", data)
        self.assertIn("results", data)
        self.assertEqual(data["count"], 1)
        self.assertEqual(len(data["results"]), 1)

    def test_following_contain_user_fields(self):
        """Results contengono User completi con campi calcolati e valori corretti."""
        followed = create_authenticated_user(username="followed1")
        self.user.following.add(followed)

        response = self.client.get(f"/api/users/{self.user.id}/following/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.data["results"][0]
        self.assertEqual(user_data["username"], "followed1")
        self.assertEqual(user_data["followers_count"], 1)
        self.assertEqual(user_data["following_count"], 0)
        # is_followed_by_me = True perche' il richiedente (target) segue followed1
        self.assertTrue(user_data["is_followed_by_me"])
        self.assertIn("bio", user_data)

    def test_following_empty(self):
        """GET following vuoti → risposta paginata vuota."""
        response = self.client.get(f"/api/users/{self.user.id}/following/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data["count"], 0)
        self.assertIsNone(data["next"])
        self.assertIsNone(data["previous"])
        self.assertEqual(data["results"], [])

    def test_following_nonexistent_user_returns_404(self):
        """GET following utente inesistente → 404 con formato {code, detail}."""
        response = self.client.get("/api/users/99999/following/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)


class TestFollowUnauthenticated(APITestCase):
    """Test per accesso non autenticato a follow/unfollow/followers/following."""

    def setUp(self):
        self.user = create_authenticated_user(username="target")
        self.anon_client = APIClient()

    def test_follow_unauthenticated_returns_401(self):
        """POST follow senza token → 401."""
        response = self.anon_client.post(f"/api/users/{self.user.id}/follow/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unfollow_unauthenticated_returns_401(self):
        """POST unfollow senza token → 401."""
        response = self.anon_client.post(f"/api/users/{self.user.id}/unfollow/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_followers_unauthenticated_returns_401(self):
        """GET followers senza token → 401."""
        response = self.anon_client.get(f"/api/users/{self.user.id}/followers/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_following_unauthenticated_returns_401(self):
        """GET following senza token → 401."""
        response = self.anon_client.get(f"/api/users/{self.user.id}/following/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
