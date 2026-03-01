"""Test auth flow: registrazione, login, refresh token.

Copre tutti i casi specificati in Story 1.1:
- AC-1: Registrazione con assegnazione gruppo toconfirm
- AC-2: Login con JWT e aggiornamento last_login
- AC-3: Refresh token con rotazione
- AC-4: Messaggi di errore in italiano
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegistrationTests(APITestCase):
    """Test endpoint POST /api/users/ (registrazione). AC-1, AC-4."""

    def test_registration_valid_data_returns_201(self):
        """Registrazione con dati validi → 201, risposta con id/username/email."""
        data = {
            "username": "mario",
            "email": "mario@test.com",
            "password": "SecureP4ss!",
        }
        response = self.client.post("/api/users/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertIn("username", response.data)
        self.assertIn("email", response.data)
        self.assertNotIn("password", response.data)
        self.assertEqual(response.data["username"], "mario")
        self.assertEqual(response.data["email"], "mario@test.com")

    def test_registration_assigns_toconfirm_group(self):
        """Il gruppo 'toconfirm' viene assegnato automaticamente alla registrazione."""
        data = {
            "username": "mario",
            "email": "mario@test.com",
            "password": "SecureP4ss!",
        }
        self.client.post("/api/users/", data, format="json")

        user = User.objects.get(username="mario")
        self.assertTrue(user.groups.filter(name="toconfirm").exists())

    def test_registration_password_is_hashed(self):
        """La password viene hashata nel database, mai salvata in chiaro."""
        data = {
            "username": "mario",
            "email": "mario@test.com",
            "password": "SecureP4ss!",
        }
        self.client.post("/api/users/", data, format="json")

        user = User.objects.get(username="mario")
        self.assertNotEqual(user.password, "SecureP4ss!")
        self.assertTrue(user.check_password("SecureP4ss!"))

    def test_registration_duplicate_username_returns_400(self):
        """Registrazione con username duplicato → errore 400 con messaggio italiano."""
        User.objects.create_user(
            username="mario", email="primo@test.com", password="SecureP4ss!"
        )
        group, _ = Group.objects.get_or_create(name="toconfirm")
        User.objects.get(username="mario").groups.add(group)

        data = {
            "username": "mario",
            "email": "secondo@test.com",
            "password": "SecureP4ss!",
        }
        response = self.client.post("/api/users/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # AC-4: messaggio in italiano (non il default inglese)
        self.assertNotIn("already exists", str(response.data))

    def test_registration_duplicate_email_returns_400(self):
        """Registrazione con email duplicata → errore 400 con messaggio italiano."""
        User.objects.create_user(
            username="mario", email="mario@test.com", password="SecureP4ss!"
        )
        group, _ = Group.objects.get_or_create(name="toconfirm")
        User.objects.get(username="mario").groups.add(group)

        data = {
            "username": "luigi",
            "email": "mario@test.com",
            "password": "SecureP4ss!",
        }
        response = self.client.post("/api/users/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # AC-4: messaggio in italiano (non il default inglese)
        self.assertNotIn("already exists", str(response.data))

    def test_registration_weak_password_returns_400(self):
        """Password interamente numerica → errore validazione."""
        data = {
            "username": "mario",
            "email": "mario@test.com",
            "password": "12345678",
        }
        response = self.client.post("/api/users/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # AC-4: messaggio in italiano (non "entirely numeric" in inglese)
        self.assertNotIn("entirely numeric", str(response.data))


class LoginTests(APITestCase):
    """Test endpoint POST /api/token/ (login JWT). AC-2, AC-4."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="mario", password="SecureP4ss!", email="mario@test.com"
        )
        group, _ = Group.objects.get_or_create(name="user")
        self.user.groups.add(group)

    def test_login_valid_credentials_returns_tokens(self):
        """Login con credenziali corrette → 200, {access, refresh}."""
        data = {"username": "mario", "password": "SecureP4ss!"}
        response = self.client.post("/api/token/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_updates_last_login(self):
        """Login con credenziali corrette aggiorna last_login."""
        self.assertIsNone(self.user.last_login)

        data = {"username": "mario", "password": "SecureP4ss!"}
        self.client.post("/api/token/", data, format="json")

        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)

    def test_login_invalid_credentials_returns_error(self):
        """Login con credenziali errate → errore con messaggio italiano."""
        data = {"username": "mario", "password": "WrongPassword!"}
        response = self.client.post("/api/token/", data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # AC-4: messaggio di errore in italiano
        self.assertIn("credenziali", str(response.data["detail"]))

    def test_login_error_does_not_reveal_username_existence(self):
        """Il messaggio di errore non rivela se l'username esiste."""
        # Tentativo con username inesistente
        response_nonexistent = self.client.post(
            "/api/token/",
            {"username": "utente_inesistente", "password": "WrongPassword!"},
            format="json",
        )

        # Tentativo con username esistente ma password errata
        response_wrong_pw = self.client.post(
            "/api/token/",
            {"username": "mario", "password": "WrongPassword!"},
            format="json",
        )

        # Entrambi devono dare lo stesso tipo di errore e lo stesso messaggio
        self.assertEqual(
            response_nonexistent.status_code, response_wrong_pw.status_code
        )
        self.assertEqual(
            str(response_nonexistent.data["detail"]),
            str(response_wrong_pw.data["detail"]),
        )


class TokenRefreshTests(APITestCase):
    """Test endpoint POST /api/token/refresh/ (refresh JWT). AC-3."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="mario", password="SecureP4ss!", email="mario@test.com"
        )
        group, _ = Group.objects.get_or_create(name="user")
        self.user.groups.add(group)

    def test_refresh_valid_token_returns_new_access(self):
        """Refresh con token valido → nuovo access token."""
        login_response = self.client.post(
            "/api/token/",
            {"username": "mario", "password": "SecureP4ss!"},
            format="json",
        )
        refresh_token = login_response.data["refresh"]

        response = self.client.post(
            "/api/token/refresh/",
            {"refresh": refresh_token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        # AC-3: rotazione attiva, deve ritornare un nuovo refresh token
        self.assertIn("refresh", response.data)

    def test_refresh_old_token_blacklisted_after_rotation(self):
        """AC-3: il vecchio refresh token viene invalidato dopo rotazione."""
        login_response = self.client.post(
            "/api/token/",
            {"username": "mario", "password": "SecureP4ss!"},
            format="json",
        )
        old_refresh = login_response.data["refresh"]

        # Prima rotazione — il vecchio token viene blacklistato
        self.client.post(
            "/api/token/refresh/",
            {"refresh": old_refresh},
            format="json",
        )

        # Tentativo di riuso del vecchio token — deve fallire
        response = self.client.post(
            "/api/token/refresh/",
            {"refresh": old_refresh},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_invalid_token_returns_error(self):
        """Refresh con token invalido → errore."""
        response = self.client.post(
            "/api/token/refresh/",
            {"refresh": "token-completamente-invalido"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # AC-4: messaggio in italiano
        self.assertIn("scaduto", str(response.data["detail"]))
