from flask import Blueprint, request, jsonify
from app.services.carbon_service import CarbonService
from app.utils.validator import validate_numeric

carbon_bp = Blueprint('carbon', __name__)

@carbon_bp.route('/calculate', methods=['POST'])
def calculate_carbon():
    data = request.get_json() or {}
    
    # Jika request mengirimkan format multi-periode (minimal 2 periode)
    _keys = [k for k in ("daily_kwh", "monthly_kwh", "yearly_kwh") if k in data]
    if len(_keys) >= 2:
        daily_kwh = data.get('daily_kwh', 0.0)
        monthly_kwh = data.get('monthly_kwh', 0.0)
        yearly_kwh = data.get('yearly_kwh', 0.0)
        emission_factor = data.get('emission_factor')
        
        # Validasi input harian, bulanan, tahunan >= 0
        is_valid_d, d_val = validate_numeric(daily_kwh, "daily_kwh", min_value=0.0)
        if not is_valid_d:
            return jsonify({"status": "error", "message": d_val}), 400
            
        is_valid_m, m_val = validate_numeric(monthly_kwh, "monthly_kwh", min_value=0.0)
        if not is_valid_m:
            return jsonify({"status": "error", "message": m_val}), 400
            
        is_valid_y, y_val = validate_numeric(yearly_kwh, "yearly_kwh", min_value=0.0)
        if not is_valid_y:
            return jsonify({"status": "error", "message": y_val}), 400
            
        factor_val = None
        if emission_factor is not None:
            is_valid_f, factor_val = validate_numeric(emission_factor, "emission_factor", min_value=0.0)
            if not is_valid_f:
                return jsonify({"status": "error", "message": factor_val}), 400
                
        result = CarbonService.calculate_all(d_val, m_val, y_val, factor_val)
        return jsonify({
            "status": "success",
            "data": result
        })

    # Fallback jika hanya mengirimkan monthly_kwh (kompatibilitas)
    monthly_kwh = data.get('monthly_kwh')
    emission_factor = data.get('emission_factor')

    is_valid_kwh, kwh_val = validate_numeric(monthly_kwh, "monthly_kwh", min_value=0.0)
    if not is_valid_kwh:
        return jsonify({
            "status": "error",
            "message": kwh_val
        }), 400

    factor_val = None
    if emission_factor is not None:
        is_valid_factor, factor_val = validate_numeric(emission_factor, "emission_factor", min_value=0.0)
        if not is_valid_factor:
            return jsonify({
                "status": "error",
                "message": factor_val
            }), 400

    carbon_val = CarbonService.calculate(kwh_val, factor_val)
    factor = factor_val if factor_val is not None else CarbonService.DEFAULT_EMISSION_FACTOR

    return jsonify({
        "status": "success",
        "data": {
            "daily_carbon_kg": round(carbon_val / 30.0, 4),
            "monthly_carbon_kg": carbon_val,
            "yearly_carbon_kg": round(carbon_val / 30.0 * 365.0, 4),
            "emission_factor": float(factor)
        }
    })
