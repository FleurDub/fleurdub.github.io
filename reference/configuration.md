# Configuration reference

This document describes how MEMORA is configured across environments.

It covers backend settings, environment variables, database configuration, and frontend integration.

---

## Backend configuration (Django)

MEMORA uses Django settings modules to manage environment-specific configuration.

Settings are organized as:

config/settings/
base.py
development.py
production.py

- `base.py` contains shared configuration.
- `development.py` contains local development settings.
- `production.py` is intended for production deployment.

The active settings module is defined through the `DJANGO_SETTINGS_MODULE` environment variable.

Example:
DJANGO_SETTINGS_MODULE=config.settings.development

---

## Environment variables

Sensitive configuration values are managed using environment variables.

These include:

- `SECRET_KEY`
- `DEBUG`
- `DATABASE_URL` (if using PostgreSQL)
- other environment-specific configuration

Environment variables prevent sensitive values from being stored in source code.

---

## Database configuration

The system supports multiple database backends depending on the environment.

### Development

Uses SQLite by default:
db.sqlite3

This simplifies local setup.

### Production (planned)

PostgreSQL is the intended production database.

PostgreSQL enables:

- advanced indexing
- JSONField querying
- full-text search support
- better performance at scale

---

## Media configuration

The backend supports media files such as:

- piece images
- designer images
- maison logos

Media configuration is definedd in Django settings:

MEDIA_ROOT
MEDIA_URL

In development, media files are stored locally.

Production storage may use external storage (S3-compatible storage).

---

## Frontend configuration

The frontend communicates with the backend API through a configured base URL.

Example:

NEXT_PUBLIC_API_URL=http://localhost:8000/api/

This allows the frontend to interact with the backend.

---

## Allowed hosts

Django restricts allowed hosts through:

ALLOWED_HOSTS

This prevents unauthorized host access.

---

## Debug mode

Debug mode is controlled through:

DEBUG=True

Debug mode should only be enabled in development.

---

## Summary

Configuration in MEMORA ensures:

- environment-specific behaviour
- secure handling of sensitive values
- scalable database support
- proper frontend-backend communication