import json

from app.database import db
from app.models.simulation import Simulation


def save_simulation(
    total_daily_kwh,
    total_monthly_kwh,
    total_yearly_kwh,
    monthly_cost,
    monthly_carbon,
    energy_score,
    category,
    devices,
):
    try:
        sim = Simulation(
            total_daily_kwh=float(total_daily_kwh),
            total_monthly_kwh=float(total_monthly_kwh),
            total_yearly_kwh=float(total_yearly_kwh),
            monthly_cost=float(monthly_cost),
            monthly_carbon=float(monthly_carbon),
            energy_score=int(energy_score),
            category=str(category),
            devices_json=json.dumps(devices),
        )
        db.session.add(sim)
        db.session.commit()
        return sim
    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        # fallback: log and return None
        print(f"save_simulation failed: {e}")
        return None


def list_simulations(limit=20, offset=0):
    q = Simulation.query.order_by(Simulation.created_at.desc()).limit(limit).offset(offset).all()
    return q


def get_simulation(sid):
    return db.session.get(Simulation, sid)


def delete_simulation(sid):
    sim = db.session.get(Simulation, sid)
    if not sim:
        return False
    db.session.delete(sim)
    db.session.commit()
    return True
