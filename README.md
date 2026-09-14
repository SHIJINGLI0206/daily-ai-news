# AI Radar

AI Radar is a dark, reading-first knowledge dashboard for daily AI trend briefs. It turns ranked signals, model momentum, research, GitHub projects, and long-form media into a calm morning scan.

## Setup

```bash
npm install
cp .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The current release uses local TypeScript seed data, so the dashboard is usable without API credentials or a backend.

## Architecture

- `app/page.tsx` — client dashboard shell and lightweight interactions (search, filters, bookmarks, responsive navigation).
- `lib/types.ts` — shared domain types for trends, models, papers, repositories, and media.
- `lib/seed-data.ts` — safe, local seed content based on the September 2026 daily AI briefs.
- `lib/services.ts` — typed `TrendService` interface, mock implementation, and API client boundary.
- `backend/app/` — FastAPI ingestion API, public-source adapters, SQLite persistence, hotness ranking, and daily scheduler.
- `.github/workflows/deploy-pages.yml` — static GitHub Pages deployment for the frontend.
- `app/globals.css` — dark/night visual system and responsive layout, using Tailwind CSS v4 plus a small set of named component styles for the dense dashboard surfaces.

The visual language is inspired by current shadcn-style dashboard patterns: dark inset navigation, compact command/search header, KPI cards, ranked feed, and modular panels. The layout is intentionally typography-led for reading rather than a chart-heavy admin console.

## Planned backend integration

The intended production path is a Python/FastAPI service behind `NEXT_PUBLIC_API_BASE_URL`:

1. Scheduled ingestion gathers official lab blogs, Hugging Face trending models, GitHub repositories, arXiv papers, podcasts, and videos.
2. PostgreSQL stores normalized metadata, source history, deduplication keys, and user bookmarks.
3. Qdrant stores embeddings for semantic search, related-topic discovery, and “what changed?” retrieval.
4. Redis handles ingestion locks, cached ranking results, and short-lived feed responses.
5. A ranking pipeline scores recency, source quality, velocity, novelty, and user topic affinity while suppressing repeated stories unless there is a material update.

The browser must never receive provider API keys. Future credentials belong in the FastAPI deployment environment or a managed secret store. `.env*` files are ignored, with `.env.example` kept as the safe contract.

## Run the FastAPI service locally

```bash
cp backend/.env.example backend/.env
PYTHONPATH=backend uvicorn app.main:app --reload --port 8000 --env-file backend/.env
```

The API exposes `/health`, `/api/trends`, `/api/ingestion/status`, and `POST /api/ingestion/run`. By default the service schedules ingestion for 07:00 in `Pacific/Auckland`; set `AI_RADAR_INGESTION_ON_STARTUP=true` when you want one immediate run during local testing. The initial adapters use public RSS feeds plus public Hugging Face and GitHub endpoints; no API keys are required, though GitHub tokens can be added later for higher rate limits.

The ranking score is intentionally transparent: 25% freshness, 25% momentum, 20% novelty, 15% source quality, 10% cross-source corroboration, and 5% user affinity, minus a repeat penalty. Exact URL/title duplicates are removed before ranking, and engagement is used as a tie-breaker for model and repository momentum.

## Deploy the frontend to GitHub Pages

The repository includes a GitHub Actions workflow. Enable GitHub Pages in repository Settings → Pages with “GitHub Actions” as the source, then push to `main`. The workflow builds a static export and publishes it at:

`https://shijingli0206.github.io/daily-ai-news/`

GitHub Pages serves the local seed data unless `NEXT_PUBLIC_API_BASE_URL` is configured to point at a deployed FastAPI service.

## Verification

```bash
npm run lint
npm run typecheck
npm run build
PYTHONPATH=backend pytest -q backend/tests
```
