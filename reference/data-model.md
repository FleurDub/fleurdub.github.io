# Data Model Reference

This document describes the MEMORA data model implemented in Django.

All entities share a common set of base fields through abstract mixins. Each entity is described with its fields, types, constraints, validation rules, and computed properties.

---

## 1. Overview

### 1.1. Entity map

| Entity     | App         | Description                                     |
|------------|-------------|-------------------------------------------------|
| `Piece`    | `pieces`    | Central archival fashion object                 |
| `Designer` | `designers` | Creator of one or more pieces                   |
| `Maison`   | `designers` | Fashion house institution                       |
| `Category` | `pieces`    | Typological classification                      |
| `Era`      | `pieces`    | Historical period                               |

---

### 1.2. Relational graph

```
Maison
  └── Designer (many-to-one via ForeignKey)
        └── Piece (many-to-one via ForeignKey)
              ├── Category (many-to-one via ForeignKey)
              └── Era (many-to-one via ForeignKey)
```

Every `Piece` belongs to a `Designer`. A `Designer` may optionally belong to a `Maison`. A `Piece` may optionally be classified under a `Category` and an `Era`.

---

### 1.3. Base mixins

All entities inherit from three abstract mixins defined in `apps/common/models.py`.

These mixins do not create database tables. Their fields are copied directly into each entity's table.

| Mixin              | Fields added                  |
|--------------------|-------------------------------|
| `UUIDModel`        | `id`                          |
| `SlugModel`        | `slug`                        |
| `TimeStampedModel` | `created_at`, `updated_at`    |

---

## 2. Base Fields

### 2.1. `id`

**Source:** `UUIDModel`

| Property     | Value                       |
|--------------|-----------------------------|
| Type         | UUID (version 4)            |
| Primary key  | Yes                         |
| Auto-generated | Yes (on creation)         |
| Editable     | No                          |
| Indexed      | Yes (automatic, primary key)|

The `id` field uses UUID v4 (random) instead of an auto-incrementing integer. This prevents sequential enumeration of resources and supports distributed imports without ID conflicts.

Example value: `550e8400-e29b-41d4-a716-446655440000`

---

### 2.2. `slug`

**Source:** `SlugModel`

| Property       | Value                                        |
|----------------|----------------------------------------------|
| Type           | string (URL-safe, `[a-z0-9-]`)               |
| Max length     | 255                                          |
| Unique         | Yes                                          |
| Indexed        | Yes                                          |
| Auto-generated | Yes, from `name` or `title` on first save    |
| Editable       | Yes (but stable by design)                   |

The slug is generated automatically from the `name` (for Designer, Maison, Category, Era) or `title` (for Piece) on first save. It is never re-generated on subsequent saves, ensuring URL stability.

If a conflict occurs, a numeric suffix is appended:

| Input name         | Slug generated       |
|--------------------|----------------------|
| `Yohji Yamamoto`   | `yohji-yamamoto`     |
| `Yohji Yamamoto`   | `yohji-yamamoto--1`  |
| `Comme des Garçons`| `comme-des-garcons`  |

---

### 2.3. `created_at`

**Source:** `TimeStampedModel`

| Property       | Value                          |
|----------------|--------------------------------|
| Type           | datetime (timezone-aware, UTC) |
| Set on         | Creation only                  |
| Editable       | No                             |
| Indexed        | Yes                            |

---

### 2.4. `updated_at`

**Source:** `TimeStampedModel`

| Property       | Value                          |
|----------------|--------------------------------|
| Type           | datetime (timezone-aware, UTC) |
| Updated on     | Every `.save()` call           |
| Editable       | No                             |
| Indexed        | No                             |

Note: `updated_at` is **not** updated by `.update()` queryset calls. Only `.save()` triggers it.

---

## 3. Piece

**Model:** `apps/pieces/models.py` — `Piece`

Piece is the central entity of the domain model. It represents an individual archival fashion object and serves as the primary entry point for exploration.

---

### 3.1. Fields

#### 3.1.1. Identity and classification

| Field        | Type                       | Required | Default  | Description                                    |
|--------------|----------------------------|----------|----------|------------------------------------------------|
| `id`         | UUID                       | —        | auto     | Primary key (see §2.1)                         |
| `slug`       | string                     | —        | auto     | URL identifier, generated from `title` (§2.2)  |
| `title`      | string (max 255)           | Yes      | —        | Descriptive title of the piece                 |
| `designer`   | ForeignKey → Designer      | Yes      | —        | Creator of the piece                           |
| `category`   | ForeignKey → Category      | No       | null     | Typological classification                     |
| `era`        | ForeignKey → Era           | No       | null     | Historical period                              |
| `year`       | integer (1400–2100)        | Yes      | —        | Year of creation                               |
| `season`     | string (max 20)            | No       | `""`     | Collection season, e.g. `SS25`, `FW24`, `AW23` |

**`designer` deletion behavior:** `PROTECT` — a designer with associated pieces cannot be deleted. Pieces must be reassigned first.

**`category` deletion behavior:** `SET_NULL` — if a category is deleted, the piece's `category` becomes `null`.

**`era` deletion behavior:** `SET_NULL` — if an era is deleted, the piece's `era` becomes `null`.

**`season` format:** Must start with `SS`, `FW`, or `AW` (case-insensitive) if provided. Examples: `SS25`, `FW24`, `AW23`.

---

#### 3.1.2. Text content

| Field         | Type                 | Required | Default | Description                                 |
|---------------|----------------------|----------|---------|---------------------------------------------|
| `description` | text (max 500)       | Yes      | —       | Short factual description, used in lists    |
| `story`       | text (unlimited)     | No       | `""`    | Extended narrative, used in detail view     |

`description` is always present and suitable for cards, lists, and SEO meta tags. `story` is optional and shown only on the detail page.

---

#### 3.1.3. Media

| Field          | Type                    | Required     | Description                                              |
|----------------|-------------------------|--------------|----------------------------------------------------------|
| `image`        | file path               | Yes          | Original image, stored at `media/pieces/{YYYY}/{MM}/`    |
| `thumbnail`    | computed (no DB column) | —            | Auto-generated 400×400 WebP crop (quality 85%)           |
| `thumbnail_small` | computed (no DB column) | —         | Auto-generated 200×200 WebP crop (quality 80%)           |
| `image_credit` | string (max 255)        | Yes (if image) | Copyright attribution                                  |
| `image_alt`    | string (max 255)        | Yes (if image) | Accessible alternative text (WCAG 2.1)                 |

Thumbnails are generated on-demand by `django-imagekit` and cached automatically. They are not stored as database columns.

`image_credit` and `image_alt` are both required whenever an image is present. This is enforced at model validation level.

---

#### 3.1.4. Provenance

| Field          | Type                              | Required | Default    | Description                                  |
|----------------|-----------------------------------|----------|------------|----------------------------------------------|
| `source`       | enum (see below)                  | Yes      | `manual`   | Origin of the record                         |
| `source_id`    | string (max 100)                  | No       | `""`       | Identifier in the external source system     |
| `external_url` | URL                               | No       | `""`       | Link to the original source page             |

**`source` values:**

| Value    | Description         |
|----------|---------------------|
| `manual` | Manual data entry   |
| `met`    | The Metropolitan Museum of Art |
| `vogue`  | Vogue Runway        |
| `vam`    | Victoria & Albert Museum |

The combination `(source, source_id)` is subject to a uniqueness constraint when `source_id` is not empty (see §3.3).

---

#### 3.1.5. Materials

| Field            | Type             | Required | Default | Description                                   |
|------------------|------------------|----------|---------|-----------------------------------------------|
| `materials_data` | JSON array       | No       | `[]`    | List of material entries with slug and percentage |

**Format:**

```json
[
  { "slug": "wool", "percentage": 70 },
  { "slug": "silk", "percentage": 30 }
]
```

Each entry has a `slug` referencing a material in the PHYSIS system, and an optional `percentage`. This field is intentionally a `JSONField` rather than a `ManyToManyField` to maintain loose coupling with PHYSIS.

---

#### 3.1.6. Publication and engagement

| Field          | Type     | Required | Default | Description                                     |
|----------------|----------|----------|---------|-------------------------------------------------|
| `is_published` | boolean  | Yes      | `true`  | Whether the piece is publicly visible           |
| `featured`     | boolean  | Yes      | `false` | Whether the piece is highlighted on the homepage|
| `view_count`   | integer  | Yes      | `0`     | Cumulative view count, incremented via API      |

`view_count` is read-only via the standard API. It is incremented exclusively through the dedicated `POST /api/pieces/{id}/increment_view/` endpoint, using a thread-safe atomic update.

---

#### 3.1.7. Audit fields

| Field        | Type     | Description                      |
|--------------|----------|----------------------------------|
| `created_at` | datetime | Creation timestamp (see §2.3)    |
| `updated_at` | datetime | Last modification timestamp (see §2.4) |

---

### 3.2. Computed properties

These properties are calculated at runtime and are not stored in the database.

| Property          | Type        | Description                                           |
|-------------------|-------------|-------------------------------------------------------|
| `decade`          | integer     | Decade of the piece: `(year // 10) * 10`              |
| `display_title`   | string      | `"{title} - {designer.name} ({year})"`                |
| `primary_material`| string\|null| Slug of the material with the highest percentage       |

Examples:

| `year` | `decade` |
|--------|----------|
| 1985   | 1980     |
| 1999   | 1990     |
| 2023   | 2020     |

---

### 3.3. Constraints

| Constraint              | Rule                                                                               |
|-------------------------|------------------------------------------------------------------------------------|
| `unique_source_piece`   | `(source, source_id)` must be unique when `source_id` is not null and not empty    |

This prevents duplicate imports from external sources (Met Museum, Vogue, etc.).

---

### 3.4. Validation rules

Validation is enforced at model level via `clean()`, called automatically on every `save()`.

| Rule                                  | Error field     | Condition                                    |
|---------------------------------------|-----------------|----------------------------------------------|
| `image_alt` is required when image present | `image_alt`  | `image` is set and `image_alt` is empty      |
| `image_credit` is required when image present | `image_credit` | `image` is set and `image_credit` is empty |
| `season` must have a valid prefix     | `season`        | `season` is set but does not start with `SS`, `FW`, or `AW` |
| `year` must be in range               | `year`          | `year < 1400` or `year > 2100`               |

---

### 3.5. Default ordering

```
['-year', 'title']
```

Pieces are ordered by year descending, then title ascending.

---

### 3.6. Indexes

| Index fields                  | Purpose                                           |
|-------------------------------|---------------------------------------------------|
| `[-year, title]`              | Supports the default ordering                     |
| `[is_published, -featured]`   | Supports published + featured filtering           |
| `[designer, -year]`           | Supports pieces-by-designer queries               |
| `[category, -year]`           | Supports pieces-by-category queries               |
| `[source]`                    | Supports filtering by provenance source           |
| `[is_published]`              | Supports published-only filtering                 |
| `[year]`                      | Supports year range queries                       |
| `[title]`                     | Supports search and alphabetical sort             |

---

### 3.7. Example

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "slug": "black-asymmetric-coat",
  "title": "Black Asymmetric Coat",
  "designer": {
    "id": "...",
    "name": "Yohji Yamamoto",
    "slug": "yohji-yamamoto",
    "maison": {
      "id": "...",
      "name": "Yohji Yamamoto Inc.",
      "slug": "yohji-yamamoto-inc"
    }
  },
  "category": {
    "id": "...",
    "name": "Jacket",
    "slug": "jacket"
  },
  "era": {
    "id": "...",
    "name": "Années 80",
    "slug": "annees-80",
    "start_year": 1980,
    "end_year": 1989
  },
  "year": 1985,
  "decade": 1980,
  "season": "FW85",
  "description": "Iconic asymmetric wool coat from the Fall/Winter 1985 collection.",
  "story": "This coat became one of Yamamoto's most referenced pieces...",
  "image_url": "https://api.memora.com/media/pieces/2024/01/black-asymmetric-coat.jpg",
  "thumbnail_url": "https://api.memora.com/media/CACHE/pieces/black-asymmetric-coat.webp",
  "image_credit": "Photo © Jane Doe",
  "image_alt": "Black asymmetric wool coat with dramatic lapel, front view",
  "source": "manual",
  "source_id": "",
  "external_url": "",
  "materials": [
    { "slug": "wool", "percentage": 100 }
  ],
  "featured": true,
  "is_published": true,
  "view_count": 1247,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:22:00Z"
}
```

---

## 4. Designer

**Model:** `apps/designers/models.py` — `Designer`

Designer represents a fashion creator (a physical person). Designers may be independent or affiliated with a Maison.

---

### 4.1. Fields

| Field         | Type                     | Required | Default | Description                                          |
|---------------|--------------------------|----------|---------|------------------------------------------------------|
| `id`          | UUID                     | —        | auto    | Primary key (see §2.1)                               |
| `slug`        | string                   | —        | auto    | URL identifier, generated from `name` (see §2.2)     |
| `name`        | string (max 200)         | Yes      | —       | Full name of the designer                            |
| `maison`      | ForeignKey → Maison      | No       | null    | Fashion house affiliation (optional for independents)|
| `birth_year`  | integer (1400–2100)      | No       | null    | Year of birth                                        |
| `death_year`  | integer (1400–2100)      | No       | null    | Year of death (null if still living)                 |
| `nationality` | string (max 100)         | No       | `""`   | Nationality                                          |
| `bio`         | text                     | No       | `""`   | Short biography                                      |
| `image`       | file path                | No       | —       | Photo, stored at `media/designers/`                  |
| `website`     | URL                      | No       | `""`   | Official website                                     |
| `instagram`   | string (max 100)         | No       | `""`   | Instagram username (without `@`)                     |
| `created_at`  | datetime                 | —        | auto    | See §2.3                                             |
| `updated_at`  | datetime                 | —        | auto    | See §2.4                                             |

**`maison` deletion behavior:** `SET_NULL` — if a maison is deleted, the designer's `maison` becomes `null`. The designer record is preserved.

---

### 4.2. Computed properties

| Property       | Type         | Description                                                     |
|----------------|--------------|-----------------------------------------------------------------|
| `pieces_count` | integer      | Number of published pieces by this designer                     |
| `is_deceased`  | boolean      | `true` if `death_year` is set                                   |
| `age`          | integer\|null | Age at death (if deceased) or current age (if birth year known) |

---

### 4.3. Constraints

| Constraint              | Rule                                                                       |
|-------------------------|----------------------------------------------------------------------------|
| `unique_designer_maison`| `(name, maison)` must be unique when `maison` is not null                  |

A designer name may appear multiple times in the database, as long as each occurrence is linked to a different maison. Independent designers (with `maison = null`) have no uniqueness constraint on name alone.

---

### 4.4. Default ordering

```
['name']
```

Designers are ordered alphabetically by name.

---

### 4.5. Indexes

| Index fields    | Purpose                            |
|-----------------|------------------------------------|
| `[name]`        | Search and alphabetical sort       |
| `[nationality]` | Filtering by nationality           |

---

### 4.6. Example

```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "slug": "rei-kawakubo",
  "name": "Rei Kawakubo",
  "maison": {
    "id": "...",
    "name": "Comme des Garçons",
    "slug": "comme-des-garcons"
  },
  "birth_year": 1942,
  "death_year": null,
  "nationality": "Japanese",
  "bio": "Rei Kawakubo is a Japanese fashion designer and founder of Comme des Garçons.",
  "image": "https://api.memora.com/media/designers/rei-kawakubo.jpg",
  "website": "https://www.comme-des-garcons.com",
  "instagram": "commedesgarcons",
  "pieces_count": 84,
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## 5. Maison

**Model:** `apps/designers/models.py` — `Maison`

Maison represents a fashion house as a commercial and institutional entity, distinct from any individual designer.

---

### 5.1. Fields

| Field          | Type                | Required | Default | Description                                       |
|----------------|---------------------|----------|---------|---------------------------------------------------|
| `id`           | UUID                | —        | auto    | Primary key (see §2.1)                            |
| `slug`         | string              | —        | auto    | URL identifier, generated from `name` (see §2.2)  |
| `name`         | string (max 200)    | Yes      | —       | Official name of the fashion house                |
| `founded_year` | integer (1400–2100) | No       | null    | Year of establishment                             |
| `country`      | string (max 100)    | Yes      | —       | Country of origin                                 |
| `description`  | text                | No       | `""`   | Description of the maison                        |
| `website`      | URL                 | No       | `""`   | Official website                                  |
| `logo`         | file path           | No       | —       | Logo image, stored at `media/maisons/`            |
| `is_active`    | boolean             | Yes      | `true`  | Whether the maison is currently active            |
| `created_at`   | datetime            | —        | auto    | See §2.3                                          |
| `updated_at`   | datetime            | —        | auto    | See §2.4                                          |

`name` is unique — no two maisons may share the same name.

`is_active` is `false` for maisons that have closed or been dissolved. Examples: Maison Martin Margiela (closed 2009), Poiret (closed 1920s).

---

### 5.2. Computed properties

| Property          | Type    | Description                                                         |
|-------------------|---------|---------------------------------------------------------------------|
| `designers_count` | integer | Number of designers affiliated with this maison                     |
| `pieces_count`    | integer | Number of published pieces by all designers of this maison          |

---

### 5.3. Constraints

`name` has a `unique=True` constraint. No two maisons may have the same name.

---

### 5.4. Default ordering

```
['name']
```

Maisons are ordered alphabetically by name.

---

### 5.5. Indexes

| Index fields           | Purpose                                  |
|------------------------|------------------------------------------|
| `[name]`               | Search and alphabetical sort             |
| `[is_active, country]` | Filtering by active status and country   |

---

### 5.6. Example

```json
{
  "id": "a3bb189e-8bf9-3888-9912-ace4e6543002",
  "slug": "comme-des-garcons",
  "name": "Comme des Garçons",
  "founded_year": 1969,
  "country": "Japan",
  "description": "Avant-garde Japanese fashion house founded by Rei Kawakubo.",
  "website": "https://www.comme-des-garcons.com",
  "logo": "https://api.memora.com/media/maisons/comme-des-garcons-logo.jpg",
  "is_active": true,
  "designers_count": 2,
  "pieces_count": 112,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## 6. Category

**Model:** `apps/pieces/models.py` — `Category`

Category represents a typological classification for pieces. It enables structural exploration across garment types.

---

### 6.1. Fields

| Field         | Type                 | Required | Default | Description                                       |
|---------------|----------------------|----------|---------|---------------------------------------------------|
| `id`          | UUID                 | —        | auto    | Primary key (see §2.1)                            |
| `slug`        | string               | —        | auto    | URL identifier, generated from `name` (see §2.2)  |
| `name`        | string (max 100)     | Yes      | —       | Category name (e.g. `Dress`, `Jacket`, `Shoes`)   |
| `description` | text                 | No       | `""`   | Description of the category                       |
| `order`       | positive integer     | Yes      | `0`     | Display order (lower value = displayed first)     |
| `created_at`  | datetime             | —        | auto    | See §2.3                                          |
| `updated_at`  | datetime             | —        | auto    | See §2.4                                          |

`name` is unique — no two categories may share the same name.

`order` controls the display sequence in navigation menus and filter lists. Categories with the same `order` value are sorted alphabetically by `name`.

---

### 6.2. Computed properties

| Property       | Type    | Description                              |
|----------------|---------|------------------------------------------|
| `pieces_count` | integer | Number of published pieces in this category |

---

### 6.3. Default ordering

```
['order', 'name']
```

Categories are ordered by `order` ascending, then by `name` ascending.

---

### 6.4. Indexes

| Index fields     | Purpose                                          |
|------------------|--------------------------------------------------|
| `[order, name]`  | Supports the default ordering                    |
| `[name]`         | Search and unique constraint enforcement         |

---

### 6.5. Example

```json
{
  "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "slug": "dress",
  "name": "Dress",
  "description": "One-piece garments covering the torso and extending below the waist.",
  "order": 1,
  "pieces_count": 234,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## 7. Era

**Model:** `apps/pieces/models.py` — `Era`

Era represents a named historical period and provides chronological context for pieces. Eras are defined by a name and a year range, allowing pieces to be grouped by cultural and historical context rather than strict calendar years.

---

### 7.1. Fields

| Field         | Type                | Required | Default | Description                                       |
|---------------|---------------------|----------|---------|---------------------------------------------------|
| `id`          | UUID                | —        | auto    | Primary key (see §2.1)                            |
| `slug`        | string              | —        | auto    | URL identifier, generated from `name` (see §2.2)  |
| `name`        | string (max 100)    | Yes      | —       | Name of the era (e.g. `Années 80`, `Belle Époque`)|
| `start_year`  | integer (1400–2100) | Yes      | —       | First year of the era (inclusive)                 |
| `end_year`    | integer (1400–2100) | No       | null    | Last year of the era (null if era is ongoing)     |
| `description` | text                | Yes      | —       | Historical and cultural context of the era        |
| `created_at`  | datetime            | —        | auto    | See §2.3                                          |
| `updated_at`  | datetime            | —        | auto    | See §2.4                                          |

`name` is unique — no two eras may share the same name.

`end_year` is nullable to represent ongoing eras (e.g. `Années 2020`).

---

### 7.2. Validation rules

| Rule                                        | Condition                                      |
|---------------------------------------------|------------------------------------------------|
| `end_year` must be after `start_year`       | `end_year` is set and `end_year <= start_year` |

---

### 7.3. Default ordering

```
['start_year']
```

Eras are ordered chronologically by `start_year` ascending.

---

### 7.4. Indexes

| Index fields               | Purpose                                                    |
|----------------------------|------------------------------------------------------------|
| `[start_year, end_year]`   | Supports range queries (e.g. which era contains year X)    |

---

### 7.5. Examples

| name          | start_year | end_year | slug          |
|---------------|------------|----------|---------------|
| Belle Époque  | 1890       | 1914     | belle-epoque  |
| Années 20     | 1920       | 1929     | annees-20     |
| Années 80     | 1980       | 1989     | annees-80     |
| Années 2020   | 2020       | null     | annees-2020   |

```json
{
  "id": "b7e23ec2-9204-4b8a-a25b-7b54a6d2c5f1",
  "slug": "annees-80",
  "name": "Années 80",
  "start_year": 1980,
  "end_year": 1989,
  "description": "The 1980s were defined by power dressing, Japanese avant-garde, and the rise of designer branding.",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

## 8. Relational Summary

### 8.1. Foreign keys

| Relationship             | From     | To         | Nullable | On delete  |
|--------------------------|----------|------------|----------|------------|
| `Piece.designer`         | Piece    | Designer   | No       | PROTECT    |
| `Piece.category`         | Piece    | Category   | Yes      | SET_NULL   |
| `Piece.era`              | Piece    | Era        | Yes      | SET_NULL   |
| `Designer.maison`        | Designer | Maison     | Yes      | SET_NULL   |

---

### 8.2. Reverse relations

| Accessor                        | Returns                                |
|---------------------------------|----------------------------------------|
| `designer.pieces.all()`         | All pieces by a given designer         |
| `category.pieces.all()`         | All pieces in a given category         |
| `era.pieces.all()`              | All pieces belonging to a given era    |
| `maison.designers.all()`        | All designers affiliated with a maison |

---

### 8.3. Traversal depth

The domain model supports navigation up to three levels deep:

```
Piece → Designer → Maison
Piece → Category
Piece → Era
```

From a single piece, a client can reach its designer, the designer's maison, the piece's category, and the piece's era — and from any of those, reach all other related pieces.
