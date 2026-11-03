# Sports Platform

Full-stack football match dashboard. A FastAPI service pulls fixture data from a football API, and a Next.js frontend lets users browse matches, past results, and individual match pages.

## Features

- Match list grouped for quick browsing
- Past match view backed by cached data
- Individual match detail pages
- REST API separating the frontend from the third-party data provider

## Tech Stack

- **Backend:** Python, FastAPI, Docker
- **Frontend:** Next.js, React, TypeScript
- **Database:** SQL schema in `database/schema.sql`

## Repository Layout

```text
backend/app/
  routes/    API routes
  services/  Football API client
database/    Schema
frontend/    Next.js app
```

## Running Locally

Backend:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd backend
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```
