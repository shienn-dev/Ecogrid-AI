from flask import Blueprint, jsonify, request

from app.services.advisor_service import AdvisorService

advisor_bp = Blueprint("advisor", __name__)


@advisor_bp.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json() or {}
    devices = data.get("devices")
    if devices is None:
        # support legacy: monthly_kwh + devices with name/hours
        devices = data.get("devices", [])
    if not isinstance(devices, list) or len(devices) == 0:
        return jsonify({"status": "error", "message": "devices harus list tidak kosong"}), 400
    if len(devices) > 50:
        return jsonify({"status": "error", "message": "Maksimal 50 perangkat"}), 400
    # Validate each device is dict-like to prevent crash
    for i, d in enumerate(devices):
        if not isinstance(d, dict):
            return (
                jsonify(
                    {"status": "error", "message": f"Perangkat ke-{i + 1} harus berupa objek."}
                ),
                400,
            )

    total_daily = data.get("total_daily_kwh")
    total_monthly = data.get("monthly_kwh") or data.get("total_monthly_kwh")

    # Validate numbers if provided — pakai validator (tolak NaN/Infinity)
    from app.utils.validator import validate_numeric

    if total_daily is not None:
        is_valid, val = validate_numeric(total_daily, "total_daily_kwh", min_value=0.0)
        if not is_valid:
            return jsonify({"status": "error", "message": val}), 400
        total_daily = val
    if total_monthly is not None:
        is_valid, val = validate_numeric(total_monthly, "monthly_kwh", min_value=0.0)
        if not is_valid:
            return jsonify({"status": "error", "message": val}), 400
        total_monthly = val

    # Validate device fields
    for i, d in enumerate(devices):
        if "watt" in d:
            is_valid, val = validate_numeric(
                d.get("watt"), f"watt perangkat ke-{i + 1}", min_value=0.0
            )
            if not is_valid:
                return jsonify({"status": "error", "message": val}), 400
        if "hours_per_day" in d:
            is_valid, val = validate_numeric(
                d.get("hours_per_day"), f"jam perangkat ke-{i + 1}", min_value=0.0, max_value=24.0
            )
            if not is_valid:
                return jsonify({"status": "error", "message": val}), 400
        if "hours" in d:
            is_valid, val = validate_numeric(
                d.get("hours"), f"jam perangkat ke-{i + 1}", min_value=0.0, max_value=24.0
            )
            if not is_valid:
                return jsonify({"status": "error", "message": val}), 400

    result = AdvisorService.analyze(
        devices, total_daily_kwh=total_daily, total_monthly_kwh=total_monthly
    )
    return jsonify({"status": "success", "data": result})


@advisor_bp.route("/tips", methods=["GET"])
def tips():
    device = request.args.get("device")
    data = AdvisorService.get_tips(device)
    return jsonify({"status": "success", "data": data})
