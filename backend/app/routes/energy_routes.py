import html
from flask import Blueprint, request, jsonify, current_app
from app.services.energy_service import EnergyService
from app.services.cost_service import CostService
from app.services.carbon_service import CarbonService
from app.services.insight_service import InsightService
from app.utils.validator import validate_numeric

energy_bp = Blueprint('energy', __name__)

@energy_bp.route('/calculate', methods=['POST'])
def calculate_energy():
    data = request.get_json() or {}
    max_devices = current_app.config.get("MAX_DEVICES", 50)
    
    # Memeriksa jika request bertipe list perangkat (multiple)
    if "devices" in data:
        devices = data["devices"]
        if not isinstance(devices, list) or len(devices) == 0:
            return jsonify({
                "status": "error",
                "message": "Parameter 'devices' harus berupa list yang tidak kosong."
            }), 400
        if len(devices) > max_devices:
            return jsonify({
                "status": "error",
                "message": f"Jumlah perangkat melebihi batas maksimum {max_devices}."
            }), 400
            
        validated_devices = []
        for i, dev in enumerate(devices):
            name = dev.get('device_name', '').strip()
            watt = dev.get('watt')
            hours_per_day = dev.get('hours_per_day')
            
            if not name:
                return jsonify({
                    "status": "error",
                    "message": f"Nama perangkat pada input ke-{i+1} wajib diisi."
                }), 400
                
            # Validasi watt > 0
            is_valid_watt, watt_val = validate_numeric(watt, f"watt perangkat ke-{i+1} ({name})", min_value=0.01)
            if not is_valid_watt:
                return jsonify({
                    "status": "error",
                    "message": watt_val
                }), 400
                
            # Validasi jam > 0 dan <= 24
            is_valid_hours, hours_val = validate_numeric(hours_per_day, f"jam penggunaan perangkat ke-{i+1} ({name})", min_value=0.01, max_value=24.0)
            if not is_valid_hours:
                return jsonify({
                    "status": "error",
                    "message": hours_val
                }), 400
                
            validated_devices.append({
                "device_name": html.escape(name),
                "watt": watt_val,
                "hours_per_day": hours_val
            })
            
        result = EnergyService.calculate_multiple(validated_devices)
        
        # Hitung skor energi dan generate insights
        insights_data = InsightService.generate_insights(
            result["devices"],
            result["total_daily_kwh"],
            result["total_monthly_kwh"]
        )
        result["energy_score"] = insights_data["energy_score"]
        result["category"] = insights_data["category"]
        result["insights"] = insights_data["insights"]
        # Inline cost/carbon unified
        result["cost"] = CostService.calculate_all(result["total_daily_kwh"], result["total_monthly_kwh"], result["total_yearly_kwh"])
        result["carbon"] = CarbonService.calculate_all(result["total_daily_kwh"], result["total_monthly_kwh"], result["total_yearly_kwh"])

        # Persist if ?save=true
        if request.args.get("save", "false").lower() in ("true", "1"):
            try:
                from app.repositories.simulation_repo import save_simulation
                hist = save_simulation(
                    total_daily_kwh=result["total_daily_kwh"],
                    total_monthly_kwh=result["total_monthly_kwh"],
                    total_yearly_kwh=result["total_yearly_kwh"],
                    monthly_cost=result["cost"]["monthly_cost"],
                    monthly_carbon=result["carbon"]["monthly_carbon_kg"],
                    energy_score=result["energy_score"],
                    category=result["category"],
                    devices=result["devices"]
                )
                if hist:
                    result["history_id"] = hist.id
            except Exception:
                pass
        
        return jsonify({
            "status": "success",
            "data": result
        })
        
    # Fallback ke mode single device
    device_name = data.get('device_name', '').strip()
    watt = data.get('watt')
    hours_per_day = data.get('hours_per_day')

    if not device_name:
        return jsonify({
            "status": "error",
            "message": "Parameter 'device_name' atau 'devices' wajib diisi."
        }), 400

    # Validasi watt > 0
    is_valid_watt, watt_val = validate_numeric(watt, "watt", min_value=0.01)
    if not is_valid_watt:
        return jsonify({
            "status": "error",
            "message": watt_val
        }), 400

    # Validasi jam > 0 dan <= 24
    is_valid_hours, hours_val = validate_numeric(hours_per_day, "hours_per_day", min_value=0.01, max_value=24.0)
    if not is_valid_hours:
        return jsonify({
            "status": "error",
            "message": hours_val
        }), 400

    result = EnergyService.calculate(watt_val, hours_val)
    # Escape device name for safe storage/display
    safe_name = html.escape(device_name)
    result["device_name"] = safe_name
    result["watt"] = watt_val
    result["hours_per_day"] = hours_val
    result["contribution_percentage"] = 100.0

    devices_list = [result]
    insights_data = InsightService.generate_insights(
        devices_list,
        result["daily_kwh"],
        result["monthly_kwh"]
    )

    # Persist if ?save=true and DB available
    save = request.args.get("save", "false").lower() in ("true", "1")
    history_id = None
    if save:
        try:
            from app.repositories.simulation_repo import save_simulation
            # need cost/carbon inline for history
            cost_data = CostService.calculate_all(result["daily_kwh"], result["monthly_kwh"], result["yearly_kwh"])
            carbon_data = CarbonService.calculate_all(result["daily_kwh"], result["monthly_kwh"], result["yearly_kwh"])
            hist = save_simulation(
                total_daily_kwh=result["daily_kwh"],
                total_monthly_kwh=result["monthly_kwh"],
                total_yearly_kwh=result["yearly_kwh"],
                monthly_cost=cost_data["monthly_cost"],
                monthly_carbon=carbon_data["monthly_carbon_kg"],
                energy_score=insights_data["energy_score"],
                category=insights_data["category"],
                devices=devices_list
            )
            history_id = hist.id if hist else None
        except Exception:
            pass

    # Inline cost/carbon for unified response (Phase 3 optimization)
    cost_inline = CostService.calculate_all(result["daily_kwh"], result["monthly_kwh"], result["yearly_kwh"])
    carbon_inline = CarbonService.calculate_all(result["daily_kwh"], result["monthly_kwh"], result["yearly_kwh"])

    resp_data = {
        "devices": devices_list,
        "total_daily_kwh": result["daily_kwh"],
        "total_monthly_kwh": result["monthly_kwh"],
        "total_yearly_kwh": result["yearly_kwh"],
        "ranked_devices": [{
            "device_name": safe_name,
            "monthly_kwh": result["monthly_kwh"],
            "contribution_percentage": 100.0
        }],
        "energy_score": insights_data["energy_score"],
        "category": insights_data["category"],
        "insights": insights_data["insights"],
        "cost": cost_inline,
        "carbon": carbon_inline
    }
    if history_id is not None:
        resp_data["history_id"] = history_id

    return jsonify({
        "status": "success",
        "data": resp_data
    })
