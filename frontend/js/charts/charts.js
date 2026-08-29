let ChartCtor = null;
let instances = {};

async function getChart() {
  if (ChartCtor) return ChartCtor;
  // Try ESM CDN, fallback to UMD global if offline fails
  try {
    const mod = await import("https://cdn.jsdelivr.net/npm/chart.js@4.4.7/+esm");
    ChartCtor = mod.Chart;
    const { registerables } = mod;
    ChartCtor.register(...registerables);
    return ChartCtor;
  } catch (e) {
    // fallback: try local or fail silently
    console.warn("Chart.js load failed", e);
    return null;
  }
}

export async function renderContribution(canvasId, rankedDevices) {
  const Chart = await getChart();
  if (!Chart) return;
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (instances[canvasId]) instances[canvasId].destroy();
  const labels = rankedDevices.map((d) => d.device_name);
  const data = rankedDevices.map((d) => Number(d.monthly_kwh.toFixed(2)));
  const colors = ["#0f766e", "#0e7490", "#475569", "#d97706", "#059669", "#64748b"];
  instances[canvasId] = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "kWh / bulan",
          data,
          backgroundColor: labels.map((_, i) => colors[i % colors.length] + "E6"),
          borderColor: labels.map((_, i) => colors[i % colors.length]),
          borderWidth: 1,
          borderRadius: 8,
          barThickness: 18,
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (c) => `${c.label}: ${c.raw} kWh/bulan`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: "#f1f5f9" },
          ticks: { color: "#64748b", font: { size: 11 } },
        },
        y: {
          grid: { display: false },
          ticks: { color: "#0f172a", font: { size: 12, weight: "600" } },
        },
      },
      animation: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? false : { duration: 600 },
    },
  });
}

export async function renderPeriod(canvasId, totals) {
  const Chart = await getChart();
  if (!Chart) return;
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (instances[canvasId]) instances[canvasId].destroy();
  const labels = ["Harian", "Bulanan", "Tahunan"];
  const kwh = [totals.daily, totals.monthly, totals.yearly];
  instances[canvasId] = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "kWh",
          data: kwh,
          backgroundColor: ["#0f766eE6", "#0e7490E6", "#475569E6"],
          borderColor: ["#0f766e", "#0e7490", "#475569"],
          borderWidth: 1,
          borderRadius: 8,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: (c) => `${c.raw.toFixed(2)} kWh` } },
      },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#64748b", font: { size: 11 } } },
        y: { grid: { color: "#f1f5f9" }, ticks: { color: "#64748b", font: { size: 11 } } },
      },
      animation: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? false : { duration: 600 },
    },
  });
}

export async function renderDonut(canvasId, rankedDevices) {
  const Chart = await getChart();
  if (!Chart) return;
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  if (instances[canvasId]) instances[canvasId].destroy();
  const labels = rankedDevices.map((d) => `${d.device_name} (${d.contribution_percentage.toFixed(1)}%)`);
  const data = rankedDevices.map((d) => d.contribution_percentage);
  const colors = ["#0f766e", "#0e7490", "#475569", "#d97706", "#059669", "#94a3b8"];
  instances[canvasId] = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{ data, backgroundColor: colors, borderWidth: 1, borderColor: "#ffffff", hoverOffset: 6 }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "62%",
      plugins: {
        legend: { position: "bottom", labels: { color: "#475569", font: { size: 11 }, boxWidth: 12, padding: 16 } },
        tooltip: { callbacks: { label: (c) => `${c.label}: ${c.raw.toFixed(1)}%` } },
      },
      animation: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? false : { duration: 600 },
    },
  });
}

export function destroyAll() {
  for (const k of Object.keys(instances)) {
    try { instances[k].destroy(); } catch {}
  }
  instances = {};
}
