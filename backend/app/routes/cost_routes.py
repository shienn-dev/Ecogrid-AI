from flask import Blueprint, request, jsonify
from app.services.cost_service import CostService
from app.utils.validator import validate_numeric

cost_bp = Blueprint('cost', __name__)

@cost_bp.route('/calculate', methods=['POST'])
def calculate_cost():
    data = request.get_json() or {}
    
    # Jika request mengirimkan format multi-periode (daily+monthly+yearly atau minimal 2 periode)
    _keys = [k for k in ("daily_kwh", "monthly_kwh", "yearly_kwh") if k in data]
    if len(_keys) >= 2:
        daily_kwh = data.get('daily_kwh', 0.0)
        monthly_kwh = data.get('monthly_kwh', 0.0)
        yearly_kwh = data.get('yearly_kwh', 0.0)
        tariff_per_kwh = data.get('tariff_per_kwh')
        
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
            
        tariff_val = None
        if tariff_per_kwh is not None:
            is_valid_t, tariff_val = validate_numeric(tariff_per_kwh, "tariff_per_kwh", min_value=0.0)
            if not is_valid_t:
                return jsonify({"status": "error", "message": tariff_val}), 400
                
        result = CostService.calculate_all(d_val, m_val, y_val, tariff_val)
        return jsonify({
            "status": "success",
            "data": result
        })

    # Fallback jika hanya mengirimkan monthly_kwh (kompatibilitas)
    monthly_kwh = data.get('monthly_kwh')
    tariff_per_kwh = data.get('tariff_per_kwh')

    is_valid_kwh, kwh_val = validate_numeric(monthly_kwh, "monthly_kwh", min_value=0.0)
    if not is_valid_kwh:
        return jsonify({
            "status": "error",
            "message": kwh_val
        }), 400

    tariff_val = None
    if tariff_per_kwh is not None:
        is_valid_tariff, tariff_val = validate_numeric(tariff_per_kwh, "tariff_per_kwh", min_value=0.0)
        if not is_valid_tariff:
            return jsonify({
                "status": "error",
                "message": tariff_val
            }), 400

    cost_val = CostService.calculate(kwh_val, tariff_val)
    tariff = tariff_val if tariff_val is not None else CostService.DEFAULT_TARIFF

    return jsonify({
        "status": "success",
        "data": {
            "daily_cost": round(cost_val / 30.0, 2),
            "monthly_cost": cost_val,
            "yearly_cost": round(cost_val / 30.0 * 365.0, 2),
            "tariff_per_kwh": float(tariff)
        }
    })
