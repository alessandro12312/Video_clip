import { describe, expect, it } from "vitest";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

describe("MSW handlers", () => {
  it("GET /api/videos/ ritorna formato paginato", async () => {
    const response = await fetch(`${API_BASE}/api/videos/`);
    const data = await response.json();

    expect(response.ok).toBe(true);
    expect(data).toHaveProperty("count");
    expect(data).toHaveProperty("next");
    expect(data).toHaveProperty("previous");
    expect(data).toHaveProperty("results");
    expect(data.results).toHaveLength(1);
    expect(data.results[0].title).toBe("Test Video");
  });

  it("POST /api/token/ con credenziali valide ritorna JWT tokens", async () => {
    const response = await fetch(`${API_BASE}/api/token/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: "testuser",
        password: "testpass123",
      }),
    });
    const data = await response.json();

    expect(response.ok).toBe(true);
    expect(data).toHaveProperty("access", "mock-access-token");
    expect(data).toHaveProperty("refresh", "mock-refresh-token");
  });

  it("POST /api/users/ registra un nuovo utente", async () => {
    const response = await fetch(`${API_BASE}/api/users/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: "newuser",
        email: "new@test.com",
        password: "TestPass123!",
      }),
    });
    const data = await response.json();

    expect(response.status).toBe(201);
    expect(data.username).toBe("newuser");
    expect(data.email).toBe("new@test.com");
  });

  it("GET /api/videos/:id ritorna dettaglio video", async () => {
    const response = await fetch(`${API_BASE}/api/videos/1/`);
    const data = await response.json();

    expect(response.ok).toBe(true);
    expect(data.id).toBe(1);
    expect(data.title).toBe("Test Video");
    expect(data).toHaveProperty("average_rating");
  });

  it("GET /api/users/:id ritorna profilo utente", async () => {
    const response = await fetch(`${API_BASE}/api/users/1/`);
    const data = await response.json();

    expect(response.ok).toBe(true);
    expect(data.id).toBe(1);
    expect(data.username).toBe("testuser");
  });
});
