import os

# ---------------------------------------------------------------------------
# Sourced defaults — see docs/research_references.md for full citations.
# ---------------------------------------------------------------------------

# PLN household tariff presets (Rp / kWh).
# Source: PLN Tarif Adjustment (R-1/TR 1300 VA & 2200 VA = Rp 1.444,70).
TARIFF_PRESETS = {
    "450VA": {"label": "R-1/TR 450 VA (subsidi)", "tariff": 415.0},
    "900VA": {"label": "R-1/TR 900 VA (subsidi)", "tariff": 605.0},
    "1300VA": {"label": "R-1/TR 1300 VA", "tariff": 1444.70},
    "2200VA": {"label": "R-1/TR 2200 VA", "tariff": 1444.70},
    "3500VA": {"label": "R-2/TR 3500 VA", "tariff": 1699.53},
    "6600VA": {"label": "R-3/TR 6600 VA+", "tariff": 1699.53},
}

# Emission factors (kg CO2 / kWh) by grid.
# Source: Ember (2026) / Our World in Data — carbon intensity of electricity.
# Indonesia 2025: 680.25 gCO2/kWh. Regional variation exists within Indonesia
# (Java-Bali is lower than Sumatra/Kalimantan); a national average is an
# approximation and is documented as such in the UI.
EMISSION_FACTORS = {
    "ID": {"label": "Indonesia (PLN, rata-rata nasional)", "factor": 0.68},
    "ID_JAVA": {"label": "Indonesia — Jawa-Bali", "factor": 0.65},
    "ID_SUMATRA": {"label": "Indonesia — Sumatra", "factor": 0.72},
    "ID_KALIMANTAN": {"label": "Indonesia — Kalimantan", "factor": 0.79},
    "WORLD": {"label": "Rata-rata dunia", "factor": 0.48},
}

# Consumption tiers (kWh / month) aligned to PLN household classes.
# Source: PLN/ESDM household consumption by golongan tarif.
CONSUMPTION_TIERS = {
    "efficient_max": float(os.getenv("TIER_EFFICIENT_MAX", "130")),  # 900 VA class
    "high_max": float(os.getenv("TIER_HIGH_MAX", "250")),  # 1300 VA class
}

# Solar estimation constants.
# Source: IEC 61724 / NREL PVWatts — Performance Ratio for tropical residential.
SOLAR_DEFAULTS = {
    "performance_ratio": float(os.getenv("SOLAR_PERFORMANCE_RATIO", "0.75")),
    "usable_area_factor": float(os.getenv("SOLAR_USABLE_AREA_FACTOR", "0.85")),
    "cost_per_kwp": float(os.getenv("SOLAR_COST_PER_KWP", "15000000")),
}

# Carbon equivalents for relatable communication.
# Source: US EPA Greenhouse Gas Equivalencies Calculator (methodology).
CARBON_EQUIVALENTS = {
    "kg_co2_per_tree_year": 60.0,  # 0.060 t CO2/tree/yr (urban, 10-yr, weighted)
    "kg_co2_per_motorcycle_km": 0.058,  # derived: 40 km/L, 2.31 kg CO2/L
    "kg_co2_per_led_hour": 0.0068,  # 10 W LED for 1 h at 0.68 kg/kWh
}


class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")
    TESTING = False
    # CORS: comma-separated origins, default allow localhost dev servers
    CORS_ORIGINS = [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS",
            "http://127.0.0.1:5000,http://localhost:5000,"
            "http://127.0.0.1:5500,http://localhost:5500,"
            "http://127.0.0.1:8000,http://localhost:8000,"
            "http://127.0.0.1:3000,http://localhost:3000",
        ).split(",")
        if o.strip()
    ]
    CORS_ALLOW_ALL = os.getenv("CORS_ALLOW_ALL", "false").lower() in ("true", "1")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024)))  # 16KB
    MAX_DEVICES = int(os.getenv("MAX_DEVICES", "50"))
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database/energy.db")

    # Rp/kWh — default aligns to R-1/TR 1300 VA (most common non-subsidised)
    DEFAULT_TARIFF = float(os.getenv("DEFAULT_TARIFF", "1444.70"))
    # kg CO2/kWh — Indonesia national average (Ember 2026: 0.680)
    DEFAULT_EMISSION_FACTOR = float(os.getenv("DEFAULT_EMISSION_FACTOR", "0.68"))

    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")


class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"
    CORS_ALLOW_ALL = True
