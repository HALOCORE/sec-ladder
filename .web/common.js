// common.js — Slimmed-down UI utilities for static apps.
//
// This is a self-contained template version. The original lives at
//   ../../special_ui/server_ccneo/static/common.js
// and contains additional concerns (E2E encryption, file cache, workspace
// management, runmd polling, linehash diff, Monaco scrollIntoView helper)
// that only matter inside the ccneo shell. They've been removed here.
//
// What's kept:
//   - JSONML rendering (render_patch, jsonml_try, jsonml_lazy_cached)
//   - HTTP helpers (request, getJSONAsync, postJSONAsync) — NO encryption
//   - DOM helpers ($, $$, $id, delegate)
//   - Async helpers (sleepAsync, sleepUntilAsync)
//   - Function helpers (debounce, throttle)
//   - Toast notifications (requires Toastify in HTML)
//   - createSmartConfirm (modal dialog factory) — requires sc-* CSS in common.css
//   - backdropDismissAttrs (click-outside-to-dismiss helper)
//
// Everything is exported on window.UI at the bottom of the file.

console.log("===== common.js loaded =====");

// ==================== Async helpers ====================

function sleepAsync(ms) { return new Promise(r => setTimeout(r, ms)); }
async function sleepUntilAsync(cond, interval) {
  while (!cond()) await sleepAsync(interval);
}

// ==================== HTTP ====================

function request(obj, resp_type = null) {
  return new Promise((resolve, reject) => {
    let xhr = new XMLHttpRequest();
    if (resp_type) xhr.responseType = resp_type;
    xhr.open(obj.method || "GET", obj.url);
    if (obj.headers) {
      for (let k of Object.keys(obj.headers)) xhr.setRequestHeader(k, obj.headers[k]);
    }
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) resolve(xhr.response);
      else reject({ status: xhr.status, body: xhr.response });
    };
    xhr.onerror = (e) => reject(e);
    xhr.send(obj.body);
  });
}

async function getAsync(url) {
  return await request({ url, method: "GET" });
}

async function getJSONAsync(url) {
  return JSON.parse(await getAsync(url));
}

async function postJSONAsync(url, data) {
  let body = JSON.stringify(data);
  let result = await request({
    url,
    method: "POST",
    headers: { "Content-Type": "application/json;charset=UTF-8" },
    body,
  });
  return JSON.parse(result);
}

// ==================== Function helpers ====================

function debounce(func, wait, immediate) {
  let timeout;
  return function () {
    let ctx = this, args = arguments;
    let later = function () { timeout = null; if (!immediate) func.apply(ctx, args); };
    let callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(ctx, args);
  };
}

function throttle(func, limit) {
  let inThrottle;
  return function () {
    if (!inThrottle) {
      func.apply(this, arguments);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// ==================== Toast notifications ====================

function toast_info(s)    { Toastify({ text: s, gravity: "bottom", position: "center", className: "toast-info",    duration: 3000 }).showToast(); }
function toast_error(s)   { Toastify({ text: s, gravity: "bottom", position: "center", className: "toast-error",   duration: 6000 }).showToast(); }
function toast_success(s) { Toastify({ text: s, gravity: "bottom", position: "center", className: "toast-success", duration: 3000 }).showToast(); }

// ==================== JSONML rendering ====================

let _JSONML_LAZY_CACHE = {};

function jsonml_cache_clear() { _JSONML_LAZY_CACHE = {}; }
function jsonml_cache_invalidate(key) { delete _JSONML_LAZY_CACHE[key]; }

/** Lazy-load + cache async data, render placeholder until ready. */
function jsonml_lazy_cached(cache_key, arg, loader_async_f, jml_f, render_callback) {
  if (!(cache_key in _JSONML_LAZY_CACHE)) {
    _JSONML_LAZY_CACHE[cache_key] = { status: "LOADING" };
    (async () => {
      try {
        let result = await loader_async_f(arg);
        _JSONML_LAZY_CACHE[cache_key] = { status: "LOADED", data: result };
      } catch (e) {
        _JSONML_LAZY_CACHE[cache_key] = { status: "ERROR", error: e };
      }
      render_callback();
    })();
  }
  let cached = _JSONML_LAZY_CACHE[cache_key];
  if (cached.status === "LOADING") return ["div.loading-indicator", "Loading..."];
  if (cached.status === "ERROR")   return ["div.error-indicator",   "Error: " + String(cached.error)];
  return jml_f(cached.data);
}

/** Wrap a JSONML-generating function with try/catch. */
function jsonml_try(jsonml_func, args) {
  try { return jsonml_func(...args); }
  catch (e) { console.error("JSONML generation error:", e); return ["div.jsonml-error", "Error: " + String(e)]; }
}

/** Patch `elem` with JSONML produced by `jsonml_or_func`. */
function render_patch(elem, jsonml_or_func, data) {
  let jml = (typeof jsonml_or_func === "function") ? jsonml_or_func(data) : jsonml_or_func;
  IncrementalDOM.patch(elem, jsonml2idom, jml);
}

// ==================== DOM helpers ====================

function $(sel)   { return document.querySelector(sel); }
function $$(sel)  { return document.querySelectorAll(sel); }
function $id(id)  { return document.getElementById(id); }

function delegate(container, eventType, selector, handler) {
  container.addEventListener(eventType, (e) => {
    let target = e.target.closest(selector);
    if (target && container.contains(target)) handler(e, target);
  });
}

// ==================== Smart Confirm Dialog Factory ====================
// Modal dialog with optional fields (text / combobox / select / radio /
// checkbox / textarea / info). Requires:
//   - #sc-backdrop + #sc-dialog elements in the page HTML.
//   - .sc-* CSS rules from common.css.
// Returns { show(config), dismiss(confirmed) }. See JSDoc on `show` below.
//
// config: {
//   title: string,
//   message?: string,
//   confirmLabel: string,
//   confirmCls?: string,            // ".sc-danger" | ".sc-warning" | ".sc-teal" | ".sc-green"
//   fields?: Array<Field>,
//   validate?: ({...values}) => string|null   // return error string to keep open
// }

function createSmartConfirm(backdropEl, dialogEl) {
  let _resolve = null;
  let _values = {};
  let _errMsg = null;

  function show(config) {
    if (_resolve) return Promise.resolve({ confirmed: false, values: {} });
    _values = {};
    _errMsg = null;
    if (config.fields) for (let f of config.fields) _values[f.key] = f.value || "";
    return new Promise(resolve => {
      _resolve = resolve;
      _render(config);
      backdropEl.style.display = "flex";
      document.addEventListener("keydown", _keyHandler);
    });
  }

  function dismiss(confirmed) {
    backdropEl.style.display = "none";
    document.removeEventListener("keydown", _keyHandler);
    let resolve = _resolve;
    _resolve = null;
    if (resolve) resolve({ confirmed, values: confirmed ? { ..._values } : {} });
  }

  function _keyHandler(e) {
    if (e.key === "Escape") { dismiss(false); e.preventDefault(); e.stopImmediatePropagation(); }
  }

  function _render(config) {
    let rows = [];
    if (config.fields) {
      for (let f of config.fields) {
        if (f.type === "text" || f.type === "combobox") {
          let attrs = {
            id: "sc-input-" + f.key,
            oninput: (e) => { _values[f.key] = e.target.value; },
            onkeydown: (e) => { if (e.key === "Enter") dismiss(true); },
          };
          if (f.placeholder) attrs.placeholder = f.placeholder;
          if (f.type === "combobox") attrs.list = "sc-dl-" + f.key;
          let row = ["div.sc-field", { key: "sc-f-" + f.key },
            ["label.sc-label", f.label],
            ["input.sc-input", attrs],
          ];
          if (f.type === "combobox") {
            row.push(["datalist", { id: "sc-dl-" + f.key },
              ...f.options.map(o => ["option", { value: o }])
            ]);
          }
          rows.push(row);
        } else if (f.type === "select") {
          rows.push(["div.sc-field", { key: "sc-f-" + f.key },
            ["label.sc-label", f.label],
            ["select.sc-select", {
              id: "sc-input-" + f.key,
              onchange: (e) => { _values[f.key] = e.target.value; },
            },
              ...f.options.map(o => {
                let val = typeof o === "object" ? o.value : o;
                let lbl = typeof o === "object" ? o.label : (o || "(none)");
                return ["option", { value: val, selected: val === f.value ? true : undefined }, lbl];
              })
            ]
          ]);
        } else if (f.type === "radio") {
          rows.push(["div.sc-field", { key: "sc-f-" + f.key },
            ["label.sc-label", f.label],
            ["div.sc-radio-group",
              ...f.options.map(o => {
                let val = typeof o === "object" ? o.value : o;
                let lbl = typeof o === "object" ? o.label : o;
                return ["label.sc-radio-item", { key: "sc-r-" + f.key + "-" + val },
                  ["input", { type: "radio", name: "sc-radio-" + f.key, value: val,
                    checked: val === f.value ? true : undefined,
                    onchange: (e) => { _values[f.key] = e.target.value; } }],
                  ["span", lbl]
                ];
              })
            ]
          ]);
        } else if (f.type === "checkbox") {
          rows.push(["div.sc-field", { key: "sc-f-" + f.key },
            ["label.sc-checkbox-item",
              ["input", { type: "checkbox", id: "sc-input-" + f.key,
                checked: f.value === "true" ? true : undefined,
                onchange: (e) => { _values[f.key] = e.target.checked ? "true" : "false"; } }],
              ["span", f.label]
            ]
          ]);
        } else if (f.type === "textarea") {
          rows.push(["div.sc-field", { key: "sc-f-" + f.key },
            ["label.sc-label", f.label],
            ["textarea.sc-textarea", {
              id: "sc-input-" + f.key,
              rows: f.rows || 4,
              placeholder: f.placeholder || "",
              skip: true,
              oninput: (e) => { _values[f.key] = e.target.value; },
            }]
          ]);
        } else if (f.type === "info") {
          rows.push(["div.sc-field", { key: "sc-f-" + f.key },
            f.label ? ["label.sc-label", f.label] : undefined,
            ["pre.sc-info", f.value]
          ]);
        }
      }
    }

    render_patch(dialogEl, () =>
      ["div.sc-content",
        ["div.sc-title", config.title],
        config.message ? ["div.sc-message", config.message] : undefined,
        rows.length > 0 ? ["div.sc-fields", ...rows] : undefined,
        _errMsg ? ["div.sc-error", _errMsg] : undefined,
        ["div.sc-actions",
          ["button.sc-btn.sc-btn-cancel", { onclick: () => dismiss(false) }, "Cancel"],
          ["button.sc-btn" + (config.confirmCls || ".sc-danger"), {
            onclick: () => {
              if (config.validate) {
                let err = config.validate({ ..._values });
                if (err) { _errMsg = err; _render(config); return; }
              }
              _errMsg = null;
              dismiss(true);
            }
          }, config.confirmLabel]
        ]
      ]
    );

    // Imperative value sync for inputs/selects/radios/checkboxes.
    // IncrementalDOM doesn't reliably set .value/.checked, and we want re-renders
    // (triggered by validation errors) to preserve what the user typed.
    if (config.fields) {
      for (let f of config.fields) {
        if (f.type === "radio") {
          let cur = _values[f.key];
          for (let r of dialogEl.querySelectorAll('input[name="sc-radio-' + f.key + '"]')) r.checked = (r.value === cur);
        } else if (f.type === "checkbox") {
          let el = document.getElementById("sc-input-" + f.key);
          if (el) el.checked = (_values[f.key] === "true");
        } else if (f.type === "info") {
          // pre block, no value to sync
        } else {
          let el = document.getElementById("sc-input-" + f.key);
          if (el && el.value !== _values[f.key]) el.value = _values[f.key] || "";
        }
      }
    }

    setTimeout(() => {
      if (config.fields) {
        for (let f of config.fields) {
          if (f.type === "text" || f.type === "combobox") {
            let el = document.getElementById("sc-input-" + f.key);
            if (el) { el.focus(); el.select(); return; }
          }
        }
      }
      let btn = dialogEl.querySelector(".sc-btn:not(.sc-btn-cancel)");
      if (btn) btn.focus();
    }, 0);
  }

  // Click-outside-to-dismiss with mousedown guard (so selecting text inside an
  // input and releasing on the backdrop doesn't accidentally close the dialog).
  let _mouseDownOnBackdrop = false;
  backdropEl.addEventListener("mousedown", (e) => { _mouseDownOnBackdrop = (e.target === backdropEl); });
  backdropEl.addEventListener("click", (e) => {
    let armed = _mouseDownOnBackdrop;
    _mouseDownOnBackdrop = false;
    if (armed && e.target === backdropEl) dismiss(false);
  });

  return { show, dismiss };
}

// ==================== Backdrop dismiss helper ====================
// Returns { onmousedown, onclick } attrs for any backdrop element.
// Mousedown guard prevents drag-to-select-then-release-on-backdrop from
// dismissing the panel.

let _BD_ARMED = false;
function backdropDismissAttrs(onDismiss) {
  return {
    onmousedown: (e) => { _BD_ARMED = (e.target === e.currentTarget); },
    onclick: (e) => {
      let armed = _BD_ARMED;
      _BD_ARMED = false;
      if (armed && e.target === e.currentTarget) onDismiss(e);
    },
  };
}

// ==================== Window export ====================

if (typeof window !== "undefined") {
  window.UI = {
    sleepAsync, sleepUntilAsync,
    request, getAsync, getJSONAsync, postJSONAsync,
    debounce, throttle,
    toast_info, toast_error, toast_success,
    jsonml_cache_clear, jsonml_cache_invalidate, jsonml_lazy_cached, jsonml_try, render_patch,
    $, $$, $id, delegate,
    createSmartConfirm, backdropDismissAttrs,
  };
}
