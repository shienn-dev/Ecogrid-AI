# feat.md

# EcoGrid AI Feature Specification

Version: MVP v1.0

---

# 1. ELECTRICITY USAGE TRACKER

## Tujuan

Menghitung konsumsi energi listrik berdasarkan perangkat yang digunakan pengguna.

---

## Deskripsi

Pengguna dapat menambahkan daftar perangkat elektronik yang digunakan setiap hari.

Setiap perangkat memiliki:

* Nama perangkat
* Daya (Watt)
* Durasi penggunaan per hari (Jam)

Sistem akan menghitung:

* Konsumsi energi harian
* Konsumsi energi bulanan
* Konsumsi energi tahunan

---

## Input

### Device Name

Contoh:

* Laptop
* AC
* Kulkas
* Lampu

Tipe:
String

---

### Power Consumption

Satuan:
Watt (W)

Contoh:

* Laptop = 65
* AC = 800
* TV = 120

Tipe:
Integer

---

### Usage Duration

Satuan:
Jam/Hari

Contoh:

* 8
* 12
* 24

Tipe:
Float

---

## Formula

Energi Harian:

kWh = (Watt × Jam Penggunaan) / 1000

Contoh:

65 × 8 / 1000

= 0.52 kWh

---

Energi Bulanan:

kWh Harian × 30

---

Energi Tahunan:

kWh Harian × 365

---

## Output

* Daily Energy Usage
* Monthly Energy Usage
* Yearly Energy Usage

---

# 2. ELECTRICITY COST CALCULATOR

## Tujuan

Menghitung estimasi biaya listrik berdasarkan konsumsi energi.

---

## Deskripsi

Sistem mengambil total konsumsi listrik dari Electricity Usage Tracker lalu menghitung estimasi biaya.

---

## Input

Total Energy Usage (kWh)

Tarif PLN

Default:

Rp1.444,70 / kWh

(Nantinya bisa diubah oleh pengguna)

---

## Formula

Biaya = kWh × Tarif

---

## Output

* Biaya Harian
* Biaya Bulanan
* Biaya Tahunan

---

# 3. CARBON FOOTPRINT CALCULATOR

## Tujuan

Menunjukkan dampak lingkungan dari penggunaan listrik.

---

## Deskripsi

Menghitung emisi karbon berdasarkan konsumsi energi listrik.

---

## Input

Total konsumsi energi (kWh)

---

## Faktor Emisi

Gunakan asumsi awal:

0.85 kg CO₂ / kWh

(Bisa diperbarui berdasarkan data resmi di masa depan)

---

## Formula

Emisi Karbon = kWh × Faktor Emisi

---

## Output

* CO₂ Harian
* CO₂ Bulanan
* CO₂ Tahunan

---

## Insight

Contoh:

"Penggunaan listrik Anda menghasilkan sekitar 180 kg CO₂ per bulan."

---

# 4. SOLAR PANEL SIMULATOR

## Tujuan

Memberikan estimasi manfaat penggunaan panel surya.

---

## Deskripsi

Pengguna memasukkan kondisi rumah dan sistem akan memperkirakan produksi energi panel surya.

---

## Input

### Roof Area

Satuan:
m²

Contoh:
40

---

### Solar Panel Efficiency

Default:
20%

---

### Peak Sun Hours

Default:
4.5 jam/hari

---

## Formula

Potensi Daya:

Area × Efisiensi × 1000

---

Produksi Harian:

Kapasitas Sistem × Peak Sun Hours

---

Produksi Bulanan:

Produksi Harian × 30

---

## Output

* Kapasitas Sistem (kWp)
* Produksi Harian
* Produksi Bulanan
* Penghematan Biaya

---

## Insight

Contoh:

"Panel surya dapat mengurangi tagihan listrik hingga Rp450.000 per bulan."

---

# 5. AI ENERGY ADVISOR

## Tujuan

Memberikan rekomendasi penghematan energi.

---

## Deskripsi

Versi MVP menggunakan Rule-Based System.

Belum menggunakan Machine Learning.

---

## Rule 1

Jika:

AC > 8 jam/hari

Maka:

"Tingkat penggunaan AC cukup tinggi. Pertimbangkan menaikkan suhu 1-2°C."

---

## Rule 2

Jika:

Lampu > 10 jam/hari

Maka:

"Pertimbangkan menggunakan lampu LED hemat energi."

---

## Rule 3

Jika:

Konsumsi listrik > 300 kWh/bulan

Maka:

"Konsumsi listrik Anda tergolong tinggi. Evaluasi perangkat dengan penggunaan terbesar."

---

## Rule 4

Jika:

Atap > 30 m²

Maka:

"Rumah Anda memiliki potensi yang baik untuk pemasangan panel surya."

---

## Output

Daftar rekomendasi personal.

Contoh:

* Kurangi penggunaan AC
* Gunakan lampu LED
* Pertimbangkan panel surya

---

# 6. DASHBOARD

## Tujuan

Menampilkan seluruh data dalam satu halaman.

---

## Widget

### Energy Summary Card

Menampilkan:

* Daily Usage
* Monthly Usage
* Yearly Usage

---

### Cost Summary Card

Menampilkan:

* Daily Cost
* Monthly Cost
* Yearly Cost

---

### Carbon Summary Card

Menampilkan:

* Daily Carbon
* Monthly Carbon
* Yearly Carbon

---

### Solar Potential Card

Menampilkan:

* Potensi Produksi
* Potensi Penghematan

---

### AI Recommendation Card

Menampilkan rekomendasi dari AI Energy Advisor.

---

# CHARTS

## Energy Usage Chart

Grafik konsumsi energi.

---

## Cost Chart

Grafik biaya listrik.

---

## Carbon Emission Chart

Grafik emisi karbon.

---

# FUTURE FEATURES

* Login System
* User Profile
* Historical Data
* Smart Meter Integration
* Weather API
* Solar Irradiance API
* Machine Learning Recommendation System
* LLM Energy Assistant
* Mobile Application
