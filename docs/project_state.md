# Project State — EcoGrid AI

> Generated: 2026-08-28 | Auditor acting as Senior Engineer / Architect / Product / UI-UX Lead  
> Evidence-based audit. All claims reference actual source files. No invention.

---

## 1. Current Architecture

### 1.1 High-Level Overview

```
User (Browser)
  ↓  HTTP POST JSON  (hardcoded http://127.0.0.1:5000)
Vanilla HTML/CSS/JS  (frontend/index.html:180-534 inline <script>)
  ↓  Fetch API (Promise.all for cost+carbon)
Flask 3.1.3  (backend/app/__init__.py:7 create_app factory)
  ├─ Blueprint: /api/energy  → backend/app/routes/energy_routes.py:6
  ├─ Blueprint: /api/cost    → backend/app/routes/cost_routes.py:5
  └─ Blueprint: /api/carbon  → backend/app/routes/carbon_routes.py:5
        ↓  calls
  Services (stateless pure functions):
    EnergyService  → backend/app/services/energy_service.py:1
    CostService    → backend/app/services/cost_service.py:1
    CarbonService  → backend/app/services/carbon_service.py:1
    InsightService → backend/app/services/insight_service.py:1
        ↓  returns
  JSON Response (no persistence layer)
```

No database, no ORM, no repository layer, no external services, no AI services. Completely stateless request/response calculator.

### 1.2 Backend Detail

- **Framework**: Flask 3.1.3 + flask-cors 6.0.5 (`backend/requirements.txt:4-5`), Werkzeug 3.1.8, Jinja2 3.1.6 — Flask is listed but Jinja2 templating is unused (API-only).
- **Entry point**: `backend/app.py:7-9` imports `create_app` and runs `app.run(debug=True, host="127.0.0.1", port=5000)` — debug always on, host bound to localhost only.
- **Factory**: `backend/app/__init__.py:7` creates Flask app, enables global CORS (`CORS(app)` with no origin whitelist), registers 3 blueprints with `/api/energy`, `/api/cost`, `/api/carbon` prefixes, exposes `/` health check.
- **Routing layer**: Thin controllers that validate input via `validate_numeric` (`backend/app/utils/validator.py:1`) then delegate to services. No middleware, no error handlers, no request logging, no rate limiting.
- **Service layer**: Cleanly separated business logic — each service is a class with `@staticmethod` methods. No dependency injection, no interfaces.
- **Config**: No config file, no `.env` handling, no environment variable usage. Constants hardcoded inside services (tariff `1444.70`, emission `0.87`).
- **Python version**: `backend/venv/pyvenv.cfg` indicates 3.14.5 but no `runtime.txt` or `pyproject.toml` pinning.

### 1.3 Frontend Detail

- **Stack**: Vanilla HTML5 + CSS3 + Vanilla JS, no bundler, no framework, no package.json. `frontend/index.html:1-537` is a single monolithic file (HTML + inline `<script>` 350+ lines DOM manipulation).
- **Folders `frontend/css/` and `frontend/js/`**: Both empty (verified via `ls`/`read` dir — 0 entries) despite `docs/system_architecture.md:94-100` documenting `api.js`, `dashboard.js`, `charts.js` there.
- **Orphan file**: `frontend/script.js:1-27` is dead legacy single-device calculator (never imported by `index.html` — `index.html:12` links only `style.css`).
- **Styling**: Single `frontend/style.css:1-846`, 846 lines, single global stylesheet. Uses CSS variables (`:root` at line 4), Glassmorphism (`backdrop-filter: blur(16px)` at line 151), glowing orb pseudo-elements (`body::before` line 41).
- **No component system**: Repeater built by string-interpolated `innerHTML` (`index.html:191`), no templating, no state library.
- **API integration**: Hardcoded `fetch('http://127.0.0.1:5000/api/...')` at `index.html:327`, `index.html:346`, `index.html:355` — breaks in any non-local environment. No abstraction layer, no error retry, no timeout.

### 1.4 Data & Persistence

- **Current**: No database. `datasets/` empty, `.gitignore:4` ignores `*.db` but no DB file exists, no `models/` folder, no `database/` folder despite `docs/system_architecture.md:116-121` prescribing `database/db.py` and `models/device.py`.
- **In-memory only**: Multi-device list lives only in JS memory; page refresh loses all data. No localStorage, no sessionStorage, no IndexedDB.
- **Schema**: None implemented. Documented schema in `docs/system_architecture.md:328-351` (`devices`, `simulations` tables) is entirely unimplemented.

### 1.5 Documentation vs Reality Gap

| Documented | Actual |
|---|---|
| `frontend/css/style.css`, `frontend/js/api.js` etc. (`docs/system_architecture.md:92-100`) | Empty dirs, single `style.css` at root `frontend/` |
| SQLite DB, `database/db.py`, `models/` (`docs/project_idea.md:135-145`) | Does not exist |
| Chart.js (`docs/project_idea.md:134`, `system_architecture.md:46`) | Not installed, not imported, no `<canvas>` element |
| Solar/Wind simulators (`docs/feature.md:212-276`) | No routes, no services |
| `dashboard.html` (`docs/project_idea.md:140`) | Does not exist |
| `docs/Design.md` | 0 bytes — empty file |
| `docs/agents.md` claims phases 1-1.4 complete | Partially true — but contains untested bugs (see §7) |

### 1.6 File Inventory (non-venv)

```
backend/app.py
backend/app/__init__.py
backend/app/routes/{energy,cost,carbon}_routes.py
backend/app/services/{energy,cost,carbon,insight}_service.py
backend/app/utils/validator.py
backend/requirements.txt
backend/test_api.py
frontend/index.html
frontend/style.css
frontend/script.js  (dead)
docs/{agents,feature,project_idea,system_architecture}.md
```

---

## 2. Current Features

Verified against source, not docs.

| Feature | Status | Evidence |
|---|---|---|
| **Single-device energy calc** (W×H/1000 → daily/monthly/yearly) | **COMPLETE** | `energy_service.py:3-19`, `energy_routes.py:72-126` fallback branch. Works but buggy (see §4). |
| **Multi-device calc + contribution % + ranking** | **COMPLETE** (buggy) | `energy_service.py:22-81`, `energy_routes.py:13-70`. `calculate_multiple` correctly computes pct and `sorted(ranked_devices)`. Frontend repeater `index.html:183-272` adds/removes rows, `hitungEnergi:282-312` gathers devices. |
| **Cost calculation multi-period** | **COMPLETE** | `cost_service.py:14-24`, `cost_routes.py:8-41` supports `daily/monthly/yearly_kwh` + optional tariff. Frontend `index.html:345-364` calls in parallel. |
| **Carbon calculation multi-period** | **COMPLETE** | `carbon_service.py:14-24`, `carbon_routes.py:12-41`. Default factor 0.87. |
| **Strict validation (name, watt>0, 0<hours≤24)** | **COMPLETE** | `validator.py:1-20`, enforced in `energy_routes.py:23-47` and frontend `index.html:292-304`. Dual validation present. |
| **Results table (Harian/Bulanan/Tahunan × kWh/Biaya/CO2)** | **COMPLETE** | `index.html:62-94` table + `index.html:384-403` population. |
| **Device ranking + progress bar (color: low/med/high)** | **COMPLETE** | `index.html:97-105` + `index.html:405-437` rendering, CSS `style.css:528-605` with `.progress-high/medium/low`. |
| **Energy Score (10-100) + category (Excellent/Good/Average/Needs Improvement)** | **COMPLETE** (logic flawed) | `insight_service.py:107-142` scoring. Display `index.html:109-114` + `index.html:440-458`. Badge colors `style.css:660-683`. |
| **Rule-based Insight Engine (4 rules + what-if)** | **COMPLETE** | `insight_service.py:31-105` structured cards `{type,icon,title,description}`. Rendered `index.html:118-125` + `index.html:460-488`. |
| **Add/Remove device rows + disabled delete when 1 left** | **COMPLETE** | `index.html:183-272`, `updateRemoveButtonsVisibility:260-272`. |
| **Energy Flow visualization (Rumah→Total→Perangkat→Biaya→CO2→Insight)** | **COMPLETE** (static) | `index.html:137-174`, CSS `style.css:768-825` flex desktop → 3×2 grid mobile. No interactivity, purely decorative. |
| **Tip box (contextual tip based on most wasteful device)** | **COMPLETE** | `index.html:128-135` + `index.html:490-512`. String matching on device name. |
| **Placeholder empty state before calculation** | **COMPLETE** | `index.html:49-53` + `style.css:268-301`. |
| **Loading state on button** | **COMPLETE** | `index.html:322-323` spinner + disabled. |
| **Responsive side-by-side layout (460px + 1fr @992px)** | **COMPLETE** | `style.css:140-145` + `style.css:83-87`. Mobile stacked. |

---

## 3. Missing Features

Against `docs/feature.md` v1.0, `docs/project_idea.md`, and target hierarchy (Dashboard → Metrics → Analytics → Ranking → Insights → etc.):

| Missing | Documented Where | Impact |
|---|---|---|
| **Solar Panel Simulator** (roof area, efficiency, peak sun → kWp, generation, saving) | `feature.md:212-285`, `system_architecture.md:258-286`, `project_idea.md:55-64` | Roadmap Phase 4 — not started. No `solar_service.py`, no `/api/solar/simulate`. |
| **Wind Turbine Simulator** | `project_idea.md:65-70` | Not started. |
| **Historical Analytics / Persistence** | `feature.md:441-448`, `project_idea.md:96-102`, `system_architecture.md:343-351` simulations table | No DB, no `GET /api/history`, no charts over time. Zero persistence. |
| **Charts (Energy/Cost/Carbon)** | `feature.md:419-437`, `system_architecture.md:43-47` Chart.js, `system_architecture.md:446-448` dashboard layout | No `<canvas>`, no Chart.js import, no `charts.js`. Dashboard spec not implemented. |
| **Tariff configurability by user** | `feature.md:136-142` | Tariff hardcoded `1444.70` in `cost_service.py:3`, frontend never sends custom `tariff_per_kwh`. Route supports it but UI does not expose it. |
| **Emission factor configurability** | `feature.md:179-185` | Same — hardcoded `0.87`, UI not exposed. |
| **Authentication / User profile / Login** | `feature.md:441-443`, `system_architecture.md:469` | Not started, no session, no JWT. |
| **Dashboard with KPI cards (Daily/Monthly/Yearly separate cards)** | `feature.md:364-417`, task target hierarchy | Current shows one table, not four KPI cards. Not data-first hierarchy. |
| **Device Configuration CRUD (edit, save, templates)** | Target direction `Detailed Analytics → Device Configuration` | Only ephemeral add/remove, no edit-in-place, no device presets. |
| **Weather / Solar Irradiance API** | `feature.md:445-446`, `system_architecture.md:477` | Not started. |
| **LLM / ML Advisor (beyond rule-based)** | `feature.md:288-361`, `project_idea.md:125-131` | Intentionally deferred — correctly not implemented. Architecture leaves room. |
| **Mobile App, Smart Meter, IoT** | `feature.md:444-448`, roadmap Phases 5-7 | Out of scope for now — correctly not started. |

---

## 4. Technical Debt

### 4.1 Bugs (Verified by Execution)

- **P1 — Single-device Insight Crash** `backend/app/routes/energy_routes.py:103-108` + `insight_service.py:95`  
  Single-device fallback builds `devices_list = [result]` where `result` from `EnergyService.calculate` lacks `watt`, `hours_per_day`. `InsightService.generate_insights` accesses `top_device["hours_per_day"]` at line 95 → `KeyError`. Reproduced: `test_energy_calculate_single_success` → ERROR (run `D:/Telkom_sch/Ecogrid-Ai/backend/venv/Scripts/python.exe backend/test_api.py` 2026-08-28: `FAILED (failures=1, errors=1)`). Frontend always uses multi-device path so bug hidden in production, but API contract broken for any single-device caller.

- **P1 — Energy Score Under-penalization** `insight_service.py:112-129`  
  Test `test_energy_score_variations` expects heavy scenario (AC 1200W 12h 432 kWh + Heater 1500W 5h 225 kWh, total 657 kWh) → `Needs Improvement` (<50). Actual score computes to ~ `Average` (≥50). Deduction caps (`min(30, ...)`, `min(20, ...)`) too lenient vs spec. Fix requires recalibrating weights.

- **P2 — Inconsistent yearly calculation constant**  
  `energy_service.py:13` uses `×365`, `cost_routes.py:69-72` fallback uses `×12` on monthly figure (360 days), `carbon_routes.py:69-72` same. Mixed year definitions (365 vs 360).

### 4.2 Architecture & Maintainability

- **Monolithic frontend**: `index.html:1-537` mixes markup, style link, and 350 lines of imperative JS. No modules (`frontend/js/` empty), no `api.js` abstraction, violates separation `Presentation / API / Business Logic`. Hard to test, reuse, or scale. Duplicated rupiah formatter, duplicated fetch logic.
- **Hardcoded API base URL**: `index.html:327,346,355` — `http://127.0.0.1:5000` baked in 3 places. No config, breaks under reverse proxy, Docker, or production host.
- **No environment/config management**: No `config.py`, no `.env`, no `app.config.from_object`. Secrets/constants inline. `app.py:12` `debug=True` hardcoded (should be env-driven).
- **No error handling middleware**: No `@app.errorhandler`, no 404/500 JSON envelopes, no centralized logging. Errors leak raw Flask HTML in edge cases.
- **No database layer**: Roadmap Phase 3 requires history, but zero scaffolding exists. Will need migration path.
- **Dead code**: `frontend/script.js` legacy calculator is unreferenced but shipped. `frontend/css/`, `frontend/js/` empty dirs mislead about modularity.
- **No typing / linting / formatting**: No `mypy`, `ruff`, `black`, `eslint`. `validator.py` returns mixed tuple `(bool, str|float)` ambiguous.
- **No CI/CD**: No GitHub Actions, no `Makefile`, no Docker, no `pyproject.toml`. `requirements.txt` unpinned transitives (lists `blinker`, `click` etc. but not `gunicorn` for prod).

### 4.3 Validation & Data Handling

- `energy_service.py:35-36` blindly `float(dev.get("watt"))` — should be validated earlier but service trusts caller. No schema object (Pydantic/dataclass).
- Frontend validation duplicates backend messages but with different wording (`alert` strings in `index.html:293-303` vs JSON errors). No shared schema.
- No max watt cap — `100000W` would pass, unrealistic but not clamped.

---

## 5. UI/UX Problems

Evaluated live via source + style audit against target: *Modern Enterprise Energy Management — professional, clean, data-first, calm, premium, reliable, technical*.

### 5.1 Visual System Mismatch (Critical)

- **Current aesthetic**: Dark glassmorphism (`--bg-color:#0b0f19`, `card-bg: rgba(17,24,39,0.7)`, `backdrop-filter: blur(16px)` at `style.css:5-6,149-153`), neon gradients (`linear-gradient(135deg, #10b981, #06b6d4)` button `style.css:235`), glowing orb animations (`style.css:42-64`), drop shadows — directly violates brief's *Avoid: excessive glassmorphism, neon, gradients, generic AI dashboard*.
- **Target DNA** calls for Stripe/Linear/Vercel/IBM Carbon — light, airy, grid-based, restrained color, strong typography hierarchy. Current is cyber-dark. Requires full redesign, not tweak.

### 5.2 Information Hierarchy

- **No KPI hero**: Task hierarchy says Dashboard → Key Metrics (How much? How much cost? How much carbon? Which device worst? What to improve?). Current hero is just a logo + subtitle subtitle “Kalkulator Pintar” (`index.html:18-23`). No KPI cards above the fold. Results appear only after interaction, leaving empty placeholder occupying prime space.
- **Table vs cards**: Results shown as single 4-column table (`index.html:64-94`) — low scannability. Enterprise pattern is 3-4 KPI cards (Today/Month/Year) with distinct visual weight, trends, units. Table buries the answers.
- **Ranking and Score compete**: Score (circular large number) and insights sit in `grid-template-columns:1fr 2fr` (`style.css:610-612`) with unequal weight; on mobile stacks correctly but score badge loses emphasis.

### 5.3 Layout & Spacing

- Container max-width jumps `540px → 1200px` at 992px (`style.css:76-87`) — no intermediate 768-991 stepping, causes awkward tablet whitespace. `gap:2rem` on desktop but card padding remains `2.5rem` (`style.css:154`) → dense.
- Flow visualization flex (`style.css:769-778`) collapses to `grid 3×2` at 768px hiding arrows (`display:none` line 823) — but icons/labels shrink to `0.72rem` (line 806) near unreadable.
- `device-item-card` each has full label + icon + badge (`style.css:398-432`) — visually heavy when 5+ devices.

### 5.4 Typography

- Single font `Outfit` (`style.css:2,15`) — good, but scale is flat: `h1 2.2rem`, `score 2.75rem`, `table 0.9rem`, `placeholder p 0.88rem` — insufficient contrast between data and chrome. No tabular numbers (`font-variant-numeric`) for kWh/cost columns → misaligned digits.
- Category badge is `0.75rem` uppercase tracking `1px` — too small for key status indicator.

### 5.5 Charts & Data Visualization

- **No charts**: Brief and `feature.md:419-437` expect bar/line charts for energy/cost/carbon. Current relies solely on table and progress bars. No `Chart.js` or alternative, no `<canvas>`. Users cannot see distribution over time.

### 5.6 States (Critical Gaps)

- **Empty state**: Placeholder (`index.html:49-53`) is verbose paragraph — no illustration, no call-to-action, no sample data affordance. Good intent but weak conversion.
- **Loading**: Only button spinner (`index.html:323`); table/ranking not skeletonized, so layout shift on render.
- **Error**: Errors shown via `alert()` (`index.html:293,298,303,527`) — blocks thread, not inline, not dismissible card. Backend JSON errors (`energy_routes.py:30`) are never surfaced inline.
- **Success**: No toast, no persistence hint, no “copy results”.

### 5.7 Accessibility

- No `<label for=>` association — `<label>` without `for` and `<input>` without `id`/`aria` (`index.html:203-206`). Screen readers cannot bind.
- Color-contrast on `var(--text-secondary)#9ca3af` over `rgba(255,255,255,0.03)` inputs likely fails WCAG AA.
- No keyboard focus ring beyond browser default; custom `box-shadow:0 0 0 4px var(--primary-glow)` on focus (`style.css:210`) but low contrast on dark bg.
- No `aria-live` for dynamic ranking/insights updates.
- Icons are decorative but lack `aria-hidden="true"`.

### 5.8 Responsiveness

- Desktop side-by-side works (`style.css:141-143`), but at `601-991px` the 460px fixed left column would overflow — actual breakpoint is 992px, so tablets (768-991) stay stacked 1-col with narrow `540px` container → poor use of space.
- Results table `overflow-x:auto` (`style.css:477`) allows horizontal scroll on mobile — but columns (Period/kWh/Cost/CO2) compress unreadably; better to stack cards on mobile.

### 5.9 Consistency

- Mixed languages: UI Indonesian (`Belum Ada Hasil`, `Tambah Perangkat`), code/test English — intentional but badge categories are English (`Excellent`, `Good`) inconsistent.
- Inline styles mixed with CSS classes (`index.html:128,138-139` `style=` attributes) vs centralized variables — hard to theme.
- Tip box uses `border:1px dashed` (`style.css:347`) while ranking uses `solid` — inconsistent border language.

---

## 6. Security Concerns

- **Global CORS** `app/__init__.py:11` `CORS(app)` without `origins=` allows any origin. Should whitelist frontend origin, or at least not in production. Exposure low for stateless calc, but bad habit for portfolio.
- **Debug mode always on** `app.py:12` `debug=True` — leaks stack traces, enables interactive debugger. Must be env-gated (`FLASK_ENV`/`FLASK_DEBUG`).
- **No input sanitization beyond numeric checks**: `device_name` stored/returned and injected via `innerHTML` at `index.html:424` `ranking-item-name` and `index.html:473` insight `description` includes `<strong>{name}</strong>` HTML from backend (`insight_service.py:37`). Backend does not escape HTML; frontend does `innerHTML =` → XSS if name is `<img onerror=...>`. Must escape or use `textContent`.
- **No rate limiting / request size limit**: `request.get_json()` with no `MAX_CONTENT_LENGTH`. Large `devices` array could DoS (e.g., 10k entries). No pagination.
- **No dependency pinning strategy**: `requirements.txt` pins w/o hashes, no `pip-tools`, but not outdated (checked 2026-08-28: Flask 3.1.3 latest).
- **No secrets handling**: None needed yet, but `.gitignore:3` correctly ignores `.env` — ready for future.
- **Error leakage**: `validate_numeric` returns raw messages with internal param names — not leaking secrets, but 500 errors (e.g., the `KeyError` above) return Flask HTML debug page in `debug=True`.

---

## 7. Testing Status

- **Runner**: `unittest` via `python backend/test_api.py` (no pytest, no coverage tool).
- **Coverage**: 9 test cases in `test_api.py:12-192`:
  - `test_home_status` — pass
  - `test_energy_calculate_single_success` — **ERROR** (KeyError insight, §4.1)
  - `test_energy_calculate_multiple_success` — pass
  - `test_energy_calculate_invalid_watt` — pass
  - `test_energy_calculate_invalid_hours` — pass
  - `test_cost_calculate_multi_period_success` — pass
  - `test_carbon_calculate_multi_period_success` — pass
  - `test_insight_engine_rules` — pass
  - `test_energy_score_variations` — **FAIL** (score logic)
- **Result**: `FAILED (failures=1, errors=1)` in 0.238s (execution 2026-08-28 evidence). 77% pass.
- **Untested critical paths**:
  - Missing watt/hours edge (`None`, `""`, arrays) — only 0 and 24.1 tested.
  - Empty `devices: []` → 400 tested implicitly? Not explicit.
  - `device_name` empty string for multi — not tested for leading/trailing spaces.
  - Cost/carbon fallback (`monthly_kwh` only) not tested.
  - Custom tariff/emission_factor not tested.
  - Frontend: zero tests (no Jest/Vitest/Playwright).
  - No integration test for full `energy → cost → carbon` parallel flow as frontend does.
  - No performance test.
- **How to run**: `D:/Telkom_sch/Ecogrid-Ai/backend/venv/Scripts/python.exe backend/test_api.py` — works, but README does not document it (no README at repo root).
- **CI**: None. No GitHub Actions, no pre-commit hook (`.git/hooks` are samples).

---

## 8. Recommended Architecture

Target: portfolio-grade, clean, scalable to roadmap without over-engineering.

```
EcoGrid AI — Recommended (Incremental, not rewrite)

Client (Browser)
  │
  ├─ Frontend (Vanilla → Modular ES Modules, no framework needed for Phase 2)
  │   ├─ design-system/  (tokens: colors, typography, spacing, shadows)
  │   ├─ components/     (KpiCard, DeviceRow, RankingBar, InsightCard)
  │   ├─ api/client.js   (centralized fetch, baseURL from config, error normalization)
  │   ├─ store/          (tiny pub/sub or localStorage for history)
  │   └─ charts/         (Chart.js wrapper, lazy-load)
  │
  └─ API Gateway (Flask, later FastAPI optional)
      ├─ Presentation:  app/routes/* (thin, schema-validated via Pydantic/marshmallow)
      ├─ Application:   app/services/* (pure, testable, no Flask deps)
      ├─ Domain:        app/models/domain.py (dataclasses: Device, CalculationResult)
      ├─ Infrastructure:
      │    ├─ app/config.py (env-driven, 12-factor, python-dotenv)
      │    ├─ app/database/ (SQLAlchemy + SQLite → Postgres ready, Alembic)
      │    ├─ app/repositories/ (DeviceRepo, SimulationRepo)
      │    └─ app/utils/ (validator, error handlers, logger)
      └─ External:     app/integrations/ (weather, solar irradiance — future)

Persistence: SQLite (dev) → PostgreSQL (prod) — file `database/energy.db` gitignored
Observability: structlog + Flask error handlers returning JSON envelopes {status, data|message}
Security: CORS whitelist, RATE_LIMIT, HTML escape, MAX_CONTENT_LENGTH, debug gated
Tests: pytest + coverage + Playwright for frontend
Deploy: gunicorn + Dockerfile + .dockerignore, env vars
```

**Why not framework migration now**: Vanilla is sufficient for portfolio if modularized (ES modules, component functions, clear `api/client.js`). React/Vue would be rewrite waste before product-market fit. Recommend staying vanilla through Phase 3, then evaluate.

**Key changes vs current**:
- Extract inline `<script>` to `frontend/js/app.js` + `api.js` + `components/` (fixes empty `js/` debt).
- Centralize API base via `frontend/js/config.js` reading `meta[name=api-base]` or `window.__ECG_CONFIG`.
- Add `backend/app/config.py` with `Config.from_env()` driving `CORS_ORIGINS`, `DEBUG`, `DATABASE_URL`, `DEFAULT_TARIFF`.
- Add `backend/app/models/` dataclasses + `database` SQLAlchemy scaffold (no behavior change yet, but unblocks history).
- Add global error handler (`@app.errorhandler`) returning JSON, and HTML escape for `device_name`.

---

## 9. Recommended Development Order

Execution sequence — each step leaves app deployable. No big-bang.

1. **Patch & Stabilize (0.5 week)** — Fix P1 bugs (single-device crash, score calibration), add `MAX_CONTENT_LENGTH`, escape HTML, gate `debug` via env, pin API base to relative URL. Make `main` green (all 9 tests pass + 2 new regression tests).
2. **Config & Quality Baseline (0.5 week)** — Add `config.py`, `python-dotenv`, `pytest`+`coverage`, `ruff`/`black`, pre-commit, GitHub Actions running tests, document `README.md` with `how to run`.
3. **Design System & Frontend Modularization (1.5 weeks)** — Build token set (Material 3 + IBM Carbon + Tailwind UI refs), rewrite `style.css` to light enterprise system, split `index.html` script into `frontend/js/{api,store,components,app}.js`, remove dead `script.js`, implement KPI cards replacing table-primary view (table kept as secondary).
4. **Dashboard & Charts (1 week)** — Add Chart.js (or lightweight `chart.js` 4.x), implement Energy/Cost/Carbon bar chart + ranking donut, wire `cost`/`carbon` via single `/api/energy/calculate` response (eliminate parallel fetches — backend can compute all).
5. **Persistence & History (1 week)** — Add SQLAlchemy + SQLite, `POST /api/energy/calculate` optionally saves simulation, `GET /api/history`, `GET /api/history/:id`, localStorage fallback. Add migration.
6. **Solar Simulator (0.75 week)** — New `solar_service.py` + `POST /api/solar/simulate`, UI card “Solar Potential” with inputs (roof, efficiency, sun hours) and outputs (kWp, generation, saving, payback).
7. **Polish & Hardening (0.75 week)** — A11y (labels, aria-live, contrast), rate limit, CORS whitelist, empty/loading/error states, performance (lazy charts, debounce), SEO meta, Docker, deploy guide.

See `docs/master_implementation_plan.md` for detailed phases.

---

## 10. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Single-device bug masked by frontend** but breaks API contract for external callers | High | High — portfolio reviewer tries `curl` single-device → 500 | Fix immediately in Phase 0; add contract test. |
| **Glassmorphism redesign is large** — rewriting 846-line CSS risks regressions | Medium | Medium — visual breakage | Token-driven incremental: keep layout, replace palette + shadows first, then components. Snapshot tests (Playwright screenshots). |
| **No DB → history feature blocked**; adding DB late forces service rework | Medium | High | Scaffold DB early (Phase 1) even if unused — zero-risk additive. |
| **Hardcoded API URL** breaks deployed demo (common portfolio failure) | High | High | Switch to relative `/api/...` + reverse proxy or env `API_BASE` before any deploy. |
| **XSS via device_name** (`innerHTML`) | Medium | Medium (portfolio security review) | Escape on backend (`html.escape`) + frontend `textContent` + test with `<script>` payload. |
| **Test suite false confidence** (only 9 cases, 2 fail) | High | Medium | Expand to 20+ cases, add `pytest --cov` gate 80% before Phase 2 merge. |
| **Empty `docs/Design.md`** — design decisions not captured, leads to drift | Low | Low | Fill with tokens + component specs during Phase 2; treat as living doc. |
| **Chart.js bundle size** + no lazy load → slower FCP | Low | Low | Dynamic `import('chart.js')` only when results shown. |
| **Scoring model subjective** — portfolio reviewer may question “Average vs Needs Improvement” thresholds | Medium | Low | Document formula in `docs/feature.md` + expose breakdown in UI tooltip. |
| **Python 3.14 very new** — some hosted runtimes lag | Low | Low | Pin `python_version` in `runtime.txt` / Dockerfile to 3.11+ compatible, test CI on 3.11,3.12,3.14. |

---

**Files audited** (evidence refs): `backend/app.py`, `backend/app/__init__.py:1-25`, `backend/app/routes/*`, `backend/app/services/*`, `backend/app/utils/validator.py`, `backend/requirements.txt`, `backend/test_api.py:1-194`, `frontend/index.html:1-537`, `frontend/style.css:1-846`, `frontend/script.js`, `docs/agents.md`, `docs/feature.md`, `docs/project_idea.md`, `docs/system_architecture.md`, `docs/Design.md`, `.gitignore`.

