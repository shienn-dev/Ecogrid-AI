from flask import Blueprint, jsonify

from app.config import (
    CARBON_EQUIVALENTS,
    CONSUMPTION_TIERS,
    EMISSION_FACTORS,
    SOLAR_DEFAULTS,
    TARIFF_PRESETS,
    Config,
)

meta_bp = Blueprint("meta", __name__)


@meta_bp.route("/presets", methods=["GET"])
def presets():
    """
    Expose sourced reference data so the frontend never hardcodes numbers.
    All values documented in docs/research_references.md
    """
    return jsonify(
        {
            "status": "success",
            "data": {
                "tariffs": TARIFF_PRESETS,
                "emission_factors": EMISSION_FACTORS,
                "consumption_tiers": CONSUMPTION_TIERS,
                "solar_defaults": SOLAR_DEFAULTS,
                "carbon_equivalents": CARBON_EQUIVALENTS,
                "defaults": {
                    "tariff": Config.DEFAULT_TARIFF,
                    "emission_factor": Config.DEFAULT_EMISSION_FACTOR,
                },
            },
        }
    )


@meta_bp.route("/sources", methods=["GET"])
def sources():
    """Cite where the defaults come from — keeps the app honest."""
    return jsonify(
        {
            "status": "success",
            "data": [
                {
                    "field": "emission_factor",
                    "value": Config.DEFAULT_EMISSION_FACTOR,
                    "unit": "kg CO2/kWh",
                    "source": "Ember (2026) / Our World in Data — carbon intensity of electricity, Indonesia",
                    "url": "https://ourworldindata.org/grapher/carbon-intensity-electricity",
                },
                {
                    "field": "tariff_default",
                    "value": Config.DEFAULT_TARIFF,
                    "unit": "Rp/kWh",
                    "source": "PLN Tarif Adjustment — R-1/TR 1300 VA household",
                    "url": "https://web.pln.co.id/pelanggan/tarif-tenaga-listrik",
                },
                {
                    "field": "consumption_tiers",
                    "value": CONSUMPTION_TIERS,
                    "unit": "kWh/month",
                    "source": "PLN/ESDM household consumption by golongan tarif (900 VA / 1300 VA / 2200 VA)",
                    "url": "https://www.esdm.go.id/",
                },
                {
                    "field": "solar_performance_ratio",
                    "value": SOLAR_DEFAULTS["performance_ratio"],
                    "unit": "ratio",
                    "source": "NREL PVWatts default / IEC 61724 Performance Ratio definition",
                    "url": "https://pvwatts.nrel.gov/",
                },
                {
                    "field": "carbon_equivalents",
                    "value": CARBON_EQUIVALENTS,
                    "unit": "mixed",
                    "source": "US EPA Greenhouse Gas Equivalencies Calculator (tree sequestration, fuel factors)",
                    "url": "https://www.epa.gov/energy/greenhouse-gas-equivalencies-calculator-calculations-and-references",
                },
                {
                    "field": "peak_sun_hours_presets",
                    "value": "Jakarta 4.5 / Surabaya 5.0 / Kupang 5.5",
                    "unit": "kWh/m2/day",
                    "source": "Global Solar Atlas (World Bank / Solargis) long-term PVOUT",
                    "url": "https://globalsolaratlas.info/",
                },
            ],
        }
    )
