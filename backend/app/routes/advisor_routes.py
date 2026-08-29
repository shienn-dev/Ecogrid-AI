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

    total_daily = data.get("total_daily_kwh")
    total_monthly = data.get("monthly_kwh") or data.get("total_monthly_kwh")

    # Validate numbers if provided
    if total_daily is not None:
        try:
            total_daily = float(total_daily)
            if total_daily < 0:
                raise ValueError
        except Exception:
            return jsonify({"status": "error", "message": "total_daily_kwh harus angka >=0"}), 400
    if total_monthly is not None:
        try:
            total_monthly = float(total_monthly)
            if total_monthly < 0:
                raise ValueError
        except Exception:
            return jsonify({"status": "error", "message": "monthly_kwh harus angka >=0"}), 400

    result = AdvisorService.analyze(
        devices, total_daily_kwh=total_daily, total_monthly_kwh=total_monthly
    )
    return jsonify({"status": "success", "data": result})


@advisor_bp.route("/tips", methods=["GET"])
def tips():
    device = request.args.get("device")
    data = AdvisorService.get_tips(device)
    return jsonify({"status": "success", "data": data})
