# URL Shortener

A scalable URL shortener: turn long URLs into short links and redirect visitors to the original URL. Built with **FastAPI**, **PostgreSQL**, and **Redis**, with a simple web UI and APIs designed for high traffic on both creation and redirect.

---

## What It Does

- **Shorten:** Give it a long URL; you get back a short link (e.g. `http://localhost:8000/1`).
- **Redirect:** When someone opens the short link, they are sent (302) to the original long URL.
- **Web UI:** On the home page you can paste a long URL to get a short one, or paste a short URL to jump to the real link.

---

## Architecture (Plain English)

### The Big Picture

The app has two main flows: **creating** short URLs and **redirecting** when someone clicks them. Both are built to scale.

- **Creating a short URL:** The app gets a new number from Redis, turns it into a short code (using Base62, so codes stay short and readable), saves the mapping in PostgreSQL, and also stores it in Redis so the next redirect is fast. The browser or API gets back the full short URL.

- **Redirecting:** When a request hits a short link, the app looks up the short code in Redis first. If it’s there, it immediately sends a redirect to the long URL (very fast). If not, it looks in PostgreSQL, stores the result in Redis for next time, then redirects. So most redirects never touch the database.

### Why This Design

- **Redis for the counter:** New IDs come from Redis (`INCR`) instead of the database. That avoids overloading the DB on heavy write traffic and keeps creation fast.

- **Base62 for short codes:** Each number is encoded in Base62 (digits + lower- and uppercase letters). You get short, unique codes (e.g. `1`, `2`, `a`, `b` …) without checking for collisions.

- **Redis as cache for redirects:** Redirects are read-heavy. By caching “short code → long URL” in Redis, most requests are served from memory in under a millisecond. PostgreSQL is used as the durable store and for cache misses.

- **Async everywhere:** FastAPI, asyncpg, and async Redis are used so the server can handle many concurrent requests without blocking.

### Unique / Standout Points

1. **Scalable on both paths:** Generation scales via Redis-backed IDs and connection pooling; redirects scale via a Redis-first cache so the DB is only hit on cache miss.

2. **No collision short codes:** Base62 of a global counter means every short code is unique by design; no retries or collision checks.

3. **Clean layered structure:** Routes call services; services use repositories (PostgreSQL) and Redis. Config, DB, and Redis live in `core`; no business logic there. See [STRUCTURE.md](STRUCTURE.md).

4. **Redirect path stays lean:** Lookup and redirect only; no analytics or heavy work in the hot path, so redirect latency stays low.

5. **Optional cache TTL:** Redis cache can use a TTL (via `REDIS_CACHE_TTL_SECONDS`) to cap memory while still serving most traffic from cache.

---

## Tech Stack

- **Python 3.10+**, **FastAPI**, **Pydantic**
- **PostgreSQL** (async via asyncpg + SQLAlchemy 2)
- **Redis** (async) for ID counter and redirect cache
- **Jinja2** for the home-page UI

---

## Features

| Feature | Description |
|--------|-------------|
| **Web UI** | Home page (`/`) with a form to shorten a URL and a form to open a short URL (redirect). |
| **POST /shorten** | API to create a short URL (Redis INCR → Base62 → PostgreSQL → Redis cache). |
| **GET /{short_code}** | Redirects (302) to the long URL (Redis first, then PostgreSQL on miss). |
| **GET /health** | Health check for load balancers. |
| **OpenAPI docs** | Interactive API docs at `/docs`. |

---

## Setup

### Option A: Run locally

1. **Create a virtualenv and install dependencies**

   ```bash
   cd url-shortner
   python -m venv venv
   source venv/bin/activate   # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

2. **Configure environment**

   Copy `.env.example` to `.env` and set:

   - `DATABASE_URL` – PostgreSQL URL (e.g. `postgresql+asyncpg://user:pass@localhost:5432/url_shortener`)
   - `REDIS_URL` – Redis URL (e.g. `redis://localhost:6379/0`)
   - `BASE_URL` – Base URL for short links (e.g. `http://localhost:8000`)

3. **Database**

   Tables are created automatically on first run. To use migrations instead:

   ```bash
   alembic upgrade head
   ```

4. **Run the app**

   ```bash
   uvicorn app.main:app --reload
   ```

   - **Web UI:** http://localhost:8000  
   - **API docs:** http://localhost:8000/docs  

### Option B: Run with Docker

From the project root:

```bash
docker compose up --build
```

This starts the app, PostgreSQL, and Redis. The app is at http://localhost:8000 and uses the `db` and `redis` services. Tables are created on startup.

---

## Usage

**Web UI:** Open http://localhost:8000. Use “Get short URL” to shorten a long URL and “Go to URL” to open a short link.

**API (shorten):**

```bash
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/long"}'
# → {"short_url":"http://localhost:8000/1"}
```

**Redirect:** Open `http://localhost:8000/1` in a browser (or `curl -I http://localhost:8000/1`) to get a 302 to the long URL.

---

## Project structure

See [STRUCTURE.md](STRUCTURE.md) for the full layout. In short:

- **api/routes** – HTTP endpoints (shorten, redirect, home page).
- **services** – Business logic (shorten flow, resolve flow using Redis + DB).
- **repositories** – Database access (PostgreSQL).
- **core** – Config, DB session, Redis client.
- **models** – SQLAlchemy table definitions.
- **schemas** – Pydantic request/response models.
- **templates** – Jinja2 HTML for the home page.

---

## Tests

Tests need PostgreSQL and Redis (e.g. local Redis and a test DB). They use Redis DB 1 by default (see `tests/conftest.py`).

```bash
pytest tests/ -v
```

---

## Configuration

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL URL; use `postgresql+asyncpg://...` for async. |
| `REDIS_URL` | Redis connection URL. |
| `BASE_URL` | Base URL for short links (no trailing slash). |
| `REDIS_CACHE_TTL_SECONDS` | Optional TTL for Redis cache entries; omit for no expiry. |
