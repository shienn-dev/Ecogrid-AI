export function el(tag, attrs = {}, children = []) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v;
    else if (k === "text") e.textContent = v;
    else if (k === "html") e.innerHTML = v;
    else if (k.startsWith("on") && typeof v === "function") e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v);
  }
  for (const c of [].concat(children)) {
    if (c == null) continue;
    if (typeof c === "string") e.appendChild(document.createTextNode(c));
    else e.appendChild(c);
  }
  return e;
}

export function showToast(message, type = "info", ttl = 4000) {
  let stack = document.getElementById("toast-stack");
  if (!stack) {
    stack = el("div", { id: "toast-stack", class: "toast-stack", "aria-live": "polite" });
    document.body.appendChild(stack);
  }
  const icon = type === "error" ? "fa-circle-exclamation" : type === "success" ? "fa-circle-check" : "fa-circle-info";
  const t = el("div", { class: `toast ${type}`, role: "status" }, [
    el("i", { class: `fa-solid ${icon}`, style: "margin-top:2px;color:var(--text-tertiary)" }),
    el("div", {}, [el("div", { text: message })]),
  ]);
  stack.appendChild(t);
  setTimeout(() => {
    t.style.opacity = "0";
    t.style.transform = "translateY(4px)";
    setTimeout(() => t.remove(), 250);
  }, ttl);
}
