import json
from datetime import UTC, datetime

from app.database import db


class Simulation(db.Model):
    __tablename__ = "simulations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    total_daily_kwh = db.Column(db.Float, nullable=False)
    total_monthly_kwh = db.Column(db.Float, nullable=False)
    total_yearly_kwh = db.Column(db.Float, nullable=False)
    monthly_cost = db.Column(db.Float, nullable=False)
    monthly_carbon = db.Column(db.Float, nullable=False)
    energy_score = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(32), nullable=False)
    devices_json = db.Column(db.Text, nullable=False)  # JSON string

    def to_dict(self):
        try:
            devices = json.loads(self.devices_json) if self.devices_json else []
        except Exception:
            devices = []
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "total_daily_kwh": self.total_daily_kwh,
            "total_monthly_kwh": self.total_monthly_kwh,
            "total_yearly_kwh": self.total_yearly_kwh,
            "monthly_cost": self.monthly_cost,
            "monthly_carbon": self.monthly_carbon,
            "energy_score": self.energy_score,
            "category": self.category,
            "devices": devices,
        }
