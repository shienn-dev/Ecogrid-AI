import json
import os

from app.services.insight_service import InsightService


class AdvisorService:
    _tips_cache = None

    @classmethod
    def _load_tips(cls):
        if cls._tips_cache is not None:
            return cls._tips_cache
        # try datasets/tips.json relative to backend
        candidates = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "datasets", "tips.json"),
            os.path.join(os.path.dirname(__file__), "..", "..", "datasets", "tips.json"),
            "backend/datasets/tips.json",
            "datasets/tips.json",
        ]
        for p in candidates:
            try:
                ap = os.path.abspath(p)
                if os.path.exists(ap):
                    with open(ap, encoding="utf-8") as f:
                        cls._tips_cache = json.load(f)
                        return cls._tips_cache
            except Exception:
                continue
        cls._tips_cache = []
        return cls._tips_cache

    @staticmethod
    def analyze(devices, total_daily_kwh=None, total_monthly_kwh=None):
        # Normalize devices: expect list of {device_name or name, watt, hours_per_day or hours}
        norm = []
        for d in devices or []:
            name = d.get("device_name") or d.get("name") or "Perangkat"
            watt = d.get("watt", 0)
            hours = d.get("hours_per_day", d.get("hours", 0))
            try:
                monthly_kwh = (
                    float(watt) * float(hours) / 1000 * 30
                    if watt and hours
                    else float(d.get("monthly_kwh", 0) or 0)
                )
            except Exception:
                monthly_kwh = 0
            norm.append(
                {
                    "device_name": str(name),
                    "watt": float(watt or 0),
                    "hours_per_day": float(hours or 0),
                    "monthly_kwh": monthly_kwh,
                    "contribution_percentage": 0,  # will compute if needed
                }
            )
        # Compute contributions if totals given
        if total_monthly_kwh and total_monthly_kwh > 0:
            for n in norm:
                n["contribution_percentage"] = round(
                    (n["monthly_kwh"] / total_monthly_kwh) * 100, 2
                )
        elif norm:
            tot = sum(n["monthly_kwh"] for n in norm)
            if tot > 0:
                for n in norm:
                    n["contribution_percentage"] = round((n["monthly_kwh"] / tot) * 100, 2)
                if total_monthly_kwh is None:
                    total_monthly_kwh = tot
                if total_daily_kwh is None:
                    total_daily_kwh = tot / 30

        if total_daily_kwh is None:
            total_daily_kwh = sum(n["monthly_kwh"] for n in norm) / 30 if norm else 0
        if total_monthly_kwh is None:
            total_monthly_kwh = sum(n["monthly_kwh"] for n in norm)

        insights = InsightService.generate_insights(norm, total_daily_kwh, total_monthly_kwh)
        # Add priority mapping
        prioritized = []
        for ins in insights["insights"]:
            # simple priority: danger=1, warning=2, info=3, success=4
            prio = {"danger": 1, "warning": 2, "info": 3, "success": 4}.get(ins["type"], 3)
            prioritized.append({**ins, "priority": prio})
        prioritized.sort(key=lambda x: x["priority"])
        # Cap 5 max as per Phase6
        prioritized = prioritized[:6]

        return {
            "energy_score": insights["energy_score"],
            "category": insights["category"],
            "recommendations": prioritized,
            "total_daily_kwh": round(total_daily_kwh, 4),
            "total_monthly_kwh": round(total_monthly_kwh, 4),
        }

    @classmethod
    def get_tips(cls, device_query=None):
        tips_data = cls._load_tips()
        if not device_query:
            return tips_data
        q = device_query.lower()
        filtered = []
        for entry in tips_data:
            kws = [k.lower() for k in entry.get("keywords", [])]
            if any(k in q for k in kws) or entry.get("device") == q:
                filtered.append(entry)
        if not filtered:
            # fallback to umum
            filtered = [e for e in tips_data if e.get("device") == "umum"]
        return filtered
