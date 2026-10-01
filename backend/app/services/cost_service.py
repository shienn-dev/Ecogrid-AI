from app.config import Config


class CostService:
    # Tarif default R-1/TR 1300 VA (paling umum non-subsidi).
    # Source: PLN Tarif Adjustment — lihat docs/research_references.md.
    # Configurable via DEFAULT_TARIFF env.
    DEFAULT_TARIFF = Config.DEFAULT_TARIFF

    @staticmethod
    def calculate(kwh: float, tariff_per_kwh: float | None = None) -> float:
        """Menghitung biaya listrik untuk jumlah kWh tertentu."""
        tariff = tariff_per_kwh if tariff_per_kwh is not None else CostService.DEFAULT_TARIFF
        return round(kwh * tariff, 2)

    @staticmethod
    def calculate_all(
        daily_kwh: float,
        monthly_kwh: float,
        yearly_kwh: float,
        tariff_per_kwh: float | None = None,
    ) -> dict:
        """
        Menghitung perkiraan biaya listrik (harian, bulanan, tahunan) sekaligus.
        """
        tariff = tariff_per_kwh if tariff_per_kwh is not None else CostService.DEFAULT_TARIFF
        return {
            "daily_cost": CostService.calculate(daily_kwh, tariff),
            "monthly_cost": CostService.calculate(monthly_kwh, tariff),
            "yearly_cost": CostService.calculate(yearly_kwh, tariff),
            "tariff_per_kwh": float(tariff),
        }
