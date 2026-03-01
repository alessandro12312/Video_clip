"""Test auth flow: registrazione, login, refresh token."""

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from cs_clips.tests.conftest import create_authenticated_user

User = get_user_model()


class RegistrationTests(APITestCase):
    """Test endpoint POST /api/users/ (registrazione)."""

    def test_registration_creates_user_with_toconfirm_group(self):
        """La registrazione crea utente e assegna gruppo 'toconfirm'."""
        data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "TestPassword123!",
        }
        response = self.client.post("/api/users/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username="newuser")
        self.assertTrue(user.groups.filter(name="toconfirm").exists())


class LoginTests(APITestCase):
    """Test endpoint POST /api/token/ (login JWT)."""

    def setUp(self):
        self.user = create_authenticated_user()

    def test_login_returns_jwt_tokens(self):
        """Login con credenziali valide ritorna access e refresh token."""
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post("/api/token/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials_returns_401(self):
        """Login con credenziali errate ritorna 401."""
        data = {"username": "testuser", "password": "wrongpassword"}
        response = self.client.post("/api/token/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshTests(APITestCase):
    """Test endpoint POST /api/token/refresh/ (refresh JWT)."""

    def setUp(self):
        self.user = create_authenticated_user()

    def test_refresh_returns_new_access_token(self):
        """Refresh con token valido ritorna nuovo access token."""
        # Prima ottieni tokens via login
        login_response = self.client.post(
            "/api/token/",
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        refresh_token = login_response.data["refresh"]

        # Poi usa refresh token
        response = self.client.post(
            "/api/token/refresh/",
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
