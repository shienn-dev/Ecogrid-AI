class CarbonService:
    # Faktor emisi rata-rata grid Indonesia: ~0.87 kg CO2 / kWh
    DEFAULT_EMISSION_FACTOR = 0.87

    @staticmethod
    def calculate(kwh: float, emission_factor: float = None) -> float:
        """
        Menghitung emisi karbon untuk jumlah kWh tertentu.
        """
        factor = emission_factor if emission_factor is not None else CarbonService.DEFAULT_EMISSION_FACTOR
        return round(kwh * factor, 4)

    @staticmethod
    def calculate_all(daily_kwh: float, monthly_kwh: float, yearly_kwh: float, emission_factor: float = None) -> dict:
        """
        Menghitung perkiraan emisi karbon (kg CO2) untuk periode harian, bulanan, dan tahunan sekaligus.
        """
        factor = emission_factor if emission_factor is not None else CarbonService.DEFAULT_EMISSION_FACTOR
        return {
            "daily_carbon_kg": CarbonService.calculate(daily_kwh, factor),
            "monthly_carbon_kg": CarbonService.calculate(monthly_kwh, factor),
            "yearly_carbon_kg": CarbonService.calculate(yearly_kwh, factor),
            "emission_factor": float(factor)
        }
