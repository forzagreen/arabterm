# arabterm website

Static site for [arabterm.db](../arabterm.db), deployed to <https://forzagreen.github.io/arabterm/>.

## Stack

[Astro](https://astro.build/) static site generator. The build reads `arabterm.db` directly via `better-sqlite3` and emits one HTML page per dictionary (paginated 1000 terms / page), plus a per-dictionary JSON download. No data is checked in; everything is derived from the DB at build time.

## Commands

```sh
npm install            # install deps
npm run dev            # local dev server at http://localhost:4321/arabterm/
npm run build          # static build into ./dist/
npm run preview        # serve ./dist/ for verification
```

## Layout

| Path | Purpose |
|---|---|
| `src/lib/db.ts` | SQLite reader and legacy-slug map |
| `src/layouts/BaseLayout.astro` | RTL Arabic shell, GA tag, header/footer |
| `src/pages/index.astro` | Home — lists all 53 dictionaries |
| `src/pages/about.astro` | Project description |
| `src/pages/[dict]/index.astro` | Dictionary page 1 + redirect handler for legacy unprefixed slugs |
| `src/pages/[dict]/page/[page].astro` | Paginated terms (page 2..N) |
| `src/pages/[dict]/terms.json.ts` | Per-dictionary JSON download |

## Legacy URLs

The original site used unprefixed slugs (e.g. `/water_engineering/`). These now redirect to the canonical `name_tech` URL (`/at_water_engineering/`). The map lives in `LEGACY_SLUGS` in [src/lib/db.ts](src/lib/db.ts).

## Deployment

Pushed to `main` triggers [`.github/workflows/gh-pages.yml`](../.github/workflows/gh-pages.yml), which runs `npm run build` and uploads `website/dist/` to GitHub Pages.
