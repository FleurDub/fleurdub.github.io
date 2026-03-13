# How to add archival data (admin → API  → UI)

This guide shows how to add a minimal set of archival data to MEMORA and verify it end-to-end:

1. Create related entities in Django Admin (Era, Category Maison, Designer)
2. Create a Piece linked to those entities
3. Verify the result via the REST API
4. Verify the result in the Next.js UI

> **Note:** This guide assumes you can run MEMORA locally. If not, follow 'docs/how-to/run-the-project.md' first.

---

## 1. Open Django Admin

Open:

- `http://localhost:8000/admin/`

Log in with an admin user (superuser).

---

## 2. Create the minimal relational context

### 2.1 Create an Era

Create an Era that will be linked to Pieces.

Recommended fields to fill:
- name (human-readable)
- slug (URL-safe identifier)

> **Tip:** Keep slugs stable because they are used in filtering and URLs.

---

### 2.2 Create a Category

Create a Category representing a typology.

Recommended fields:
- name
- slug

---

### 2.3 (Optional) Create a Maison

If you want to link a Designer to an institutional context, create a Maison.

Recommended fields:
- name
- slug
- nationality (if relevant)
- birth_year (if relevant)
- maison (optional)

---

## 3. Create a Piece

Create a Piece and link it to the entities above.

Minimum recommended fields for a useful record:
- title
- description
- designer (FK)
- era (FK)
- category (FK)

Optional but recommended:
- image (if you want it to be considered "complete")
- season
- source
- materials_data (if available)
- is_published (if you want it visible in "published-only" views)
- featured (for curated selection)

---

## 4. Verify the Piece via the API

### 4.1 List pieces

Open in a browser or use curl:

```bash
curl http://localhost:8000/api/pieces/

```
You should see your new Piece in the list.

### 4.2 Retrieve the Piece by ID

Copy the id (UUID) from the list response, then:

```bash
curl http://localhost:8000/api/pieces/<piece_uuid>/

```
Verify that relational fields are present (designer, era, category) and consistent.

### 4.3 Verify relational filtering

Filter by designer slug:

```bash
curl "http://localhost:8000/api/pieces/?designer=<designer_slug>"

```
Filter by designer slug:

```bash
curl "http://localhost:8000/api/pieces/?era=<era_slug>"

```
Filter by category slug:

```bash
curl "http://localhost:8000/api/pieces/?category=<category_slug>"

```
> **Note:** See docs/reference/filtering.md for the complete list of supported filters.

### 4.4 Verify completeness filtering (optional)

If your record:
- title
- description
- image
- category
- non-empty materials_data

It should be considered complete:

```bash
curl "http://localhost:8000/api/pieces/?is_complete=true"

```
If it is missing any of these, it should appear under:

```bash
curl "http://localhost:8000/api/pieces/?is_complete=false"

```

### 5. Verify in the Next.js UI

Ensure the frontend is running:
- http://localhost:3000/

#### 5.1 Find the Piece in the listing

Navigate to:
- /pieces

Confirm your Piece is visible (depending on whether you UI filters to published pieces).

#### 5.2 Open the Piece detail view

Click your Piece, or navigate directly to:
- /pieces/<piece_id>

Confirm the relational context is displayed (designer, era, category).

### 6. Recommended workflow for beta datasets

When building a beta dataset, a productive editorial workflow is:

1. Create minimal records quickly (title + relations)
2. Mark as published only once essential fields are present
3. Use completeness filtering to prioritise enrichment
4. Curate "featured" pieces for demos and UX testing

This workflow supports incremental archival enrichment without blocking exploration.