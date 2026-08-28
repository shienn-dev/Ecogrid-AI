# system_architecture.md

# EcoGrid AI System Architecture

Version: MVP v1.0

---

# OVERVIEW

EcoGrid AI menggunakan arsitektur sederhana berbasis Client-Server.

```text
User
  ↓
Frontend (HTML/CSS/JavaScript)
  ↓
Flask API
  ↓
Calculation Engine
  ↓
SQLite Database
  ↓
Response
  ↓
Dashboard
```

---

# SYSTEM COMPONENTS

## Frontend

Bertanggung jawab untuk:

* Menampilkan antarmuka pengguna
* Mengambil input pengguna
* Mengirim request ke backend
* Menampilkan hasil perhitungan

Teknologi:

* HTML
* CSS
* JavaScript
* Chart.js

---

## Backend

Bertanggung jawab untuk:

* Menerima request
* Memvalidasi data
* Menghitung energi
* Menghitung biaya
* Menghitung emisi karbon
* Menghasilkan rekomendasi AI

Teknologi:

* Python
* Flask

---

## Database

Bertanggung jawab untuk:

* Menyimpan data perangkat
* Menyimpan hasil simulasi

Teknologi:

* SQLite

---

# FOLDER STRUCTURE

```text
ecogrid-ai/

├── frontend/
│
│   ├── index.html
│   ├── dashboard.html
│
│   ├── css/
│   │   └── style.css
│
│   ├── js/
│   │   ├── api.js
│   │   ├── dashboard.js
│   │   └── charts.js
│
├── backend/
│
│   ├── app.py
│
│   ├── routes/
│   │   ├── energy_routes.py
│   │   ├── solar_routes.py
│   │   └── advisor_routes.py
│
│   ├── services/
│   │   ├── energy_service.py
│   │   ├── carbon_service.py
│   │   ├── cost_service.py
│   │   ├── solar_service.py
│   │   └── advisor_service.py
│
│   ├── database/
│   │   └── db.py
│
│   └── models/
│       ├── device.py
│       └── simulation.py
│
├── docs/
│
├── screenshots/
│
└── README.md
```

---

# DATA FLOW

## Scenario 1

User menghitung konsumsi listrik.

```text
User Input

↓

Frontend Form

↓

POST /api/energy/calculate

↓

Energy Service

↓

Response JSON

↓

Dashboard
```

---

# API DESIGN

Base URL:

```text
/api
```

---

## ENERGY CALCULATION

Endpoint:

```text
POST /api/energy/calculate
```

Request:

```json
{
  "device_name": "Laptop",
  "power_watt": 65,
  "hours_per_day": 8
}
```

Response:

```json
{
  "daily_kwh": 0.52,
  "monthly_kwh": 15.6,
  "yearly_kwh": 189.8
}
```

---

## COST CALCULATION

Endpoint:

```text
POST /api/cost/calculate
```

Request:

```json
{
  "monthly_kwh": 150
}
```

Response:

```json
{
  "daily_cost": 7223,
  "monthly_cost": 216705,
  "yearly_cost": 2600460
}
```

---

## CARBON CALCULATION

Endpoint:

```text
POST /api/carbon/calculate
```

Request:

```json
{
  "monthly_kwh": 150
}
```

Response:

```json
{
  "monthly_co2": 127.5,
  "yearly_co2": 1530
}
```

---

## SOLAR SIMULATION

Endpoint:

```text
POST /api/solar/simulate
```

Request:

```json
{
  "roof_area": 40,
  "efficiency": 0.20,
  "sun_hours": 4.5
}
```

Response:

```json
{
  "system_kwp": 8,
  "daily_generation": 36,
  "monthly_generation": 1080,
  "estimated_saving": 1560000
}
```

---

## AI ADVISOR

Endpoint:

```text
POST /api/advisor/analyze
```

Request:

```json
{
  "monthly_kwh": 350,
  "devices": [
    {
      "name": "AC",
      "hours": 12
    }
  ]
}
```

Response:

```json
{
  "recommendations": [
    "Kurangi penggunaan AC",
    "Gunakan lampu LED",
    "Pertimbangkan panel surya"
  ]
}
```

---

# DATABASE DESIGN

## TABLE: devices

```sql
CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    power_watt REAL NOT NULL,
    hours_per_day REAL NOT NULL
);
```

---

## TABLE: simulations

```sql
CREATE TABLE simulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monthly_kwh REAL,
    monthly_cost REAL,
    monthly_co2 REAL,
    created_at TIMESTAMP
);
```

---

# SERVICES

## energy_service.py

Tugas:

* Menghitung konsumsi listrik

Functions:

```python
calculate_energy()
```

---

## cost_service.py

Tugas:

* Menghitung biaya listrik

Functions:

```python
calculate_cost()
```

---

## carbon_service.py

Tugas:

* Menghitung emisi karbon

Functions:

```python
calculate_carbon()
```

---

## solar_service.py

Tugas:

* Simulasi panel surya

Functions:

```python
calculate_solar()
```

---

## advisor_service.py

Tugas:

* Rule-based recommendation

Functions:

```python
generate_recommendations()
```

---

# DASHBOARD LAYOUT

```text
┌─────────────────────────────┐
│          HEADER             │
└─────────────────────────────┘

┌──────────┐ ┌──────────┐
│ ENERGY   │ │ COST     │
└──────────┘ └──────────┘

┌──────────┐ ┌──────────┐
│ CARBON   │ │ SOLAR    │
└──────────┘ └──────────┘

┌─────────────────────────────┐
│      AI RECOMMENDATION      │
└─────────────────────────────┘

┌─────────────────────────────┐
│           CHARTS            │
└─────────────────────────────┘
```

---

# MVP COMPLETION CRITERIA

Project dianggap selesai ketika:

* User dapat menambahkan perangkat
* Sistem menghitung kWh
* Sistem menghitung biaya
* Sistem menghitung emisi karbon
* Sistem menjalankan simulasi panel surya
* Sistem menghasilkan rekomendasi AI
* Dashboard menampilkan grafik
* Seluruh fitur berjalan tanpa error utama

---

# FUTURE ARCHITECTURE

Versi selanjutnya:

* Authentication System
* PostgreSQL
* Docker
* CI/CD
* Machine Learning Model
* Weather API Integration
* Mobile App
* Smart Meter Integration
* LLM Energy Assistant
