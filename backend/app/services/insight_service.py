class InsightService:
    @staticmethod
    def generate_insights(devices: list, total_daily_kwh: float, total_monthly_kwh: float) -> dict:
        """
        Insight Engine: Rule-Based System (Tanpa AI/LLM API)
        Menerima hasil perhitungan energi seluruh perangkat dan mengembalikan rekomendasi serta skor energi.
        
        Setiap rekomendasi terstruktur sebagai dict:
        {
            "type": "danger" | "warning" | "info" | "success",
            "icon": "fa-solid fa-...",
            "title": "Judul Insight",
            "description": "Deskripsi rinci insight"
        }
        """
        insights = []
        
        if not devices:
            return {
                "energy_score": 100,
                "category": "Excellent",
                "insights": []
            }
            
        # Urutkan berdasarkan bulanan kWh menurun untuk mencari perangkat terboros
        sorted_devices = sorted(devices, key=lambda x: x.get("monthly_kwh", 0), reverse=True)
        top_device = sorted_devices[0]
        top_name = top_device["device_name"]
        top_pct = top_device["contribution_percentage"]
        
        # --- RULE 1: Dominasi Beban (> 50% konsumsi bulanan) ---
        if top_pct > 50.0:
            insights.append({
                "type": "danger",
                "icon": "fa-solid fa-triangle-exclamation",
                "title": "Beban Dominan Terdeteksi",
                "description": f"Perangkat <strong>{top_name}</strong> menyumbang <strong>{top_pct}%</strong> konsumsi bulanan rumah Anda. Perangkat ini adalah penyumbang terbesar dan harus menjadi fokus utama penghematan."
            })
        else:
            insights.append({
                "type": "info",
                "icon": "fa-solid fa-chart-pie",
                "title": "Penyumbang Terbesar",
                "description": f"Perangkat <strong>{top_name}</strong> adalah penyumbang energi terbesar di rumah Anda dengan kontribusi sebesar <strong>{top_pct}%</strong>."
            })
            
        # --- RULE 2: Total Konsumsi Listrik Rumah Tangga ---
        if total_monthly_kwh > 300.0:
            insights.append({
                "type": "danger",
                "icon": "fa-solid fa-bolt-lightning",
                "title": "Konsumsi Sangat Tinggi",
                "description": f"Total konsumsi listrik bulanan Anda sangat tinggi (<strong>{round(total_monthly_kwh, 1)} kWh</strong>), melebihi batas 300 kWh/bulan. Pertimbangkan audit energi untuk menghindari lonjakan tagihan."
            })
        elif total_monthly_kwh > 150.0:
            insights.append({
                "type": "warning",
                "icon": "fa-solid fa-circle-exclamation",
                "title": "Konsumsi Di Atas Rata-rata",
                "description": f"Total konsumsi listrik bulanan Anda sedang menuju tinggi (<strong>{round(total_monthly_kwh, 1)} kWh</strong>). Batasi penggunaan alat berdaya besar untuk tetap efisien."
            })
        else:
            insights.append({
                "type": "success",
                "icon": "fa-solid fa-leaf",
                "title": "Konsumsi Efisien",
                "description": f"Konsumsi bulanan Anda sebesar <strong>{round(total_monthly_kwh, 1)} kWh</strong> berada dalam kategori hemat (di bawah 150 kWh/bulan). Pertahankan kebiasaan baik ini!"
            })
            
        # --- RULE 3: Perangkat Menyala > 12 jam/hari ---
        for dev in devices:
            hours = dev.get("hours_per_day", 0.0)
            name = dev.get("device_name", "Perangkat")
            if 12.0 < hours < 24.0:
                insights.append({
                    "type": "warning",
                    "icon": "fa-solid fa-clock",
                    "title": f"Evaluasi Durasi: {name}",
                    "description": f"Perangkat <strong>{name}</strong> menyala selama <strong>{hours} jam per hari</strong>. Disarankan mengevaluasi durasi penggunaan ini demi efisiensi energi."
                })
                
        # --- RULE 4: Perangkat Aktif 24 Jam ---
        for dev in devices:
            hours = dev.get("hours_per_day", 0.0)
            name = dev.get("device_name", "Perangkat")
            if hours >= 24.0:
                insights.append({
                    "type": "info",
                    "icon": "fa-solid fa-arrows-spin",
                    "title": f"Beban Konstan 24 Jam: {name}",
                    "description": f"Perangkat <strong>{name}</strong> berjalan terus-menerus selama 24 jam. Hal ini normal untuk alat seperti kulkas atau router, tetapi pastikan menggunakan model hemat energi."
                })

        # --- RULE BONUS: Potensi Penghematan (What-if) ---
        top_hours = top_device["hours_per_day"]
        top_watt = top_device["watt"]
        if top_hours > 2.0 and total_daily_kwh > 0:
            saved_daily_kwh = (top_watt * 2.0) / 1000.0
            reduction_pct = (saved_daily_kwh / total_daily_kwh) * 100.0
            insights.append({
                "type": "success",
                "icon": "fa-solid fa-hand-holding-dollar",
                "title": "Tips Potensi Penghematan",
                "description": f"Jika penggunaan <strong>{top_name}</strong> dikurangi 2 jam/hari, total konsumsi energi harian rumah Anda akan turun sekitar <strong>{round(reduction_pct, 1)}%</strong>."
            })

        # --- PERHITUNGAN ENERGY SCORE ---
        # Dirancang mudah dikembangkan. Skor dasar dimulai dari 100.
        score = 100.0
        
        # A. Pengurangan berdasarkan volume konsumsi bulanan (target ideal < 150 kWh)
        if total_monthly_kwh > 150.0:
            kwh_deduction = min(30.0, (total_monthly_kwh - 150.0) * 0.1)
            score -= kwh_deduction
            
        # B. Pengurangan berdasarkan rata-rata jam penggunaan perangkat harian
        avg_hours = sum(d["hours_per_day"] for d in devices) / len(devices)
        if avg_hours > 8.0:
            hours_deduction = min(20.0, (avg_hours - 8.0) * 1.5)
            score -= hours_deduction
            
        # C. Pengurangan dari perangkat beban berat (>500W) yang beroperasi > 4 jam
        heavy_devices = [d for d in devices if d["watt"] > 500.0 and d["hours_per_day"] > 4.0]
        if heavy_devices:
            score -= min(15.0, (5.0 * len(heavy_devices)))
            
        # D. Pengurangan akibat adanya satu beban dominan (>50% kontribusi)
        if top_pct > 50.0:
            score -= 8.0
            
        # Batasi skor antara 10 hingga 100
        score = max(10, min(100, round(score)))
        
        # Klasifikasikan kategori
        if score >= 90:
            category = "Excellent"
        elif score >= 70:
            category = "Good"
        elif score >= 50:
            category = "Average"
        else:
            category = "Needs Improvement"
            
        return {
            "energy_score": score,
            "category": category,
            "insights": insights
        }
