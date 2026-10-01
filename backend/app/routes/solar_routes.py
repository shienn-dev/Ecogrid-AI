from flask import Blueprint, jsonify, request

from app.config import EMISSION_FACTORS, SOLAR_DEFAULTS, Config
from app.services.solar_service import SolarService
from app.utils.validator import validate_numeric

solar_bp = Blueprint("solar", __name__)


@solar_bp.route("/simulate", methods=["POST"])
def simulate_solar():
    data = request.get_json() or {}

    roof_area = data.get("roof_area")
    efficiency = data.get("efficiency", 0.20)
    sun_hours = data.get("sun_hours", 4.5)
    tariff = data.get("tariff_per_kwh", Config.DEFAULT_TARIFF)
    emission_factor = data.get("emission_factor", Config.DEFAULT_EMISSION_FACTOR)
    performance_ratio = data.get("performance_ratio")
    usable_area_factor = data.get("usable_area_factor")
    cost_per_kwp = data.get("cost_per_kwp")
    household_monthly_kwh = data.get("household_monthly_kwh")

    ok, roof_val = validate_numeric(roof_area, "roof_area", min_value=1, max_value=1000)
    if not ok:
        return jsonify({"status": "error", "message": roof_val}), 400

    ok, eff_val = validate_numeric(efficiency, "efficiency", min_value=0.05, max_value=0.30)
    if not ok:
        return jsonify({"status": "error", "message": eff_val}), 400

    ok, sun_val = validate_numeric(sun_hours, "sun_hours", min_value=1, max_value=10)
    if not ok:
        return jsonify({"status": "error", "message": sun_val}), 400

    ok, tariff_val = validate_numeric(tariff, "tariff_per_kwh", min_value=0)
    if not ok:
        return jsonify({"status": "error", "message": tariff_val}), 400

    ok, factor_val = validate_numeric(emission_factor, "emission_factor", min_value=0)
    if not ok:
        return jsonify({"status": "error", "message": factor_val}), 400

    # Optional advanced params — validate only if supplied
    pr_val = None
    if performance_ratio is not None:
        ok, pr_val = validate_numeric(
            performance_ratio, "performance_ratio", min_value=0.3, max_value=1.0
        )
        if not ok:
            return jsonify({"status": "error", "message": pr_val}), 400

    uaf_val = None
    if usable_area_factor is not None:
        ok, uaf_val = validate_numeric(
            usable_area_factor, "usable_area_factor", min_value=0.3, max_value=1.0
        )
        if not ok:
            return jsonify({"status": "error", "message": uaf_val}), 400

    cpp_val = None
    if cost_per_kwp is not None:
        ok, cpp_val = validate_numeric(cost_per_kwp, "cost_per_kwp", min_value=0)
        if not ok:
            return jsonify({"status": "error", "message": cpp_val}), 400

    usage_val = None
    if household_monthly_kwh is not None:
        ok, usage_val = validate_numeric(
            household_monthly_kwh, "household_monthly_kwh", min_value=0
        )
        if not ok:
            return jsonify({"status": "error", "message": usage_val}), 400

    result = SolarService.calculate_with_offset(
        household_monthly_kwh=float(usage_val) if usage_val is not None else None,
        roof_area=roof_val,
        efficiency=eff_val,
        sun_hours=sun_val,
        tariff_per_kwh=tariff_val,
        emission_factor=factor_val,
        performance_ratio=pr_val,
        usable_area_factor=uaf_val,
        cost_per_kwp=cpp_val,
    )
    return jsonify({"status": "success", "data": result})


@solar_bp.route("/presets", methods=["GET"])
def solar_presets():
    """Expose sourced defaults so the frontend never hardcodes them."""
    return jsonify(
        {
            "status": "success",
            "data": {
                "performance_ratio": SOLAR_DEFAULTS["performance_ratio"],
                "usable_area_factor": SOLAR_DEFAULTS["usable_area_factor"],
                "cost_per_kwp": SOLAR_DEFAULTS["cost_per_kwp"],
                "emission_factors": EMISSION_FACTORS,
            },
        }
    )
