from flask import Blueprint, request, jsonify
from app.services.energy_service import EnergyService
from app.services.insight_service import InsightService
from app.utils.validator import validate_numeric

energy_bp = Blueprint('energy', __name__)

@energy_bp.route('/calculate', methods=['POST'])
def calculate_energy():
    data = request.get_json() or {}
    
    # Memeriksa jika request bertipe list perangkat (multiple)
    if "devices" in data:
        devices = data["devices"]
        if not isinstance(devices, list) or len(devices) == 0:
            return jsonify({
                "status": "error",
                "message": "Parameter 'devices' harus berupa list yang tidak kosong."
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
                "device_name": name,
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
    result["device_name"] = device_name
    result["contribution_percentage"] = 100.0

    devices_list = [result]
    insights_data = InsightService.generate_insights(
        devices_list,
        result["daily_kwh"],
        result["monthly_kwh"]
    )

    return jsonify({
        "status": "success",
        "data": {
            "devices": devices_list,
            "total_daily_kwh": result["daily_kwh"],
            "total_monthly_kwh": result["monthly_kwh"],
            "total_yearly_kwh": result["yearly_kwh"],
            "ranked_devices": [{
                "device_name": device_name,
                "monthly_kwh": result["monthly_kwh"],
                "contribution_percentage": 100.0
            }],
            "energy_score": insights_data["energy_score"],
            "category": insights_data["category"],
            "insights": insights_data["insights"]
        }
    })
