export function getApiBase() {
  // Priority: global override, then meta tag, then relative
  const g = typeof window !== "undefined" ? window.__ECG_API_BASE : "";
  if (g) return g.replace(/\/$/, "");
  const meta = typeof document !== "undefined" ? document.querySelector('meta[name="api-base"]') : null;
  const m = meta ? meta.getAttribute("content") : "";
  if (m) return m.replace(/\/$/, "");
  return ""; // relative
}

export function apiPath(path) {
  const base = getApiBase();
  return `${base}${path}`;
}
