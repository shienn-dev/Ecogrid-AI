/**
 * Chart renderers — built to IBM Carbon data-visualization guidance.
 * See docs/research_references.md §7.
 *
 *   • Color palettes — categorical sequence applied strictly in order
 *   • Chart anatomy  — title, axes, ticks, axis title, legend, tooltip
 *   • Dashboards     — consistent layout/spacing, legends in a fixed position
 *
 * Chart.js is loaded once as an ES module and cached. We do NOT rely on a
 * window.Chart global — the ESM build does not create one.
 */

let chartPromise = null;

function loadChart() {
  if (!chartPromise) {
    chartPromise = import("https://cdn.jsdelivr.net/npm/chart.js@4.4.7/+esm")
      .then((mod) => {
        const C = mod.Chart || mod.default;
        if (!C) throw new Error("Chart.js export not found");
        C.register(...(mod.registerables || []));
        return C;
      })
      .catch((e) => {
        console.error("Chart.js failed to load", e);
        chartPromise = null; // allow a retry on the next render
        return null;
      });
  }
  return chartPromise;
}

const instances = {};

function destroy(id) {
  if (instances[id]) {
    try {
      instances[id].destroy();
    } catch {
      /* already gone */
    }
    delete instances[id];
  }
}

/* Carbon categorical sequence, read from CSS so there is one source of truth. */
function categorical(n) {
  const s = getComputedStyle(document.documentElement);
  const seq = [];
  for (let i = 1; i <= 14; i++) {
    const c = s.getPropertyValue(`--cat-${i}`).trim();
    if (c) seq.push(c);
  }
  if (!seq.length) seq.push("#6929c4", "#1192e8", "#005d5d", "#9f1853");
  return Array.from({ length: n }, (_, i) => seq[i % seq.length]);
}

/* Carbon monochromatic teal ramp. */
function sequential(n) {
  const s = getComputedStyle(document.documentElement);
  const ramp = ["--seq-2", "--seq-3", "--seq-4", "--seq-5", "--seq-6", "--seq-7"]
    .map((v) => s.getPropertyValue(v).trim())
    .filter(Boolean);
  if (!ramp.length) ramp.push("#9ef0f0", "#3ddbd9", "#08bdba");
  return Array.from({ length: n }, (_, i) => ramp[i % ramp.length]);
}

function tokens() {
  const s = getComputedStyle(document.documentElement);
  const get = (v) => s.getPropertyValue(v).trim();
  return {
    grid: get("--chart-grid") || "#e5e7eb",
    tick: get("--chart-tick") || "#6b7280",
    label: get("--chart-label") || "#1f2937",
    surface: get("--surface") || "#fff",
    font: "Inter, system-ui, sans-serif",
    reduced: window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  };
}

function fmtNum(v, digits = 1) {
  const n = Number(v);
  if (!Number.isFinite(n)) return "0";
  return n.toLocaleString("id-ID", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function axisOpts(t, { yTitle, xTitle, rotate = false } = {}) {
  const title = (text) =>
    text
      ? {
          display: true,
          text,
          color: t.tick,
          font: { family: t.font, size: 11, weight: "500" },
          padding: { top: 6, bottom: 6 },
        }
      : undefined;

  return {
    x: {
      grid: { display: false },
      border: { display: false },
      ticks: {
        color: t.tick,
        font: { family: t.font, size: 11 },
        maxRotation: rotate ? 45 : 0,
        minRotation: 0,
        autoSkip: false,
      },
      title: title(xTitle),
    },
    y: {
      beginAtZero: true,
      grid: { color: t.grid, drawTicks: false },
      border: { display: false },
      ticks: { color: t.tick, font: { family: t.font, size: 11 }, padding: 8 },
      title: title(yTitle),
    },
  };
}

function baseOpts(t, { scales, plugins, indexAxis } = {}) {
  return {
    indexAxis: indexAxis || "x",
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "nearest", intersect: true },
    layout: { padding: { top: 4, right: 4, bottom: 0, left: 0 } },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "rgba(17,24,39,0.95)",
        titleColor: "#ffffff",
        bodyColor: "#e5e7eb",
        titleFont: { family: t.font, size: 12, weight: "600" },
        bodyFont: { family: t.font, size: 12 },
        padding: 10,
        cornerRadius: 6,
        displayColors: true,
        boxWidth: 8,
        boxHeight: 8,
        boxPadding: 4,
      },
      ...(plugins || {}),
    },
    scales,
    animation: t.reduced ? false : { duration: 420, easing: "easeOutQuart" },
  };
}

/* ------------------------------------------------------------------ DEVICE BAR
 * Horizontal bar, sorted descending. Carbon: simple bar for ranking.
 */
export async function renderContribution(canvasId, rankedDevices) {
  const C = await loadChart();
  const canvas = document.getElementById(canvasId);
  if (!C || !canvas) return;
  destroy(canvasId);

  const t = tokens();
  const items = [...(rankedDevices || [])].sort(
    (a, b) => Number(b.monthly_kwh) - Number(a.monthly_kwh)
  );
  if (!items.length) return;

  // Height tracks the number of devices so bars never squash and a short
  // list never leaves a well of empty plot area.
  const wrap = canvas.parentElement;
  if (wrap) wrap.style.height = `${Math.max(170, items.length * 42 + 54)}px`;

  const labels = items.map((d) => d.device_name);
  const values = items.map((d) => Number(d.monthly_kwh));

  instances[canvasId] = new C(canvas, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "kWh/bulan",
          data: values,
          backgroundColor: categorical(items.length),
          borderRadius: 3,
          borderSkipped: false,
          barPercentage: 0.6,
          categoryPercentage: 0.8,
        },
      ],
    },
    options: baseOpts(t, {
      indexAxis: "y",
      scales: {
        x: {
          beginAtZero: true,
          grid: { color: t.grid, drawTicks: false },
          border: { display: false },
          ticks: { color: t.tick, font: { family: t.font, size: 11 }, padding: 6 },
          title: {
            display: true,
            text: "kWh per bulan",
            color: t.tick,
            font: { family: t.font, size: 11, weight: "500" },
            padding: { top: 6 },
          },
        },
        y: {
          grid: { display: false },
          border: { display: false },
          ticks: { color: t.label, font: { family: t.font, size: 12, weight: "600" } },
        },
      },
      plugins: {
        tooltip: {
          callbacks: { label: (c) => `${fmtNum(c.raw, 1)} kWh/bulan` },
        },
      },
    }),
  });
}

/* ------------------------------------------------------------- PERIOD COMPARE
 * One metric across three periods -> monochrome ramp, not three categories.
 */
export async function renderPeriod(canvasId, totals) {
  const C = await loadChart();
  const canvas = document.getElementById(canvasId);
  if (!C || !canvas) return;
  destroy(canvasId);

  const t = tokens();
  const wrap = canvas.parentElement;
  if (wrap) wrap.style.height = "220px";

  instances[canvasId] = new C(canvas, {
    type: "bar",
    data: {
      labels: ["Harian", "Bulanan", "Tahunan"],
      datasets: [
        {
          label: "kWh",
          data: [totals.daily, totals.monthly, totals.yearly],
          backgroundColor: sequential(3),
          borderRadius: 4,
          borderSkipped: false,
          barPercentage: 0.5,
          categoryPercentage: 0.7,
        },
      ],
    },
    options: baseOpts(t, {
      scales: axisOpts(t, { yTitle: "kWh" }),
      plugins: {
        tooltip: { callbacks: { label: (c) => `${fmtNum(c.raw, 2)} kWh` } },
      },
    }),
  });
}

/* ---------------------------------------------------------------------- DONUT
 * Carbon: past ~5 slices a donut stops being readable; a slice under 1 degree
 * is not drawn at all. Cap at 5 + "Lainnya", legend on the right, total as a
 * big number in the middle (Carbon circular-chart KPI pattern).
 */
export async function renderDonut(canvasId, rankedDevices) {
  const C = await loadChart();
  const canvas = document.getElementById(canvasId);
  if (!C || !canvas) return;
  destroy(canvasId);

  const t = tokens();
  const list = rankedDevices || [];
  if (!list.length) return;

  const MAX = 5;
  const top = list.slice(0, MAX);
  const restPct = list.slice(MAX).reduce((s, d) => s + Number(d.contribution_percentage || 0), 0);

  const labels = top.map((d) => d.device_name);
  const data = top.map((d) => Number(d.contribution_percentage) || 0);
  if (restPct > 0.05) {
    labels.push("Lainnya");
    data.push(restPct);
  }

  const wrap = canvas.parentElement;
  if (wrap) wrap.style.height = "230px";

  instances[canvasId] = new C(canvas, {
    type: "doughnut",
    data: {
      labels,
      datasets: [
        {
          data,
          backgroundColor: categorical(labels.length),
          borderColor: t.surface,
          borderWidth: 2,
          hoverOffset: 4,
        },
      ],
    },
    options: baseOpts(t, {
      scales: {},
      plugins: {
        legend: {
          display: true,
          position: "right",
          labels: {
            color: t.label,
            font: { family: t.font, size: 11 },
            boxWidth: 8,
            boxHeight: 8,
            usePointStyle: true,
            pointStyle: "rectRounded",
            padding: 9,
          },
        },
        tooltip: {
          callbacks: {
            label: (c) => `${c.label}: ${fmtNum(c.raw, 1)}%`,
          },
        },
      },
    }),
  });

  const center = document.getElementById("donut-total");
  if (center) {
    const total = list.reduce((s, d) => s + Number(d.monthly_kwh || 0), 0);
    center.textContent = fmtNum(total, 1);
  }
}

export function destroyAll() {
  Object.keys(instances).forEach(destroy);
}
