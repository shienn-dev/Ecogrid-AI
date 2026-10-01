class SolarService:
    """
    Solar Potential Simulator — deterministic estimation.

    Industry formula (IEC 61724 / NREL PVWatts):
        system_kwp       = roof_area × usable_area_factor × efficiency × 1 kW/m² (STC)
        daily_generation = system_kwp × peak_sun_hours × performance_ratio

    Why the correction factors exist (see docs/research_references.md):
      • usable_area_factor (~0.85): real roof area is never 100% panel — windows,
        vents, chimneys, walkways and setbacks reduce usable area. Assuming 1.0
        overestimates capacity.
      • performance_ratio (~0.75): real systems lose energy to inverter
        conversion (~4%), wiring (~2%), soiling (~2-3%), temperature derating
        (~8-10% in tropical heat), mismatch (~2%) and shading. Assuming 1.0
        overestimates generation by ~33%.

    All outputs are ESTIMATES, not physical measurements. Assumptions are
    returned in the response so they can be shown to the user.
    """

    # Source: NREL PVWatts default PR for residential; IEC 61724 definition.
    DEFAULT_PERFORMANCE_RATIO = 0.75
    # Source: industry rule-of-thumb for pitched residential roofs.
    DEFAULT_USABLE_AREA_FACTOR = 0.85
    # Source: Indonesian rooftop PV installed cost range Rp 12-18 jt/kWp (IESR/ESDM 2024).
    DEFAULT_COST_PER_KWP = 15_000_000.0

    @staticmethod
    def calculate(
        roof_area: float,
        efficiency: float = 0.20,
        sun_hours: float = 4.5,
        tariff_per_kwh: float = 1444.70,
        emission_factor: float = 0.68,
        performance_ratio: float | None = None,
        usable_area_factor: float | None = None,
        cost_per_kwp: float | None = None,
    ) -> dict:
        pr = (
            performance_ratio
            if performance_ratio is not None
            else SolarService.DEFAULT_PERFORMANCE_RATIO
        )
        uaf = (
            usable_area_factor
            if usable_area_factor is not None
            else SolarService.DEFAULT_USABLE_AREA_FACTOR
        )
        cpp = cost_per_kwp if cost_per_kwp is not None else SolarService.DEFAULT_COST_PER_KWP

        # Usable area after physical obstructions
        usable_area = roof_area * uaf
        # Nameplate capacity at Standard Test Conditions (1000 W/m²)
        system_kwp = usable_area * efficiency * 1.0
        # Raw DC-equivalent then derated by performance ratio
        daily_generation = system_kwp * sun_hours * pr
        monthly_generation = daily_generation * 30.0
        yearly_generation = daily_generation * 365.0

        estimated_saving = monthly_generation * tariff_per_kwh
        yearly_saving = yearly_generation * tariff_per_kwh

        carbon_reduction = monthly_generation * emission_factor
        yearly_carbon = yearly_generation * emission_factor

        system_cost = system_kwp * cpp
        payback_years = (system_cost / yearly_saving) if yearly_saving > 0 else None

        return {
            "system_kwp": round(system_kwp, 3),
            "usable_area_m2": round(usable_area, 2),
            "daily_generation": round(daily_generation, 3),
            "monthly_generation": round(monthly_generation, 3),
            "yearly_generation": round(yearly_generation, 3),
            "estimated_saving": round(estimated_saving, 2),
            "yearly_saving": round(yearly_saving, 2),
            "carbon_reduction_kg": round(carbon_reduction, 3),
            "yearly_carbon_reduction_kg": round(yearly_carbon, 3),
            "system_cost_estimate": round(system_cost, 2),
            "payback_years": round(payback_years, 2) if payback_years is not None else None,
            # Offset relative to household usage — filled by caller if usage known
            "assumptions": {
                "irradiance": "1 kW/m² STC (1000 W/m²)",
                "performance_ratio": pr,
                "usable_area_factor": uaf,
                "cost_per_kwp": cpp,
                "formula": (
                    "usable_area = roof × usable_factor; "
                    "kWp = usable_area × efficiency; "
                    "daily = kWp × sun_hours × performance_ratio"
                ),
                "note": (
                    "Estimasi saja — memperhitungkan rugi inverter, kabel, suhu, "
                    "kotoran, dan shading melalui Performance Ratio. Belum "
                    "memodelkan tilt, azimuth, atau variasi cuaca musiman."
                ),
                "pr_source": "NREL PVWatts default / IEC 61724",
            },
            "inputs": {
                "roof_area": roof_area,
                "efficiency": efficiency,
                "sun_hours": sun_hours,
                "tariff_per_kwh": tariff_per_kwh,
                "emission_factor": emission_factor,
            },
        }

    @staticmethod
    def calculate_with_offset(
        household_monthly_kwh: float | None = None,
        **kwargs,
    ) -> dict:
        """Solar estimate plus how much of the household usage it offsets."""
        result = SolarService.calculate(**kwargs)
        if household_monthly_kwh and household_monthly_kwh > 0:
            coverage = result["monthly_generation"] / household_monthly_kwh
            result["offset"] = {
                "household_monthly_kwh": round(household_monthly_kwh, 3),
                "coverage_ratio": round(coverage, 4),
                "coverage_percent": round(min(coverage, 1.0) * 100, 1),
                "remaining_monthly_kwh": round(
                    max(household_monthly_kwh - result["monthly_generation"], 0.0), 3
                ),
                "surplus_monthly_kwh": round(
                    max(result["monthly_generation"] - household_monthly_kwh, 0.0), 3
                ),
            }
        else:
            result["offset"] = None
        return result
