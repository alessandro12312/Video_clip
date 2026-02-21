# Panoramica Progetto - Video_clip

> Generato automaticamente il 2026-02-14 | Scan level: deep

## Cos'è Video_clip

Video_clip è una piattaforma web di **contest video settimanali** dove gli utenti possono:

- Caricare video in tre categorie: **Clutch**, **Funny**, **Fail**
- Votare i video degli altri utenti (scala 1-5)
- Commentare i video con timestamp sincronizzati alla riproduzione
- Seguire altri utenti e vedere i loro video nel feed
- Partecipare a contest settimanali automatici con vincitore calcolato algoritmicamente

---

## Struttura Repository

| Parte | Percorso | Stato | Tecnologia |
|-------|----------|-------|------------|
| **Backend** | `backend/` | Attivo | Django 5.1.6 + DRF 3.15.1 |
| **Frontend** | `frontend/` | Da sviluppare | TBD |
| **Database** | `db/` | Attivo (Docker) | PostgreSQL 16 |
| **Documentazione** | `docs/` | Generata | Markdown |

**Tipo repository:** Monorepo
**Tipo progetto:** Backend API (brownfield — frontend greenfield)

---

## Stack Tecnologico

| Categoria | Tecnologia | Versione |
|-----------|-----------|----------|
| Framework Backend | Django + DRF | 5.1.6 + 3.15.1 |
| Database | PostgreSQL | 16 |
| Autenticazione | JWT (SimpleJWT) | 5.3.1 |
| API Docs | drf-spectacular (OpenAPI 3.0) | 0.28.0 |
| Video Processing | moviepy | 2.2.1 |
| Container | Docker Compose | — |
| Linguaggio | Python | 3.x |

---

## Architettura

**Pattern:** API-centric monolith con ViewSet-based REST

- Django single-app (`cs_clips`) con tutta la logica di business
- 4 ViewSets CRUD + 2 APIViews custom per contest
- JWT stateless per autenticazione
- Permessi basati su ruoli (groups: toconfirm, user, superuser)
- Processing video sincrono
- Storage media locale

---

## Funzionalità Implementate

### Utenti
- Registrazione con assegnazione automatica ruolo `toconfirm`
- Login JWT (access 12h, refresh 1d)
- Profilo con followers/following
- Follow/unfollow utenti
- CRUD completo

### Video
- Upload con calcolo automatico durata (moviepy)
- Assegnazione automatica a contest settimanale per tag
- Feed "following" (video degli utenti seguiti)
- Top-rated con filtro temporale (day/week/month/year/all)
- Incremento visualizzazioni atomico
- Eliminazione con cleanup file fisico

### Rating
- Voto da 1 a 5 per video
- Vincolo: un solo voto per utente per video
- Media voto calcolata dinamicamente

### Commenti
- Commenti timestampati (ancorati a un secondo del video)
- Validazione: timestamp entro la durata del video

### Contest
- Contest settimanali automatici (lunedì-domenica) per tag
- Chiusura manuale con calcolo vincitore
- Algoritmo spareggio ponderato (ratings 50%, views 30%, comments 20%)
- Storico vincitori con paginazione

---

## Documentazione Generata

- [Panoramica Progetto](./project-overview.md) — Questo file
- [Architettura](./architecture.md) — Pattern architetturale, stack, diagrammi
- [Contratti API](./api-contracts.md) — Tutti gli endpoint con request/response
- [Modelli Dati](./data-models.md) — Schema database, relazioni, vincoli
- [Analisi Albero Sorgente](./source-tree-analysis.md) — Struttura directory annotata
- [Guida Sviluppo](./development-guide.md) — Setup, comandi, convenzioni

---

## Link Rapidi

| Risorsa | URL |
|---------|-----|
| Swagger UI | http://127.0.0.1:8000/api/docs/ |
| ReDoc | http://127.0.0.1:8000/api/redoc/ |
| Django Admin | http://127.0.0.1:8000/admin/ |
| pgAdmin | http://127.0.0.1:8080/ |
| API Root | http://127.0.0.1:8000/api/ |
