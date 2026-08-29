from flask import Blueprint, jsonify, request

from app.config import Config
from app.services.solar_service import SolarService
from app.utils.validator import validate_numeric

solar_bp = Blueprint("solar", __name__)


@solar_bp.route("/simulate", methods=["POST"])
def simulate_solar():
    data = request.get_json() or {}
    roof_area = data.get("roof_area")
    efficiency = data.get("efficiency", 0.20)
    sun_hours = data.get("sun_hours", 4.5)
    tariff = data.get(
        "tariff_per_kwh", Config.DEFAULT_TARIFF if hasattr(Config, "DEFAULT_TARIFF") else 1444.70
    )
    emission_factor = data.get("emission_factor", 0.87)

    # Validate roof_area 1-1000
    ok, val = validate_numeric(roof_area, "roof_area", min_value=1, max_value=1000)
    if not ok:
        return jsonify({"status": "error", "message": val}), 400
    roof_val = val

    ok, val = validate_numeric(efficiency, "efficiency", min_value=0.05, max_value=0.30)
    if not ok:
        return jsonify({"status": "error", "message": val}), 400
    eff_val = val

    ok, val = validate_numeric(sun_hours, "sun_hours", min_value=1, max_value=10)
    if not ok:
        return jsonify({"status": "error", "message": val}), 400
    sun_val = val

    tariff_val = None
    if tariff is not None:
        ok, val = validate_numeric(tariff, "tariff_per_kwh", min_value=0)
        if not ok:
            return jsonify({"status": "error", "message": val}), 400
        tariff_val = val
    else:
        tariff_val = 1444.70

    factor_val = None
    if emission_factor is not None:
        ok, val = validate_numeric(emission_factor, "emission_factor", min_value=0)
        if not ok:
            return jsonify({"status": "error", "message": val}), 400
        factor_val = val
    else:
        factor_val = 0.87

    result = SolarService.calculate(roof_val, eff_val, sun_val, tariff_val, factor_val)
    return jsonify({"status": "success", "data": result})
