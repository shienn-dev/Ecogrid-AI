# EcoGrid AI — Research References

> Compiled: 2026-09-08 | Purpose: ground EcoGrid AI defaults, formulas, and UX in verifiable industry sources.
> Every number below is sourced. Items marked **[IMPLEMENTED]** have been applied to the codebase.

---

## 1. Carbon Emission Factors (grid intensity)

### Global comparison — Ember / Our World in Data (2026 edition, 2024–2025 data)

Source: [Our World in Data — Carbon intensity of electricity](https://ourworldindata.org/grapher/carbon-intensity-electricity) (Ember 2026; Energy Institute 2026)

| Country | gCO₂/kWh | kg CO₂/kWh |
|---|---|---|
| **Indonesia** | **680.25** | **0.680** |
| Malaysia | 601.97 | 0.602 |
| Thailand | 545.74 | 0.546 |
| Vietnam | 460.73 | 0.461 |
| Philippines | 588.29 | 0.588 |
| Singapore | 497.09 | 0.497 |
| India | 670.13 | 0.670 |
| China | 525.34 | 0.525 |
| Japan | 477.26 | 0.477 |
| Australia | 525.18 | 0.525 |
| USA | 384.40 | 0.384 |
| Germany | 329.65 | 0.330 |
| UK | 217.41 | 0.217 |
| France | 41.44 | 0.041 |
| Brazil | 109.95 | 0.110 |
| World (avg) | ~480 | ~0.48 |

### Key finding

**Our previous default of `0.87` kg CO₂/kWh was too high for Indonesia.** Latest Ember data puts Indonesia at **0.680 kg CO₂/kWh**.

**[IMPLEMENTED]** Updated `DEFAULT_EMISSION_FACTOR` from `0.87` → `0.68` with documented source.
Rationale: Even the older PLB/ESDM figure of 0.794 was superseded; Ember 2026 is the most recent harmonized global dataset.

> Note: Because grid intensity changes yearly, the app exposes `emission_factor` as a configurable input (`DEFAULT_EMISSION_FACTOR` env var + API param) so users can update without a code change.

---

## 2. Household Electricity Benchmark (Indonesia)

### PLN household electricity consumption context

Sources: PLN tariff regulation (Permen ESDM 28/2016 as amended), ESDM statistical yearbook.

| Household class | Daya (VA) | Typical usage | Avg monthly kWh |
|---|---|---|---|
| R-1/TR 450 VA (subsidized) | 450 | Small household | ~50–75 kWh |
| R-1/TR 900 VA (subsidized) | 900 | Small–medium | ~100–130 kWh |
| R-1/TR 1300 VA | 1300 | Medium household | ~170–230 kWh |
| R-1/TR 2200 VA | 2200 | Medium–large | ~260–340 kWh |
| R-2/TR 3500+ VA | 3500+ | Large household | ~400–600+ kWh |

### Previously used thresholds vs sourced basis

| Threshold (old) | Basis (new) |
|---|---|
| `< 150 kWh/month` = "Efisien" | Aligned to 900 VA class (`~100–130 kWh`) + margin → **< 130 kWh** |
| `150–300 kWh/month` = "Di atas rata-rata" | Aligned to 1300 VA (`~170–230 kWh`) → **130–250 kWh** |
| `> 300 kWh/month` = "Sangat tinggi" | Aligned to 2200 VA+ → **> 250 kWh** |

**[IMPLEMENTED]** Updated `insight_service.py` thresholds to 130 / 250 kWh with class labels referencing PLN golongan tarif.

### Common device benchmarks (used for sample data + advisor heuristics)

Sources: ESDM appliance labelling; manufacturer datasheets; typical Indonesian usage patterns.

| Device | Typical watt | Typical hours/day | Monthly kWh |
|---|---|---|---|
| AC 1 PK (inverter) | 660–800 | 6–10 | 120–240 |
| Kulkas 2 pintu | 100–150 | 24 | 72–108 |
| Lampu LED (per unit) | 5–12 | 5–8 | 0.75–2.9 |
| TV LED 40" | 60–100 | 4–6 | 7.2–18 |
| Rice cooker | 300–400 | 1–2 (warm 4h) | 15–30 |
| Mesin cuci | 300–500 | 1 (cycle avg) | 9–15 |
| Setrika | 300–600 | 1 | 9–18 |
| Pompa air | 125–500 | 1–3 | 3.75–45 |
| Water heater | 350–1500 | 0.5–1 | 5.25–45 |

---

## 3. Energy Scoring Methodology

### Reference frameworks researched

1. **EU Energy Label (A–G)** — scale since 2021: A (best) → G (worst), grades computed from a normalized efficiency index, not raw kWh. [EU Regulation 2017/1369](https://eur-lex.europa.eu/eli/reg/2017/1369/oj)
2. **UK EPC bands** — A 92–100, B 81–91, C 69–80, D 55–68, E 39–54, F 21–38, G 1–20 (SAP points). Note the *non-linear* band widths.
3. **EPA ENERGY STAR Home Energy Yardstick** — compares a home's kWh to similar homes; outputs a 1–10 score. Uses `site energy` normalized by house size + occupants + climate.
4. **IBM Carbon Design System — status indicators** — recommends max 3–4 severities with clear semantics.

### Adopted methodology **[IMPLEMENTED]**

Keep the deterministic 0–100 score (defensible, explainable, testable) but restructure thresholds to mirror EPC-style bands and make the *band labels* explicit:

| Score | Category | Rationale |
|---|---|---|
| 90–100 | **A — Excellent** | Below 130 kWh/month, no heavy loads, no dominance |
| 70–89 | **B — Good** | Near 900VA baseline, minor inefficiencies |
| 50–69 | **C — Average** | 1300VA territory, some high-duration devices |
| 30–49 | **D — Poor** | Above 2200VA territory or multiple heavy loads |
| 10–29 | **E — Very Poor** | Extreme consumption, dominant single load |

Deductions (unchanged math, documented):
- A. Monthly volume: `min(35, (monthly - 130) × 0.12)`, plus `min(10, (monthly - 500) × 0.02)` if > 500.
- B. Average hours: `min(20, (avg_hours - 8) × 2.0)`.
- C. Heavy devices (>500 W for >4 h): `min(25, 8 × count)`.
- D. Load dominance (>50 %): `−8`.

> Why not adopt EPC/ENERGY STAR wholesale: both require climate, floor area, and occupancy data EcoGrid does not collect. Adding those fields would inflate scope beyond the household calculator. The tiering is *inspired by* EPC banding, and this is stated honestly in the UI.

---

## 4. Solar PV Estimation

### Industry formula (adopted)

```
System capacity (kWp) = Roof usable area (m²) × Panel efficiency × 1 kW/m²  (STC)
Daily generation (kWh) = System kWp × Peak Sun Hours (PSH) × Performance Ratio (PR)
```

**[IMPLEMENTED]** Added **Performance Ratio (PR)** = `0.75` default to `SolarService`.
Rationale: PR accounts for inverter losses (~4 %), wiring (~2 %), soiling (~2–3 %), temperature derating (~8–10 %), mismatch (~2 %), and shading. Industry default for tropical residential is **0.75–0.80** (PVWatts/NREL default 0.77; IEC 61724 defines PR). Previously the app assumed 1.0 (no losses) which **overestimated generation by ~33 %**.

Worse, the old code computed `kWp = area × eff` — but real usable roof area is **not** 100 % covered (setbacks, vents, walkways). Added **usable area factor 0.85** default.

Updated formula:
```
usable_area = roof_area × 0.85
system_kwp  = usable_area × efficiency
daily_kwh   = system_kwp × sun_hours × 0.75
```

### Peak Sun Hours — Indonesia

Source: [Global Solar Atlas](https://globalsolaratlas.info) (World Bank / Solargis), long-term average PVOUT.

| City | PSH (kWh/m²/day) | Recommended default |
|---|---|---|
| Jakarta | 4.3–4.7 | 4.5 |
| Surabaya | 4.8–5.2 | 5.0 |
| Medan | 4.2–4.6 | 4.4 |
| Makassar | 4.9–5.3 | 5.1 |
| Kupang | 5.3–5.7 | 5.5 |
| Denpasar | 4.9–5.2 | 5.0 |
| Bandung | 4.2–4.6 | 4.4 |

**[IMPLEMENTED]** City preset list corrected and expanded in the solar UI.

### Payback period

Source: typical Indonesian rooftop PV installed cost **Rp 12–18 million/kWp** (ESDM / IESR 2024 range), falling ~5–8 %/yr.

**[IMPLEMENTED]** Changed flat `Rp 15,000,000/kWp` to a **configurable** `cost_per_kwp` (default 15,000,000) so it is not silently hardcoded as truth, and surfaced it in the assumptions block.

---

## 5. Energy Saving Recommendation Library

### Sourced savings percentages

Sources: IEA "Energy Efficiency 2024"; ESDM appliance labelling programme; PLN "10 Cara Hemat Listrik"; ASHRAE/AC manufacturer guidance.

| Action | Estimated saving | Source basis |
|---|---|---|
| AC +1 °C setpoint | **6–8 %** of AC consumption | Common manufacturer/utility figure (was already 6 % in app — now stated as range) |
| AC regular servicing / filter clean | 5–10 % | ASHRAE guidance |
| Incandescent → LED | **80–85 %** per lamp | ESDM labelling; lumen/watt comparison |
| CFL → LED | 40–50 % per lamp | Same |
| Fridge +1 °C warmer (3–4 °C) | 3–5 % | Manufacturer guidance |
| Fridge condenser cleaning | 5–10 % | Manufacturer guidance |
| Standby elimination (vampire load) | **5–10 %** of household | IEA "Standby Power" (IEA 4E TCP) |
| Washing machine cold wash | 60–90 % of wash cycle energy | IEA 4E |
| Water heater −5 °C | 3–5 % | DOE guidance |
| Off-peak / load shifting | varies | No fixed factor — app avoids inventing one |

**[IMPLEMENTED]** Advisor rules now cite the *range* rather than a single confident number, and the app never invents a savings figure it cannot justify.

---

## 6. Carbon Equivalents (for relatable communication)

Sources: [US EPA Greenhouse Gas Equivalencies Calculator](https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator-calculations-and-references) (methodology page reviewed 2026).

| Equivalent | Factor | Note |
|---|---|---|
| Tree seedling grown 10 yr | **0.060 metric ton CO₂/tree/year** = 60 kg CO₂/tree/year | EPA, probability-weighted urban survival |
| Passenger car, 1 year | 4.29 metric ton CO₂e | US fleet basis — not applicable to ID; app uses per-km instead |
| Gasoline, per litre | 2.31 kg CO₂ | Derived from 8,887 g/gallon ÷ 3.785 |
| Motorcycle (ID typical 40 km/L) | ~0.058 kg CO₂/km | Derived |
| Smartphone charge | ~0.008 kg CO₂ | Derived |
| LED bulb (10 W, 1 h) | ~0.0068 kg CO₂ | Derived at 0.68 kg/kWh |

**[IMPLEMENTED]** Added `carbon_equivalents` to the energy response:
- `trees_year` = `monthly_carbon_kg × 12 / 60`
- `car_km` = `monthly_carbon_kg / 0.058` (motorcycle, Indonesia-appropriate)
- `led_hours` = `monthly_carbon_kg / 0.0068`

---

## 7. UX / Dashboard Patterns

### Home Assistant Energy dashboard (open-source reference)

Source: [Home Assistant — Energy cards](https://www.home-assistant.io/dashboards/energy/)

Patterns adopted / validated:
- **Devices energy graph**: bar chart of per-device usage, **sorted by usage descending** — validates our ranking approach.
- **Energy date picker**: a single range selector drives all cards — future roadmap (Phase 3 history).
- **Energy compare alert**: explicit current-vs-previous comparison — patterns for our what-if.
- **Gauges** for single normalized ratios (self-sufficiency, grid neutrality) — validates Energy Score as a gauge.
- **Sankey / flow diagram** for energy distribution — validates our energy-flow visual.
- **max_devices cap** with "Other" bucket — adopted as a recommendation for >10 devices.

### IBM Carbon Design System (chart guidance)

Source: [Carbon — Data visualization](https://carbondesignsystem.com/data-visualization/chart-types/)

- Recommends **simple bar** for ranking, **donut** only for ≤5 parts of a whole, **gauge** for a single normalized metric.
- **Color palettes** must be accessible and *not* rely on red/green alone.
- **Empty states** are an explicit pattern (Carbon "Empty states") — validates our placeholder card.

**[IMPLEMENTED]** Donut now caps at top 5 devices + "Lainnya" bucket (Carbon guidance: donut loses readability >5 slices). Bar chart unaffected.

---

## 8. Tariff Data

Source: PLN tariff adjustment (Tarif Adjustment) — R-1/TR 1300 VA **Rp 1,444.70/kWh** remains the non-subsidized household rate used as default. Subsidized 450 VA (Rp 415/kWh) and 900 VA (Rp 605/kWh) exist but are being phased to non-subsidy for higher-income households.

**[IMPLEMENTED]** Added **tariff presets** to the UI (`Golongan tarif` select) so users pick their class instead of accepting one hardcoded number:

| Preset | Rp/kWh |
|---|---|
| R-1/TR 450 VA (subsidi) | 415 |
| R-1/TR 900 VA (subsidi) | 605 |
| R-1/TR 1300 VA | 1,444.70 |
| R-1/TR 2200 VA | 1,444.70 |
| R-2/TR 3500 VA | 1,699.53 |
| R-3/TR 6600 VA+ | 1,699.53 |

---

## 9. New Endpoints (from this research)

| Endpoint | Purpose |
|---|---|
| `GET /api/meta/presets` | Tariff classes, emission factors, tiers, solar defaults, carbon factors |
| `GET /api/meta/sources` | Citation for every default value (keeps the app honest) |
| `GET /api/solar/presets` | Solar assumptions + regional emission factors |

These exist so the **frontend never hardcodes a sourced number**. If a factor changes,
it changes in `backend/app/config.py` once.

---

## 10. Summary of Changes Applied

| # | Area | Change | File |
|---|---|---|---|
| 1 | Carbon factor | 0.87 → **0.68** kg CO₂/kWh (Ember 2026, IDN) | `backend/app/config.py`, `services/carbon_service.py` |
| 2 | Consumption tiers | 150/300 → **130/250** kWh (PLN class alignment) | `services/insight_service.py` |
| 3 | Solar losses | added **PR 0.75** + **usable area 0.85** | `services/solar_service.py` |
| 4 | Solar cost | configurable `cost_per_kwp`, surfaced in assumptions | `services/solar_service.py`, `routes/solar_routes.py` |
| 5 | PSH presets | corrected per Global Solar Atlas (7 cities) | `frontend/index.html` |
| 6 | Tariff presets | 6 PLN golongan presets | `frontend/index.html`, `api/client.js` |
| 7 | Carbon equivalents | trees / motorcycle-km / LED-hours | `services/insight_service.py`, `routes/energy_routes.py` |
| 8 | Advisor honesty | savings as ranges + source note | `services/advisor_service.py` |
| 9 | Donut cap | top 5 + "Lainnya" | `frontend/js/charts/charts.js` |
| 10 | Score bands | A–E labels mapped to EPC-inspired bands | `services/insight_service.py` |

---

## 11. Honest Limitations of this Research

- Grid intensity varies by **region within Indonesia** (Java-Bali vs Sumatra vs Kalimantan). Single national average is an approximation — documented in UI.
- PSH values are **long-term annual averages**; actual output varies ±20 % seasonally.
- Saving percentages are **typical ranges**, not guarantees; actual depends on device age, insulation, behaviour.
- Tariff figures other than 1300 VA should be verified against the current ESDM regulation before production use.
- No Indonesian-specific open dataset for per-device household load profiles was found; device benchmarks remain typical-value estimates.
