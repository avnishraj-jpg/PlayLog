# PlayLog - Database Schema

## 1. Overview

PlayLog uses **SQLite** as its relational database.

The database stores two main categories of information:

1. **Game data** - information retrieved from the IGDB API.
2. **User data** - the user's personal relationship with each game, including status, rating, reviews, favourites, and play history.

The database is designed for a **single-user application** and should remain simple, normalized, and easy to extend.

---

## 2. Design Principles

- SQLite is used for the initial version.
- IGDB is the primary external source for game metadata.
- IGDB data and user-specific data are kept separate.
- Many-to-many relationships are represented using junction tables.
- Repeated data should not be unnecessarily duplicated.
- Analytics should be calculated from existing data rather than stored separately.
- Recommendation results are calculated dynamically rather than permanently stored.
- The schema should support future features without unnecessary complexity.

---

# 3. Entity Relationship Overview

```text
                              ┌──────────────┐
                              │    games     │
                              └──────┬───────┘
                                     │
             ┌───────────────────────┼────────────────────────┐
             │                       │                        │
             ▼                       ▼                        ▼
      ┌─────────────┐       ┌──────────────┐        ┌────────────────┐
      │ game_genres │       │game_platforms│        │game_companies │
      └──────┬──────┘       └──────┬───────┘        └───────┬────────┘
             │                     │                        │
             ▼                     ▼                        ▼
        ┌─────────┐           ┌───────────┐           ┌───────────┐
        │ genres  │           │ platforms │           │ companies │
        └─────────┘           └───────────┘           └───────────┘


                              ┌──────────────┐
                              │    games     │
                              └──────┬───────┘
                                     │
                  ┌──────────────────┼──────────────────┐
                  │                  │                  │
                  ▼                  ▼                  ▼
           ┌────────────┐    ┌─────────────┐    ┌───────────────┐
           │ user_games │    │ game_images │    │ game_sessions │
           └──────┬─────┘    └─────────────┘    └───────────────┘
                  │
                  ▼
              ┌────────┐
              │ lists  │
              └───┬────┘
                  │
                  ▼
             ┌──────────┐
             │list_games│
             └──────────┘
```

---

# 4. Tables

## 4.1 `games`

Stores canonical game information obtained primarily from IGDB.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal PlayLog identifier |
| `igdb_id` | INTEGER | NOT NULL, UNIQUE | IGDB game identifier |
| `name` | TEXT | NOT NULL | Game name |
| `slug` | TEXT | | URL-friendly game identifier |
| `summary` | TEXT | | Short game description |
| `storyline` | TEXT | | Additional storyline information |
| `first_release_date` | INTEGER | | Unix timestamp of first release |
| `cover_image_id` | TEXT | | IGDB image identifier for the cover |
| `igdb_rating` | REAL | | Rating provided by IGDB |
| `igdb_rating_count` | INTEGER | | Number of IGDB ratings |
| `critic_rating` | REAL | | Aggregated critic rating, when available |
| `critic_rating_count` | INTEGER | | Number of critic ratings |
| `created_at` | TEXT | NOT NULL | Record creation timestamp |
| `updated_at` | TEXT | NOT NULL | Last update timestamp |

### Notes

`igdb_id` is used to prevent the same game from being imported multiple times.

User-specific ratings must **not** be stored in this table.

---

## 4.2 `genres`

Stores game genres retrieved from IGDB.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal identifier |
| `igdb_id` | INTEGER | NOT NULL, UNIQUE | IGDB genre identifier |
| `name` | TEXT | NOT NULL | Genre name |
| `slug` | TEXT | | URL-friendly identifier |

Examples:

- Action
- Adventure
- RPG
- Strategy
- Simulation
- Sports
- Racing

---

## 4.3 `game_genres`

Junction table connecting games and genres.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `game_id` | INTEGER | NOT NULL, FK | References `games.id` |
| `genre_id` | INTEGER | NOT NULL, FK | References `genres.id` |

### Primary Key

```text
(game_id, genre_id)
```

### Relationship

```text
games ↔ genres
```

A game can have multiple genres, and a genre can contain multiple games.

---

## 4.4 `platforms`

Stores gaming platforms retrieved from IGDB.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal identifier |
| `igdb_id` | INTEGER | NOT NULL, UNIQUE | IGDB platform identifier |
| `name` | TEXT | NOT NULL | Platform name |
| `slug` | TEXT | | URL-friendly identifier |

Examples:

- PC
- PlayStation 5
- Xbox Series X|S
- Nintendo Switch
- Android
- iOS

---

## 4.5 `game_platforms`

Junction table connecting games and platforms.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `game_id` | INTEGER | NOT NULL, FK | References `games.id` |
| `platform_id` | INTEGER | NOT NULL, FK | References `platforms.id` |

### Primary Key

```text
(game_id, platform_id)
```

### Relationship

```text
games ↔ platforms
```

---

## 4.6 `companies`

Stores companies involved in game development or publishing.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal identifier |
| `igdb_id` | INTEGER | NOT NULL, UNIQUE | IGDB company identifier |
| `name` | TEXT | NOT NULL | Company name |
| `slug` | TEXT | | URL-friendly identifier |

A single company may be both a developer and publisher.

---

## 4.7 `game_companies`

Junction table connecting games and companies.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `game_id` | INTEGER | NOT NULL, FK | References `games.id` |
| `company_id` | INTEGER | NOT NULL, FK | References `companies.id` |
| `role` | TEXT | NOT NULL | Company's role for the game |

### Allowed roles

```text
developer
publisher
```

### Primary Key

```text
(game_id, company_id, role)
```

This allows the same company to appear as both developer and publisher.

---

## 4.8 `game_images`

Stores image references associated with games.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal identifier |
| `game_id` | INTEGER | NOT NULL, FK | References `games.id` |
| `image_id` | TEXT | NOT NULL | IGDB image identifier |
| `image_type` | TEXT | NOT NULL | Type of image |
| `display_order` | INTEGER | | Ordering for display |

### Allowed image types

```text
cover
screenshot
artwork
```

The application will construct image URLs from the stored IGDB image identifier when needed.

---

## 4.9 `user_games`

Stores the user's personal relationship with a game.

This table is separate from `games` because game metadata belongs to IGDB, while this information belongs to the PlayLog user.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal identifier |
| `game_id` | INTEGER | NOT NULL, UNIQUE, FK | References `games.id` |
| `status` | TEXT | NOT NULL | Current user status |
| `user_rating` | REAL | | Personal rating from 0.0 to 10.0 |
| `is_favourite` | INTEGER | NOT NULL DEFAULT 0 | Whether the game is a favourite |
| `review` | TEXT | | Personal review or notes |
| `playtime_minutes` | INTEGER | NOT NULL DEFAULT 0 | Total manually recorded playtime |
| `date_added` | TEXT | NOT NULL | Date game was added |
| `date_started` | TEXT | | Date game was started |
| `date_completed` | TEXT | | Date game was completed |
| `date_dropped` | TEXT | | Date game was dropped |
| `last_played` | TEXT | | Most recent play date |
| `created_at` | TEXT | NOT NULL | Record creation timestamp |
| `updated_at` | TEXT | NOT NULL | Last update timestamp |

### Allowed statuses

```text
wishlist
backlog
playing
completed
dropped
```

### Rating

Ratings use a scale of:

```text
0.0 – 10.0
```

with half-point increments supported.

Examples:

```text
7.0
8.5
9.5
10.0
```

### Favourite

SQLite does not have a native BOOLEAN type.

Therefore:

```text
0 = false
1 = true
```

will be used for `is_favourite`.

---

## 4.10 `game_sessions`

Stores individual gaming sessions.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal identifier |
| `game_id` | INTEGER | NOT NULL, FK | References `games.id` |
| `started_at` | TEXT | NOT NULL | Session start timestamp |
| `ended_at` | TEXT | | Session end timestamp |
| `duration_minutes` | INTEGER | | Session duration |
| `notes` | TEXT | | Optional session notes |

### Purpose

This allows PlayLog to eventually provide analytics such as:

- Playtime per game
- Playtime per week/month/year
- Most played games
- Gaming activity over time

`playtime_minutes` in `user_games` represents the aggregate total, while `game_sessions` stores the underlying history.

---

## 4.11 `lists`

Stores custom user-created game collections.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal identifier |
| `name` | TEXT | NOT NULL | List name |
| `description` | TEXT | | List description |
| `created_at` | TEXT | NOT NULL | Creation timestamp |
| `updated_at` | TEXT | NOT NULL | Last update timestamp |

Examples:

```text
My Favourite RPGs
Games I Want to Play
Best Indie Games
Games to Play With Friends
```

---

## 4.12 `list_games`

Junction table connecting custom lists and games.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `list_id` | INTEGER | NOT NULL, FK | References `lists.id` |
| `game_id` | INTEGER | NOT NULL, FK | References `games.id` |
| `position` | INTEGER | | Ordering of games within a list |

### Primary Key

```text
(list_id, game_id)
```

---

# 5. Tables Not Stored

## Analytics

Analytics will **not** have a dedicated database table.

Metrics will be calculated from the existing data.

Examples:

- Total games
- Games completed
- Average personal rating
- Favourite genres
- Games by platform
- Rating distribution
- Completion rate
- Total playtime
- Games played over time

This prevents duplication and keeps analytics automatically up to date.

---

## Recommendations

Recommendation results will **not** initially be stored in the database.

Recommendations will be calculated dynamically using the recommendation engine.

Initial pipeline:

```text
User's game library
        ↓
Game metadata
        ↓
Feature extraction
        ↓
TF-IDF representation
        ↓
Cosine similarity
        ↓
Recommended games
```

Recommendation caching may be introduced later if performance requires it.

---

# 6. Relationships

### Game → User

```text
games 1 ─────── 0..1 user_games
```

A game may or may not be in the user's PlayLog library.

---

### Game ↔ Genre

```text
games 1 ─────── * game_genres * ─────── 1 genres
```

Many-to-many relationship.

---

### Game ↔ Platform

```text
games 1 ─────── * game_platforms * ─────── 1 platforms
```

Many-to-many relationship.

---

### Game ↔ Company

```text
games 1 ─────── * game_companies * ─────── 1 companies
```

Many-to-many relationship.

---

### Game → Images

```text
games 1 ─────── * game_images
```

A game can have multiple images.

---

### Game → Sessions

```text
games 1 ─────── * game_sessions
```

A game can have multiple play sessions.

---

### List ↔ Game

```text
lists 1 ─────── * list_games * ─────── 1 games
```

Many-to-many relationship.

---

# 7. Foreign Key Rules

SQLite foreign key enforcement must be enabled for every database connection:

```sql
PRAGMA foreign_keys = ON;
```

Foreign keys should use cascading deletes where appropriate.

For example, deleting a game should remove its associated:

- genre relationships
- platform relationships
- company relationships
- images
- play sessions
- user library entry
- list relationships

This prevents orphaned records.

---

# 8. Indexes

The following indexes should be created to improve query performance.

### `games`

```text
UNIQUE INDEX on igdb_id
INDEX on name
INDEX on first_release_date
```

### `genres`

```text
UNIQUE INDEX on igdb_id
```

### `platforms`

```text
UNIQUE INDEX on igdb_id
```

### `companies`

```text
UNIQUE INDEX on igdb_id
```

### `user_games`

```text
UNIQUE INDEX on game_id
INDEX on status
INDEX on user_rating
INDEX on is_favourite
```

### `game_sessions`

```text
INDEX on game_id
INDEX on started_at
```

These indexes support common PlayLog operations such as searching games, filtering the library, and generating analytics.

---

# 9. Data Ownership

The database follows this ownership model:

```text
IGDB
 │
 ├── Game metadata
 ├── Genres
 ├── Platforms
 ├── Companies
 └── Images
       │
       ▼
   PlayLog Database
       │
       └── User information
             ├── Status
             ├── Rating
             ├── Favourite
             ├── Review
             ├── Playtime
             ├── Dates
             └── Sessions
```

IGDB data may be refreshed when necessary.

User data must never be overwritten by an IGDB refresh.

---

# 10. Future Extensions

The following features are intentionally not part of the initial database implementation but can be added later:

- Keywords
- Themes
- Game modes
- Player perspectives
- Franchises
- Collections
- DLC and expansions
- Game series
- Trailers/videos
- External websites
- Achievements
- Multiple users
- Public reviews
- Social features
- Friends/following
- Comments and likes

The current schema is designed so that these can be introduced without fundamentally redesigning the existing core.

---

# 11. Version

**Schema Version:** 1.0  
**Database:** SQLite  
**Application:** PlayLog  
**Status:** Initial design