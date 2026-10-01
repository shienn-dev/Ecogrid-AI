import { api } from "./api/client.js";
import { createDeviceRow, readDevices, reindex } from "./components/DeviceRow.js";
import { fmtCo2, fmtKwh, fmtRupiah, escapeHtml } from "./utils/format.js";
import { showToast } from "./utils/dom.js";
import { setState } from "./store/appStore.js";
import { renderContribution, renderDonut, renderPeriod } from "./charts/charts.js";

/* ---------------------------------------------------------------- DOM refs */
const deviceList = document.getElementById("device-list");
const form = document.getElementById("energy-form");
const btnAdd = document.getElementById("btn-add-device");
const btnCalc = document.getElementById("hitung-btn");
const resultsEmpty = document.getElementById("results-placeholder");
const resultsEl = document.getElementById("results");
const kpiGrid = document.getElementById("kpi-grid");
const equivalentsEl = document.getElementById("carbon-equivalents");
const rankingList = document.getElementById("ranking-list");
const insightsContainer = document.getElementById("insights-container");
const insightCount = document.getElementById("insight-count");
const scoreVal = document.getElementById("energy-score-val");
const scoreCat = document.getElementById("energy-score-category");
const scoreRing = document.getElementById("score-ring");
const detailedTableBody = document.getElementById("detailed-tbody");
const whatifWrap = document.getElementById("whatif-wrap");
const whatifSlider = document.getElementById("whatif-slider");
const whatifValue = document.getElementById("whatif-value");
const whatifName = document.getElementById("whatif-device-name");
const whatifDelta = document.getElementById("whatif-delta");
const historyList = document.getElementById("history-list");
const historyEmpty = document.getElementById("history-empty");

/* ------------------------------------------------------------ device rows */
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
if (deviceList.children.length === 0) addDevice();

/* ----------------------------------------------------------- what-if model */
let currentResult = null;
let whatifHours = 2;

whatifSlider?.addEventListener("input", (e) => {
  whatifHours = parseInt(e.target.value, 10);
  whatifValue.textContent = `${whatifHours} jam / hari`;
  renderWhatIf();
});

function renderWhatIf() {
  if (!currentResult) return;
  const ranked = currentResult.ranked_devices || [];
  if (!ranked.length) return;

  const top = ranked[0];
  const topDevice =
    currentResult.devices.find((d) => d.device_name === top.device_name) || currentResult.devices[0];
  if (!topDevice) return;

  const savedDaily = (Number(topDevice.watt) * whatifHours) / 1000;
  const savedMonthly = savedDaily * 30;
  const daily = currentResult.total_daily_kwh || 0;
  const pct = daily > 0 ? (savedDaily / daily) * 100 : 0;
  const tariff = currentResult.cost?.tariff_per_kwh ?? 1444.7;
  const factor = currentResult.carbon?.emission_factor ?? 0.68;

  if (whatifName) whatifName.textContent = top.device_name;
  whatifDelta.innerHTML = `
    <span>Hemat <strong>${fmtKwh(savedMonthly)} kWh/bln</strong> (${pct.toFixed(1)}%)</span>
    <span><strong>${fmtRupiah(savedMonthly * tariff)}</strong> / bulan</span>
    <span><strong>${(savedMonthly * factor).toFixed(1)} kg CO₂</strong> / bulan</span>`;
}

/* ----------------------------------------------------------------- loading */
function setLoading(loading) {
  btnCalc.disabled = loading;
  btnCalc.innerHTML = loading
    ? '<i class="fa-solid fa-spinner fa-spin"></i> Menghitung'
    : '<i class="fa-solid fa-calculator"></i> Hitung';
  setState({ loading });
}

/* --------------------------------------------------------------- KPI cards */
function badgeClass(cat) {
  if (cat === "Excellent") return "excellent";
  if (cat === "Good") return "good";
  if (cat === "Average") return "average";
  return "needs";
}

function scoreColor(cat) {
  const map = {
    Excellent: "var(--alert-green)",
    Good: "var(--cat-2)",
    Average: "var(--alert-orange)",
    Poor: "var(--alert-red)",
    "Needs Improvement": "var(--alert-red)",
  };
  return map[cat] || "var(--primary)";
}

function renderKpis(data) {
  const cost = data.cost || {};
  const carbon = data.carbon || {};
  const tariff = cost.tariff_per_kwh ?? 1444.7;
  const factor = carbon.emission_factor ?? 0.68;

  // Hierarchy (Carbon): the headline metric gets the largest area and the
  // strongest accent; supporting metrics stay quiet.
  kpiGrid.innerHTML = `
    <div class="kpi kpi--primary" style="--kpi-accent: var(--primary)">
      <div class="kpi-head">
        <span class="kpi-label">Konsumsi bulanan</span>
        <span class="kpi-icon"><i class="fa-solid fa-bolt"></i></span>
      </div>
      <div class="kpi-value tabular">${fmtKwh(data.total_monthly_kwh)}<span class="kpi-unit">kWh</span></div>
      <div class="kpi-sub">Harian ${fmtKwh(data.total_daily_kwh)} · Tahunan ${fmtKwh(data.total_yearly_kwh)} kWh</div>
      <div class="kpi-foot"><i class="fa-solid fa-house"></i> Total rumah tangga</div>
    </div>

    <div class="kpi" style="--kpi-accent: var(--alert-orange)">
      <div class="kpi-head">
        <span class="kpi-label">Biaya bulanan</span>
        <span class="kpi-icon"><i class="fa-solid fa-wallet"></i></span>
      </div>
      <div class="kpi-value tabular" style="font-size:var(--fs-18)">${fmtRupiah(cost.monthly_cost ?? 0)}</div>
      <div class="kpi-sub">Harian ${fmtRupiah(cost.daily_cost ?? 0)} · Tahunan ${fmtRupiah(cost.yearly_cost ?? 0)}</div>
      <div class="kpi-foot"><i class="fa-solid fa-tag"></i> Tarif ${tariff.toLocaleString("id-ID")} /kWh</div>
    </div>

    <div class="kpi" style="--kpi-accent: var(--cat-3)">
      <div class="kpi-head">
        <span class="kpi-label">Emisi bulanan</span>
        <span class="kpi-icon"><i class="fa-solid fa-leaf"></i></span>
      </div>
      <div class="kpi-value tabular" style="font-size:var(--fs-18)">${fmtCo2(carbon.monthly_carbon_kg ?? 0)}</div>
      <div class="kpi-sub">Harian ${fmtCo2(carbon.daily_carbon_kg ?? 0)} · Tahunan ${fmtCo2(carbon.yearly_carbon_kg ?? 0)}</div>
      <div class="kpi-foot"><i class="fa-solid fa-industry"></i> Faktor grid ${factor} kg/kWh</div>
    </div>

    <div class="kpi" style="--kpi-accent: ${scoreColor(data.category)}">
      <div class="kpi-head">
        <span class="kpi-label">Energy Score</span>
        <span class="kpi-icon"><i class="fa-solid fa-gauge-high"></i></span>
      </div>
      <div class="kpi-value tabular">${Number(data.energy_score) || 0}<span class="kpi-unit">/100</span></div>
      <div class="kpi-sub">
        <span class="score-badge ${badgeClass(data.category)}">${
          data.grade ? data.grade + " · " : ""
        }${escapeHtml(data.category || "—")}</span>
      </div>
      <div class="kpi-foot"><i class="fa-solid fa-arrow-trend-up"></i> Makin tinggi makin efisien</div>
    </div>`;

  renderEquivalents(data.carbon_equivalents);
}

function renderEquivalents(eq) {
  if (!equivalentsEl) return;
  if (!eq) {
    equivalentsEl.innerHTML = "";
    return;
  }
  equivalentsEl.innerHTML = `
    <div class="card">
      <div class="card-pad">
        <div class="card-header">
          <h3 class="card-title"><i class="fa-solid fa-scale-balanced"></i> Setara dengan</h3>
          <span class="card-subtitle">Emisi bulanan Anda</span>
        </div>
        <div class="equivalents">
          <div class="equiv-item">
            <i class="fa-solid fa-tree" style="color:var(--alert-green)"></i>
            <div>
              <div class="equiv-value">${eq.trees_year}</div>
              <div class="equiv-label">pohon dewasa per tahun</div>
            </div>
          </div>
          <div class="equiv-item">
            <i class="fa-solid fa-motorcycle" style="color:var(--alert-orange)"></i>
            <div>
              <div class="equiv-value">${Number(eq.motorcycle_km).toLocaleString("id-ID")}</div>
              <div class="equiv-label">km berkendara motor</div>
            </div>
          </div>
          <div class="equiv-item">
            <i class="fa-solid fa-lightbulb" style="color:var(--cat-2)"></i>
            <div>
              <div class="equiv-value">${Number(eq.led_hours).toLocaleString("id-ID")}</div>
              <div class="equiv-label">jam menyalakan lampu LED</div>
            </div>
          </div>
        </div>
      </div>
    </div>`;
}

/* ----------------------------------------------------------------- ranking */
function renderRanking(ranked) {
  rankingList.innerHTML = "";
  (ranked || []).forEach((d, i) => {
    const pct = Number(d.contribution_percentage) || 0;
    const cls = pct > 50 ? "high" : pct > 20 ? "mid" : "low";

    const row = document.createElement("div");
    row.className = "ranking-item";
    row.innerHTML = `
      <div class="rank-no">${i + 1}</div>
      <div class="rank-body">
        <div class="rank-top">
          <span class="rank-name">${escapeHtml(d.device_name)}</span>
          <span class="rank-meta">${pct.toFixed(1)}%</span>
        </div>
        <div class="progress"><div class="progress-fill ${cls}" style="width:0%"></div></div>
      </div>
      <div class="rank-value">${fmtKwh(d.monthly_kwh)}</div>`;
    rankingList.appendChild(row);

    const fill = row.querySelector(".progress-fill");
    requestAnimationFrame(() => {
      setTimeout(() => {
        fill.style.width = `${Math.min(100, pct)}%`;
      }, 60 + i * 50);
    });
  });
}

/* ---------------------------------------------------------------- insights */
function sanitizeHtml(html) {
  let text = String(html ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
  for (const tag of ["strong", "em", "b", "i", "u", "br"]) {
    text = text
      .replace(new RegExp(`&lt;${tag}&gt;`, "gi"), `<${tag}>`)
      .replace(new RegExp(`&lt;/${tag}&gt;`, "gi"), `</${tag}>`)
      .replace(new RegExp(`&lt;${tag}\\s*/&gt;`, "gi"), `<${tag}/>`);
  }
  return text;
}

function renderInsights(insights) {
  insightsContainer.innerHTML = "";
  const list = insights || [];
  if (insightCount) insightCount.textContent = list.length ? `${list.length} temuan` : "";

  if (!list.length) {
    const el = document.createElement("div");
    el.className = "insight success";
    el.innerHTML = `<div class="insight-head"><i class="fa-solid fa-leaf"></i> Efisiensi optimal</div>
      <div class="insight-desc">Tidak ada temuan khusus — pemakaian Anda tergolong wajar.</div>`;
    insightsContainer.appendChild(el);
    return;
  }

  for (const ins of list) {
    const div = document.createElement("div");
    div.className = `insight ${ins.type}`;
    const icon = String(ins.icon || "fa-solid fa-circle-info").replace(/[^a-zA-Z0-9\s\-_]/g, "");
    div.innerHTML = `<div class="insight-head"><i class="${icon}"></i> ${sanitizeHtml(ins.title)}</div>
      <div class="insight-desc">${sanitizeHtml(ins.description)}</div>`;
    insightsContainer.appendChild(div);
  }
}

/* ------------------------------------------------------------------- score */
function renderScore(score, category) {
  const value = Number(score) || 0;
  scoreVal.textContent = String(value);
  scoreCat.textContent = category || "—";
  scoreCat.className = `score-badge ${badgeClass(category)}`;
  scoreCat.style.color = "";

  if (scoreRing) {
    const circumference = 2 * Math.PI * 38; // r=38
    scoreRing.setAttribute("stroke-dasharray", String(circumference));
    scoreRing.style.stroke = scoreColor(category);
    scoreRing.setAttribute("stroke-dashoffset", String(circumference));
    requestAnimationFrame(() => {
      setTimeout(() => {
        scoreRing.setAttribute("stroke-dashoffset", String(circumference * (1 - value / 100)));
      }, 80);
    });
  }
}

/* ------------------------------------------------------------------- table */
function renderDetailedTable(data) {
  const rows = [
    { label: "Harian", kwh: data.total_daily_kwh, cost: data.cost?.daily_cost, co2: data.carbon?.daily_carbon_kg },
    { label: "Bulanan", kwh: data.total_monthly_kwh, cost: data.cost?.monthly_cost, co2: data.carbon?.monthly_carbon_kg },
    { label: "Tahunan", kwh: data.total_yearly_kwh, cost: data.cost?.yearly_cost, co2: data.carbon?.yearly_carbon_kg },
  ];
  detailedTableBody.innerHTML = rows
    .map(
      (r) => `<tr>
        <td><strong>${r.label}</strong></td>
        <td>${fmtKwh(r.kwh ?? 0)} kWh</td>
        <td>${fmtRupiah(r.cost ?? 0)}</td>
        <td>${fmtCo2(r.co2 ?? 0)}</td>
      </tr>`
    )
    .join("");
}

/* ----------------------------------------------------------------- history */
function renderHistory() {
  import("./store/historyStore.js").then(({ fetchHistory }) => {
    fetchHistory(6, 0).then((items) => {
      if (!historyList) return;
      if (!items || !items.length) {
        historyEmpty.style.display = "block";
        historyList.innerHTML = "";
        return;
      }
      historyEmpty.style.display = "none";
      historyList.innerHTML = "";
      for (const h of items) {
        const row = document.createElement("div");
        row.className = "ranking-item";
        const when = new Date(h.created_at);
        const whenText = isNaN(when.getTime()) ? "Waktu tidak diketahui" : when.toLocaleString("id-ID");

        const no = document.createElement("div");
        no.className = "rank-no";
        no.innerHTML = '<i class="fa-solid fa-check" style="color:var(--alert-green)"></i>';

        const body = document.createElement("div");
        body.className = "rank-body";
        const name = document.createElement("div");
        name.className = "rank-name";
        name.textContent = whenText;
        const meta = document.createElement("div");
        meta.className = "rank-meta";
        meta.textContent = `${fmtKwh(h.total_monthly_kwh || 0)} kWh/bln · ${fmtRupiah(h.monthly_cost || 0)}`;
        body.appendChild(name);
        body.appendChild(meta);

        const val = document.createElement("div");
        val.className = "rank-value";
        val.textContent = h.energy_score ?? "—";

        row.appendChild(no);
        row.appendChild(body);
        row.appendChild(val);
        historyList.appendChild(row);
      }
    });
  });
}

/* ---------------------------------------------------------------- submit */
let isSubmitting = false;

async function handleSubmit(e) {
  e.preventDefault();
  if (isSubmitting) return;

  const { ok, devices } = readDevices(deviceList);
  if (!ok) return showToast("Periksa input yang ditandai merah", "error");
  if (!devices.length) return showToast("Tambahkan minimal satu perangkat", "error");
  if (devices.length > 50) return showToast("Maksimal 50 perangkat", "error");

  isSubmitting = true;
  setLoading(true);
  resultsEmpty.style.display = "none";
  resultsEl.style.display = "block";
  resultsEl.setAttribute("aria-busy", "true");

  kpiGrid.innerHTML = Array(4).fill('<div class="skeleton" style="height:118px"></div>').join("");
  rankingList.innerHTML = Array(3).fill('<div class="skeleton" style="height:44px"></div>').join("");
  if (equivalentsEl) equivalentsEl.innerHTML = "";

  const tariffSel = document.getElementById("tariff-preset");
  const tariffPerKwh = tariffSel
    ? parseFloat(tariffSel.selectedOptions[0]?.dataset.tariff || "")
    : undefined;

  try {
    const res = await api.calculateEnergy(devices, {
      save: true,
      tariffPerKwh: Number.isFinite(tariffPerKwh) ? tariffPerKwh : undefined,
    });
    const data = res.data;
    currentResult = data;
    setState({ result: data, error: null });

    renderKpis(data);
    renderRanking(data.ranked_devices);
    renderInsights(data.insights);
    renderScore(data.energy_score, data.category);
    renderDetailedTable(data);

    renderContribution("chart-contribution", data.ranked_devices);
    renderDonut("chart-donut", data.ranked_devices);
    renderPeriod("chart-period", {
      daily: data.total_daily_kwh,
      monthly: data.total_monthly_kwh,
      yearly: data.total_yearly_kwh,
    });

    whatifWrap.style.display = "block";
    renderWhatIf();

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
    } catch { /* history is best-effort */ }
    renderHistory();

    const live = document.getElementById("results-live");
    if (live) {
      live.textContent = `${fmtKwh(data.total_monthly_kwh)} kWh per bulan, biaya ${fmtRupiah(
        data.cost?.monthly_cost ?? 0
      )}, skor ${data.energy_score} ${data.category}.`;
    }

    resultsEl.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    console.error(err);
    showToast(err.message || "Gagal menghitung", "error");
    resultsEmpty.style.display = "block";
    resultsEl.style.display = "none";
    setState({ error: err.message });
  } finally {
    isSubmitting = false;
    setLoading(false);
    resultsEl.setAttribute("aria-busy", "false");
  }
}

form.addEventListener("submit", handleSubmit);

/* ------------------------------------------------------------- collapsible */
document.querySelectorAll("[data-collapsible]").forEach((wrap) => {
  const btn = wrap.querySelector(".collapsible-trigger");
  const panel = wrap.querySelector(".collapsible-panel");
  if (!btn || !panel) return;
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

/* --------------------------------------------------------------- sample data
 * Values are realistic Indonesian household loads (see research refs §2).
 */
document.getElementById("btn-sample")?.addEventListener("click", () => {
  deviceList.innerHTML = "";
  const samples = [
    { name: "AC 1 PK", watt: 800, hours: 6 },
    { name: "Kulkas 2 Pintu", watt: 120, hours: 24 },
    { name: "Lampu LED ×5", watt: 60, hours: 5 },
    { name: "TV LED 40\"", watt: 80, hours: 4 },
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
  showToast(`${samples.length} contoh perangkat dimuat`, "info");
});

renderHistory();
window.__ecogrid = { api, getState: () => ({ result: currentResult }) };
