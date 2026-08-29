from flask import Blueprint, request, jsonify
from app.database import db
from app.models.simulation import Simulation
from app.repositories.simulation_repo import list_simulations, get_simulation, delete_simulation

history_bp = Blueprint("history", __name__)

@history_bp.route("", methods=["GET"])
@history_bp.route("/", methods=["GET"])
def list_history():
    try:
        limit = int(request.args.get("limit", "20"))
        offset = int(request.args.get("offset", "0"))
    except ValueError:
        return jsonify({"status": "error", "message": "limit/offset harus angka"}), 400
    limit = max(1, min(100, limit))
    offset = max(0, offset)
    try:
        items = list_simulations(limit=limit, offset=offset)
        data = [i.to_dict() for i in items]
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@history_bp.route("/<int:sid>", methods=["GET"])
def get_one(sid):
    try:
        sim = get_simulation(sid)
        if not sim:
            return jsonify({"status": "error", "message": "Riwayat tidak ditemukan"}), 404
        return jsonify({"status": "success", "data": sim.to_dict()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@history_bp.route("/<int:sid>", methods=["DELETE"])
def delete_one(sid):
    try:
        ok = delete_simulation(sid)
        if not ok:
            return jsonify({"status": "error", "message": "Riwayat tidak ditemukan"}), 404
        return jsonify({"status": "success", "message": "Riwayat dihapus"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Alternative POST to create manually (optional)
@history_bp.route("", methods=["POST"])
@history_bp.route("/", methods=["POST"])
def create_history():
    data = request.get_json() or {}
    # Expect same as simulation
    required = ["total_daily_kwh", "total_monthly_kwh", "total_yearly_kwh", "monthly_cost", "monthly_carbon", "energy_score", "category", "devices"]
    for f in required:
        if f not in data:
            return jsonify({"status": "error", "message": f"Field {f} wajib"}), 400
    from app.repositories.simulation_repo import save_simulation
    sim = save_simulation(
        total_daily_kwh=data["total_daily_kwh"],
        total_monthly_kwh=data["total_monthly_kwh"],
        total_yearly_kwh=data["total_yearly_kwh"],
        monthly_cost=data["monthly_cost"],
        monthly_carbon=data["monthly_carbon"],
        energy_score=data["energy_score"],
        category=data["category"],
        devices=data["devices"],
    )
    if not sim:
        return jsonify({"status": "error", "message": "Gagal menyimpan"}), 500
    return jsonify({"status": "success", "data": sim.to_dict()}), 201
