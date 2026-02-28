# Architettura — Backend Video_clip

> Generato automaticamente il 2026-02-28 | Deep Scan | Workflow: document-project v1.2.0

---

## Executive Summary

Il backend è un **monolite API-centric** costruito con Django 5.1.6 + Django REST Framework 3.15.1. Espone una REST API completa per una piattaforma di video clip contest settimanali, con autenticazione JWT stateless, storage S3-compatible (MinIO) e scheduler per la chiusura automatica dei contest.

---

## Stack Tecnologico

| Categoria | Tecnologia | Versione |
|---|---|---|
| Framework | Django + DRF | 5.1.6 / 3.15.1 |
| Database | PostgreSQL + psycopg | 16 / 3.2.4 |
| Auth | SimpleJWT | 5.3.1 |
| Storage | MinIO + boto3 + django-minio-backend | 7.2.15 / 1.38.41 / 3.8.0 |
| Video | moviepy + imageio-ffmpeg | 2.2.1 / 0.6.0 |
| Scheduler | APScheduler + django-apscheduler | 3.11.0 / 0.7.0 |
| API Docs | drf-spectacular | 0.28.0 |
| CORS | django-cors-headers | 4.7.0 |
| Monitoring | Prometheus + Flower | 0.22.1 / 2.0.1 |
| Task Queue | Celery + Redis (ready, non attivo) | 5.5.3 / 5.2.1 |

---

## Pattern Architetturale

### API-Centric Monolith con ViewSet-based REST

```
┌─────────────────────────────────────────────────┐
│                   Django App                     │
├─────────────────────────────────────────────────┤
│  URL Router (DefaultRouter + path())             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ users/  │  │ videos/ │  │comments/│ ...     │
│  └────┬────┘  └────┬────┘  └────┬────┘        │
│       ▼            ▼            ▼              │
│  ┌──────────────────────────────────────┐      │
│  │         ViewSets (ModelViewSet)       │      │
│  │  + @action per operazioni custom      │      │
│  └───────────────┬──────────────────────┘      │
│                  ▼                              │
│  ┌──────────────────────────────────────┐      │
│  │      Serializers (I/O separation)     │      │
│  │  Input / Output / Update per dominio  │      │
│  └───────────────┬──────────────────────┘      │
│                  ▼                              │
│  ┌──────────────────────────────────────┐      │
│  │         Permission Classes            │      │
│  │  RoleBased / OnlyUsers / OnlyAdmins   │      │
│  └───────────────┬──────────────────────┘      │
│                  ▼                              │
│  ┌──────────────────────────────────────┐      │
│  │            Models (ORM)               │      │
│  │  User, Video, Contest, Comment, Rating│      │
│  └───────────────┬──────────────────────┘      │
│                  ▼                              │
│  ┌────────────┐  ┌────────────┐                │
│  │ PostgreSQL │  │   MinIO    │                │
│  └────────────┘  └────────────┘                │
└─────────────────────────────────────────────────┘
```

### Struttura Modulare per Dominio

Ogni dominio ha la propria directory in `cs_clips/api/{dominio}/`:
- `{dominio}_views.py` — ViewSet o APIView
- `{dominio}_serializers.py` — Serializer I/O
- `{dominio}_urls.py` — URL patterns

Domini: users, videos, comments, ratings, contests

---

## Architettura Dati

### 5 Modelli Core

```
User ──1:N──► Video ──N:1──► Contest
  │             │
  │ 1:N         │ 1:N
  ▼             ▼
Rating ◄──N:1── Video
Comment ◄──N:1── Video
```

- **User**: AbstractUser + email unique + following M2M (asimmetrico)
- **Video**: File su MinIO, durata estratta via FFmpeg, tag per contest
- **Contest**: Settimanale per tag, winner FK su Video, auto-close via scheduler
- **Comment**: Testo + timestamp_second (ancorato al video)
- **Rating**: Voto 1-5, unique per (user, video)

### Storage

- **Database**: PostgreSQL 16 per dati strutturati
- **Object Storage**: MinIO (S3) per file video — presigned URL con scadenza 1h
- **Cleanup**: django_cleanup elimina file orfani

---

## Autenticazione e Autorizzazione

### JWT Stateless (SimpleJWT)

| Parametro | Valore |
|---|---|
| Access Token | 12 ore |
| Refresh Token | 1 giorno |
| Rotation | Attiva |
| Custom Claim | Nessuno (standard JWT) |

### Sistema Permessi a Gruppi

| Gruppo | Permessi |
|---|---|
| `toconfirm` | Solo lettura (GET/HEAD/OPTIONS) |
| `user` | CRUD, DELETE solo propri contenuti |
| `admin` | Accesso completo |
| Superuser | Bypass tutti i controlli |

---

## API Design

- **35 endpoint** in 5 domini
- **Paginazione**: PageNumberPagination (page_size=10)
- **Errori**: handler centralizzato con formato `{code, detail}`
- **Upload**: multipart/form-data + estrazione durata FFmpeg
- **Swagger**: `/api/docs/` (drf-spectacular)

---

## Background Jobs

### APScheduler

- **Job**: `close_contests` — cron ogni giovedì 11:33 UTC
- **Algoritmo**: media voti → spareggio ponderato (voti 50%, views 30%, commenti 20%)
- **Avvio**: automatico in `CsClipsConfig.ready()`

### Celery (Ready, Non Attivo)

Pacchetti installati (Celery 5.5.3, Redis 5.2.1, Flower 2.0.1) ma non configurati. APScheduler usato al posto.

---

## Gap e Limitazioni

| Gap | Severità | Note |
|---|---|---|
| `VideoSerializer` inesistente in video_views.py | Alta | Bug: update/partial_update causerebbe NameError |
| Import `Response` mancante in user_views.py | Alta | Bug runtime |
| Paginazione followers/following non implementata | Media | Dichiarata ma non funzionante |
| CORS allow all origins | Media | Solo per sviluppo |
| SECRET_KEY hardcoded | Alta | Da spostare in .env per produzione |
| DEBUG=True default | Media | Da configurare per produzione |
| Nessun test automatizzato | Media | Da implementare |
| Celery non configurato | Bassa | APScheduler funziona per il caso d'uso corrente |
| Nessun filtro video per utente | Media | Frontend filtra client-side |
| Endpoint `by-username` mancante | Alta | Frontend lo chiama ma non esiste |
