class CostService:
    # Tarif Listrik R-1/TR 1300 VA ke atas per 2026 kurang lebih Rp 1.444,70
    DEFAULT_TARIFF = 1444.70

    @staticmethod
    def calculate(kwh: float, tariff_per_kwh: float = None) -> float:
        """
        Menghitung biaya listrik untuk jumlah kWh tertentu.
        """
        tariff = tariff_per_kwh if tariff_per_kwh is not None else CostService.DEFAULT_TARIFF
        return round(kwh * tariff, 2)

    @staticmethod
    def calculate_all(daily_kwh: float, monthly_kwh: float, yearly_kwh: float, tariff_per_kwh: float = None) -> dict:
        """
        Menghitung perkiraan biaya listrik untuk periode harian, bulanan, dan tahunan sekaligus.
        """
        tariff = tariff_per_kwh if tariff_per_kwh is not None else CostService.DEFAULT_TARIFF
        return {
            "daily_cost": CostService.calculate(daily_kwh, tariff),
            "monthly_cost": CostService.calculate(monthly_kwh, tariff),
            "yearly_cost": CostService.calculate(yearly_kwh, tariff),
            "tariff_per_kwh": float(tariff)
        }
