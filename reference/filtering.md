# Filtering Reference

The MEMORA API supports relational and attribute-based filtering.

Filtering is implemented using django-filter.

---

## Piece filters

### By designer

GET /api/pieces/?designer=pierre-balmain

### By era

GET /api/pieces/?era=1950s

### By category

GET /api/pieces/?category=dress

---

## Text filters

GET /api/pieces/?title_contains=dress

---

## Completeness filter

GET /api/pieces/?is_complete=true

A piece is considered complete if it includes:

- title
- description
- image
- category
- materials_data