export function fmtKwh(v) {
  return `${Number(v).toFixed(2)}`;
}
export function fmtRupiah(v) {
  return new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(v).replace(/\s/g, " ");
}
export function fmtCo2(v) {
  return `${Number(v).toFixed(2)} kg`;
}
export function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
export function pct(v) {
  return `${Number(v).toFixed(1)}%`;
}
