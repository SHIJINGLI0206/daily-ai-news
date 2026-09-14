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
- `lib/services.ts` — typed `TrendService` interface plus a mock implementation. The UI can later swap this for a FastAPI-backed service without changing its components.
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

## Verification

```bash
npm run lint
npm run typecheck
npm run build
```

