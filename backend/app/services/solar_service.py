class SolarService:
    """
    Solar Potential Simulator — deterministic estimation.
    Formula:
      system_kwp = roof_area * efficiency * 1.0  (1kW per m² at 100% eff, STC)
      daily_generation = system_kwp * sun_hours
      monthly_generation = daily * 30
      yearly_generation = daily * 365
      estimated_saving = monthly_generation * tariff
      carbon_reduction = monthly_generation * emission_factor
    All estimates, not physical measurements — assumptions documented.
    """

    @staticmethod
    def calculate(
        roof_area: float,
        efficiency: float = 0.20,
        sun_hours: float = 4.5,
        tariff_per_kwh: float = 1444.70,
        emission_factor: float = 0.87,
    ) -> dict:
        system_kwp = roof_area * efficiency * 1.0
        daily_generation = system_kwp * sun_hours
        monthly_generation = daily_generation * 30.0
        yearly_generation = daily_generation * 365.0
        estimated_saving = monthly_generation * tariff_per_kwh
        yearly_saving = yearly_generation * tariff_per_kwh
        carbon_reduction = monthly_generation * emission_factor
        yearly_carbon = yearly_generation * emission_factor
        # Simple payback: system cost estimate Rp 15jt per kWp (illustrative)
        cost_per_kwp = 15000000.0
        system_cost = system_kwp * cost_per_kwp
        payback_years = (system_cost / yearly_saving) if yearly_saving > 0 else None
        return {
            "system_kwp": round(system_kwp, 3),
            "daily_generation": round(daily_generation, 3),
            "monthly_generation": round(monthly_generation, 3),
            "yearly_generation": round(yearly_generation, 3),
            "estimated_saving": round(estimated_saving, 2),
            "yearly_saving": round(yearly_saving, 2),
            "carbon_reduction_kg": round(carbon_reduction, 3),
            "yearly_carbon_reduction_kg": round(yearly_carbon, 3),
            "system_cost_estimate": round(system_cost, 2),
            "payback_years": round(payback_years, 2) if payback_years is not None else None,
            "assumptions": {
                "irradiance": "1 kW/m² STC",
                "formula": "kWp = area × efficiency × 1kW/m²; generation = kWp × sun_hours",
                "note": "Estimasi saja — tanpa shading, tilt, orientasi, degradasi, atau variasi cuaca.",
            },
            "inputs": {
                "roof_area": roof_area,
                "efficiency": efficiency,
                "sun_hours": sun_hours,
                "tariff_per_kwh": tariff_per_kwh,
                "emission_factor": emission_factor,
            },
        }
