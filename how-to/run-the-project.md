# How to run MEMORA locally

This guide explains how to run MEMORA locally for development.

It covers:
- backend (Django/DRF)
- database
- admin
- frontend (Next.js)
- documentation build (Sphinx)

---

## Prerequesites

- Python 3.11+
- Node.js 18+
- Git
- (Recommended) PostgreSQL if you want to use JSONField filtering as intended

---

## Backend setup (Django / DRF)

1) Create and activate a virtual environment:

```bash
python -m venv venv
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

```

2) Install backend dependencies:

```bash
pip install -r requirements.txt

```
> Note: If you repository uses multiple requirements files, install the development one (requirements/dev.txt) instead.

3) Apply migrations:

```bash
python manage.py migrate

```

4) Create an admin user:

```bash
python manage.py createsuperuser

```

5) Run the backend server:

```bash
python manage.py runserver

```

The API should be available at:

- http://localhost:8000/api/

---

## Django Admin

Open:

- http://localhost:8000/admin/

Log in with the superuser created earlier.

From the admin interface you can:

- create/edit Pieces, Designers, Eras, Categories, Maisons
- manage publication flags (is_published, featured)
- attach media where applicable

---

## Frontend setup (Next.js)

From the project root:

1) Install frontend dependencies:

```bash
cd frontend
npm install

```
2) Configure the backend API URL (example):

Create a .env.local file in frontend/:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/

```
3) Run the frontend:

```bash
npm run dev

```

The UI should be available at:

- http://localhost:3000/

---

## Run backend tests

From the project root (backend environment activated):

```bash
python manage.py test

```

---

## Build documentation (Sphinx)

From the project root (backend evironment activated):

1) Go to docs:

```bash
cd docs

```

2) Build HTML docs:

```bash
# Windows
.\make.bat html

# macOS/Linux
make html
```

Open:

- docs/build/html/index.html


## Troubleshooting

### API connection issues (frontend)

- Ensure backend is running on http://localhost:8000/
- Ensure NEXT_PUBLIC_API_URL matches your backend API root (including /api/)
- Check CORS configuration if you changed ports/domains

### PostgreSQL-specific filtering

Some filtering features (JSONFIELD containment for materials) are PostgreSQL dependent.

If using SQLite in development, those filters may behave differently or be less performant.

See: docs/reference/filtering.md