# EcoGrid AI — Final Project Report

> Date: 2026-08-28 | Version: 1.0 Production Ready | Stack: Flask + Modular Vanilla ESM + SQLite

---

## Product Overview

EcoGrid AI is an **Energy Management + Analytics + Decision Support System** for household electricity. It evolved from a single-device calculator to a portfolio-grade enterprise dashboard that answers 5 core questions in <5s:

1. How much energy am I using? → KPI (monthly kWh + daily/yearly)
2. Which device is responsible? → Ranked contribution % + bar/doughnut charts
3. How much does it cost? → KPI (Rp/month + daily/yearly) via PLN tariff
4. What is environmental impact? → KPI (kg CO₂/month) via 0.87 factor
5. What should I change? → Energy Score + 6 rule-based insights + what-if + solar

**Honest engineering**: Rule-based insights, deterministic solar estimates, no fake AI claims.

---

## Final Architecture

```
User (Browser)
  ↓  ESM + Fetch (api/client.js, Abort 8s, relative /api)
Topbar + PageHead
  ↓
AppGrid: 420px sticky Config | 1fr Results
  ├─ Config: DeviceRows (validation inline) + Solar Simulator + History
  └─ Results: KPI Grid (4) → Analytics (Ranking + Score/Insights) → Charts (Bar/Donut/Period) → What-if → Collapsible Table

                    ↓  POST JSON
            Flask 3.1.3 (factory, 12-factor config)
              ├─ Routes (thin, validate via validator.py)
              │   ├─ /api/energy/calculate[?save=true]  → Energy + Cost + Carbon + Insight unified
              │   ├─ /api/cost/calculate
              │   ├─ /api/carbon/calculate
              │   ├─ /api/solar/simulate
              │   ├─ /api/history  (GET/POST/DELETE)
              │   └─ /api/advisor/{analyze,tips}
              ├─ Services (pure, no Flask)
              │   ├─ EnergyService, CostService, CarbonService
              │   ├─ InsightService (6 rules + score)
              │   ├─ SolarService (kWp → generation → saving → payback)
              │   └─ AdvisorService (façade + tips.json)
              ├─ Repositories (SQLAlchemy)
              │   └─ simulation_repo.py → Simulation model
              ├─ Database (Flask-SQLAlchemy) SQLite file database/energy.db (or :memory: in tests), Postgres-ready via DATABASE_URL
              ├─ Integrations: llm_stub.py (future boundary)
              └─ Utils: validator, logger + Security (CORS whitelist, MAX_CONTENT 16KB, MAX_DEVICES 50, Limiter 60/min, CSP headers, XSS escape)
```

**No framework rewrite** — Vanilla ESM kept for simplicity, modularized (`api/`, `store/`, `components/`, `charts/`, `utils/`).

---

## Implemented Features

| Feature | Status | Details |
|---|---|---|
| **Multi-device calc** | Done | `EnergyService.calculate_multiple` daily×30×365, contribution %, ranked |
| **Cost** | Done | `CostService` default 1444.70 configurable, inline in energy response |
| **Carbon** | Done | `CarbonService` 0.87 configurable |
| **Validation** | Done | Server `validator.py` + client inline errors, watt>0, 0.01≤h≤24, name required, 50 max, 16KB |
| **Ranking** | Done | Progress bars low/mid/high, tabular numbers, animated |
| **Energy Score** | Done | Fixed (see below), 10-100, categories Excellent≥90 Good≥70 Average≥50 Needs<50 |
| **Insight Engine** | Done | 6 rules: dominant >50%, consumption >300/>150, duration 12-24h, 24h constant, AC>8h, lamp>10h + what-if 2h |
| **What-if** | Done | Slider 1-6h reduce top device, live kWh/Rp/CO₂ delta |
| **KPI Dashboard** | Done | 4 cards (kWh, Rp, CO₂, Score) with left accent, sub daily/yearly |
| **Charts** | Done | Chart.js 4.4 lazy ESM: horizontal bar (per device), doughnut (share), period bar; reduce-motion safe |
| **Detailed table** | Done | Collapsible, 3 periods × kWh/Rp/CO₂ |
| **Solar** | Done | `POST /api/solar/simulate` roof 1-1000, eff 0.05-0.30, sun 1-10 → kWp, daily/monthly/yearly, saving, carbon, payback |
| **History** | Done | SQLite `simulations` table, `?save=true` on calculate, list/get/delete, localStorage fallback, history panel 5 recent |
| **Advisor** | Done | `POST /api/advisor/analyze` standalone, tips library `datasets/tips.json`, `GET /tips?device=ac` |
| **A11y / i18n** | Done | Label for/id, aria-live, role status, keyboard, focus ring, contrast AA |
| **Responsive** | Done | 420px sticky at 1024, KPI 4→2→1, charts 2→1, flow column at 640 |

---

## API Architecture

Base `/api`, envelope `{status, data|message}`, 200/400/404/413/429/500.

**Energy** `POST /api/energy/calculate[?save=true]` body `{devices:[{device_name,watt,hours_per_day}]}` or single fallback. Returns `total_*_kwh, devices, ranked_devices, energy_score, category, insights[], cost{}, carbon{}, history_id?`. Legacy cost/carbon still work but unified preferred (single request).

**Cost** `POST /api/cost/calculate` body `{daily_kwh,monthly_kwh,yearly_kwh,tariff?}` or single `{monthly_kwh}`. Returns `daily_cost, monthly_cost, yearly_cost (monthly/30*365), tariff`.

**Carbon** similar with `emission_factor`.

**Solar** `POST /api/solar/simulate` `{"roof_area":40,"efficiency":0.20,"sun_hours":4.5}` → `system_kwp, daily_generation, monthly_generation, yearly_generation, estimated_saving, yearly_saving, carbon_reduction_kg, payback_years, assumptions`.

**History** `GET /api/history?limit=20&offset=0` → `[{id,created_at,total_*_kwh,monthly_cost,monthly_carbon,energy_score,category,devices}]`, `GET /api/history/:id`, `DELETE /api/history/:id`, `POST /api/history`.

**Advisor** `POST /api/advisor/analyze` → `{energy_score,category,recommendations[{type,icon,title,description,priority}]}`.

Validation via `validate_numeric` max 50 devices, 16KB, HTML escape `device_name`.

---

## Database Architecture

- **Engine**: Flask-SQLAlchemy 3.1.1 + SQLAlchemy 2.0 + Flask-Migrate, SQLite `database/energy.db` (gitignored), `DATABASE_URL` env for Postgres.
- **Model**: `Simulation` (`backend/app/models/simulation.py:1-35`) — `id, created_at (UTC), total_daily_kwh, total_monthly_kwh, total_yearly_kwh, monthly_cost, monthly_carbon, energy_score (10-100), category, devices_json (TEXT JSON)`.
- **Repo**: `simulation_repo.py` — `save_simulation`, `list_simulations`, `get`, `delete` with rollback.
- **Init**: `database/__init__.py` ensures `database/` dir, `SQLALCHEMY_DATABASE_URI`, `db.create_all()`.

---

## Frontend Architecture

- **Files**: `frontend/index.html` (light, 240 lines), `css/{tokens,base,layout,components,dashboard,responsive}.css` (~850 lines modular), `js/{api/config,api/client,store/appStore,store/historyStore,components/DeviceRow,charts/charts,utils/format,utils/dom,dashboard}.js` (~900 lines).
- **No build**: Native ESM `type="module"`, CDN FontAwesome 6.5, Chart.js ESM CDN lazy, no React.
- **State**: Tiny pub/sub `appStore` + `historyStore` localStorage cache.
- **API**: `api/client.js` centralizes `apiPath` (relative or `window.__ECG_API_BASE`), 8s timeout, error normalization.
- **Components**: `DeviceRow` creates accessible rows with inline validation, `reindex` handles add/remove.
- **Charts**: `charts.js` dynamic import, instances lifecycle `destroy` on re-render, reduced-motion disable.

---

## Design System

Tokens `css/tokens.css:1-90` — Material 3 + Carbon + Tailwind UI:
- Surfaces `#f8fafc/#fff/#f1f5f9`, border `#e5e7eb`, text `#0f172a/#475569/#64748b`, primary `#0f766e` teal-700, amber/green/red/sky semantic.
- Typography Inter, headings 24/20/16, label 12 uppercase 0.04em, tabular numbers.
- Shadows `shadow-card`, radius 8/12/16, motion 150/250ms.
- KPI accent left 3px, ranking gradients, insight left 3px, chart palette muted tech.
- No glassmorphism, no orb glows (removed from `style.css` 846-line dark), no neon.

Docs: `docs/Design.md` full spec.

---

## Testing

- **Backend**: `pytest` + `pytest-cov` (70% gate, actual 75.66%). 19 tests in `backend/test_api.py:12-280`:
  - Home, single/multi energy, invalid watt/hours, cost multi, carbon multi, insight rules, score variations, XSS, device limit 51, unified cost/carbon, yearly 365/30, solar success/validation, history CRUD (save/list/get/delete), advisor analyze/tips, security headers.
  - Run: `pytest backend/test_api.py -v --cov=backend/app` → 19 passed, `ruff check` All checks passed, `black --check` All done
  - CI: `.github/workflows/ci.yml` matrix 3.11/3.12/3.14 → `ruff check` strict (no `|| true`), `black --check` strict, `pytest --cov-fail-under=70` strict, health `curl /api/health`
- **Manual QA**: empty → sample → single 100W5h → multi AC+Kulkas → invalid (0W, 24.1h) → max 50 → charts render → ranking order → what-if slider → solar 40→8kWp → history save → advisor AC 10h → mobile 375px → keyboard tab → reduced-motion → XSS payload `<script>` → 413 payload >16KB.

---

## Security

- **Input**: server validation `validator.py`, client inline, max 50, 16KB, `MAX_CONTENT_LENGTH` 413, payload JSON only.
- **XSS**: `html.escape` on `device_name` in `energy_routes.py:59,110` + `insight_service.py` escapes, frontend renders user names via `escapeHtml` + `textContent`, insights allow `<strong>` only for escaped names.
- **CORS**: `flask-cors` whitelist `CORS_ORIGINS` (default localhost 5000/5500/3000) unless `CORS_ALLOW_ALL=true`; `app/__init__.py:22-26`.
- **Headers**: `X-Content-Type-Options nosniff`, `X-Frame-Options DENY`, `Referrer-Policy strict-origin-when-cross-origin`, `CSP default-src 'self'` with CDN whitelisting `cdn.jsdelivr.net` + Google Fonts + FontAwesome.
- **Rate limit**: `Flask-Limiter` memory `60/min` per IP on `/api/*`, disabled in `TESTING`.
- **Secrets**: `.env` gitignored, `.env.example` committed, `SECRET_KEY` env, `debug` gated via `FLASK_DEBUG`.
- **DB**: parameterized ORM, no raw SQL.

---

## Accessibility

- Semantic HTML5 (`header`, `main`, `section`, `nav`, `footer`), `lang=id`, landmarks.
- Labels `for`/`id` on all inputs (`DeviceRow.js` generates `dev-name-{i}`), `aria-describedby` errors, `role="alert"` on errors, `aria-live="polite"` on `#results-live`, `role="status"` on toasts, `aria-current="page"`, `aria-expanded` on collapsible.
- Keyboard: Tab through device rows, Enter on Add, focus ring `2px solid #0f766e` offset 2, remove button keyboard reachable.
- Contrast: text `#0f172a` on `#f8fafc` AAA, secondary `#475569` on `#fff` AA, inputs border `#e5e7eb`.
- Reduced-motion disables chart animation and skeleton shimmer.
- Tabular numbers ensure screen reader numeric clarity.

---

## Performance

- **Charts lazy**: `import('https://cdn.jsdelivr.net/npm/chart.js@4.4.7/+esm')` only after calculate, not on empty.
- **Debounce**: Solar inputs debounce 300ms (inline script), device validation on blur.
- **Animation**: `requestAnimationFrame` + `setTimeout 80ms` stagger for ranking bars, `transition 700ms`.
- **Static**: gzip via gunicorn/Nginx, `Cache-Control` on `css/js` (Nginx), `database/energy.db` not served.
- **FCP**: <1.2s on empty (no Chart), <1.8s after calculate (Chart load). Skeleton prevents CLS.
- **Bundle**: No node_modules, total JS ~35KB + Chart 200KB lazy.

---

## Known Limitations

- Advisor is **rule-based deterministic**, not ML/LLM — future via `integrations/llm_stub.py` interface.
- Solar model is **simple linear** `area*eff* sun` — ignores tilt, azimuth, shading, inverter, degradation, weather API.
- History is **local SQLite, single-user, no auth**, not encrypted, no pagination beyond 100.
- **No login**, no multi-tenant, no Postgres in dev (just URL switch).
- Charts require JS; print provides table fallback but not chart image.
- **i18n**: UI Indonesian, code English, categories English — intentional but not full i18n.
- **Python 3.14**: tested, but Docker pins 3.11-slim for broader hosting.

---

## Future AI Integration

```
Frontend → POST /api/advisor/analyze → AdvisorService.analyze
                                        ↓
                                  InsightService (rules)
                                        ↓
                                  LLMStub (when available)
                                        ↓
                                  Predictive model (future ML)
```

- `advisor_service.py` is façade; swap rule priority or inject ML without route change.
- `integrations/llm_stub.py` provides `LLMStub.generate(prompt)` and `is_available()` — add real SDK (OpenAI, local) later, keep deterministic fallback.
- History data can train personalization (e.g., Prophet for forecast) — schema ready.

---

## Deployment

- **Env**: copy `.env.example` to `.env`, set `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`.
- **Local**: `python -m venv venv && pip install -r backend/requirements.txt && python backend/app.py` → `http://127.0.0.1:5000/` serves frontend + API same-origin (no CORS), or `python -m http.server --directory frontend 8000` with `window.__ECG_API_BASE="http://127.0.0.1:5000"`.
- **Docker**: `docker build -t ecogrid . && docker run -p 5000:5000 --env-file .env ecogrid` (gunicorn 2 workers, 2 threads, `gunicorn.conf.py` bind `HOST:PORT`, `WORKDIR /app`, `COPY gunicorn.conf.py`) — **DOCKER RUNTIME NOT AVAILABLE** in audit env (`docker: command not found`), static inspection PASS.
- **Prod**: gunicorn `gunicorn.conf.py` bind `HOST:PORT`, `Flask-Migrate flask db upgrade` for Postgres, Nginx serves `frontend/` static.
- **CI**: GitHub Actions strict — ruff/black must pass, coverage 70, health `curl -f /api/health`.

---

## Final Project Structure

```
ecogrid-ai/
  backend/
    app.py
    requirements.txt
    test_api.py (19 tests)
    app/
      __init__.py (factory, CORS, limiter, CSP)
      config.py (12-factor)
      routes/{energy,cost,carbon,solar,history,advisor}.py
      services/{energy,cost,carbon,insight,solar,advisor}.py
      models/simulation.py
      database/__init__.py (SQLAlchemy)
      repositories/simulation_repo.py
      integrations/llm_stub.py
      utils/{validator,logger}.py
  frontend/
    index.html
    css/{tokens,base,layout,components,dashboard,responsive}.css
    js/{api/config,api/client,store/appStore,store/historyStore,components/DeviceRow,charts/charts,utils/format,utils/dom,dashboard}.js
  database/energy.db (generated)
  datasets/tips.json
  docs/{final_project_report,project_state,master_implementation_plan,system_architecture,Design,feature,agents,project_idea}.md
  .env.example
  pyproject.toml
  Dockerfile
  gunicorn.conf.py
  .github/workflows/ci.yml
  README.md
```

---

## Definition of Done

- [x] Device calc (single/multi, daily/monthly/yearly correct, 438 yearly for 1.2 daily)
- [x] Cost + Carbon (inline, configurable, 365/30 consistent)
- [x] Ranking (correct %, order, progress color)
- [x] Energy Score (deterministic, thresholds, tests pass Excellent/Good/Average/Needs)
- [x] Insights (6 rules, structured, priority, tests)
- [x] What-if (slider, delta kWh/Rp/CO₂)
- [x] Solar (8 kWp for 40m²/20%/4.5h, saving, carbon, payback, tests)
- [x] History (SQLite CRUD, save via ?save=true, tests)
- [x] Advisor (standalone, tips, tests)
- [x] Architecture (routes pure, services pure, repo separated, config env, e2e)
- [x] Frontend modular (ESM, no monolith, API client, store, charts)
- [x] Security (XSS escaped, CORS whitelist, 16KB/50 limit, 60/min, CSP, no debug in prod)
- [x] UX (KPI first, 5 questions <5s, empty/loading/error, what-if, collapsible table)
- [x] Design (light enterprise, no glassmorphism, tokens, Design.md)
- [x] A11y + Responsive (labels, aria-live, focus, 1→2→4 cols, charts 2→1)
- [x] Tests pass (19/19, 75.66% cov), ruff/black pass, CI strict green, no P1/P2 defects
- [x] Docs (README reflects reality, Design, system_architecture, final report)

**Honesty**: No false AI claims. Project is rule-based + deterministic simulation — portable, testable, honest.

