# URL Shortener – Clean Code Structure

```
url-shortner/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, lifespan, include_routers
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── shorten.py         # POST /shorten
│   │       └── redirect.py        # GET /{short_code} → 302
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Settings (DB URL, Redis URL, base URL)
│   │   ├── database.py            # Async engine, session factory, get_db
│   │   └── redis.py               # Redis client, get_redis, close_redis
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── url.py                 # SQLAlchemy Url model
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── shorten.py             # ShortenRequest, ShortenResponse (Pydantic)
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── url_repository.py      # create_url, get_long_url_by_short_code
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── url_service.py         # shorten_url, resolve (Redis + repo)
│   │
│   └── utils/
│       ├── __init__.py
│       └── base62.py              # encode(id), decode(short_code)
│
├── migrations/
│   └── versions/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_shorten.py
│   └── test_redirect.py
│
├── .env.example
├── requirements.txt
├── README.md
└── STRUCTURE.md
```

## Layer Responsibilities

| Layer           | Responsibility |
|----------------|----------------|
| **api/routes** | HTTP: parse request, call service, return response/redirect |
| **services**   | Business flow: Redis INCR, Base62, persist, cache |
| **repositories** | Data access: insert/select URLs in PostgreSQL |
| **core**       | Config, DB session, Redis client |
| **schemas**    | Request/response validation (Pydantic) |
| **models**     | Table definition (SQLAlchemy ORM) |
| **utils**      | Pure helpers (Base62) |
