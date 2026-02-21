# Modelli Dati - Video_clip Backend

> Generato automaticamente il 2026-02-14 | Scan level: deep

## Panoramica

Database PostgreSQL 16 gestito tramite Django ORM con 5 modelli custom + gruppi Django built-in.
Driver: psycopg 3.2.4 | 14 migrazioni applicate.

---

## Diagramma Relazioni

```
┌──────────────┐     M:M (following)      ┌──────────────┐
│              │◄────────────────────────►│              │
│     User     │                          │     User     │
│  (AbstractUser)                         │  (self-ref)  │
│              │                          │              │
└──────┬───────┘                          └──────────────┘
       │
       │ 1:N (uploader)        1:N (user)         1:N (user)
       │
       ▼                        ▼                   ▼
┌──────────────┐         ┌──────────────┐    ┌──────────────┐
│    Video     │◄────────│   Rating     │    │   Comment    │
│              │  1:N    │              │    │              │
│              │         │  value: 1-5  │    │  timestamp_  │
│              │◄────────│  unique:     │    │  second      │
│              │         │  (user,video)│    │              │
└──────┬───────┘         └──────────────┘    └──────────────┘
       │                                            │
       │ N:1 (contest)                              │
       │                                     1:N (video)
       ▼                                            │
┌──────────────┐                                    │
│   Contest    │                                    │
│              │◄───────────────────────────────────┘
│  winner ────►│ 1:1 (FK to Video)
│  tag: enum   │
│  weekly      │
└──────────────┘

┌──────────────┐
│    Group     │  (Django built-in)
│              │  M:N con User
│  toconfirm   │
│  user        │
│  superuser   │
└──────────────┘
```

---

## Modelli

### User (extends AbstractUser)

**Tabella:** `cs_clips_user`
**Auth model:** `AUTH_USER_MODEL = 'cs_clips.User'`

| Campo | Tipo | Vincoli | Descrizione |
|-------|------|---------|-------------|
| id | BigAutoField | PK, auto | ID utente |
| username | CharField | unique, required | Nome utente (ereditato) |
| email | EmailField | unique, required | Email (reso obbligatorio) |
| password | CharField | required | Password (hashed, ereditato) |
| first_name | CharField | optional | Nome (ereditato) |
| last_name | CharField | optional | Cognome (ereditato) |
| is_active | BooleanField | default=True | Account attivo (ereditato) |
| is_staff | BooleanField | default=False | Accesso admin (ereditato) |
| is_superuser | BooleanField | default=False | Superutente (ereditato) |
| last_login | DateTimeField | nullable | Ultimo accesso (aggiornato da JWT) |
| date_joined | DateTimeField | auto | Data registrazione (ereditato) |
| created_at | DateTimeField | auto_now_add | Timestamp creazione |
| updated_at | DateTimeField | auto_now | Timestamp aggiornamento |
| following | M2M(self) | symmetrical=False | Utenti seguiti |
| groups | M2M(Group) | blank=False | Gruppi/ruoli (obbligatorio) |
| user_permissions | M2M(Permission) | blank=True | Permessi specifici |

**Relazioni inverse:**
- `followers` → M2M inversa di `following`
- `uploaded_videos` → Video caricati dall'utente
- `ratings` → Rating dati dall'utente
- `comments` → Commenti scritti dall'utente

**Note:**
- `groups` è `blank=False` — ogni utente DEVE appartenere ad almeno un gruppo
- Al momento della registrazione viene assegnato automaticamente al gruppo `toconfirm`

---

### Contest

**Tabella:** `cs_clips_contest`

| Campo | Tipo | Vincoli | Descrizione |
|-------|------|---------|-------------|
| id | BigAutoField | PK, auto | ID contest |
| name | CharField(100) | required | Nome generato (es: "2025giugno2clutch") |
| tag | CharField(20) | choices, required | Categoria: `clutch`, `funny`, `fail` |
| start_date | DateField | required | Lunedì della settimana |
| end_date | DateField | required | Domenica della settimana |
| winner | FK(Video) | nullable, SET_NULL | Video vincitore |
| is_closed | BooleanField | default=False | Contest chiuso |
| closed_at | DateTimeField | nullable | Timestamp chiusura |

**Vincoli:**
- `unique_together: (start_date, end_date, tag)` — un contest per settimana per tag

**Enum Tag:**

| Valore | Label |
|--------|-------|
| `clutch` | Clutch |
| `funny` | Funny |
| `fail` | Fail |

**Logica contest settimanale:**
- Periodo: lunedì → domenica
- Creazione automatica alla prima upload video con quel tag nella settimana
- Nome formato: `{anno}{mese_italiano}{settimana_del_mese}{tag}`
- Se chiuso anticipatamente, il prossimo upload crea un nuovo contest con suffisso `(N)`

---

### Video

**Tabella:** `cs_clips_video`

| Campo | Tipo | Vincoli | Descrizione |
|-------|------|---------|-------------|
| id | BigAutoField | PK, auto | ID video |
| title | CharField(100) | required | Titolo del video |
| file | FileField | upload_to='videos/' | File video |
| uploader | FK(User) | CASCADE, required | Chi ha caricato il video |
| contest | FK(Contest) | SET_NULL, nullable | Contest associato |
| tag | CharField(20) | choices, required | Categoria (stesso enum di Contest) |
| views | IntegerField | default=0 | Contatore visualizzazioni |
| duration | PositiveIntegerField | default=0 | Durata in secondi (calcolata auto) |
| created_at | DateTimeField | auto_now_add | Timestamp creazione |
| updated_at | DateTimeField | auto_now | Timestamp aggiornamento |

**Relazioni inverse:**
- `ratings` → Rating ricevuti dal video
- `comments` → Commenti sul video
- `won_contests` → Contest vinti da questo video

**Comportamenti speciali:**
- `delete()` → Override: cancella anche il file fisico dal filesystem
- `duration` → Calcolata automaticamente nel serializer via moviepy durante la creazione
- `views` → Incrementato atomicamente via `F('views') + 1`
- `contest` → Assegnato automaticamente tramite `get_or_create_current_contest(tag)`

**TODO nel codice:**
- Rimuovere `default=Contest.Tag.FUNNY` per `tag` in produzione
- Rimuovere `default=0` per `duration` in produzione

---

### Rating

**Tabella:** `cs_clips_rating`

| Campo | Tipo | Vincoli | Descrizione |
|-------|------|---------|-------------|
| id | BigAutoField | PK, auto | ID rating |
| user | FK(User) | CASCADE, required | Utente che vota |
| video | FK(Video) | CASCADE, required | Video votato |
| value | IntegerField | min=1, max=5 | Punteggio (scala 1-5) |
| created_at | DateTimeField | auto_now_add | Timestamp creazione |
| updated_at | DateTimeField | auto_now | Timestamp aggiornamento |

**Vincoli:**
- `unique_together: (user, video)` — un solo voto per utente per video

---

### Comment

**Tabella:** `cs_clips_comment`

| Campo | Tipo | Vincoli | Descrizione |
|-------|------|---------|-------------|
| id | BigAutoField | PK, auto | ID commento |
| user | FK(User) | CASCADE, required | Autore del commento |
| video | FK(Video) | CASCADE, required | Video commentato |
| content | TextField | required | Testo del commento |
| timestamp_second | PositiveIntegerField | default=0 | Secondo del video (posizione) |
| created_at | DateTimeField | auto_now_add | Timestamp creazione |
| updated_at | DateTimeField | auto_now | Timestamp aggiornamento |

**Validazione custom (nel serializer):**
- `timestamp_second` >= 0
- `timestamp_second` <= durata del video
- Il video deve avere una durata impostata

**Note:**
- Un utente può lasciare più commenti sullo stesso video
- I commenti sono "ancorati" a un momento specifico del video (per feature "commenti nel player")

**TODO nel codice:**
- Rimuovere `default=0` per `timestamp_second` in produzione

---

## Gruppi e Ruoli (Django Auth)

Gestiti tramite il sistema `auth.Group` di Django, creati nella migrazione `0002_create_groups`.

| Gruppo | Descrizione | Permessi |
|--------|-------------|----------|
| `toconfirm` | Utente appena registrato, in attesa di conferma | Solo lettura (SAFE_METHODS) |
| `user` | Utente confermato | CRUD completo, delete solo dei propri contenuti |
| (superuser) | Amministratore | Accesso completo, nessuna restrizione |

**Flusso ruoli:**
1. Registrazione → assegnato a `toconfirm`
2. (Processo manuale/admin) → promosso a `user`
3. (Admin panel) → flag `is_superuser` per admin

---

## Evoluzione Schema (Migrazioni)

| # | Migrazione | Descrizione |
|---|-----------|-------------|
| 0001 | initial | Modelli base: User, Video, Rating, Comment |
| 0002 | create_groups | Creazione gruppi Django (toconfirm, user) |
| 0003 | contest_video_contest | Aggiunto modello Contest, FK Video→Contest |
| 0004 | contest_is_closed | Aggiunto campo `is_closed` a Contest |
| 0005 | contest_closed_at | Aggiunto campo `closed_at` a Contest |
| 0006 | video_views | Aggiunto campo `views` a Video |
| 0007 | contest_winner | Aggiunto FK `winner` a Contest (→Video) |
| 0008-0010 | alter_user_email | Reso email unique e obbligatoria |
| 0011 | alter_user_user_permissions | Aggiornamento relazione permessi utente |
| 0012 | alter_user_groups_alter_user_user_permissions | Aggiornamento relazioni gruppi e permessi |
| 0013 | comment_timestamp_second_contest_tag_video_duration | Aggiunti: timestamp_second, tag contest, duration video |
| 0014 | user_following_alter_comment_timestamp_second | Aggiunta relazione M2M following/followers |

---

## Note per lo Sviluppo Frontend

1. **ID utente** — Tutti i modelli usano BigAutoField, i riferimenti utente nelle risposte API sono per `username` (stringa) nei campi read-only
2. **Cascate di eliminazione:**
   - Eliminare un utente → elimina tutti i suoi video, rating e commenti
   - Eliminare un video → elimina tutti i rating e commenti associati + file fisico
   - Eliminare un contest → i video restano (`SET_NULL`)
3. **Media URL** — I file video sono serviti da `http://.../media/videos/filename.mp4`
4. **Commenti timestampati** — Il frontend dovrà gestire la visualizzazione dei commenti sincronizzati con il player video
5. **Contest automatici** — Non serve creare contest manualmente, vengono creati all'upload del primo video per tag nella settimana
6. **Paginazione** — Tutti gli endpoint lista sono paginati (10 per pagina)
