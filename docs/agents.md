# Riwayat Pengembangan EcoGrid AI (agents.md)

Dokumen ini mencatat seluruh riwayat pengerjaan, refaktorisasi, keputusan arsitektur, dan fitur yang telah diimplementasikan oleh Agent AI pada proyek **EcoGrid AI**.

---

## 📅 Fase 1: MVP V1 (Kalkulator Energi Tunggal)

### 1. Inisialisasi Backend (Flask)
* **Arsitektur**: Menggunakan *Modular Clean Architecture* dengan Blueprint Flask untuk memisahkan rute, logika bisnis (services), dan utilitas validasi.
* **Komponen yang Dibuat**:
  * `backend/app.py`: Entry point server utama yang berjalan pada port 5000.
  * `backend/app/__init__.py`: Factory pattern Flask yang mengaktifkan CORS (`flask-cors`) agar dapat diakses oleh frontend eksternal.
  * `backend/app/utils/validator.py`: Utilitas pembantu untuk validasi tipe data numerik.
  * `backend/app/services/`:
    * `energy_service.py`: Logika konversi Watt & Jam ke kWh (Harian & Bulanan).
    * `cost_service.py`: Logika perkiraan biaya listrik PLN (tarif default Rp 1.444,70 / kWh).
    * `carbon_service.py`: Perhitungan emisi karbon (faktor emisi default 0.87 kg CO2 / kWh).
  * `backend/app/routes/`:
    * `energy_routes.py`, `cost_routes.py`, `carbon_routes.py`: Menerima payload JSON, memvalidasi input, memanggil service terkait, dan mengembalikan respons terstandarisasi.
  * `backend/test_api.py`: Automated unit tests untuk memverifikasi fungsionalitas seluruh endpoint API.

### 2. Antarmuka Frontend (HTML5 & CSS3)
* **Desain**: Tampilan modern bertema ramah lingkungan dengan gaya *Glassmorphism* (latar belakang transparan blur, bayangan lembut, gradasi warna hijau ke teal).
* **Integrasi**: Menghubungkan form input dengan API backend secara asinkron menggunakan Fetch API (`async/await` dan `Promise.all` untuk request paralel).

---

## 📅 Fase 1.2: Dukungan Multi-Perangkat, Kalkulasi Tahunan & Ranking Terboros

### 1. Refaktorisasi Backend (Multi-Device & Multi-Period)
* **`energy_service.py`**:
  * Menghitung nilai harian, bulanan (30 hari), dan tahunan (365 hari) kWh.
  * Menghitung kontribusi persen energi perangkat terhadap total konsumsi: `(kwh_perangkat / total_kwh) * 100`.
  * Mengurutkan daftar perangkat secara descending (menurun) untuk peringkat konsumsi (ranking terboros).
* **`cost_service.py` & `carbon_service.py`**:
  * Menambahkan fungsi `calculate_all` untuk menghitung biaya dan emisi karbon untuk 3 periode sekaligus (Harian, Bulanan, Tahunan) dalam satu kali request paralel.
* **Penegakan Validasi Ketat**:
  * Nama Perangkat wajib diisi.
  * Daya Listrik (`watt`) wajib lebih besar dari `0`.
  * Jam Penggunaan (`hours_per_day`) wajib lebih besar dari `0` dan tidak boleh melebihi `24` jam.
  * Diimplementasikan di sisi backend (`energy_routes.py`) dan frontend.

### 2. Pembaruan UI/UX Frontend
* **Form-Repeater Dinamis**:
  * Pengguna dapat menambah baris input baru dengan tombol **"+ Tambah Perangkat"** atau menghapus baris perangkat tertentu secara dinamis.
  * Tombol hapus dinonaktifkan secara otomatis jika hanya ada satu baris tersisa untuk menjaga validitas data.
* **Tabel Perbandingan Hasil**:
  * Menggantikan layout grid lama menjadi tabel perbandingan ringkas dan elegan untuk periode **Harian**, **Bulanan**, dan **Tahunan** (menampilkan KWH, Biaya, dan Emisi CO2 sekaligus).
* **Peringkat Konsumsi Energi Perangkat**:
  * Menampilkan urutan perangkat paling boros beserta persentase kontribusinya.
  * Menggunakan **progress bar dinamis** dengan warna gradasi berbasis persentase:
    * **Merah** (>50%): Kategori sangat boros.
    * **Kuning/Oranye** (20% - 50%): Kategori sedang.
    * **Biru/Hijau** (<=20%): Kategori hemat/efisien.

### 3. Pengujian Berkelanjutan (`test_api.py`)
* Memperbarui file automated tests untuk menguji skenario multi-perangkat, validasi baru, serta kalkulasi multi-periode (Harian, Bulanan, Tahunan).

---

## 📅 Fase 1.3: Energy Score & Insight Generator (Rekomendasi Cerdas)

### 1. Inovasi Logika & Service Baru
* **`insight_service.py`**:
  * Menghitung **Energy Score** (skor 10-100) berdasarkan total konsumsi kWh bulanan, rata-rata jam penggunaan, penggunaan alat berat (>500W), dan persentase dominasi beban.
  * Klasifikasi kategori skor: **Excellent** (90-100), **Good** (70-89), **Average** (50-69), dan **Needs Improvement** (<50).
  * Menghasilkan daftar **Insight Rekomendasi Dinamis**:
    1. Persentase kontribusi perangkat terboros.
    2. Peringatan durasi aktif perangkat berjalan lama (>= 20 jam).
    3. Analisis Skenario (What-if): "Jika perangkat terboros dikurangi 2 jam/hari, konsumsi listrik turun X%."
    4. Perbandingan konsumsi rumah tangga dengan rata-rata standar tipe 900VA (120 kWh/bulan).
* **Integrasi Rute API**:
  * Mengintegrasikan `InsightService` di dalam `energy_routes.py` agar mengembalikan data skor dan insight secara otomatis dalam respon API kalkulasi energi.

### 2. Peningkatan Dashboard UI/UX
* **Dashboard Analisis & Rekomendasi**:
  * Grid responsif 2 kolom:
    * **Sisi Kiri (Energy Score)**: Menampilkan kartu skor besar dengan badge kategori dinamis yang berganti warna (Hijau, Biru, Oranye, Merah) tergantung kategori nilai.
    * **Sisi Kanan (Analisis & Insight)**: Menampilkan daftar rekomendasi cerdas secara real-time yang dihasilkan backend.
* **Layout Desktop Side-by-Side**:
  * Mengatur kontainer utama (`.container`) agar melebar hingga `1200px` pada layar desktop (min-width: 992px) guna memaksimalkan ruang kosong di samping kanan dan kiri.
  * Membagi tampilan menjadi 2 panel terpisah berdampingan (`grid-template-columns: 460px 1fr`):
    * **Panel Kiri**: Form input interaktif untuk menambah/mengurangi baris data perangkat elektronik.
    * **Panel Kanan**: Panel output hasil kalkulasi, di mana pada keadaan awal (*initial load*) akan menampilkan kartu *placeholder state* kosong yang elegan ("Belum Ada Hasil Perhitungan"). Ketika tombol Hitung diklik, placeholder disembunyikan dan visualisasi hasil kalkulasi, skor energi, dan rekomendasi langsung muncul secara dinamis.
  * Menjaga layout bertumpuk vertikal (*stacked*) yang responsif pada resolusi tablet/mobile untuk pengalaman pengguna yang optimal di semua perangkat.

---

## 📅 Fase 1.4: Upgrade Insight Engine & Visualisasi Alur Energi (Energy Flow)

### 1. Inovasi Rule-Based Insight Engine
* **`insight_service.py`**:
  * Melakukan *upgrade* penuh dari model list string menjadi terstruktur dengan format kartu rekomendasi (memiliki `type`, `icon`, `title`, dan `description`).
  * Implementasi sistem berbasis aturan (*rule-based system*) murni tanpa LLM/AI eksternal:
    * **Rule 1 (Dominasi Beban)**: Jika satu perangkat menyumbang > 50% total kWh bulanan, berikan peringatan status *danger* berisi persentase kontribusinya.
    * **Rule 2 (Batas Konsumsi Rumah Tangga)**: Jika konsumsi bulanan > 300 kWh, tandai sebagai *danger* (sangat tinggi). Jika > 150 kWh, tandai sebagai *warning* (menengah/di atas rata-rata). Jika di bawah 150 kWh, tandai sebagai *success* (efisien).
    * **Rule 3 (Evaluasi Durasi Penggunaan)**: Mendeteksi perangkat yang menyala berdurasi antara 12 hingga 24 jam/hari untuk disarankan evaluasi durasi.
    * **Rule 4 (Beban Konstan 24 Jam)**: Memberikan informasi/penjelasan ramah bagi perangkat bersiaga 24 jam (kulkas, router) agar dipahami kontribusinya pada konsumsi listrik konstan.
    * **Rule Bonus (What-If)**: Rekomendasi penghematan simulasi pengurangan 2 jam per hari untuk perangkat terboros.

### 2. Fitur 4 - Visualisasi Alur Pemrosesan Data (Energy Flow)
* **Diagram Alur Pemrosesan**:
  * Menambahkan visualisasi statis diagram alur data di bagian bawah panel hasil:
    `Rumah` ➔ `Total Energi` ➔ `Perangkat` ➔ `Biaya Listrik` ➔ `Emisi Karbon` ➔ `Insight`
  * Desain diagram menggunakan CSS Flexbox transparan glassmorphic yang premium di desktop, dan bertransformasi otomatis menjadi grid 3x2 yang rapi di layar mobile (tanpa chevron overflow).

### 3. Pengujian Unit Test Komprehensif
* Memperbarui `backend/test_api.py` dengan menambahkan dua test case baru:
  * `test_insight_engine_rules`: Memastikan seluruh aturan (R1, R2, R3, R4) dapat terdeteksi dengan payload data tiruan secara akurat.
  * `test_energy_score_variations`: Menguji kebenaran hasil perhitungan tingkat skor energi (dari Excellent hingga Needs Improvement).



