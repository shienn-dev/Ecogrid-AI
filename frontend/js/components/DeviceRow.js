export function createDeviceRow(index, onRemove) {
  const card = document.createElement("div");
  card.className = "device-card";
  card.dataset.index = String(index);
  // Compact card: name on its own line, watt + hours share a row so the
  // slider shows real content rather than a tall empty column.
  card.innerHTML = `
    <div class="device-head">
      <div class="device-title"><i class="fa-solid fa-plug"></i> Perangkat ${index + 1}</div>
      <button type="button" class="btn-remove" aria-label="Hapus perangkat">
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>
    <div class="field">
      <label class="label" for="dev-name-${index}">Nama</label>
      <input id="dev-name-${index}" class="input device-name" type="text"
             placeholder="AC, Kulkas, TV" autocomplete="off" required
             aria-describedby="err-name-${index}" />
      <div id="err-name-${index}" class="field-error" role="alert"></div>
    </div>
    <div class="device-fields">
      <div class="field">
        <label class="label" for="dev-watt-${index}">Daya</label>
        <div class="input-wrap">
          <input id="dev-watt-${index}" class="input device-watt" type="number"
                 inputmode="decimal" placeholder="150" min="0.1" step="any" required
                 style="padding-left:10px; padding-right:26px"
                 aria-describedby="err-watt-${index}" />
          <span class="input-badge">W</span>
        </div>
        <div id="err-watt-${index}" class="field-error" role="alert"></div>
      </div>
      <div class="field">
        <label class="label" for="dev-hours-${index}">Jam/hari</label>
        <div class="input-wrap">
          <input id="dev-hours-${index}" class="input device-hours" type="number"
                 inputmode="decimal" placeholder="8" min="0.01" max="24" step="any" required
                 style="padding-left:10px; padding-right:26px"
                 aria-describedby="err-hours-${index}" />
          <span class="input-badge">jam</span>
        </div>
        <div id="err-hours-${index}" class="field-error" role="alert"></div>
      </div>
    </div>
  `;
  const btn = card.querySelector(".btn-remove");
  btn.addEventListener("click", () => onRemove(card));
  // inline validation helpers
  const nameEl = card.querySelector(".device-name");
  const wattEl = card.querySelector(".device-watt");
  const hoursEl = card.querySelector(".device-hours");
  function setErr(input, id, msg) {
    const err = card.querySelector(`#${id}`);
    if (msg) {
      input.setAttribute("aria-invalid", "true");
      err.textContent = msg;
      err.dataset.visible = "true";
    } else {
      input.removeAttribute("aria-invalid");
      err.textContent = "";
      err.dataset.visible = "false";
    }
  }
  nameEl.addEventListener("blur", () => {
    const v = nameEl.value.trim();
    setErr(nameEl, `err-name-${index}`, v ? "" : "Nama perangkat wajib diisi.");
  });
  wattEl.addEventListener("blur", () => {
    const v = parseFloat(wattEl.value);
    setErr(wattEl, `err-watt-${index}`, !wattEl.value || isNaN(v) || v <= 0 ? "Daya harus > 0." : "");
  });
  hoursEl.addEventListener("blur", () => {
    const v = parseFloat(hoursEl.value);
    let msg = "";
    if (!hoursEl.value || isNaN(v)) msg = "Jam wajib diisi.";
    else if (v <= 0 || v > 24) msg = "Jam harus 0.01–24.";
    setErr(hoursEl, `err-hours-${index}`, msg);
  });
  return card;
}

export function readDevices(container) {
  const cards = [...container.querySelectorAll(".device-card")];
  const devices = [];
  let ok = true;
  for (const card of cards) {
    const name = card.querySelector(".device-name").value.trim();
    const watt = card.querySelector(".device-watt").value;
    const hours = card.querySelector(".device-hours").value;
    const nameErr = card.querySelector(`[id^="err-name-"]`);
    const wattErr = card.querySelector(`[id^="err-watt-"]`);
    const hoursErr = card.querySelector(`[id^="err-hours-"]`);
    // reset
    for (const e of [nameErr, wattErr, hoursErr]) { e.textContent=""; e.dataset.visible="false"; }
    for (const inp of card.querySelectorAll(".input")) inp.removeAttribute("aria-invalid");

    if (!name) {
      nameErr.textContent = "Nama perangkat wajib diisi.";
      nameErr.dataset.visible = "true";
      card.querySelector(".device-name").setAttribute("aria-invalid","true");
      ok = false;
    }
    const w = parseFloat(watt);
    if (!watt || isNaN(w) || w <= 0) {
      wattErr.textContent = "Daya harus > 0.";
      wattErr.dataset.visible = "true";
      card.querySelector(".device-watt").setAttribute("aria-invalid","true");
      ok = false;
    }
    const h = parseFloat(hours);
    if (!hours || isNaN(h) || h <= 0 || h > 24) {
      hoursErr.textContent = "Jam harus 0.01–24.";
      hoursErr.dataset.visible = "true";
      card.querySelector(".device-hours").setAttribute("aria-invalid","true");
      ok = false;
    }
    if (name && !isNaN(w) && w>0 && !isNaN(h) && h>0 && h<=24) {
      devices.push({ device_name: name, watt: w, hours_per_day: h });
    }
  }
  return { ok, devices };
}

export function reindex(container) {
  const cards = [...container.querySelectorAll(".device-card")];

  cards.forEach((card, i) => {
    card.dataset.index = String(i);

    const title = card.querySelector(".device-title");
    title.innerHTML = `<i class="fa-solid fa-plug"></i> Perangkat ${i + 1}`;

    // IDs must be unique and labels must point at the right input
    const pairs = [
      [".device-name", `dev-name-${i}`, `err-name-${i}`],
      [".device-watt", `dev-watt-${i}`, `err-watt-${i}`],
      [".device-hours", `dev-hours-${i}`, `err-hours-${i}`],
    ];
    pairs.forEach(([inputSel, id, errId]) => {
      const input = card.querySelector(inputSel);
      if (!input) return;
      input.id = id;
      input.setAttribute("aria-describedby", errId);
    });

    const labels = card.querySelectorAll(".label");
    if (labels[0]) labels[0].setAttribute("for", `dev-name-${i}`);
    if (labels[1]) labels[1].setAttribute("for", `dev-watt-${i}`);
    if (labels[2]) labels[2].setAttribute("for", `dev-hours-${i}`);

    const errs = card.querySelectorAll(".field-error");
    if (errs[0]) errs[0].id = `err-name-${i}`;
    if (errs[1]) errs[1].id = `err-watt-${i}`;
    if (errs[2]) errs[2].id = `err-hours-${i}`;
  });

  // Keep at least one row; hide the remove control when it is the only one.
  cards.forEach((card) => {
    const btn = card.querySelector(".btn-remove");
    if (btn) btn.style.display = cards.length <= 1 ? "none" : "grid";
  });
}
