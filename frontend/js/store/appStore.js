// Tiny pub/sub store for calculation results
const listeners = new Set();
let state = {
  devices: [],
  result: null, // last calculation data
  loading: false,
  error: null,
};

export function getState() {
  return state;
}

export function setState(patch) {
  state = { ...state, ...patch };
  for (const fn of listeners) fn(state);
}

export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export function resetResult() {
  setState({ result: null, error: null });
}
