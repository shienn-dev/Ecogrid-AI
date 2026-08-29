import { apiPath } from "./config.js";

async function request(path, { method = "GET", body, signal, headers = {} } = {}) {
  const url = apiPath(path);
  const opts = {
    method,
    headers: { "Content-Type": "application/json", ...headers },
    signal,
  };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const controller = !signal ? new AbortController() : null;
  const timeout = setTimeout(() => controller && controller.abort(), 8000);
  try {
    const res = await fetch(url, { ...opts, signal: signal || controller?.signal });
    const json = await res.json().catch(() => ({}));
    if (!res.ok) {
      const msg = json.message || `Request failed (${res.status})`;
      const err = new Error(msg);
      err.status = res.status;
      err.data = json;
      throw err;
    }
    return json;
  } finally {
    clearTimeout(timeout);
  }
}

export const api = {
  calculateEnergy(devices, opts = {}) {
    const save = opts.save ? "?save=true" : "";
    // unified expects {devices}
    return request(`/api/energy/calculate${save}`, { method: "POST", body: { devices } });
  },
  calculateCost(payload) {
    return request(`/api/cost/calculate`, { method: "POST", body: payload });
  },
  calculateCarbon(payload) {
    return request(`/api/carbon/calculate`, { method: "POST", body: payload });
  },
  simulateSolar(payload) {
    return request(`/api/solar/simulate`, { method: "POST", body: payload });
  },
  listHistory(limit = 20, offset = 0) {
    return request(`/api/history?limit=${limit}&offset=${offset}`);
  },
  getHistory(id) {
    return request(`/api/history/${id}`);
  },
  deleteHistory(id) {
    return request(`/api/history/${id}`, { method: "DELETE" });
  },
  analyzeAdvisor(payload) {
    return request(`/api/advisor/analyze`, { method: "POST", body: payload });
  },
  getAdvisorTips(device) {
    const q = device ? `?device=${encodeURIComponent(device)}` : "";
    return request(`/api/advisor/tips${q}`);
  },
};
