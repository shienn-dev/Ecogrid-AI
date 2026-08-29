import { api } from "./api/client.js";
import { createDeviceRow, readDevices, reindex } from "./components/DeviceRow.js";
import { fmtKwh, fmtRupiah, fmtCo2, escapeHtml } from "./utils/format.js";
import { showToast } from "./utils/dom.js";
import { getState, setState } from "./store/appStore.js";
import { renderContribution, renderDonut, renderPeriod } from "./charts/charts.js";

const deviceList = document.getElementById("device-list");
const form = document.getElementById("energy-form");
const btnAdd = document.getElementById("btn-add-device");
const btnCalc = document.getElementById("hitung-btn");
const resultsEmpty = document.getElementById("results-placeholder");
const resultsEl = document.getElementById("results");
const kpiGrid = document.getElementById("kpi-grid");
const rankingList = document.getElementById("ranking-list");
const insightsContainer = document.getElementById("insights-container");
const scoreVal = document.getElementById("energy-score-val");
const scoreCat = document.getElementById("energy-score-category");
const scoreBar = document.getElementById("score-bar-fill");
const detailedTableBody = document.getElementById("detailed-tbody");
const whatifWrap = document.getElementById("whatif-wrap");
const whatifSlider = document.getElementById("whatif-slider");
const whatifValue = document.getElementById("whatif-value");
const whatifDelta = document.getElementById("whatif-delta");
const historyList = document.getElementById("history-list");
const historyEmpty = document.getElementById("history-empty");

// Device management
function addDevice() {
  const row = createDeviceRow(deviceList.children.length, (card) => {
    card.remove();
    reindex(deviceList);
  });
  deviceList.appendChild(row);
  reindex(deviceList);
  row.querySelector(".device-name").focus();
}

btnAdd.addEventListener("click", addDevice);
// initial row
if (deviceList.children.length === 0) addDevice();

// What-if state
let currentResult = null;
let whatifHours = 2;

whatifSlider?.addEventListener("input", (e) => {
  whatifHours = parseInt(e.target.value, 10);
  whatifValue.textContent = `${whatifHours} jam / hari`;
  renderWhatIf();
});

function renderWhatIf() {
  if (!currentResult) return;
  const ranked = currentResult.ranked_devices;
  if (!ranked || ranked.length === 0) return;
  const top = ranked[0];
  const topDevice = currentResult.devices.find((d) => d.device_name === top.device_name) || currentResult.devices[0];
  const watt = topDevice.watt;
  const savedDaily = (watt * whatifHours) / 1000;
  const savedMonthly = savedDaily * 30;
  const pct = (savedDaily / currentResult.total_daily_kwh) * 100;
  const costPerKwh = currentResult.cost ? currentResult.cost.tariff_per_kwh : 1444.7;
  const savedCost = savedMonthly * costPerKwh;
  const carbonFactor = currentResult.carbon ? currentResult.carbon.emission_factor : 0.87;
  const savedCarbon = savedMonthly * carbonFactor;
  whatifDelta.innerHTML = `Hemat <strong>${savedMonthly.toFixed(2)} kWh/bulan (${pct.toFixed(1)}%)</strong> · <strong>${fmtRupiah(savedCost)}</strong> / bulan · <strong>${savedCarbon.toFixed(2)} kg CO₂</strong>`;
}

function setLoading(isLoading) {
  if (isLoading) {
    btnCalc.disabled = true;
    btnCalc.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Menghitung…';
    setState({ loading: true });
  } else {
    btnCalc.disabled = false;
    btnCalc.innerHTML = '<i class="fa-solid fa-calculator"></i> Hitung';
    setState({ loading: false });
  }
}

function renderKpis(data) {
  // data contains total_*_kwh, cost, carbon, energy_score
  const dailyKwh = fmtKwh(data.total_daily_kwh);
  const monthlyKwh = fmtKwh(data.total_monthly_kwh);
  const yearlyKwh = fmtKwh(data.total_yearly_kwh);
  const cost = data.cost || { daily_cost: data.total_daily_kwh * 1444.7, monthly_cost: data.total_monthly_kwh * 1444.7, yearly_cost: data.total_yearly_kwh * 1444.7 };
  const carbon = data.carbon || { daily_carbon_kg: data.total_daily_kwh * 0.87, monthly_carbon_kg: data.total_monthly_kwh * 0.87, yearly_carbon_kg: data.total_yearly_kwh * 0.87 };

  kpiGrid.innerHTML = `
    <div class="kpi" style="--kpi-accent: var(--primary); --kpi-accent-bg: var(--primary-50)">
      <div class="kpi-head">
        <div class="kpi-label">Konsumsi Energi</div>
        <div class="kpi-icon"><i class="fa-solid fa-bolt"></i></div>
      </div>
      <div class="kpi-value tabular">${monthlyKwh} <span style="font-size:0.55em;font-weight:600;color:var(--text-tertiary)">kWh/bln</span></div>
      <div class="kpi-sub">Harian ${dailyKwh} kWh · Tahunan ${yearlyKwh} kWh</div>
      <div class="kpi-foot"><i class="fa-solid fa-chart-simple" style="color:var(--primary)"></i> Total rumah tangga</div>
    </div>
    <div class="kpi" style="--kpi-accent: #d97706; --kpi-accent-bg: #fffbeb">
      <div class="kpi-head">
        <div class="kpi-label">Estimasi Biaya</div>
        <div class="kpi-icon" style="--kpi-accent:#d97706;--kpi-accent-bg:#fffbeb"><i class="fa-solid fa-wallet"></i></div>
      </div>
      <div class="kpi-value tabular" style="font-size:1.35rem">${fmtRupiah(cost.monthly_cost)} <span style="font-size:0.55em;font-weight:600;color:var(--text-tertiary)">/bulan</span></div>
      <div class="kpi-sub">Harian ${fmtRupiah(cost.daily_cost)} · Tahunan ${fmtRupiah(cost.yearly_cost)}</div>
      <div class="kpi-foot"><i class="fa-solid fa-coins" style="color:#d97706"></i> Tarif ${cost.tariff_per_kwh?.toFixed ? cost.tariff_per_kwh.toFixed(2) : "1444.70"} /kWh</div>
    </div>
    <div class="kpi" style="--kpi-accent: #475569; --kpi-accent-bg: #f1f5f9">
      <div class="kpi-head">
        <div class="kpi-label">Emisi CO₂</div>
        <div class="kpi-icon" style="--kpi-accent:#475569;--kpi-accent-bg:#f1f5f9"><i class="fa-solid fa-leaf"></i></div>
      </div>
      <div class="kpi-value tabular" style="font-size:1.35rem">${fmtCo2(carbon.monthly_carbon_kg)} <span style="font-size:0.55em;font-weight:600;color:var(--text-tertiary)">/bulan</span></div>
      <div class="kpi-sub">Harian ${fmtCo2(carbon.daily_carbon_kg)} · Tahunan ${fmtCo2(carbon.yearly_carbon_kg)}</div>
      <div class="kpi-foot"><i class="fa-solid fa-cloud" style="color:#475569"></i> Faktor ${carbon.emission_factor} kg/kWh</div>
    </div>
    <div class="kpi" style="--kpi-accent: var(--primary); --kpi-accent-bg: var(--primary-50)">
      <div class="kpi-head">
        <div class="kpi-label">Energy Score</div>
        <div class="kpi-icon"><i class="fa-solid fa-gauge-high"></i></div>
      </div>
      <div class="kpi-value tabular">${data.energy_score} <span style="font-size:0.55em;font-weight:600;color:var(--text-tertiary)">/100</span></div>
      <div class="kpi-sub"><span class="score-badge ${badgeClass(data.category)}" style="padding:4px 8px;font-size:11px">${escapeHtml(data.category)}</span></div>
      <div class="kpi-foot">Semakin tinggi, semakin efisien</div>
    </div>
  `;
}

function badgeClass(cat) {
  if (cat === "Excellent") return "excellent";
  if (cat === "Good") return "good";
  if (cat === "Average") return "average";
  return "needs";
}

function renderRanking(ranked) {
  rankingList.innerHTML = "";
  ranked.forEach((d, i) => {
    const pct = d.contribution_percentage;
    let cls = "low";
    if (pct > 50) cls = "high";
    else if (pct > 20) cls = "mid";
    const row = document.createElement("div");
    row.className = "ranking-item";
    row.innerHTML = `
      <div class="ranking-top">
        <div>
          <div class="ranking-name">#${i + 1} ${escapeHtml(d.device_name)}</div>
          <div class="ranking-meta">${fmtKwh(d.monthly_kwh)} kWh/bln · ${pct.toFixed(1)}%</div>
        </div>
        <span class="badge-rank">${pct.toFixed(1)}%</span>
      </div>
      <div class="progress" aria-hidden="true">
        <div class="progress-fill ${cls}" style="width:0%"></div>
      </div>
    `;
    rankingList.appendChild(row);
    requestAnimationFrame(() => {
      const fill = row.querySelector(".progress-fill");
      setTimeout(() => (fill.style.width = `${Math.min(100, pct)}%`), 50 + i * 80);
    });
  });
}

function renderInsights(insights) {
  insightsContainer.innerHTML = "";
  if (!insights || insights.length === 0) {
    const el = document.createElement("div");
    el.className = "insight success";
    el.innerHTML = `<div class="insight-head"><i class="fa-solid fa-leaf"></i> Efisiensi Optimal</div><div class="insight-desc">Tidak ada rekomendasi khusus. Penggunaan energi Anda tergolong normal.</div>`;
    insightsContainer.appendChild(el);
    return;
  }
  for (const ins of insights) {
    const div = document.createElement("div");
    div.className = `insight ${ins.type}`;
    // description contains <strong> from backend (escaped device names)
    div.innerHTML = `<div class="insight-head"><i class="${escapeHtml(ins.icon)}"></i> ${escapeHtml(ins.title)}</div><div class="insight-desc">${ins.description}</div>`;
    insightsContainer.appendChild(div);
  }
}

function renderScore(score, category) {
  scoreVal.textContent = String(score);
  scoreCat.textContent = category;
  scoreCat.className = `score-badge ${badgeClass(category)}`;
  if (scoreBar) {
    requestAnimationFrame(() => {
      scoreBar.style.width = "0%";
      setTimeout(() => (scoreBar.style.width = `${score}%`), 100);
    });
  }
}

function renderDetailedTable(data) {
  const cost = data.cost;
  const carbon = data.carbon;
  const rows = [
    { label: "Harian", kwh: data.total_daily_kwh, cost: cost?.daily_cost, co2: carbon?.daily_carbon_kg },
    { label: "Bulanan", kwh: data.total_monthly_kwh, cost: cost?.monthly_cost, co2: carbon?.monthly_carbon_kg },
    { label: "Tahunan", kwh: data.total_yearly_kwh, cost: cost?.yearly_cost, co2: carbon?.yearly_carbon_kg },
  ];
  detailedTableBody.innerHTML = rows
    .map(
      (r) => `
    <tr>
      <td><strong>${r.label}</strong></td>
      <td class="tabular" style="color:var(--primary);font-weight:600">${fmtKwh(r.kwh)}</td>
      <td class="tabular" style="color:#d97706;font-weight:600">${fmtRupiah(r.cost ?? 0)}</td>
      <td class="tabular" style="color:var(--danger);font-weight:600">${fmtCo2(r.co2 ?? 0)}</td>
    </tr>
  `
    )
    .join("");
}

function renderHistoryLocal() {
  // Try to fetch from API, fallback local
  import("./store/historyStore.js").then(({ fetchHistory }) => {
    fetchHistory(5, 0).then((items) => {
      if (!historyList) return;
      if (!items || items.length === 0) {
        historyEmpty.style.display = "block";
        historyList.innerHTML = "";
        return;
      }
      historyEmpty.style.display = "none";
      historyList.innerHTML = items
        .map(
          (h) => `
        <div class="ranking-item" style="padding:12px">
          <div class="ranking-top">
            <div>
              <div class="ranking-name">${new Date(h.created_at).toLocaleString("id-ID")}</div>
              <div class="ranking-meta">${fmtKwh(h.total_monthly_kwh)} kWh/bln · ${fmtRupiah(h.monthly_cost || 0)} · Score ${h.energy_score}</div>
            </div>
            <span class="badge-rank">${escapeHtml(h.category)}</span>
          </div>
        </div>
      `
        )
        .join("");
    });
  });
}

async function handleSubmit(e) {
  e.preventDefault();
  const { ok, devices } = readDevices(deviceList);
  if (!ok) {
    showToast("Periksa kembali input perangkat yang bertanda merah.", "error");
    return;
  }
  if (devices.length === 0) {
    showToast("Tambahkan minimal satu perangkat.", "error");
    return;
  }
  if (devices.length > 50) {
    showToast("Maksimal 50 perangkat.", "error");
    return;
  }

  setLoading(true);
  resultsEmpty.style.display = "none";
  resultsEl.style.display = "block";
  resultsEl.setAttribute("aria-busy", "true");

  // Skeleton
  kpiGrid.innerHTML = `<div class="skeleton" style="height:96px"></div><div class="skeleton" style="height:96px"></div><div class="skeleton" style="height:96px"></div><div class="skeleton" style="height:96px"></div>`;
  rankingList.innerHTML = `<div class="skeleton" style="height:72px"></div><div class="skeleton" style="height:72px"></div>`;

  try {
    const res = await api.calculateEnergy(devices, { save: true });
    const data = res.data;
    currentResult = data;
    setState({ result: data, error: null });

    // Render all
    renderKpis(data);
    renderRanking(data.ranked_devices);
    renderInsights(data.insights);
    renderScore(data.energy_score, data.category);
    renderDetailedTable(data);
    // Charts lazy
    renderContribution("chart-contribution", data.ranked_devices);
    renderDonut("chart-donut", data.ranked_devices);
    renderPeriod("chart-period", { daily: data.total_daily_kwh, monthly: data.total_monthly_kwh, yearly: data.total_yearly_kwh });
    // What-if
    whatifWrap.style.display = "block";
    renderWhatIf();
    // History
    try {
      const { pushLocal } = await import("./store/historyStore.js");
      pushLocal({
        created_at: new Date().toISOString(),
        total_monthly_kwh: data.total_monthly_kwh,
        monthly_cost: data.cost?.monthly_cost,
        monthly_carbon: data.carbon?.monthly_carbon_kg,
        energy_score: data.energy_score,
        category: data.category,
        devices: data.devices,
      });
    } catch {}
    renderHistoryLocal();
    showToast("Perhitungan berhasil.", "success");
    resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
    // aria-live
    const live = document.getElementById("results-live");
    if (live) live.textContent = `Hasil: ${data.total_monthly_kwh.toFixed(2)} kWh per bulan, biaya ${fmtRupiah(data.cost.monthly_cost)}, skor ${data.energy_score} ${data.category}.`;
  } catch (err) {
    console.error(err);
    showToast(err.message || "Gagal menghitung. Coba lagi.", "error");
    resultsEmpty.style.display = "block";
    resultsEl.style.display = "none";
    setState({ error: err.message });
  } finally {
    setLoading(false);
    resultsEl.setAttribute("aria-busy", "false");
  }
}

form.addEventListener("submit", handleSubmit);

// Collapsible
document.querySelectorAll("[data-collapsible]").forEach((wrap) => {
  const btn = wrap.querySelector(".collapsible-trigger");
  const panel = wrap.querySelector(".collapsible-panel");
  btn.addEventListener("click", () => {
    const open = panel.dataset.open === "true";
    panel.dataset.open = open ? "false" : "true";
    btn.setAttribute("aria-expanded", String(!open));
    const chevron = btn.querySelector("i.fa-chevron-down, i.fa-chevron-up");
    if (chevron) {
      chevron.className = open ? "fa-solid fa-chevron-down" : "fa-solid fa-chevron-up";
    }
  });
});

// Sample data
document.getElementById("btn-sample")?.addEventListener("click", () => {
  deviceList.innerHTML = "";
  const samples = [
    { name: "AC 1 PK", watt: 800, hours: 6 },
    { name: "Kulkas 2 Pintu", watt: 120, hours: 24 },
    { name: "Lampu LED x5", watt: 12, hours: 5 },
  ];
  samples.forEach((s, i) => {
    const row = createDeviceRow(i, (c) => {
      c.remove();
      reindex(deviceList);
    });
    deviceList.appendChild(row);
    row.querySelector(".device-name").value = s.name;
    row.querySelector(".device-watt").value = String(s.watt);
    row.querySelector(".device-hours").value = String(s.hours);
  });
  reindex(deviceList);
  showToast("Data contoh dimuat. Klik Hitung.", "info");
});

// Initial history
renderHistoryLocal();

// Expose for e2e
window.__ecogrid = { getState, api };
