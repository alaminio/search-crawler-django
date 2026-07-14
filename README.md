# search-crawler-django

A tiny Django web app that scrapes DuckDuckGo search results and returns them as HTML or JSON.

## Features

- Search scraper via `requests` + `BeautifulSoup` (DuckDuckGo HTML endpoint)
- Clean dark UI (Tailwind CDN)
- JSON API endpoint (`/api/?search=<query>`) for programmatic use
- Env-driven configuration; no secrets in code
- WhiteNoise-based static file serving (no separate CDN needed)
- Test suite covering the scraper and views

## Requirements

- Python 3.10+
- pip

## Setup

```bash
git clone https://github.com/alaminio/search-crawler-django.git
cd search-crawler-django

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env — generate a new DJANGO_SECRET_KEY:
python -c "import secrets; print(secrets.token_urlsafe(50))"

python manage.py migrate
python manage.py runserver
```

Open http://localhost:8000.

## Endpoints

| Route          | Description                                             |
| -------------- | ------------------------------------------------------- |
| `GET /`        | HTML search UI                                          |
| `GET /api/`    | JSON: `{ query, results: [{title, url, snippet}] }`     |
| `GET /admin/`  | Django admin                                            |

Example:

```bash
curl "http://localhost:8000/api/?search=django"
```

```json
{
  "query": "django",
  "results": [
    { "title": "...", "url": "https://...", "snippet": "..." }
  ]
}
```

## Environment variables

See `.env.example`. Highlights:

- `DJANGO_SECRET_KEY` — required in production
- `DJANGO_DEBUG` — `true` in dev, `false` in production
- `DJANGO_ALLOWED_HOSTS` — comma-separated hostnames
- `DJANGO_CSRF_TRUSTED_ORIGINS` — comma-separated origins with scheme
- `DJANGO_SECURE_SSL_REDIRECT` — force HTTPS behind a TLS-terminating proxy
- `DJANGO_SECURE_HSTS_SECONDS` — HSTS max-age (set to `31536000` in production)

## Tests

```bash
python manage.py test
```

The scraper is mocked, so tests do not hit the upstream engine.

## Deployment

Any Python-friendly PaaS. Includes a `Procfile` for platforms that consume it (Railway, Fly.io, Render, etc.):

```
web: gunicorn search_engine.wsgi --log-file -
release: python manage.py migrate --noinput
```

Set the env vars from `.env.example` in the platform's dashboard. Set `DJANGO_DEBUG=false` and provide a real `DJANGO_SECRET_KEY`.

## Notes

- Scraping DuckDuckGo is a best-effort operation. If markup changes or requests are throttled, the scraper returns an empty list instead of crashing.
- This is a demo/learning project. For production search, prefer official APIs (Brave Search API, Bing Web Search API, etc.).

## License

MIT
