# EcoGrid AI — Energy Management & Decision Support System

> Portfolio-grade Energy Management + Analytics + Decision Support for household electricity consumption.  
> **Stack**: Flask + Modular Vanilla ESM + SQLite (SQLAlchemy). No framework rewrite, clean separation.

![EcoGrid AI](https://img.shields.io/badge/Phase-Production--Ready-0f766e?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1.3-000000?logo=flask)
![License](https://img.shields.io/badge/License-MIT-e5e7eb)

---

## Overview

EcoGrid AI started as a single-device electricity calculator and has evolved into a professional energy analytics platform:

- **Configure** household devices (watt, hours/day) with strict validation.
- **Calculate** daily / monthly / yearly kWh, cost (PLN tariff), carbon (0.87 kg CO2/kWh default).
- **Rank** devices by consumption + contribution %.
- **Score** efficiency (Energy Score 10-100, categories Excellent/Good/Average/Needs Improvement).
- **Recommend** via rule-based Insight Engine (explainable, deterministic, no fake AI).
- **Simulate** what-if (reduce usage 2h) and **solar potential** (roof area → kWp → saving).
- **Persist** history in SQLite and review analytics.

Answers 5 core questions in <5s: *How much? Which device worst? How much cost? Carbon? What to improve?*

### Design DNA

Light enterprise (Stripe / Linear / IBM Carbon / Vercel / Material 3 / Tailwind UI / Lucide) — clean, calm, data-first, premium, technical. No glassmorphism, no neon, no cyberpunk.

---

## Features

| Area | Detail |
|---|---|
| **Calculator** | Multi-device, daily×30×365, contribution %, ranked view |
| **Cost** | PLN tariff configurable (`DEFAULT_TARIFF=1444.70`), daily/monthly/yearly |
| **Carbon** | Emission factor `0.87`, daily/monthly/yearly kg CO₂ |
| **Score & Insights** | 6 rules + what-if, structured cards `{type,icon,title,description}` |
| **Dashboard** | KPI cards, bar/doughnut charts (Chart.js lazy), ranking bars, period comparison |
| **What-if** | Interactive slider reduce top device 1-3h → live kWh/cost/carbon delta |
| **Solar** | Roof area × efficiency × sun hours → kWp, generation, saving, payback, CO₂ reduction |
| **History** | SQLite, SQLAlchemy, `POST /save`, `GET /api/history`, filter, trend chart |
| **Advisor** | `POST /api/advisor/analyze` rule-based (AC>8h, lamp>10h), tip library |
| **Security** | XSS escape, CORS whitelist, MAX_CONTENT 16KB, max 50 devices, rate limit 60/min, debug gated |
| **A11y** | Semantic HTML, label-for, aria-live, keyboard, focus ring, contrast AA, reduced-motion |

---

## Architecture

```
Frontend (Vanilla ESM, no React)
  index.html
  css/{tokens,base,layout,components,dashboard,responsive}.css
  js/{api/client, store/appStore+historyStore, components/*, charts/*, utils/*}

Backend (Flask)
  app/__init__.py  (factory, CORS, error handlers, DB init)
  app/config.py    (12-factor env)
  app/routes/{energy,cost,carbon,solar,history,advisor}.py  (thin)
  app/services/{energy,cost,carbon,insight,solar,advisor}.py (pure)
  app/repositories/simulation_repo.py
  app/models/simulation.py
  app/database/db.py (SQLAlchemy)
  app/utils/{validator,logger}
  app/integrations/llm_stub.py (future AI boundary)

DB: SQLite file `database/energy.db` (gitignored) → Postgres-ready via DATABASE_URL
```

See `docs/system_architecture.md` for diagrams and `docs/Design.md` for tokens.

---

## Quick Start

### Prerequisites
- Python 3.11+ (3.14 tested)
- Modern browser (Chrome/Firefox/Edge)

### Backend

```bash
python -m venv venv
# Windows: venv\Scripts\activate  |  Unix: source venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env  # edit if needed
# Dev run
python backend/app.py
# → http://127.0.0.1:5000  (health: /api/health)
```

Prod:

```bash
gunicorn --config gunicorn.conf.py "backend.app:create_app()" 
# or docker
docker build -t ecogrid .
docker run -p 5000:5000 --env-file .env ecogrid
```

### Frontend

No build step — native ESM:

- Dev: open `frontend/index.html` via **Live Server** or `python -m http.server --directory frontend 5500`, set `window.__ECG_API_BASE="http://127.0.0.1:5000"` if needed (default relative `/api`).
- Prod: Flask can serve `frontend/` static or Nginx.

### Tests

```bash
# All backend tests
python -m pytest backend/test_api.py -v
# With coverage
pytest --cov=backend/app --cov-report=term-missing -v
# Single
pytest backend/test_api.py::EcoGridTestCase::test_energy_calculate_single_success -v
```

---

## API

Base: `/api` (relative). All POST JSON, response envelope `{status:"success"|"error", data|message}`.

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/api/energy/calculate` | `{devices:[{device_name,watt,hours_per_day}]}` or single `{device_name,watt,hours_per_day}` | `total_*_kwh, devices, ranked_devices, energy_score, category, insights, cost{}, carbon{}` |
| POST | `/api/energy/calculate?save=true` | same | same + `history_id` |
| POST | `/api/cost/calculate` | `{daily_kwh,monthly_kwh,yearly_kwh, tariff_per_kwh?}` or `{monthly_kwh}` | `daily_cost, monthly_cost, yearly_cost, tariff_per_kwh` |
| POST | `/api/carbon/calculate` | same with `emission_factor?` | `daily_carbon_kg, monthly_carbon_kg, yearly_carbon_kg` |
| POST | `/api/solar/simulate` | `{roof_area, efficiency?=0.20, sun_hours?=4.5, tariff_per_kwh?}` | `system_kwp, daily_generation, monthly_generation, estimated_saving, yearly_generation, carbon_reduction_kg` |
| GET | `/api/history?limit=20&offset=0` | — | `[{id, created_at, total_monthly_kwh, monthly_cost, monthly_carbon, energy_score, category, devices}]` |
| GET | `/api/history/:id` | — | single simulation |
| DELETE | `/api/history/:id` | — | `{status:"success"}` |
| POST | `/api/advisor/analyze` | `{monthly_kwh?, devices:[{name,hours}]}` or `{devices}` | `{recommendations:[{type,icon,title,description}]}` |
| GET | `/api/advisor/tips?device=ac` | — | filtered tips |

Validation: `watt>0`, `0.01≤hours≤24`, name required, max 50 devices, payload ≤16KB. Errors → 400 with `message`.

### Examples

```bash
curl -X POST http://127.0.0.1:5000/api/energy/calculate \
  -H "Content-Type: application/json" \
  -d '{"devices":[{"device_name":"AC","watt":800,"hours_per_day":6},{"device_name":"Kulkas","watt":120,"hours_per_day":24}]}'

curl -X POST http://127.0.0.1:5000/api/solar/simulate \
  -H "Content-Type: application/json" \
  -d '{"roof_area":40,"efficiency":0.20,"sun_hours":4.5}'
```

---

## Configuration

All via env (see `.env.example`):

| Key | Default | Desc |
|---|---|---|
| `FLASK_DEBUG` | `false` | enable debug/reloader |
| `HOST` | `127.0.0.1` | bind host |
| `PORT` | `5000` | port |
| `CORS_ORIGINS` | localhost:5000,5500 | comma whitelist |
| `CORS_ALLOW_ALL` | `false` | if true, allow * |
| `MAX_CONTENT_LENGTH` | `16384` | 16KB |
| `MAX_DEVICES` | `50` | per request |
| `DATABASE_URL` | `sqlite:///database/energy.db` | SQLAlchemy URL |
| `DEFAULT_TARIFF` | `1444.70` | Rp/kWh |
| `DEFAULT_EMISSION_FACTOR` | `0.87` | kg CO₂/kWh |
| `SECRET_KEY` | dev | Flask secret |
| `RATE_LIMIT_PER_MINUTE` | `60` | per IP |

Frontend: `window.__ECG_API_BASE` (default `""` → relative). Set via `<meta name="api-base">` or `js/api/config.js`.

---

## Project Structure

```
ecogrid-ai/
  backend/
    app.py
    requirements.txt
    test_api.py
    app/
      __init__.py
      config.py
      routes/{energy,cost,carbon,solar,history,advisor}.py
      services/{energy,cost,carbon,insight,solar,advisor}.py
      models/simulation.py
      database/db.py
      repositories/simulation_repo.py
      integrations/llm_stub.py
      utils/{validator,logger}.py
  frontend/
    index.html
    css/{tokens,base,layout,components,dashboard,responsive}.css
    js/{api/client,api/config,store/appStore,store/historyStore,components/*,charts/*,utils/*}
  database/energy.db   (generated, ignored)
  datasets/tips.json
  docs/{project_state,system_architecture,Design,feature,agents,final_project_report}.md
  .env.example
  pyproject.toml
  Dockerfile
  gunicorn.conf.py
```

---

## Testing

- Backend: `unittest` + `pytest --cov` (70% gate). Covers validation, single/multi, cost/carbon, insight rules, solar, history, advisor, XSS, limits.
- Frontend: manual QA checklist + `vitest` for store/client logic (see `frontend/js` tests).
- CI: GitHub Actions matrix 3.11/3.12/3.14 → ruff + black + pytest + health check.

---

## Roadmap

- Phase 0 Stabilize ✅ (bugs, XSS, limits)
- Phase 1 Foundation ✅ (config, test, CI)
- Phase 2 Design System (light enterprise, modular ESM)
- Phase 3 Dashboard (KPI, charts, what-if)
- Phase 4 Solar Simulator
- Phase 5 History (SQLite)
- Phase 6 Advisor (rule → future AI boundary)
- Phase 7 Security/Polish/Deploy

See `docs/master_implementation_plan.md`.

---

## Security

- Server-side validation only trusted, HTML escape via `html.escape` on `device_name`, frontend renders via `textContent` for user strings and `innerHTML` only for controlled `<strong>` in insights.
- `MAX_CONTENT_LENGTH`, `MAX_DEVICES`, `Flask-Limiter` 60/min on `/api/*`, CORS whitelist, security headers, `SECRET_KEY` env, debug gated, no SQL injection (ORM parameterized).

---

## Accessibility & Performance

- Labels `for`/`id`, `aria-live="polite"` on results, `role="status"` on toasts, keyboard nav, focus `2px solid #0f766e`, contrast AA, `prefers-reduced-motion` disables chart animation, `prefers-color-scheme` dark variant.
- Charts lazy `import('chart.js')` only after calculate, debounce input 300ms, `requestAnimationFrame` for bars, gzip, cache static.

---

## Deployment

```bash
docker build -t ecogrid .
docker run -p 5000:5000 --env-file .env ecogrid
# or
gunicorn -w 2 -b 0.0.0.0:5000 "backend.app:create_app()"
```

Frontend static can be served via Nginx or `Flask.send_from_directory("frontend", path)`.

---

## Known Limitations

- Rule-based advisor is deterministic, not ML/LLM — honest by design (`docs/agents.md`).
- Solar simulation uses simple `area*eff* sun_hours` model; real irradiance, tilt, shading not modeled — documented as estimate.
- History stored locally SQLite, no auth/multi-user, not encrypted.
- Charts require JS; print fallback provides table.

---

## License

MIT — see `LICENSE` (if not present, treat as MIT for portfolio use).

---

Built with engineering honesty. No “AI-powered” claims without AI.

