# Modelli Dati — Backend Video_clip

> Generato automaticamente il 2026-02-28 | Deep Scan | Workflow: document-project v1.2.0

---

## Panoramica

Il backend definisce **5 modelli** nel package `cs_clips.models/`, organizzati con convenzione 1-file-per-modello:

| Modello | File | Descrizione |
|---------|------|-------------|
| `User` | `cs_clips/models/user.py` | Utente custom (estende AbstractUser) |
| `Video` | `cs_clips/models/video.py` | Video caricato da un utente |
| `Contest` | `cs_clips/models/contest.py` | Contest settimanale con tag/categoria |
| `Comment` | `cs_clips/models/comment.py` | Commento timestampato su un video |
| `Rating` | `cs_clips/models/rating.py` | Valutazione numerica (1-5) su un video |

**AUTH_USER_MODEL** = `'cs_clips.User'` | **DEFAULT_AUTO_FIELD** = `BigAutoField` (int64)

---

## User

**Estende**: `AbstractUser`

### Campi Ereditati

| Campo | Tipo | Vincoli |
|---|---|---|
| `id` | `BigAutoField` | PK |
| `username` | `CharField(150)` | unique |
| `password` | `CharField(128)` | required |
| `email` | *sovrascritto* | — |
| `first_name` | `CharField(150)` | blank |
| `last_name` | `CharField(150)` | blank |
| `is_staff` | `BooleanField` | default=False |
| `is_superuser` | `BooleanField` | default=False |
| `is_active` | `BooleanField` | default=True |
| `date_joined` | `DateTimeField` | auto |
| `last_login` | `DateTimeField` | null |

### Campi Custom

| Campo | Tipo | Vincoli | Note |
|---|---|---|---|
| `email` | `EmailField(254)` | **unique**, not null, not blank | Sovrascrive AbstractUser |
| `created_at` | `DateTimeField` | auto_now_add | Audit |
| `updated_at` | `DateTimeField` | auto_now | Audit |

### Relazioni

| Campo | Tipo | Target | related_name | On Delete | Note |
|---|---|---|---|---|---|
| `following` | `ManyToManyField` | `self` | `'followers'` | — | Asimmetrico, blank |
| `groups` | `ManyToManyField` | `auth.Group` | `'custom_user_set'` | — | Override AbstractUser |
| `user_permissions` | `ManyToManyField` | `auth.Permission` | `'custom_user_permissions_set'` | — | Override AbstractUser |

### Relazioni Inverse

| Da Modello | Campo | related_name |
|---|---|---|
| Video | uploader | `uploaded_videos` |
| Comment | user | `comments` |
| Rating | user | `ratings` |

---

## Contest

### Choices

```python
class Tag(TextChoices):
    CLUTCH = 'clutch', 'Clutch'
    FUNNY  = 'funny',  'Funny'
    FAIL   = 'fail',   'Fail'
```

### Campi

| Campo | Tipo | Vincoli | Note |
|---|---|---|---|
| `id` | `BigAutoField` | PK | |
| `name` | `CharField(100)` | required | Nome contest |
| `tag` | `CharField(20)` | choices=Tag, default=FUNNY | Categoria |
| `start_date` | `DateField` | required | Data inizio |
| `end_date` | `DateField` | required | Data fine |
| `is_closed` | `BooleanField` | default=False | Flag chiusura |
| `closed_at` | `DateTimeField` | null, blank | Timestamp chiusura |

### Relazioni

| Campo | Tipo | Target | related_name | On Delete |
|---|---|---|---|---|
| `winner` | `ForeignKey` | Video | `'won_contests'` | SET_NULL |

### Meta

```python
unique_together = ('start_date', 'end_date', 'tag')
```

---

## Video

### Campi

| Campo | Tipo | Vincoli | Note |
|---|---|---|---|
| `id` | `BigAutoField` | PK | |
| `title` | `CharField(100)` | required | Titolo |
| `file` | `FileField` | upload_to="" | Storage MinIO |
| `views` | `IntegerField` | default=0 | Contatore views |
| `tag` | `CharField(20)` | choices=Tag, default=FUNNY | Categoria |
| `duration` | `PositiveIntegerField` | default=0 | Durata in secondi |
| `created_at` | `DateTimeField` | auto_now_add | |
| `updated_at` | `DateTimeField` | auto_now | |

### Relazioni

| Campo | Tipo | Target | related_name | On Delete |
|---|---|---|---|---|
| `uploader` | `ForeignKey` | User | `'uploaded_videos'` | CASCADE |
| `contest` | `ForeignKey` | Contest | `'videos'` | SET_NULL (null) |

### Relazioni Inverse

| Da Modello | Campo | related_name |
|---|---|---|
| Comment | video | `comments` |
| Rating | video | `ratings` |
| Contest | winner | `won_contests` |

---

## Comment

### Campi

| Campo | Tipo | Vincoli | Note |
|---|---|---|---|
| `id` | `BigAutoField` | PK | |
| `content` | `TextField` | required | Testo |
| `timestamp_second` | `PositiveIntegerField` | default=0 | Secondo nel video |
| `created_at` | `DateTimeField` | auto_now_add | |
| `updated_at` | `DateTimeField` | auto_now | |

### Relazioni

| Campo | Tipo | Target | related_name | On Delete |
|---|---|---|---|---|
| `user` | `ForeignKey` | User | `'comments'` | CASCADE |
| `video` | `ForeignKey` | Video | `'comments'` | CASCADE |

---

## Rating

### Campi

| Campo | Tipo | Vincoli | Note |
|---|---|---|---|
| `id` | `BigAutoField` | PK | |
| `value` | `IntegerField` | MinValue(1), MaxValue(5) | Voto 1-5 |
| `created_at` | `DateTimeField` | auto_now_add | |
| `updated_at` | `DateTimeField` | auto_now | |

### Relazioni

| Campo | Tipo | Target | related_name | On Delete |
|---|---|---|---|---|
| `user` | `ForeignKey` | User | `'ratings'` | CASCADE |
| `video` | `ForeignKey` | Video | `'ratings'` | CASCADE |

### Meta

```python
unique_together = ('user', 'video')  # Un utente, un voto per video
```

---

## Diagramma ER

```
┌──────────────┐
│     User     │
├──────────────┤        ┌──────────────┐
│ id      (PK) │        │   Contest    │
│ username (UQ)│        ├──────────────┤
│ email   (UQ) │        │ id      (PK) │
│ following M2M│──self  │ name         │
│ created_at   │        │ tag (choice) │
│ updated_at   │        │ start_date   │
└──┬───┬───┬───┘        │ end_date     │
   │   │   │            │ is_closed    │
   │   │   │   FK       │ winner ──FK──┤──┐
   │   │   └──────┐     └──────────────┘  │
   │   │          │                        │
   │   │   FK     │   FK                   │
   │   └────┐     │                        │
   │        │     │                        │
   │  FK    ▼     ▼                        │
   │  ┌──────────────┐                    │
   │  │    Video     │◄───────────────────┘
   │  ├──────────────┤
   │  │ id      (PK) │
   │  │ title        │
   │  │ file (MinIO) │
   │  │ views        │
   │  │ tag (choice) │
   │  │ duration     │
   │  │ uploader──FK─┤──► User
   │  │ contest──FK──┤──► Contest (null)
   │  └──┬───┬───────┘
   │     │   │
   ▼     │   │
┌────────┤   │
│Comment │   │
├────────┤   ▼
│ id(PK) │ ┌──────────┐
│ content│ │  Rating   │
│ ts_sec │ ├──────────┤
│ user FK│ │ id  (PK) │
│ videoFK│ │ value 1-5│
└────────┘ │ user  FK │
           │ video FK │
           ├──────────┤
           │UQ(user,  │
           │   video) │
           └──────────┘
```

### Relazioni Riassuntive

| Relazione | Tipo | On Delete | Cardinalità |
|---|---|---|---|
| User.following → User | M2M (self, asimmetrico) | — | N:M |
| Video.uploader → User | FK | CASCADE | N:1 |
| Video.contest → Contest | FK | SET_NULL | N:1 (opzionale) |
| Contest.winner → Video | FK | SET_NULL | 1:1 logico |
| Comment.user → User | FK | CASCADE | N:1 |
| Comment.video → Video | FK | CASCADE | N:1 |
| Rating.user → User | FK | CASCADE | N:1 |
| Rating.video → Video | FK | CASCADE | N:1 |

---

## Storico Migrazioni

| Migration | Operazione |
|---|---|
| `0001_initial` | Creazione 5 modelli + vincoli unique_together |
| `0002_alter_video_file` | `upload_to` cambiato da `'video/'` a `''` (delegato a MinIO) |

---

## Indici Database

### Automatici (Django)

| Tabella | Colonna | Tipo |
|---|---|---|
| cs_clips_user | username | UNIQUE |
| cs_clips_user | email | UNIQUE |
| cs_clips_video | uploader_id | INDEX |
| cs_clips_video | contest_id | INDEX |
| cs_clips_contest | winner_id | INDEX |
| cs_clips_comment | user_id | INDEX |
| cs_clips_comment | video_id | INDEX |
| cs_clips_rating | user_id | INDEX |
| cs_clips_rating | video_id | INDEX |

### Compositi

| Tabella | Colonne | Tipo |
|---|---|---|
| cs_clips_rating | (user_id, video_id) | UNIQUE TOGETHER |
| cs_clips_contest | (start_date, end_date, tag) | UNIQUE TOGETHER |

### Tabelle M2M

| Tabella | Collega |
|---|---|
| cs_clips_user_following | User ↔ User |
| cs_clips_user_groups | User ↔ auth.Group |
| cs_clips_user_user_permissions | User ↔ auth.Permission |

---

## Algoritmo di Spareggio

**File**: `cs_clips/utils/desempate.py`

| Metrica | Peso |
|---|---|
| Numero voti (ratings.count) | 50% |
| Visualizzazioni (views) | 30% |
| Numero commenti (comments.count) | 20% |

Normalizzazione min-max (percentile). Dipendenza: `numpy`.

---

## Modelli Mancanti (da PRD)

| Elemento | Tipo | Stato |
|---|---|---|
| `VideoLike` | Modello | Non implementato |
| `CommentLike` | Modello | Non implementato |
| `Notification` | Modello | Non implementato |
| `User.bio` | Campo | Non implementato |
| `Video.allow_download` | Campo | Non implementato |
| `Comment.is_disabled` | Campo | Non implementato |

---

## Registrazioni Admin

| Modello | Admin Class | Note |
|---|---|---|
| User | `UserAdmin` (extends BaseUserAdmin) | list_display: role, followers_count, following_count |
| Video | `VideoAdmin` | Filtri tag/data, autocomplete uploader/contest |
| Rating | `RatingAdmin` | Filtro value, autocomplete user/video |
| Comment | `CommentAdmin` | Search user/video/content |
| Contest | `ContestAdmin` | Filtri tag/is_closed, autocomplete winner |
