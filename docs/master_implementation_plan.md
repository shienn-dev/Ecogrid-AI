# Master Implementation Plan — EcoGrid AI

> Executable plan. Each phase is independently shippable and leaves `main` deployable.
> Stack remains **Flask + Vanilla JS (modular ES Modules) + SQLite** until Phase 6 review.
> No speculative AI/LLM work before Phase 6.

---

## Phase 0 — Patch & Stabilize (Foundation)

**Objective**: Make `main` green, close P1 bugs, eliminate XSS/cors/debug misconfig. Zero feature work.

**Features**
- Fix `KeyError: hours_per_day` on single-device path.
- Recalibrate `InsightService` scoring so heavy fixture → `Needs Improvement`.
- Escape `device_name` on backend (`html.escape`) and frontend (`textContent` vs `innerHTML` for user strings).
- Replace hardcoded `http://127.0.0.1:5000` with relative `/api/...` (or `window.__ECG_API_BASE` fallback).
- Gate `debug` via env (`FLASK_DEBUG` / `APP_ENV`).
- Add `MAX_CONTENT_LENGTH = 16KB`, limit `devices` array to 50 entries with 400 error.
- Align yearly constants: all services use `365` days; cost/carbon fallback uses `*365/30` not `*12`.

**Files Affected**
- `backend/app/routes/energy_routes.py:72-126` (attach watt/hours to single-device `devices_list`)
- `backend/app/services/insight_service.py:95-142` (tune deductions)
- `backend/app/__init__.py:7-15` (CORS origins, config, MAX_CONTENT_LENGTH, error handler)
- `backend/app.py:11-12` (env debug)
- `frontend/index.html:327,346,355` (API base), `index.html:422-476` (escape rendering)
- New: `backend/app/config.py`, `frontend/js/config.js` (tiny, <30 lines)

**Architecture Changes**
- Add `app/config.py` with `class Config: DEBUG, CORS_ORIGINS, MAX_CONTENT_LENGTH, DEFAULT_TARIFF, DEFAULT_EMISSION_FACTOR` loaded via `os.getenv` + `python-dotenv` (add `python-dotenv` to requirements).
- Add `@app.errorhandler(413)` + `@app.errorhandler(404)` returning JSON envelope.

**Dependencies**
- `python-dotenv` (new). No frontend deps.

**Tests**
- Regression: re-run existing 9 tests — must now ALL pass (fix expected `test_energy_calculate_single_success`, `test_energy_score_variations`).
- New unit: `test_xss_device_name` — POST `device_name="<img src=x onerror=alert(1)>"` → response escaped, no raw HTML.
- New unit: `test_device_limit_51` → 400, `test_max_content_length`.
- New unit: `test_yearly_consistency` — assert `yearly = daily*365` for cost/carbon single+multi.

**UI/UX Requirements**
- No visual change except API base fix must not break local dev (relative path works via Flask `app.run` + `Live Server` proxy note in README).

**Acceptance Criteria**
- `D:/Telkom_sch/Ecogrid-Ai/backend/venv/Scripts/python.exe -m pytest -q` → 13+ tests, 100% pass, exit 0.
- `curl -X POST /api/energy/calculate -d '{"device_name":"AC","watt":100,"hours_per_day":5}'` returns 200 with `energy_score`, no 500.
- No `innerHTML` injection of raw `device_name` (grep `innerHTML.*device_name` = 0).

**Potential Risks**
- Tuning score may still feel subjective → capture formula in comment and add tooltip in future UI, not blocking.

---

## Phase 1 — Config, Quality & Documentation Baseline

**Objective**: Portfolio-grade engineering hygiene — reproducibility, CI, docs.

**Features**
- `README.md` at repo root (run, test, env, architecture diagram).
- `pyproject.toml` / `requirements-dev.txt` with `pytest`, `pytest-cov`, `ruff`, `black`.
- `pytest` replaces `unittest` runner (keep `test_api.py` compatible), add `pytest.ini` + `coverage` gate 80%.
- Pre-commit (`ruff check`, `black --check`).
- GitHub Actions: `on: [push, pull_request]` → `python 3.11,3.12,3.14` × `pytest --cov`.
- `docs/Design.md` filled with token spec (colors, typography, spacing) — not UI code.
- `backend/app/utils/logger.py` minimal structured logging.

**Files Affected**
- New: `README.md`, `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `pytest.ini`, `backend/app/config.py` (if not done in P0), `backend/app/utils/logger.py`, `.env.example`
- Modified: `backend/requirements.txt` (pin via `pip-compile` or add `gunicorn`), `.gitignore` (add `.pytest_cache`, `.coverage`)
- Docs: `docs/Design.md` (replace 0-byte), `docs/agents.md` append Phase 0 entry

**Architecture Changes**
- No runtime arch change — purely DX.

**Dependencies**
- `pytest`, `pytest-cov`, `ruff`, `black`, `pre-commit` (dev only).

**Tests**
- CI must be green on `main` push. Coverage report artifact.

**UI/UX Requirements**
- None.

**Acceptance Criteria**
- `pip install -r requirements.txt && pytest --cov=app --cov-fail-under=80` passes.
- `README.md` contains: prerequisites, `python -m venv`, `pip install`, `flask run`, `pytest`, env vars table, project structure, known issues.
- GitHub Actions badge in README.

**Potential Risks**
- Pre-commit friction → make it optional (`pre-commit install` docs).

---

## Phase 2 — Design System & Frontend Modularization

**Objective**: Replace glassmorphism with enterprise design system and break monolith into maintainable modules. Biggest visual change.

**Features**
- **Design tokens** (`frontend/css/tokens.css`): Material 3 + IBM Carbon inspired — light theme default, dark via `prefers-color-scheme`. Colors: `surface, on-surface, primary #0f766e (teal-700), secondary #0e7490, accent #f59e0b (use sparingly), border #e5e7eb, success #059669, warning #d97706, danger #dc2626`. Spacing 4px scale, radius 8/12/16, shadow `shadow-sm/md`.
- Rewrite `style.css` from 846-line dark glass to token-driven light system. Remove `body::before/after` orb glows, remove `backdrop-filter`.
- **Modular JS**: Extract `index.html:180-534` inline script → `frontend/js/api/client.js` (fetch wrapper), `frontend/js/store/appStore.js` (tiny pub/sub), `frontend/js/components/{DeviceRow,RankingBar,InsightCard,KpiCard}.js`, `frontend/js/app.js` (bootstrap). Use ES Modules (`type="module"`).
- Implement **KPI cards** (4 cards: Daily kWh / Monthly kWh+Cost / Yearly kWh / Carbon) replacing table as primary hero. Table stays as secondary “Detailed Breakdown” collapsible.
- Improve **DeviceRow**: inline validation messages (not `alert`), `label for` + `id`, `aria-describedby`, numeric steppers, unit badges retained but refined.
- Delete dead `frontend/script.js`.
- Keep `frontend/css/` and `frontend/js/` as source of truth — no root `frontend/style.css` loose.
- **Navigation**: Add top nav bar (Logo left, “Dashboard | Analytics | Simulasi” — Analytics/Simulasi disabled with “Soon” badge for scaffolding).

**Files Affected**
- New: `frontend/css/tokens.css`, `frontend/css/components.css`, `frontend/css/layout.css`, `frontend/js/api/client.js`, `frontend/js/api/config.js`, `frontend/js/store/appStore.js`, `frontend/js/components/*.js`, `frontend/js/app.js`
- Modified: `frontend/index.html` (slim to ~120 lines, loads modules), `frontend/style.css` (refactored or split), `docs/Design.md` (token documentation)
- Removed: `frontend/script.js`

**Architecture Changes**
- Frontend adopts **Presentation / API / Store** separation. No build step — native ESM, keep deploy simple (Flask `send_from_directory` or static Nginx).
- API client centralizes `baseURL` (from `<meta name="api-base" content="/api">`), timeout via `AbortController` 8s, error normalization `{status,message}`.

**Dependencies**
- None (pure CSS/JS). Optional `lucide` icons via CDN (replace FontAwesome if desired, but keep FA if preferred).

**Tests**
- Frontend: Add `vitest` or `playwright`? Keep light: `vitest` for `client.js` + `store` unit tests (3 tests). `playwright` screenshot test for light theme render (optional, not gate).
- Manual: Lighthouse accessibility ≥90, contrast AA.

**UI/UX Requirements**
- Figma-equivalent spec (in `docs/Design.md`): card spec (padding 20px, radius 12, border 1px #e5e7eb, shadow-sm), typography scale (heading 24/20/16, body 14, label 12 uppercase tracking 0.05em), tabular numbers on kWh/cost (`font-variant-numeric: tabular-nums`), focus ring `2px solid #0f766e` offset 2px.
- KPI card spec: title 12px uppercase muted, value 28px semibold, subvalue 13px muted, accent left border 3px per metric color.
- Responsive: 1-col mobile (KPI stack), 2-col 768px, 3-col 1024px (KPI 4 spans 3). Device panel 1-col on mobile, 420px sticky left on desktop.

**Acceptance Criteria**
- No glassmorphism remnants (grep `backdrop-filter` =0, `::before` orb =0).
- `index.html` has no inline `<script>` >20 lines (only `importmap`/module tag).
- KPI cards render after calculate, values match table values (cross-check).
- `alert(` count =0 (all validation inline).
- Axe/Lighthouse a11y no critical errors.

**Potential Risks**
- Visual rewrite is largest diff — mitigated by Phase 0 stabilization first, do token → layout → components in sequence, PR per sub-step.

---

## Phase 3 — Dashboard, Analytics & Unified Calculation

**Objective**: Data-first dashboard that answers the 5 product questions in one glance, with charts.

**Features**
- **Unified endpoint**: Extend `POST /api/energy/calculate` to return `cost` + `carbon` inline (computed server-side) so frontend does single fetch (keep `/api/cost` and `/api/carbon` for backward compat but mark deprecated).
- **KPI wiring**: Wire 4 KPI cards to unified response (daily/monthly/yearly kWh, daily/monthly/yearly cost, daily/monthly/yearly CO2).
- **Charts**: `frontend/js/charts/` with `Chart.js 4.x` lazily imported (`await import('https://cdn.jsdelivr.net/npm/chart.js@4/+esm')` or local). 2 charts: (1) Device contribution horizontal bar, (2) Period comparison grouped bar (Daily/Monthly/Yearly × kWh). Carbon/cost as secondary toggles.
- **Ranking refinement**: Keep progress bars but add sort toggle, show absolute kWh + pct + estimated cost per device.
- **Insights polish**: Render insight cards with type-colored left border (already), add dismissible, add “What-if” slider (reduce top device -1/-2/-3h live preview).
- **Empty/Loading/Error states**: Skeleton loaders for KPI/charts, empty illustration with “Try sample: 2 devices” CTA that prefills, error card (not alert).

**Files Affected**
- Backend: `backend/app/routes/energy_routes.py:55-70` (inject CostService+CarbonService, return `cost:{daily,monthly,yearly}`, `carbon:{...}`), `backend/app/services/` unchanged.
- Frontend: `frontend/js/api/client.js` (single call), `frontend/js/components/KpiCard.js`, `frontend/js/charts/*.js`, `frontend/index.html` (add `<canvas id="chart-contribution">`, `<canvas id="chart-period">`).

**Architecture Changes**
- Service composition in route (route calls 3 services) — acceptable thin orchestration. Later extract `app/services/calculation_orchestrator.py` if logic grows.

**Dependencies**
- `Chart.js 4.x` (CDN ESM, no npm install required for vanilla).

**Tests**
- Backend: `test_energy_calculate_unified_includes_cost_carbon` — assert `data.cost.daily_cost == daily_kwh*1444.70`.
- Frontend: `vitest` chart data transformer unit tests (2 tests).

**UI/UX Requirements**
- Chart style: grid `#f3f4f6`, tick `#6b7280` 11px, bar radius 6, palette muted teal/cyan/amber/slate (no neon). Tooltip with tabular numbers. `prefers-reduced-motion` disables animation.
- KPI must be above fold on desktop; charts below ranking, insights rightmost column.

**Acceptance Criteria**
- Single POST to `/api/energy/calculate` returns 200 with `total_*`, `devices`, `ranked_devices`, `cost`, `carbon`, `energy_score`, `insights` — frontend uses only this one call (network tab shows 1 request vs prior 3).
- Charts render with correct data (visual check + data assertion).
- Lighthouse performance FCP <1.5s (chart lazy).

**Potential Risks**
- Chart.js ESM CDN may be blocked offline → provide local fallback `frontend/lib/chart.min.js` vendor.

---

## Phase 4 — Solar Potential Simulation (First “Simulation” Feature)

**Objective**: Deliver first simulation beyond calculator — solar — as specified in `feature.md:212-285`.

**Features**
- Backend: New `app/services/solar_service.py` with `calculate(roof_area, efficiency=0.20, sun_hours=4.5, tariff=1444.70)` → `{system_kwp, daily_generation, monthly_generation, estimated_saving, payback_years?}`. Formula: `system_kwp = roof_area * efficiency * 1.0` (kWp), `daily = system_kwp * sun_hours`, `monthly = daily*30`, `saving = monthly * tariff`. Add `POST /api/solar/simulate` validated (roof 1-1000 m², efficiency 0.05-0.30, sun 1-10).
- Frontend: New “Solar Potential” card/section below analytics, inputs (roof slider 10-200 m², efficiency select 15/18/20/22%, sun_hours location preset: Jakarta 4.5, Surabaya 5.0, etc.), result cards (kWp, daily/monthly, saving), mini “What-if roof +10m²” insight.
- Wire rule: if roof>30 → insight “Potensi baik untuk panel surya” (`feature.md:340-348` Rule 4).

**Files Affected**
- New: `backend/app/services/solar_service.py`, `backend/app/routes/solar_routes.py`, `frontend/js/components/SolarSimulator.js`, `frontend/css/solar.css` (or in components.css)
- Modified: `backend/app/__init__.py` (register `solar_bp`), `frontend/index.html` (new section), `backend/app/services/insight_service.py` (optional roof rule)

**Architecture Changes**
- New blueprint `/api/solar` — consistent with existing. No DB needed (stateless sim).

**Dependencies**
- None.

**Tests**
- `test_solar_simulate_success` — roof 40, eff 0.20, sun 4.5 → kWp 8.0, daily 36, monthly 1080.
- `test_solar_validation_roof_zero` → 400.
- Frontend: slider input validation unit test.

**UI/UX Requirements**
- Solar card: same KPI card language, icon `sun`, muted amber accent, illustration subtle. Inputs grouped, output in 2×2 grid. Mobile: inputs stacked, outputs 2-col.
- No cyber/solar-farm imagery — keep technical, data-first.

**Acceptance Criteria**
- `POST /api/solar/simulate` returns 200 with documented shape; `GET` docs in README.
- Frontend simulation updates live on input (debounced 300ms) without page reload.
- Saving formatted as Rupiah.

**Potential Risks**
- Formula oversimplification → document assumption clearly in UI footnote and service docstring.

---

## Phase 5 — Persistence & Historical Analytics

**Objective**: Unlock roadmap Phase 3 — save simulations, show history, enable analytics over time.

**Features**
- Backend: Add `SQLAlchemy` + `Flask-Migrate` (Alembic). `app/database/db.py` (`SQLAlchemy`), `app/models/simulation.py` (`id, created_at, total_daily_kwh, total_monthly_kwh, total_yearly_kwh, total_cost_monthly, total_carbon_monthly, devices_json, energy_score`). SQLite file `database/energy.db` (gitignored). Env `DATABASE_URL` (default `sqlite:///database/energy.db`).
- New endpoints: `POST /api/history` (save current calc), `GET /api/history?limit=20&offset=0` (list newest first), `GET /api/history/:id`, `DELETE /api/history/:id`. `POST /api/energy/calculate?save=true` convenience.
- Frontend: `frontend/js/store/historyStore.js` (localStorage cache + API sync), History panel (table of past runs: date, total monthly kWh, cost, score), click to reload inputs, “Clear history” with confirm. Charts: optional 7-day trend if ≥3 history entries.

**Files Affected**
- New: `backend/app/database/__init__.py`, `backend/app/database/db.py`, `backend/app/models/simulation.py`, `backend/app/repositories/simulation_repo.py`, `backend/app/routes/history_routes.py`, `backend/migrations/` (alembic), `frontend/js/store/historyStore.js`, `frontend/js/components/HistoryPanel.js`
- Modified: `backend/app/__init__.py` (init db, register history bp), `backend/requirements.txt` (SQLAlchemy, Flask-Migrate), `frontend/index.html` (history section), `frontend/js/api/client.js` (history methods)

**Architecture Changes**
- Introduces **Data Access layer** (`repositories/`) — routes never touch `db.session` directly. Services remain pure; repo is infrastructure. Prepares for Postgres switch.

**Dependencies**
- `SQLAlchemy==2.x`, `Flask-Migrate==4.x`, `alembic`.

**Tests**
- `test_history_crud` — POST save, GET list, GET id, DELETE.
- `test_history_pagination`.
- `test_calculate_with_save_true_creates_history` integration.

**UI/UX Requirements**
- History as collapsible “Riwayat” section below results, not primary hero. Empty history → illustration + “Belum ada riwayat”.
- Minimal chart for trend (line muted teal) only if data ≥3.

**Acceptance Criteria**
- `GET /api/history` returns 200 with array, persists across server restart (SQLite file).
- Frontend history survives page reload (API-backed; localStorage fallback if API down).
- Alembic migration applies cleanly on fresh clone (`flask db upgrade`).

**Potential Risks**
- SQLite file not present on first run → `db.create_all()` fallback in `create_app` for dev; migrations for prod. Document clearly.

---

## Phase 6 — AI Advisor Evolution (Rule → Predictive Prep)

**Objective**: Make “AI” in EcoGrid AI meaningful without premature LLM — harden rule engine, expose advisor API, prep for ML.

**Features**
- Extract standalone `POST /api/advisor/analyze` (`feature.md:289-361`, `system_architecture.md:290-323`) — accepts `{monthly_kwh, devices:[{name,hours}]}`, returns `{recommendations:[{type,icon,title,description}]}` reusing `InsightService` but decoupled from energy calc.
- Enhance `InsightService`: add 2 new rules from `feature.md` spec — (a) AC >8h → “Naikkan suhu 1-2°C”, (b) Lampu >10h → “Ganti LED”. Add carbon-aware tip if `monthly_co2 >100kg`.
- Add `GET /api/advisor/tips?device=ac` static tips library (JSON file `backend/datasets/tips.json` seeded from `project_idea.md` tips).
- Frontend: Advisor panel enhancement — group recommendations by `type` (danger first), show “Estimated saving” badge on what-if, add “Copy recommendations” button.
- **No LLM yet** — but add `app/integrations/llm_stub.py` with interface `generate(prompt)->str` returning mock, to show where LLM would plug in (documentation only).

**Files Affected**
- New: `backend/app/routes/advisor_routes.py`, `backend/app/services/advisor_service.py` (thin wrapper over InsightService + tips), `backend/datasets/tips.json`, `backend/app/integrations/llm_stub.py`
- Modified: `backend/app/services/insight_service.py` (2 new rules), `frontend/js/components/AdvisorPanel.js`, `docs/agents.md`

**Architecture Changes**
- Service split: `InsightService` stays core scoring; `AdvisorService` is façade for API + tip lookup. Prepares for future `ml_service.py` or `llm_service.py`.

**Dependencies**
- None (no LLM SDK yet).

**Tests**
- `test_advisor_analyze_ac_rule` — AC 12h → recommendation contains “suhu”.
- `test_advisor_analyze_lamp_rule`.
- `test_advisor_tips_by_device`.

**UI/UX Requirements**
- Recommendations remain cards with left-border color; group headers “Perlu Perhatian / Saran Efisiensi / Potensi Penghematan”.
- No chat widget yet — avoid generic AI chatbot aesthetic.

**Acceptance Criteria**
- `POST /api/advisor/analyze` works independently of `/api/energy/calculate` (can be called with arbitrary devices).
- Existing `energy/calculate` insights unchanged (backward compat).

**Potential Risks**
- Over-adding rules reduces signal → cap insights to 5 max, prioritize danger/warning.

---

## Phase 7 — Polish, Performance, Security & Deployment

**Objective**: Portfolio-ready polish — a11y, performance, security hardening, deploy.

**Features**
- **A11y**: `label for` on all inputs, `aria-live="polite"` on results, `role="status"` on toasts, keyboard nav for device rows (Enter to add), focus management, `aria-hidden` on decorative icons, color contrast AA audit fixes.
- **Performance**: Chart lazy-load, `requestAnimationFrame` for ranking bars, debounce device inputs, `Content-Encoding: gzip`, `Cache-Control` on static, `frontend` minified for prod (optional `esbuild` single bundle but keep dev ESM).
- **Security**: `CORS(app, origins=Config.CORS_ORIGINS)`, `Talisman` or `flask-cors` + headers (`X-Frame-Options`, `CSP` minimal), rate limit (`Flask-Limiter` 60/min per IP on `/api/*`), HTML escape audit, `gunicorn` prod entry.
- **Deployment**: `Dockerfile` (python:3.11-slim, gunicorn), `.dockerignore`, `docker-compose.yml` (app + optional postgres), `Procfile`/`render.yaml` example, env docs.
- **SEO/Meta**: `<meta name="description">` enriched, Open Graph tags, favicon set, `sitemap.xml` static.

**Files Affected**
- New: `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `gunicorn.conf.py`, `backend/app/middleware/rate_limit.py` (if added), `frontend/manifest.json`
- Modified: `backend/app/__init__.py` (security headers, limiter), `frontend/index.html` (meta, a11y attrs), all CSS/JS (perf tweaks)

**Architecture Changes**
- Add **Middleware layer** (rate limit, security headers) — clean separation.

**Dependencies**
- `gunicorn`, `Flask-Limiter` (or `slowapi` alternative), optional `Flask-Talisman`.

**Tests**
- `test_rate_limit_429` — 61st request in minute → 429.
- `test_security_headers_present`.
- Lighthouse CI: performance ≥90, a11y ≥95, best-practices ≥90.

**UI/UX Requirements**
- Final visual QA: compare against Stripe/Linear/Carbon refs — must feel “premium reliable”, not “AI template”. Spacing audit 4px grid, no orphans.
- Loading skeleton must match final layout size to avoid CLS.

**Acceptance Criteria**
- `docker build -t ecogrid . && docker run -p 5000:5000 ecogrid` serves app with `GET /` 200, `POST /api/energy/calculate` 200.
- `pytest` + `playwright` + `lighthouse --quiet` all pass in CI.
- No `alert()`, no `innerHTML` XSS, no `debug=True` in prod image.

**Potential Risks**
- Docker image size bloat → use slim, multi-stage not needed for portfolio.
- Rate limiter in-memory → note in docs that prod should use Redis for multi-instance.

---

## Execution Notes

- **Order is strict**: 0→1→2→3 before 4→5→6→7. Do not start Solar before unified calc is stable.
- **Branching**: `feat/phase-X-slug` per phase, PR to `main` after acceptance criteria met, CI green.
- **No framework migration** during phases 0-5. Framework decision gate only after Phase 5 review.
- **Documentation**: Each phase appends to `docs/agents.md` with date + decisions. `docs/Design.md` is source of truth for tokens.
- **Estimated effort** (solo portfolio): P0 2d, P1 2d, P2 7d, P3 5d, P4 3d, P5 5d, P6 3d, P7 4d → ~31 days (6 weeks) at 4h/day.

