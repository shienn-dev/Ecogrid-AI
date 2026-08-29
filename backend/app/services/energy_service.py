class EnergyService:
    @staticmethod
    def calculate(watt: float, hours_per_day: float) -> dict:
        """
        Menghitung konsumsi energi harian, bulanan (30 hari), dan tahunan (365 hari) dalam kWh.
        Formula:
        - kWh Harian = (Watt * Jam/Hari) / 1000
        - kWh Bulanan = kWh Harian * 30 hari
        - kWh Tahunan = kWh Harian * 365 hari
        """
        daily_kwh = (watt * hours_per_day) / 1000.0
        monthly_kwh = daily_kwh * 30.0
        yearly_kwh = daily_kwh * 365.0

        return {
            "daily_kwh": round(daily_kwh, 4),
            "monthly_kwh": round(monthly_kwh, 4),
            "yearly_kwh": round(yearly_kwh, 4),
        }

    @staticmethod
    def calculate_multiple(devices: list) -> dict:
        """
        Menghitung konsumsi energi untuk beberapa perangkat sekaligus, menghitung kontribusi,
        dan mengurutkan dari konsumsi energi terbesar ke terkecil (ranking terboros).
        """
        results = []
        total_daily_kwh = 0.0
        total_monthly_kwh = 0.0
        total_yearly_kwh = 0.0

        # Hitung konsumsi dasar untuk setiap perangkat
        for dev in devices:
            name = dev.get("device_name", "Perangkat")
            watt = float(dev.get("watt", 0.0))
            hours = float(dev.get("hours_per_day", 0.0))

            calc = EnergyService.calculate(watt, hours)

            results.append(
                {
                    "device_name": name,
                    "watt": watt,
                    "hours_per_day": hours,
                    "daily_kwh": calc["daily_kwh"],
                    "monthly_kwh": calc["monthly_kwh"],
                    "yearly_kwh": calc["yearly_kwh"],
                }
            )

            total_daily_kwh += calc["daily_kwh"]
            total_monthly_kwh += calc["monthly_kwh"]
            total_yearly_kwh += calc["yearly_kwh"]

        # Hitung persentase kontribusi energi tiap perangkat ke total bulanan
        for res in results:
            if total_monthly_kwh > 0:
                pct = (res["monthly_kwh"] / total_monthly_kwh) * 100.0
            else:
                pct = 0.0
            res["contribution_percentage"] = round(pct, 2)

        # Membuat salinan daftar perangkat yang diurutkan untuk ranking terboros
        ranked_devices = sorted(
            [
                {
                    "device_name": r["device_name"],
                    "monthly_kwh": r["monthly_kwh"],
                    "contribution_percentage": r["contribution_percentage"],
                }
                for r in results
            ],
            key=lambda x: x["monthly_kwh"],
            reverse=True,
        )

        return {
            "devices": results,
            "total_daily_kwh": round(total_daily_kwh, 4),
            "total_monthly_kwh": round(total_monthly_kwh, 4),
            "total_yearly_kwh": round(total_yearly_kwh, 4),
            "ranked_devices": ranked_devices,
        }
