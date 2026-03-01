"""Test filtro video per uploader — Story 1.4."""

from rest_framework.test import APITestCase

from cs_clips.tests.conftest import (
    create_api_client_authenticated,
    create_authenticated_user,
    create_sample_video,
)


class TestVideoFilterByUploader(APITestCase):
    """Test AC-1: filtro video per uploader via query param."""

    def setUp(self):
        self.alice = create_authenticated_user(username="alice")
        self.bob = create_authenticated_user(username="bob")
        self.client_alice = create_api_client_authenticated(self.alice)

        # Alice ha 3 video, Bob ha 2 video
        for i in range(3):
            create_sample_video(self.alice, title=f"Alice Video {i}")
        for i in range(2):
            create_sample_video(self.bob, title=f"Bob Video {i}")

    def test_filter_by_uploader_returns_only_uploader_videos(self):
        """GET /api/videos/?uploader={id} ritorna solo i video dell'uploader."""
        response = self.client_alice.get("/api/videos/", {"uploader": self.alice.id})
        self.assertEqual(response.status_code, 200)
        results = response.data["results"]
        self.assertEqual(len(results), 3)
        for video in results:
            self.assertEqual(video["uploader"], "alice")

    def test_filter_by_uploader_bob(self):
        """Filtro per Bob ritorna solo i suoi 2 video."""
        response = self.client_alice.get("/api/videos/", {"uploader": self.bob.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        for video in response.data["results"]:
            self.assertEqual(video["uploader"], "bob")

    def test_filter_uploader_no_videos_returns_empty(self):
        """Uploader senza video ritorna risposta paginata vuota."""
        eve = create_authenticated_user(username="eve")
        response = self.client_alice.get("/api/videos/", {"uploader": eve.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])
        self.assertIsNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_filter_uploader_nonexistent_returns_empty_not_404(self):
        """Uploader inesistente (ID 99999) ritorna 200 vuoto, NON 404."""
        response = self.client_alice.get("/api/videos/", {"uploader": 99999})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)
        self.assertEqual(response.data["results"], [])

    def test_filter_preserves_created_at_order(self):
        """I video filtrati mantengono ordine -created_at."""
        response = self.client_alice.get("/api/videos/", {"uploader": self.alice.id})
        self.assertEqual(response.status_code, 200)
        results = response.data["results"]
        # I piu' recenti devono essere prima (ordine decrescente)
        titles = [v["title"] for v in results]
        self.assertEqual(titles, ["Alice Video 2", "Alice Video 1", "Alice Video 0"])


class TestVideoFilterPagination(APITestCase):
    """Test AC-2: paginazione corretta con filtro uploader."""

    def setUp(self):
        self.alice = create_authenticated_user(username="alice")
        self.bob = create_authenticated_user(username="bob")
        self.client_alice = create_api_client_authenticated(self.alice)

        # Alice ha 15 video (page_size=10, due pagine)
        for i in range(15):
            create_sample_video(self.alice, title=f"Alice Video {i:02d}")
        # Bob ha 3 video (non devono interferire)
        for i in range(3):
            create_sample_video(self.bob, title=f"Bob Video {i}")

    def test_pagination_page_1_with_filter(self):
        """Pagina 1: 10 video su 15, next presente."""
        response = self.client_alice.get("/api/videos/", {"uploader": self.alice.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 15)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])
        self.assertIsNone(response.data["previous"])

    def test_pagination_page_2_with_filter(self):
        """Pagina 2: 5 video rimanenti, previous presente."""
        response = self.client_alice.get(
            "/api/videos/", {"uploader": self.alice.id, "page": 2}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 15)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNone(response.data["next"])
        self.assertIsNotNone(response.data["previous"])

    def test_pagination_preserves_uploader_param_in_next(self):
        """Il link next preserva il parametro uploader."""
        response = self.client_alice.get("/api/videos/", {"uploader": self.alice.id})
        next_url = response.data["next"]
        self.assertIn(f"uploader={self.alice.id}", next_url)

    def test_pagination_preserves_uploader_param_in_previous(self):
        """Il link previous preserva il parametro uploader."""
        response = self.client_alice.get(
            "/api/videos/", {"uploader": self.alice.id, "page": 2}
        )
        previous_url = response.data["previous"]
        self.assertIn(f"uploader={self.alice.id}", previous_url)


class TestVideoListWithoutFilter(APITestCase):
    """Test AC-3: endpoint senza filtro invariato (non-regressione)."""

    def setUp(self):
        self.alice = create_authenticated_user(username="alice")
        self.bob = create_authenticated_user(username="bob")
        self.client_alice = create_api_client_authenticated(self.alice)

        create_sample_video(self.alice, title="Alice Video")
        create_sample_video(self.bob, title="Bob Video")

    def test_no_filter_returns_all_videos(self):
        """GET /api/videos/ senza filtro ritorna tutti i video."""
        response = self.client_alice.get("/api/videos/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_following_action_not_impacted(self):
        """Custom action /following/ non e' impattata dal filtro."""
        response = self.client_alice.get("/api/videos/following/")
        self.assertEqual(response.status_code, 200)
        # Verifica struttura paginata (o array per zero following)
        data = response.data
        if isinstance(data, dict):
            self.assertIn("results", data)
            self.assertIn("count", data)

    def test_top_rated_action_not_impacted(self):
        """Custom action /top-rated/ non e' impattata dal filtro."""
        response = self.client_alice.get("/api/videos/top-rated/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertEqual(response.data["count"], 2)

    def test_filter_uploader_non_numeric_returns_error(self):
        """Uploader con valore non numerico ritorna 400."""
        response = self.client_alice.get("/api/videos/", {"uploader": "abc"})
        self.assertEqual(response.status_code, 400)
