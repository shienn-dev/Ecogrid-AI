import { api } from "../api/client.js";

const KEY = "ecogrid_history_v1";

export function loadLocal() {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "[]");
  } catch {
    return [];
  }
}
export function saveLocal(list) {
  localStorage.setItem(KEY, JSON.stringify(list.slice(0, 50)));
}

export async function fetchHistory(limit = 20, offset = 0) {
  try {
    const res = await api.listHistory(limit, offset);
    return res.data || [];
  } catch {
    // fallback local
    return loadLocal();
  }
}

export function pushLocal(entry) {
  const list = loadLocal();
  list.unshift(entry);
  saveLocal(list);
}
