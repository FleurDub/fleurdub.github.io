# API Reference

This document describes the MEMORA REST API exposed by the Django backend.

The API provides structured access to the relational domain model and enables exploration of archival data.

## 1. Overview

### 1.1. Base URL

| Environment | URL                       |
|-------------|---------------------------|
| Development | http://localhost:8000/api/|
| Production  | TBD                       |

---

### 1.2. Response format

All responses are JSON.

Relationships are represented as nested objects.

Example:
```json
{
  "id": "uuid",
  "title": "Dress",
  "designer": {
    "id": "uuid",
    "name": "Pierre Balmain"
  },
  "era": {
    "id": "uuid",
    "name": "1950s"
  },
  "category": {
    "id": "uuid",
    "name": "Dress"
  }
}
```
---

### 1.3. Authentication

The API enforces a read-public, write-restricted access model.

- Read operations are public and require no authentification.
- Write operations are restricted to admin users.

---

### 1.4. Pagination

List endpoints return paginated responses using page number pagination.

**Default page size:** 20 items per page.

#### 1.4.1. Query parameters

| Parameter   | Type    | Default | Description                     |
|-------------|---------|---------|---------------------------------|
| `page`      | integer | 1       | Page number to retrieve         |

#### 1.4.2. Response envelope

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/pieces/?page=3",
  "previous": "http://localhost:8000/api/pieces/?page=1",
  "results": [ ... ]
}
```

| Field      | Type            | Description                              |
|------------|-----------------|------------------------------------------|
| `count`    | integer         | Total number of items across all pages   |
| `next`     | string \| null  | URL of the next page, or null            |
| `previous` | string \| null  | URL of the previous page, or null        |
| `results`  | array           | Items for the current page               |

#### 1.4.3. Example

```
GET /api/pieces/?page=2
```
---

## 2. Resources

### 2.1. Pieces

Represents a fashion archival object.

#### 2.1.1. List pieces
GET /api/pieces/

Retrieve list of pieces

Parameters:
| param              |  type        | required | description                                                                                |
|--------------------|--------------|----------|--------------------------------------------------------------------------------------------|
|categories          | string (slug)| No       | Filter by categories slugs. Ex:`?categories=dress&categories=jacket`                       |
|category            | string (slug)| No       | Filter by category slug. Ex:`dress`                                                        |
|category_id         | string (uuid)| No       | Filter by category uuid.                                                                   |
|created_after       | date time    | No       | Filter by after the date and time of creation. Format: YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS   |
|created_before      | date time    | No       | Filter by before date and time of creation. Format: YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS      |
|decade              | integer      | No       | Filter by decade. Ex:`1980`                                                                |
|description_contains| string       | No       | Search in the description text                                                             |
|designer            | string (slug)| No       | Filter by designer slug. Ex:`pierre-balmain`                                               |
|designer_id         | string (uuid)| No       | Filter by designer uuid.                                                                   |
|designer_name       | string       | No       | Filter by designer's name (partial OK). Ex:`balmain`                                       |
|era                 | string (slug)| No       | Filter by era slug. Ex.`annees-80`                                                         |
|era_id              | string (uuid)| No       | Filter by era uuid                                                                         |
|featured            | boolean      | No       | Filter by featured. Ex.`featured=true`                                                     |
|has_materials       | boolean      | No       | Filter by the piece having materials or not. Ex:`has_materials=true`                       |
|is_complete         | boolean      | No       | Filter by completeness. Ex:`is_complete=True`                                              |
|is_published        | boolean      | No       | Filter by publication status. Ex:`is_published=true`                                       |
|materials_slug      | string (slug)| No       | Filter by material slug. Ex:`silk`                                                         |
|ordering            | string       | No       | Which field to use when ordering the results                                               | 
|page                | integer      | No       | Filter by a page number within the paginated result set.                                   |
|season              | string       | No       | Filter by a season collection. Ex: `SS25`                                                  |
|season_contains     | string       | No       | Partial search in season. Ex: `FW`                                                         |
|source              | string       | No       | Piece source. Ex: `?source=met`. Available values: manual, met, vam, vogue                 |
|sources             | string       | No       | Multiple sources. Ex: `?source=met&sources=vogue`. Available value: manual, met, vam, vogue|
|title_contains      | string       | No       | Search the title. Ex: `black`                                                              |
|title_startswith    | string       | No       | Title starts with. Ex: `Black`                                                             |
|updated_after       | string       | No       | After modification date                                                                    |
|updated_before      | string       | No       | Before modification date                                                                   |
|view_count_max      | integer      | No       | Filter on maximum view count                                                               |
|view_count_min      | integer      | No       | Filter on minimum view count                                                               |
|year                | integer      | No       | Filter by exact year                                                                       |
|year_max            | integer      | No       | Filter by =< year.                                                                         |
|year_min            | integer      | No       | Filter by => year.                                                                         |

Response body:
| field                            | type            | nullable | description                                     |
|----------------------------------|-----------------|----------|-------------------------------------------------|
| `count`                          | integer         | No       | Total number of pieces across all pages         |
| `next`                           | string (url)    | Yes      | URL of the next page, or null                   |
| `previous`                       | string (url)    | Yes      | URL of the previous page, or null               |
| `results`                        | array           | No       | List of pieces for the current page             |
| `results[].id`                   | string (uuid)   | No       | Unique identifier of the piece                  |
| `results[].title`                | string          | No       | Title of the piece                              |
| `results[].slug`                 | string          | No       | URL-friendly identifier of the piece            |
| `results[].designer`             | object          | No       | Designer associated with the piece              |
| `results[].designer.id`          | string (uuid)   | No       | Unique identifier of the designer               |
| `results[].designer.name`        | string          | No       | Full name of the designer                       |
| `results[].designer.slug`        | string          | No       | URL-friendly identifier of the designer         |
| `results[].designer.maison`      | object          | No       | Fashion house associated with the designer      |
| `results[].designer.maison.id`   | string (uuid)   | No       | Unique identifier of the maison                 |
| `results[].designer.maison.name` | string          | No       | Name of the maison                              |
| `results[].designer.maison.slug` | string          | No       | URL-friendly identifier of the maison           |
| `results[].category`             | object          | Yes      | Typological category of the piece               |
| `results[].category.id`          | string (uuid)   | No       | Unique identifier of the category               |
| `results[].category.name`        | string          | No       | Name of the category                            |
| `results[].category.slug`        | string          | No       | URL-friendly identifier of the category         |
| `results[].year`                 | integer         | No       | Year of creation of the piece                   |
| `results[].season`               | string          | No       | Season collection. Ex: `SS25`                   |
| `results[].image_url`            | string          | No       | URL of the main image                           |
| `results[].thumbnail_url`        | string          | No       | URL of the thumbnail image                      |
| `results[].image_alt`            | string          | No       | Alt text for the image                          |
| `results[].featured`             | boolean         | No       | Whether the piece is featured                   |
| `results[].view_count`           | integer         | No       | Number of times the piece has been viewed       |



Response example:
```json
{
  "count": 123,
  "next": "http://api.example.org/accounts/?page=4",
  "previous": "http://api.example.org/accounts/?page=2",
  "results": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "title": "string",
      "slug": "robe-rouge-balmain",
      "designer": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "string",
        "slug": "pierre-balmain",
        "maison": {
          "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
          "name": "string",
          "slug": "balmain"
        }
      },
      "category": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "string",
        "slug": "robe"
      },
      "year": 2100,
      "season": "string",
      "image_url": "string",
      "thumbnail_url": "string",
      "image_alt": "string",
      "featured": true,
      "view_count": 0
    }
  ]
}
```
Errors handling:
| Status | Condition                                                                                                         |
|--------|-------------------------------------------------------------------------------------------------------------------|
| 400    | `page`, `decade`, `year`, `year_min`, `year_max`, `view_count_min`, `view_count_max` non entier                   |
| 400    | `created_after` ou `created_before` avec un format de date invalide (attendu : YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS) |
| 400    | `featured`, `has_materials`, `is_complete`, `is_published` avec une valeur non booléenne                          |
| 400    | `source` ou `sources` avec une valeur hors des valeurs autorisées (`manual`, `met`, `vam`, `vogue`)               |
| 500    | Erreur interne du serveur (ex. base de données ou cache Redis indisponible)                                       |

> Note : une liste vide (`"results": []`) est retournée si aucune pièce ne correspond aux filtres. Ce n'est pas une erreur (HTTP 200).

#### 2.1.2. Retrieve a piece
GET /api/pieces/{id}/

Retrieve the full details of a single piece.

Path parameters:
| param | type          | required | description              |
|-------|---------------|----------|--------------------------|
| `id`  | string (uuid) | Yes      | Unique identifier of the piece |

Response body:
| field                    | type            | nullable | description                                           |
|--------------------------|-----------------|----------|-------------------------------------------------------|
| `id`                     | string (uuid)   | No       | Unique identifier of the piece                        |
| `title`                  | string          | No       | Title of the piece                                    |
| `slug`                   | string          | No       | URL-friendly identifier of the piece                  |
| `designer`               | object          | No       | Designer associated with the piece                    |
| `designer.id`            | string (uuid)   | No       | Unique identifier of the designer                     |
| `designer.name`          | string          | No       | Full name of the designer                             |
| `designer.slug`          | string          | No       | URL-friendly identifier of the designer               |
| `designer.maison`        | object          | Yes      | Fashion house associated with the designer            |
| `designer.maison.id`     | string (uuid)   | No       | Unique identifier of the maison                       |
| `designer.maison.name`   | string          | No       | Name of the maison                                    |
| `designer.maison.slug`   | string          | No       | URL-friendly identifier of the maison                 |
| `category`               | object          | Yes      | Typological category of the piece                     |
| `category.id`            | string (uuid)   | No       | Unique identifier of the category                     |
| `category.name`          | string          | No       | Name of the category                                  |
| `category.slug`          | string          | No       | URL-friendly identifier of the category               |
| `era`                    | object          | Yes      | Historical era of the piece                           |
| `era.id`                 | string (uuid)   | No       | Unique identifier of the era                          |
| `era.name`               | string          | No       | Name of the era                                       |
| `era.slug`               | string          | No       | URL-friendly identifier of the era                    |
| `era.start_year`         | integer         | No       | First year of the era                                 |
| `era.end_year`           | integer         | No       | Last year of the era                                  |
| `year`                   | integer         | No       | Year of creation of the piece                         |
| `decade`                 | integer         | No       | Decade of creation, derived from year. Ex: `1980`     |
| `season`                 | string          | Yes      | Season collection. Ex: `SS25`                         |
| `description`            | string          | Yes      | Short description of the piece                        |
| `story`                  | string          | Yes      | Long narrative text about the piece                   |
| `image_url`              | string (url)    | Yes      | URL of the main image                                 |
| `thumbnail_url`          | string (url)    | Yes      | URL of the thumbnail image                            |
| `image_alt`              | string          | Yes      | Alt text for the image                                |
| `image_credit`           | string          | Yes      | Attribution for the image                             |
| `source`                 | string          | Yes      | Data source. Values: `manual`, `met`, `vam`, `vogue`  |
| `external_url`           | string (url)    | Yes      | URL of the original source record                     |
| `materials`              | array           | No       | List of materials used in the piece                   |
| `materials[].slug`       | string          | No       | Slug identifier of the material. Ex: `silk`           |
| `materials[].name`       | string          | No       | Display name of the material. Ex: `Silk`              |
| `materials[].percentage` | integer         | Yes      | Share of the material in the piece, 0–100             |
| `featured`               | boolean         | No       | Whether the piece is featured                         |
| `is_published`           | boolean         | No       | Whether the piece is publicly visible                 |
| `view_count`             | integer         | No       | Number of times the piece has been viewed             |
| `created_at`             | string (datetime)| No      | Creation timestamp (ISO 8601)                         |
| `updated_at`             | string (datetime)| No      | Last update timestamp (ISO 8601)                      |

Response example:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "Robe du soir asymétrique",
  "slug": "robe-du-soir-asymetrique",
  "designer": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Pierre Balmain",
    "slug": "pierre-balmain",
    "maison": {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "name": "Balmain",
      "slug": "balmain"
    }
  },
  "category": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Robe",
    "slug": "robe"
  },
  "era": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Années 50",
    "slug": "annees-50",
    "start_year": 1950,
    "end_year": 1959
  },
  "year": 1955,
  "decade": 1950,
  "season": "SS55",
  "description": "Robe du soir en soie ivoire.",
  "story": "Cette robe illustre...",
  "image_url": "https://example.com/media/pieces/robe.jpg",
  "thumbnail_url": "https://example.com/media/CACHE/robe_thumb.jpg",
  "image_alt": "Robe du soir en soie ivoire, vue de face",
  "image_credit": "© Musée des Arts Décoratifs",
  "source": "manual",
  "external_url": null,
  "materials": [
    { "slug": "soie", "name": "Soie", "percentage": 100 }
  ],
  "featured": false,
  "is_published": true,
  "view_count": 142,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-06-01T08:00:00Z"
}
```

Errors handling:
| Status | Condition                              |
|--------|----------------------------------------|
| 404    | Aucune pièce trouvée avec cet `id`     |

---

#### 2.1.3. Create a piece
POST /api/pieces/

Create a new piece. Requires admin authentication.

Request body (`multipart/form-data` or `application/json`):
| field           | type            | required    | description                                                          |
|-----------------|-----------------|-------------|----------------------------------------------------------------------|
| `title`         | string          | Yes         | Title of the piece                                                   |
| `designer_id`   | string (uuid)   | Yes         | UUID of the designer                                                 |
| `year`          | integer         | Yes         | Year of creation. Must be between 1400 and 2100                      |
| `category_id`   | string (uuid)   | No          | UUID of the category                                                 |
| `era_id`        | string (uuid)   | No          | UUID of the era                                                      |
| `season`        | string          | No          | Season collection. Ex: `SS25`                                        |
| `description`   | string          | No          | Short description of the piece                                       |
| `story`         | string          | No          | Long narrative text about the piece                                  |
| `image`         | file            | No          | Main image file                                                      |
| `image_alt`     | string          | Conditional | Required if `image` is provided                                      |
| `image_credit`  | string          | No          | Attribution for the image                                            |
| `source`        | string          | No          | Data source. Values: `manual`, `met`, `vam`, `vogue`. Default: `manual` |
| `source_id`     | string          | No          | Identifier in the external source. Must be unique per source         |
| `external_url`  | string (url)    | No          | URL of the original source record                                    |
| `materials_data`| array           | No          | List of materials. Ex: `[{"slug": "silk", "percentage": 80}]`        |
| `is_published`  | boolean         | No          | Publish the piece immediately. Default: `false`                      |
| `featured`      | boolean         | No          | Feature the piece. Default: `false`                                  |

Response body: identical to [2.1.2. Retrieve a piece](#212-retrieve-a-piece).

Response example:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "Manteau noir asymétrique",
  "slug": "manteau-noir-asymetrique",
  "designer": { "...": "..." },
  "year": 1985,
  "is_published": false,
  "featured": false,
  "view_count": 0,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

Errors handling:
| Status | Condition                                                                      |
|--------|--------------------------------------------------------------------------------|
| 400    | `title` ou `designer_id` ou `year` manquant                                    |
| 400    | `year` hors de la plage 1400–2100                                              |
| 400    | `image` fourni sans `image_alt`                                                |
| 400    | `source_id` déjà utilisé pour cette `source`                                   |
| 400    | `designer_id`, `category_id` ou `era_id` invalide (UUID inexistant)            |
| 400    | `source` hors des valeurs autorisées (`manual`, `met`, `vam`, `vogue`)         |
| 401    | Utilisateur non authentifié                                                    |
| 403    | Utilisateur authentifié mais non admin                                         |

---

#### 2.1.4. Update a piece
PUT /api/pieces/{id}/

Fully replace a piece. All writable fields must be provided. Requires admin authentication.

Path parameters:
| param | type          | required | description              |
|-------|---------------|----------|--------------------------|
| `id`  | string (uuid) | Yes      | Unique identifier of the piece |

Request body: identical to [2.1.3. Create a piece](#213-create-a-piece). All fields are required.

Response body: identical to [2.1.2. Retrieve a piece](#212-retrieve-a-piece).

Errors handling:
| Status | Condition                                                              |
|--------|------------------------------------------------------------------------|
| 400    | Champ obligatoire manquant ou valeur invalide (mêmes règles que POST)  |
| 401    | Utilisateur non authentifié                                            |
| 403    | Utilisateur authentifié mais non admin                                 |
| 404    | Aucune pièce trouvée avec cet `id`                                     |

---

#### 2.1.5. Partial update a piece
PATCH /api/pieces/{id}/

Partially update a piece. Only the provided fields are updated. Requires admin authentication.

Path parameters:
| param | type          | required | description              |
|-------|---------------|----------|--------------------------|
| `id`  | string (uuid) | Yes      | Unique identifier of the piece |

Request body: any subset of the fields described in [2.1.3. Create a piece](#213-create-a-piece). Only provided fields are modified.

Response body: identical to [2.1.2. Retrieve a piece](#212-retrieve-a-piece).

Errors handling:
| Status | Condition                                                              |
|--------|------------------------------------------------------------------------|
| 400    | Valeur invalide pour un champ fourni (mêmes règles que POST)           |
| 401    | Utilisateur non authentifié                                            |
| 403    | Utilisateur authentifié mais non admin                                 |
| 404    | Aucune pièce trouvée avec cet `id`                                     |

---

#### 2.1.6. Delete a piece
DELETE /api/pieces/{id}/

Permanently delete a piece. Requires admin authentication.

Path parameters:
| param | type          | required | description              |
|-------|---------------|----------|--------------------------|
| `id`  | string (uuid) | Yes      | Unique identifier of the piece |

Response body: empty.

Errors handling:
| Status | Condition                              |
|--------|----------------------------------------|
| 401    | Utilisateur non authentifié            |
| 403    | Utilisateur authentifié mais non admin |
| 404    | Aucune pièce trouvée avec cet `id`     |

---

#### 2.1.7. Featured pieces
GET /api/pieces/featured/

Retrieve up to 10 featured pieces. Results are cached for 30 minutes.

Parameters: none.

Response body:
| field                            | type            | nullable | description                                     |
|----------------------------------|-----------------|----------|-------------------------------------------------|
| `[].id`                          | string (uuid)   | No       | Unique identifier of the piece                  |
| `[].title`                       | string          | No       | Title of the piece                              |
| `[].slug`                        | string          | No       | URL-friendly identifier of the piece            |
| `[].designer`                    | object          | No       | Designer associated with the piece              |
| `[].designer.id`                 | string (uuid)   | No       | Unique identifier of the designer               |
| `[].designer.name`               | string          | No       | Full name of the designer                       |
| `[].designer.slug`               | string          | No       | URL-friendly identifier of the designer         |
| `[].designer.maison`             | object          | Yes      | Fashion house associated with the designer      |
| `[].designer.maison.id`          | string (uuid)   | No       | Unique identifier of the maison                 |
| `[].designer.maison.name`        | string          | No       | Name of the maison                              |
| `[].designer.maison.slug`        | string          | No       | URL-friendly identifier of the maison           |
| `[].category`                    | object          | Yes      | Typological category of the piece               |
| `[].category.id`                 | string (uuid)   | No       | Unique identifier of the category               |
| `[].category.name`               | string          | No       | Name of the category                            |
| `[].category.slug`               | string          | No       | URL-friendly identifier of the category         |
| `[].year`                        | integer         | No       | Year of creation                                |
| `[].season`                      | string          | Yes      | Season collection. Ex: `SS25`                   |
| `[].image_url`                   | string (url)    | Yes      | URL of the main image                           |
| `[].thumbnail_url`               | string (url)    | Yes      | URL of the thumbnail image                      |
| `[].image_alt`                   | string          | Yes      | Alt text for the image                          |
| `[].featured`                    | boolean         | No       | Always `true`                                   |
| `[].view_count`                  | integer         | No       | Number of times the piece has been viewed       |

Response example:
```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "title": "Robe du soir asymétrique",
    "slug": "robe-du-soir-asymetrique",
    "designer": {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "name": "Pierre Balmain",
      "slug": "pierre-balmain",
      "maison": { "id": "...", "name": "Balmain", "slug": "balmain" }
    },
    "category": { "id": "...", "name": "Robe", "slug": "robe" },
    "year": 1955,
    "season": "SS55",
    "image_url": "https://example.com/media/pieces/robe.jpg",
    "thumbnail_url": "https://example.com/media/CACHE/robe_thumb.jpg",
    "image_alt": "Robe du soir en soie ivoire",
    "featured": true,
    "view_count": 142
  }
]
```

Errors handling:
| Status | Condition                          |
|--------|------------------------------------|
| 500    | Erreur interne du serveur          |

> Note : retourne un tableau vide `[]` si aucune pièce n'est marquée comme featured. Ce n'est pas une erreur (HTTP 200).

---

#### 2.1.8. Pieces by decade
GET /api/pieces/by_decade/

Retrieve a paginated list of pieces belonging to a given decade.

Parameters:
| param    | type    | required | description                                                       |
|----------|---------|----------|-------------------------------------------------------------------|
| `decade` | integer | Yes      | Decade to filter by. Must be a multiple of 10. Ex: `1980`         |
| `page`   | integer | No       | Page number to retrieve                                           |

Response body: identical to [2.1.1. List pieces](#211-list-pieces) (paginated envelope with `PieceListSerializer` items).

Errors handling:
| Status | Condition                                          |
|--------|----------------------------------------------------|
| 400    | Paramètre `decade` manquant                        |
| 400    | `decade` non entier                                |
| 400    | `decade` non multiple de 10                        |
| 400    | `decade` hors de la plage 1800–2100                |

> Note : une liste vide (`"results": []`) est retournée si aucune pièce n'appartient à cette décennie. Ce n'est pas une erreur (HTTP 200).

---

#### 2.1.9. Global statistics
GET /api/pieces/stats/

Retrieve aggregated statistics about the collection. Results are cached for 1 hour.

Parameters: none.

Response body:
| field                             | type    | nullable | description                                        |
|-----------------------------------|---------|----------|----------------------------------------------------|
| `total_pieces`                    | integer | No       | Total number of pieces in the collection           |
| `total_designers`                 | integer | No       | Total number of distinct designers                 |
| `total_categories`                | integer | No       | Total number of distinct categories                |
| `decade_distribution`             | object  | No       | Number of pieces per decade                        |
| `decade_distribution.<decade>`    | integer | No       | Count of pieces for that decade. Ex: `"1980": 234` |
| `top_designers`                   | array   | No       | Top 10 designers by number of pieces               |
| `top_designers[].name`            | string  | No       | Full name of the designer                          |
| `top_designers[].slug`            | string  | No       | URL-friendly identifier of the designer            |
| `top_designers[].num_pieces`      | integer | No       | Number of pieces for this designer                 |

Response example:
```json
{
  "total_pieces": 1247,
  "total_designers": 89,
  "total_categories": 12,
  "decade_distribution": {
    "1950": 87,
    "1960": 134,
    "1970": 201,
    "1980": 234,
    "1990": 456,
    "2000": 135
  },
  "top_designers": [
    { "name": "Yohji Yamamoto", "slug": "yohji-yamamoto", "num_pieces": 156 },
    { "name": "Pierre Balmain", "slug": "pierre-balmain", "num_pieces": 98 }
  ]
}
```

Errors handling:
| Status | Condition                 |
|--------|---------------------------|
| 500    | Erreur interne du serveur |

---

#### 2.1.10. Increment view count
POST /api/pieces/{id}/increment_view/

Increment the view counter of a piece by 1. Thread-safe. Public endpoint.

Path parameters:
| param | type          | required | description              |
|-------|---------------|----------|--------------------------|
| `id`  | string (uuid) | Yes      | Unique identifier of the piece |

Request body: empty.

Response body:
| field        | type    | nullable | description                        |
|--------------|---------|----------|------------------------------------|
| `view_count` | integer | No       | Updated view count after increment |

Response example:
```json
{
  "view_count": 143
}
```

Errors handling:
| Status | Condition                              |
|--------|----------------------------------------|
| 404    | Aucune pièce trouvée avec cet `id`     |

---

#### 2.1.11. Publish a piece
POST /api/pieces/{id}/publish/

Set a piece as published (`is_published = true`). Requires admin authentication.

Path parameters:
| param | type          | required | description              |
|-------|---------------|----------|--------------------------|
| `id`  | string (uuid) | Yes      | Unique identifier of the piece |

Request body: empty.

Response body: identical to [2.1.2. Retrieve a piece](#212-retrieve-a-piece).

Errors handling:
| Status | Condition                              |
|--------|----------------------------------------|
| 400    | La pièce est déjà publiée              |
| 401    | Utilisateur non authentifié            |
| 403    | Utilisateur authentifié mais non admin |
| 404    | Aucune pièce trouvée avec cet `id`     |

---

#### 2.1.12. Unpublish a piece
POST /api/pieces/{id}/unpublish/

Set a piece as unpublished (`is_published = false`). Requires admin authentication.

Path parameters:
| param | type          | required | description              |
|-------|---------------|----------|--------------------------|
| `id`  | string (uuid) | Yes      | Unique identifier of the piece |

Request body: empty.

Response body: identical to [2.1.2. Retrieve a piece](#212-retrieve-a-piece).

Errors handling:
| Status | Condition                              |
|--------|----------------------------------------|
| 400    | La pièce est déjà dépubliée            |
| 401    | Utilisateur non authentifié            |
| 403    | Utilisateur authentifié mais non admin |
| 404    | Aucune pièce trouvée avec cet `id`     |

---

#### 2.1.13. Feature a piece
POST /api/pieces/{id}/feature/

Mark a piece as featured (`featured = true`). Requires admin authentication.

Path parameters:
| param | type          | required | description              |
|-------|---------------|----------|--------------------------|
| `id`  | string (uuid) | Yes      | Unique identifier of the piece |

Request body: empty.

Response body: identical to [2.1.2. Retrieve a piece](#212-retrieve-a-piece).

Errors handling:
| Status | Condition                              |
|--------|----------------------------------------|
| 400    | La pièce est déjà featured             |
| 401    | Utilisateur non authentifié            |
| 403    | Utilisateur authentifié mais non admin |
| 404    | Aucune pièce trouvée avec cet `id`     |

---

#### 2.1.14. Unfeature a piece
POST /api/pieces/{id}/unfeature/

Remove a piece from featured (`featured = false`). Requires admin authentication.

Path parameters:
| param | type          | required | description              |
|-------|---------------|----------|--------------------------|
| `id`  | string (uuid) | Yes      | Unique identifier of the piece |

Request body: empty.

Response body: identical to [2.1.2. Retrieve a piece](#212-retrieve-a-piece).

Errors handling:
| Status | Condition                              |
|--------|----------------------------------------|
| 400    | La pièce n'est pas featured            |
| 401    | Utilisateur non authentifié            |
| 403    | Utilisateur authentifié mais non admin |
| 404    | Aucune pièce trouvée avec cet `id`     |

---

### 2.2. Designers

Represents a fashion designer linked to a maison.

#### 2.2.1. List designers
GET /api/designers/

Retrieve a paginated list of designers. Results are cached for 15 minutes.

Parameters:
| param              | type    | required | description                                                   |
|--------------------|---------|----------|---------------------------------------------------------------|
| `search`           | string  | No       | Search by name, bio, or maison name (partial match)           |
| `ordering`         | string  | No       | Sort field. Values: `name`, `-name`, `birth_year`, `-birth_year`. Default: `name` |
| `nationality`      | string  | No       | Filter by nationality (exact, case-insensitive). Ex: `Japanese` |
| `nationality_contains` | string | No    | Filter by nationality (partial match). Ex: `Japan`            |
| `birth_year_min`   | integer | No       | Filter designers born in or after this year                   |
| `birth_year_max`   | integer | No       | Filter designers born in or before this year                  |
| `maison`           | string (slug) | No  | Filter by maison slug. Ex: `chanel`                          |
| `maison_id`        | string (uuid) | No  | Filter by maison UUID                                        |
| `has_maison`       | boolean | No       | Filter by whether the designer is linked to a maison          |
| `page`             | integer | No       | Page number to retrieve                                       |

Response body:
| field                  | type            | nullable | description                                       |
|------------------------|-----------------|----------|---------------------------------------------------|
| `count`                | integer         | No       | Total number of designers across all pages        |
| `next`                 | string (url)    | Yes      | URL of the next page, or null                     |
| `previous`             | string (url)    | Yes      | URL of the previous page, or null                 |
| `results`              | array           | No       | List of designers for the current page            |
| `results[].id`         | string (uuid)   | No       | Unique identifier of the designer                 |
| `results[].name`       | string          | No       | Full name of the designer                         |
| `results[].slug`       | string          | No       | URL-friendly identifier of the designer           |
| `results[].nationality`| string          | Yes      | Nationality of the designer                       |
| `results[].birth_year` | integer         | Yes      | Birth year of the designer                        |
| `results[].maison`     | object          | Yes      | Fashion house associated with the designer        |
| `results[].maison.id`  | string (uuid)   | No       | Unique identifier of the maison                   |
| `results[].maison.name`| string          | No       | Name of the maison                                |
| `results[].maison.slug`| string          | No       | URL-friendly identifier of the maison             |
| `results[].pieces_count`| integer        | No       | Number of pieces attributed to this designer      |

Response example:
```json
{
  "count": 89,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "name": "Yohji Yamamoto",
      "slug": "yohji-yamamoto",
      "nationality": "Japanese",
      "birth_year": 1943,
      "maison": {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "Yohji Yamamoto Inc.",
        "slug": "yohji-yamamoto-inc"
      },
      "pieces_count": 156
    }
  ]
}
```

Errors handling:
| Status | Condition                                                    |
|--------|--------------------------------------------------------------|
| 400    | `birth_year_min` ou `birth_year_max` non entier              |
| 400    | `has_maison` avec une valeur non booléenne                   |
| 500    | Erreur interne du serveur                                    |

---

#### 2.2.2. Retrieve a designer
GET /api/designers/{id}/

Retrieve the full details of a single designer, including their pieces.

Path parameters:
| param | type          | required | description                |
|-------|---------------|----------|----------------------------|
| `id`  | string (uuid) | Yes      | Unique identifier of the designer |

Response body:
| field                  | type             | nullable | description                                       |
|------------------------|------------------|----------|---------------------------------------------------|
| `id`                   | string (uuid)    | No       | Unique identifier of the designer                 |
| `name`                 | string           | No       | Full name of the designer                         |
| `slug`                 | string           | No       | URL-friendly identifier of the designer           |
| `nationality`          | string           | Yes      | Nationality of the designer                       |
| `birth_year`           | integer          | Yes      | Birth year of the designer                        |
| `death_year`           | integer          | Yes      | Death year of the designer, or null if alive      |
| `bio`                  | string           | Yes      | Biographical text                                 |
| `image`                | string (url)     | Yes      | URL of the designer's portrait image              |
| `website`              | string (url)     | Yes      | Official website URL                              |
| `instagram`            | string           | Yes      | Instagram handle                                  |
| `maison`               | object           | Yes      | Fashion house associated with the designer        |
| `maison.id`            | string (uuid)    | No       | Unique identifier of the maison                   |
| `maison.name`          | string           | No       | Name of the maison                                |
| `maison.slug`          | string           | No       | URL-friendly identifier of the maison             |
| `pieces_count`         | integer          | No       | Number of pieces attributed to this designer      |
| `pieces`               | array            | No       | Published pieces attributed to this designer      |
| `pieces[].id`          | string (uuid)    | No       | Unique identifier of the piece                    |
| `pieces[].title`       | string           | No       | Title of the piece                                |
| `pieces[].slug`        | string           | No       | URL-friendly identifier of the piece              |
| `pieces[].year`        | integer          | No       | Year of creation                                  |
| `pieces[].season`      | string           | Yes      | Season collection                                 |
| `pieces[].image_url`   | string (url)     | Yes      | URL of the main image                             |
| `pieces[].thumbnail_url`| string (url)    | Yes      | URL of the thumbnail image                        |
| `pieces[].image_alt`   | string           | Yes      | Alt text for the image                            |
| `pieces[].featured`    | boolean          | No       | Whether the piece is featured                     |
| `pieces[].view_count`  | integer          | No       | Number of times the piece has been viewed         |
| `created_at`           | string (datetime)| No       | Creation timestamp (ISO 8601)                     |

Response example:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Yohji Yamamoto",
  "slug": "yohji-yamamoto",
  "nationality": "Japanese",
  "birth_year": 1943,
  "death_year": null,
  "bio": "Yohji Yamamoto est un créateur de mode japonais...",
  "image": "https://example.com/media/designers/yohji.jpg",
  "website": "https://www.yohjiyamamoto.co.jp",
  "instagram": "@yohjiyamamoto",
  "maison": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Yohji Yamamoto Inc.",
    "slug": "yohji-yamamoto-inc"
  },
  "pieces_count": 156,
  "pieces": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "title": "Manteau noir asymétrique",
      "slug": "manteau-noir-asymetrique",
      "year": 1985,
      "season": "FW85",
      "image_url": "https://example.com/media/pieces/manteau.jpg",
      "thumbnail_url": "https://example.com/media/CACHE/manteau_thumb.jpg",
      "image_alt": "Manteau noir asymétrique",
      "featured": true,
      "view_count": 320
    }
  ],
  "created_at": "2024-01-15T10:30:00Z"
}
```

Errors handling:
| Status | Condition                                  |
|--------|--------------------------------------------|
| 404    | Aucun designer trouvé avec cet `id`        |

---

### 2.3. Categories

Represents a typological category of fashion objects (e.g. Dress, Jacket).

#### 2.3.1. List categories
GET /api/categories/

Retrieve the full list of categories, ordered by name. Results are cached for 1 hour.

Parameters: none.

Response body:
| field              | type          | nullable | description                                |
|--------------------|---------------|----------|--------------------------------------------|
| `count`            | integer       | No       | Total number of categories                 |
| `next`             | string (url)  | Yes      | URL of the next page, or null              |
| `previous`         | string (url)  | Yes      | URL of the previous page, or null          |
| `results`          | array         | No       | List of categories                         |
| `results[].id`     | string (uuid) | No       | Unique identifier of the category          |
| `results[].name`   | string        | No       | Display name of the category               |
| `results[].slug`   | string        | No       | URL-friendly identifier of the category    |

Response example:
```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "results": [
    { "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6", "name": "Dress", "slug": "dress" },
    { "id": "3fa85f64-5717-4562-b3fc-2c963f66afa7", "name": "Jacket", "slug": "jacket" }
  ]
}
```

Errors handling:
| Status | Condition                 |
|--------|---------------------------|
| 500    | Erreur interne du serveur |

---

#### 2.3.2. Retrieve a category
GET /api/categories/{slug}/

Retrieve the details of a single category.

Path parameters:
| param  | type   | required | description                    |
|--------|--------|----------|--------------------------------|
| `slug` | string | Yes      | URL-friendly identifier of the category. Ex: `dress` |

Response body:
| field    | type          | nullable | description                             |
|----------|---------------|----------|-----------------------------------------|
| `id`     | string (uuid) | No       | Unique identifier of the category       |
| `name`   | string        | No       | Display name of the category            |
| `slug`   | string        | No       | URL-friendly identifier of the category |

Response example:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Dress",
  "slug": "dress"
}
```

Errors handling:
| Status | Condition                                   |
|--------|---------------------------------------------|
| 404    | Aucune catégorie trouvée avec ce `slug`      |

---

#### 2.3.3. Pieces by category
GET /api/categories/{slug}/pieces/

Retrieve a paginated list of published pieces belonging to a given category.

Path parameters:
| param  | type   | required | description                    |
|--------|--------|----------|--------------------------------|
| `slug` | string | Yes      | URL-friendly identifier of the category. Ex: `dress` |

Parameters:
| param  | type    | required | description             |
|--------|---------|----------|-------------------------|
| `page` | integer | No       | Page number to retrieve |

Response body: identical to [2.1.1. List pieces](#211-list-pieces) (paginated envelope with `PieceListSerializer` items).

Errors handling:
| Status | Condition                                   |
|--------|---------------------------------------------|
| 404    | Aucune catégorie trouvée avec ce `slug`      |

> Note : une liste vide (`"results": []`) est retournée si aucune pièce publiée n'appartient à cette catégorie. Ce n'est pas une erreur (HTTP 200).

---

### 2.4. Eras

Represents a historical fashion period (e.g. Années 80).

#### 2.4.1. List eras
GET /api/eras/

Retrieve the full list of eras, ordered chronologically by start year. Results are cached for 1 hour.

Parameters: none.

Response body:
| field                  | type          | nullable | description                             |
|------------------------|---------------|----------|-----------------------------------------|
| `count`                | integer       | No       | Total number of eras                    |
| `next`                 | string (url)  | Yes      | URL of the next page, or null           |
| `previous`             | string (url)  | Yes      | URL of the previous page, or null       |
| `results`              | array         | No       | List of eras                            |
| `results[].id`         | string (uuid) | No       | Unique identifier of the era            |
| `results[].name`       | string        | No       | Display name of the era                 |
| `results[].slug`       | string        | No       | URL-friendly identifier of the era      |
| `results[].start_year` | integer       | No       | First year of the era                   |
| `results[].end_year`   | integer       | No       | Last year of the era                    |

Response example:
```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "name": "Années 80",
      "slug": "annees-80",
      "start_year": 1980,
      "end_year": 1989
    }
  ]
}
```

Errors handling:
| Status | Condition                 |
|--------|---------------------------|
| 500    | Erreur interne du serveur |

---

#### 2.4.2. Retrieve an era
GET /api/eras/{slug}/

Retrieve the details of a single era.

Path parameters:
| param  | type   | required | description                  |
|--------|--------|----------|------------------------------|
| `slug` | string | Yes      | URL-friendly identifier of the era. Ex: `annees-80` |

Response body:
| field        | type          | nullable | description                        |
|--------------|---------------|----------|------------------------------------|
| `id`         | string (uuid) | No       | Unique identifier of the era       |
| `name`       | string        | No       | Display name of the era            |
| `slug`       | string        | No       | URL-friendly identifier of the era |
| `start_year` | integer       | No       | First year of the era              |
| `end_year`   | integer       | No       | Last year of the era               |

Response example:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Années 80",
  "slug": "annees-80",
  "start_year": 1980,
  "end_year": 1989
}
```

Errors handling:
| Status | Condition                               |
|--------|-----------------------------------------|
| 404    | Aucune ère trouvée avec ce `slug`       |

---

#### 2.4.3. Pieces by era
GET /api/eras/{slug}/pieces/

Retrieve a paginated list of published pieces belonging to a given era.

Path parameters:
| param  | type   | required | description                  |
|--------|--------|----------|------------------------------|
| `slug` | string | Yes      | URL-friendly identifier of the era. Ex: `annees-80` |

Parameters:
| param  | type    | required | description             |
|--------|---------|----------|-------------------------|
| `page` | integer | No       | Page number to retrieve |

Response body: identical to [2.1.1. List pieces](#211-list-pieces) (paginated envelope with `PieceListSerializer` items).

Errors handling:
| Status | Condition                               |
|--------|-----------------------------------------|
| 404    | Aucune ère trouvée avec ce `slug`       |

> Note : une liste vide (`"results": []`) est retournée si aucune pièce publiée n'appartient à cette ère. Ce n'est pas une erreur (HTTP 200).

---

### 2.5. Health

#### 2.5.1. Health check
GET /api/health/

Verify the operational status of the service and its dependencies (database, cache, disk). Designed for monitoring systems (Kubernetes, Docker, load balancers).

Parameters: none.

Response body:
| field               | type    | nullable | description                                              |
|---------------------|---------|----------|----------------------------------------------------------|
| `status`            | string  | No       | Global status. Values: `healthy`, `unhealthy`            |
| `database`          | string  | No       | Database status. Values: `connected`, `error`            |
| `cache`             | string  | No       | Cache (Redis) status. Values: `connected`, `error`       |
| `disk_free_percent` | number  | No       | Percentage of free disk space remaining                  |
| `timestamp`         | string (datetime) | No | Timestamp of the check (ISO 8601)                   |
| `errors`            | array   | Yes      | List of error messages, present only when `status` is `unhealthy` |

Response example (healthy):
```json
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected",
  "disk_free_percent": 45.2,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

Response example (unhealthy):
```json
{
  "status": "unhealthy",
  "database": "connected",
  "cache": "error",
  "disk_free_percent": 45.2,
  "timestamp": "2025-01-15T10:30:00Z",
  "errors": ["Redis connection refused"]
}
```

Errors handling:
| Status | Condition                                          |
|--------|----------------------------------------------------|
| 503    | Au moins un composant est en erreur (`unhealthy`)  |

