import { http, HttpResponse } from "msw";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export const handlers = [
  // POST /api/token/ — login JWT
  http.post(`${API_BASE}/api/token/`, async ({ request }) => {
    const body = (await request.json()) as Record<string, string>;
    if (body.username === "testuser" && body.password === "testpass123") {
      return HttpResponse.json({
        access: "mock-access-token",
        refresh: "mock-refresh-token",
      });
    }
    return HttpResponse.json(
      { detail: "Credenziali non valide." },
      { status: 401 },
    );
  }),

  // POST /api/users/ — registrazione
  http.post(`${API_BASE}/api/users/`, async ({ request }) => {
    const body = (await request.json()) as Record<string, string>;
    return HttpResponse.json(
      {
        id: 1,
        username: body.username,
        email: body.email,
      },
      { status: 201 },
    );
  }),

  // GET /api/videos/ — lista paginata
  http.get(`${API_BASE}/api/videos/`, () => {
    return HttpResponse.json({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 1,
          title: "Test Video",
          tag: "clutch",
          uploader: { id: 1, username: "testuser" },
          duration: 30,
          created_at: "2026-02-28T12:00:00Z",
          file_url: "https://minio.local/video/test.mp4",
        },
      ],
    });
  }),

  // GET /api/videos/:id/ — dettaglio video
  http.get(`${API_BASE}/api/videos/:id/`, ({ params }) => {
    return HttpResponse.json({
      id: Number(params.id),
      title: "Test Video",
      tag: "clutch",
      uploader: { id: 1, username: "testuser" },
      duration: 30,
      created_at: "2026-02-28T12:00:00Z",
      file_url: "https://minio.local/video/test.mp4",
      average_rating: 4.2,
      rating_count: 5,
    });
  }),

  // GET /api/users/:id/ — profilo utente
  http.get(`${API_BASE}/api/users/:id/`, ({ params }) => {
    return HttpResponse.json({
      id: Number(params.id),
      username: "testuser",
      email: "test@test.com",
      date_joined: "2026-01-01T00:00:00Z",
    });
  }),
];
