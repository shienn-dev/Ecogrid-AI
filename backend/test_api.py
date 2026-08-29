import json
import os
import sys
import unittest

# Memasukkan direktori backend ke sys.path untuk impor modul app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.config import TestingConfig
from app.services.insight_service import InsightService


class EcoGridTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        # Ensure DB tables exist for history tests
        with self.app.app_context():
            try:
                from app.database import db

                db.create_all()
            except Exception:
                pass

    def test_home_status(self):
        """Memverifikasi endpoint root '/' merespon dengan benar"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("API is running", data["message"])

    def test_energy_calculate_single_success(self):
        """Memverifikasi perhitungan energi berhasil untuk single device (fallback)"""
        payload = {"device_name": "AC", "watt": 150, "hours_per_day": 8}
        response = self.client.post(
            "/api/energy/calculate", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["total_daily_kwh"], 1.2)
        self.assertEqual(data["data"]["total_monthly_kwh"], 36.0)
        self.assertEqual(data["data"]["total_yearly_kwh"], 438.0)  # 1.2 * 365
        self.assertEqual(len(data["data"]["devices"]), 1)
        self.assertEqual(data["data"]["devices"][0]["device_name"], "AC")
        self.assertIn("energy_score", data["data"])
        self.assertIn("category", data["data"])
        self.assertIn("insights", data["data"])

    def test_energy_calculate_multiple_success(self):
        """Memverifikasi perhitungan energi berhasil dengan beberapa perangkat sekaligus"""
        payload = {
            "devices": [
                {"device_name": "AC", "watt": 150, "hours_per_day": 8},
                {"device_name": "Kulkas", "watt": 200, "hours_per_day": 24},
            ]
        }
        response = self.client.post(
            "/api/energy/calculate", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        # AC: (150*8)/1000 = 1.2 kWh/hari, 36.0 kWh/bulan, 438 kWh/tahun
        # Kulkas: (200*24)/1000 = 4.8 kWh/hari, 144.0 kWh/bulan, 1752 kWh/tahun
        # Total: 6.0 kWh/hari, 180.0 kWh/bulan, 2190 kWh/tahun
        self.assertEqual(data["data"]["total_daily_kwh"], 6.0)
        self.assertEqual(data["data"]["total_monthly_kwh"], 180.0)
        self.assertEqual(data["data"]["total_yearly_kwh"], 2190.0)

        # Cek kontribusi (Kulkas = 144/180 = 80%, AC = 36/180 = 20%)
        self.assertEqual(data["data"]["devices"][0]["contribution_percentage"], 20.0)
        self.assertEqual(data["data"]["devices"][1]["contribution_percentage"], 80.0)

        # Cek ranking (Kulkas pertama karena konsumsi terbesar)
        self.assertEqual(data["data"]["ranked_devices"][0]["device_name"], "Kulkas")
        self.assertEqual(data["data"]["ranked_devices"][1]["device_name"], "AC")
        self.assertIn("energy_score", data["data"])
        self.assertIn("category", data["data"])
        self.assertIn("insights", data["data"])
        self.assertTrue(len(data["data"]["insights"]) > 0)

    def test_energy_calculate_invalid_watt(self):
        """Memverifikasi validasi input watt <= 0 ditolak"""
        payload = {"device_name": "AC", "watt": 0, "hours_per_day": 8}
        response = self.client.post(
            "/api/energy/calculate", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")
        self.assertIn("tidak boleh kurang dari", data["message"])

    def test_energy_calculate_invalid_hours(self):
        """Memverifikasi validasi input jam > 24 atau <= 0 ditolak"""
        payload = {"device_name": "AC", "watt": 150, "hours_per_day": 24.1}
        response = self.client.post(
            "/api/energy/calculate", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")
        self.assertIn("tidak boleh melebihi 24.0", data["message"])

    def test_cost_calculate_multi_period_success(self):
        """Memverifikasi perhitungan biaya dengan format harian, bulanan, tahunan"""
        payload = {
            "daily_kwh": 6.0,
            "monthly_kwh": 180.0,
            "yearly_kwh": 2190.0,
            "tariff_per_kwh": 1500.0,
        }
        response = self.client.post(
            "/api/cost/calculate", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["daily_cost"], 6.0 * 1500.0)
        self.assertEqual(data["data"]["monthly_cost"], 180.0 * 1500.0)
        self.assertEqual(data["data"]["yearly_cost"], 2190.0 * 1500.0)

    def test_carbon_calculate_multi_period_success(self):
        """Memverifikasi perhitungan karbon dengan format harian, bulanan, tahunan"""
        payload = {
            "daily_kwh": 6.0,
            "monthly_kwh": 180.0,
            "yearly_kwh": 2190.0,
            "emission_factor": 0.87,
        }
        response = self.client.post(
            "/api/carbon/calculate", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["data"]["daily_carbon_kg"], round(6.0 * 0.87, 4))
        self.assertEqual(data["data"]["monthly_carbon_kg"], round(180.0 * 0.87, 4))
        self.assertEqual(data["data"]["yearly_carbon_kg"], round(2190.0 * 0.87, 4))

    def test_insight_engine_rules(self):
        """Memverifikasi penegakan aturan rule-based pada Insight Engine"""
        # Skenario 1: Dominasi beban (>50%) & perangkat aktif 24 jam & >300 kWh
        devices = [
            {
                "device_name": "AC",
                "watt": 1000,
                "hours_per_day": 10,
                "monthly_kwh": 300.0,
                "contribution_percentage": 75.0,
            },
            {
                "device_name": "Kulkas",
                "watt": 100,
                "hours_per_day": 24,
                "monthly_kwh": 72.0,
                "contribution_percentage": 18.0,
            },
            {
                "device_name": "Lampu",
                "watt": 25,
                "hours_per_day": 12,
                "monthly_kwh": 9.0,
                "contribution_percentage": 2.25,
            },
        ]
        res = InsightService.generate_insights(devices, 12.7, 381.0)
        insights = res["insights"]

        # Harus memicu Rule 1: Beban Dominan Terdeteksi
        self.assertTrue(any(i["title"] == "Beban Dominan Terdeteksi" for i in insights))
        # Harus memicu Rule 2: Konsumsi Sangat Tinggi (> 300 kWh)
        self.assertTrue(any(i["title"] == "Konsumsi Sangat Tinggi" for i in insights))
        # Harus memicu Rule 4: Beban Konstan 24 Jam
        self.assertTrue(any("Beban Konstan 24 Jam" in i["title"] for i in insights))

        # Skenario 2: Perangkat > 12 jam (misal 15 jam)
        devices_2 = [
            {
                "device_name": "Kipas",
                "watt": 50,
                "hours_per_day": 15,
                "monthly_kwh": 22.5,
                "contribution_percentage": 100.0,
            }
        ]
        res_2 = InsightService.generate_insights(devices_2, 0.75, 22.5)
        insights_2 = res_2["insights"]
        # Harus memicu Rule 3: Evaluasi Durasi
        self.assertTrue(any("Evaluasi Durasi" in i["title"] for i in insights_2))

    def test_energy_score_variations(self):
        """Memverifikasi kalkulasi Energy Score berdasarkan parameter efisiensi"""
        # Skenario efisien (Konsumsi rendah, jam sedang)
        devices_clean = [
            {
                "device_name": "LED TV",
                "watt": 50,
                "hours_per_day": 4,
                "monthly_kwh": 6.0,
                "contribution_percentage": 100.0,
            }
        ]
        res_clean = InsightService.generate_insights(devices_clean, 0.2, 6.0)
        self.assertEqual(res_clean["category"], "Excellent")
        self.assertGreaterEqual(res_clean["energy_score"], 90)

        # Skenario boros (Konsumsi sangat tinggi, beban berat >500W, jam tinggi)
        devices_dirty = [
            {
                "device_name": "AC Besar",
                "watt": 1200,
                "hours_per_day": 12,
                "monthly_kwh": 432.0,
                "contribution_percentage": 80.0,
            },
            {
                "device_name": "Pemanas Air",
                "watt": 1500,
                "hours_per_day": 5,
                "monthly_kwh": 225.0,
                "contribution_percentage": 20.0,
            },
        ]
        res_dirty = InsightService.generate_insights(devices_dirty, 21.9, 657.0)
        self.assertEqual(res_dirty["category"], "Needs Improvement")
        self.assertLess(res_dirty["energy_score"], 50)

    def test_xss_escaping(self):
        """Device name dengan HTML harus di-escape"""
        payload = {
            "devices": [
                {"device_name": "<script>alert(1)</script>", "watt": 100, "hours_per_day": 5}
            ]
        }
        response = self.client.post(
            "/api/energy/calculate", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertNotIn("<script>", data["data"]["devices"][0]["device_name"])
        self.assertIn("&lt;script&gt;", data["data"]["devices"][0]["device_name"])

    def test_device_limit(self):
        """Melebihi 50 perangkat harus ditolak"""
        payload = {
            "devices": [{"device_name": f"d{i}", "watt": 10, "hours_per_day": 1} for i in range(51)]
        }
        response = self.client.post(
            "/api/energy/calculate", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("melebihi batas", json.loads(response.data)["message"])

    def test_unified_cost_carbon(self):
        """Energy calculate harus mengembalikan cost & carbon inline"""
        payload = {"devices": [{"device_name": "AC", "watt": 800, "hours_per_day": 6}]}
        response = self.client.post(
            "/api/energy/calculate", data=json.dumps(payload), content_type="application/json"
        )
        data = json.loads(response.data)["data"]
        self.assertIn("cost", data)
        self.assertIn("carbon", data)
        self.assertAlmostEqual(
            data["cost"]["monthly_cost"], data["total_monthly_kwh"] * 1444.70, places=1
        )
        self.assertAlmostEqual(
            data["carbon"]["monthly_carbon_kg"], data["total_monthly_kwh"] * 0.87, places=2
        )

    def test_cost_yearly_consistency(self):
        """Fallback yearly harus 365/30 bukan 12"""
        payload = {"monthly_kwh": 100}
        res = self.client.post(
            "/api/cost/calculate", data=json.dumps(payload), content_type="application/json"
        )
        data = json.loads(res.data)["data"]
        # yearly = monthly/30*365 * tariff
        expected = round(100 / 30 * 365 * 1444.70, 2)
        self.assertAlmostEqual(data["yearly_cost"], expected, places=1)

    def test_solar_simulate_success(self):
        """Solar simulate menghasilkan kWp dan saving"""
        payload = {"roof_area": 40, "efficiency": 0.20, "sun_hours": 4.5}
        res = self.client.post(
            "/api/solar/simulate", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)["data"]
        self.assertEqual(data["system_kwp"], 8.0)
        self.assertEqual(data["daily_generation"], 36.0)
        self.assertEqual(data["monthly_generation"], 1080.0)
        self.assertGreater(data["estimated_saving"], 0)

    def test_solar_validation(self):
        payload = {"roof_area": 0, "efficiency": 0.20, "sun_hours": 4.5}
        res = self.client.post(
            "/api/solar/simulate", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)

    def test_history_crud(self):
        """Simpan dan list history"""
        # save via ?save=true
        payload = {"devices": [{"device_name": "Kulkas", "watt": 120, "hours_per_day": 24}]}
        res = self.client.post(
            "/api/energy/calculate?save=true",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, 200)
        hid = json.loads(res.data)["data"].get("history_id")
        self.assertIsNotNone(hid)
        # list
        res = self.client.get("/api/history?limit=5")
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(json.loads(res.data)["data"]), 1)
        # get one
        res = self.client.get(f"/api/history/{hid}")
        self.assertEqual(res.status_code, 200)
        # delete
        res = self.client.delete(f"/api/history/{hid}")
        self.assertEqual(res.status_code, 200)

    def test_advisor_analyze(self):
        payload = {"devices": [{"device_name": "AC", "watt": 800, "hours_per_day": 10}]}
        res = self.client.post(
            "/api/advisor/analyze", data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)["data"]
        self.assertIn("recommendations", data)
        self.assertTrue(
            any("AC" in r["title"] or "AC" in r["description"] for r in data["recommendations"])
        )

    def test_advisor_tips(self):
        res = self.client.get("/api/advisor/tips?device=ac")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)["data"]
        self.assertTrue(len(data) > 0)

    def test_security_headers(self):
        res = self.client.get("/")
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.headers.get("X-Frame-Options"), "DENY")


if __name__ == "__main__":
    unittest.main()
