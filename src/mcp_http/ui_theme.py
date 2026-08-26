"""
Shared design tokens/components and MCP Apps bridge shim for every UI
widget in mcp_http/ui/*.html.

Owns: the ONE copy of CSS tokens/base component styles and the Bridge
handshake JS that every widget previously duplicated independently (see
docs/mcp-ui-architecture.md's duplication note and the 2026-08 UI redesign
plan). Injected server-side by ui_resources.py's read_resource_contents()
— never touched directly by any individual widget file.

Palette source: scanova.io's theme-color meta tag + Bootstrap variable
overrides (confirmed via page source). --accent and --danger are
deliberately different reds — the site's own primary color collides with
what these widgets previously used for error state.
"""

SHARED_STYLE = """
:root {
  --bg: #ffffff;
  --fg: #121314;
  --muted: #756e69;
  --border: #e6e0dc;
  --accent: #c0392b;
  --accent-hover: #a53023;
  --danger: #dc2626;
  --success: #1e824c;
  --radius: 10px;
  --row-hover: #f7f4f2;
  --shadow-sm: 0 1px 2px rgba(0,0,0,.06);
  --shadow-md: 0 4px 12px rgba(0,0,0,.05);
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #17130f;
    --fg: #f2ece9;
    --muted: #a89e98;
    --border: #332c29;
    --accent: #e0554a;
    --accent-hover: #ea6b60;
    --row-hover: #241f1c;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 16px; background: var(--bg); color: var(--fg);
  font: 14px/1.5 Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, "Noto Sans", sans-serif;
}
button {
  padding: 8px 14px; border: none; border-radius: var(--radius);
  background: var(--accent); color: #fff; font-weight: 600; cursor: pointer;
  font: inherit; font-size: 13px; transition: background .15s ease;
}
button:hover:not(:disabled) { background: var(--accent-hover); }
button:disabled { opacity: 0.45; cursor: default; }
button.link {
  background: none; color: var(--accent); text-decoration: underline;
  padding: 0; font-weight: 500;
}
button.link:hover:not(:disabled) { background: none; color: var(--accent-hover); }
button.danger { background: var(--danger); }
button.danger:hover:not(:disabled) { background: #b91c1c; }
button.secondary {
  background: transparent; color: var(--accent); border: 1px solid var(--accent);
}
button.secondary:hover:not(:disabled) { background: rgba(192,57,43,.06); }

input[type="text"], input[type="number"], input[type="color"],
select, textarea {
  padding: 7px 10px; border: 1px solid var(--border); border-radius: 8px;
  background: var(--bg); color: var(--fg); font: inherit;
}
input:focus, select:focus, textarea:focus {
  outline: none; border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(192,57,43,.15);
}
textarea { resize: vertical; }

table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: 8px 6px; border-bottom: 1px solid var(--border); font-size: 13px; }
th { color: var(--muted); font-weight: 600; }
tr:hover td { background: var(--row-hover); }

.card {
  background: var(--bg); border: 1px solid var(--border);
  border-radius: var(--radius); box-shadow: var(--shadow-sm);
}

.status { margin-top: 8px; font-size: 12px; color: var(--muted); min-height: 16px; }
.status.error, .error { color: var(--danger); }
.status.success, .success { color: var(--success); }
.empty { color: var(--muted); text-align: center; padding: 20px 0; }

fieldset { border: 1px solid var(--border); border-radius: var(--radius); padding: 12px; }
legend { padding: 0 6px; color: var(--muted); font-size: 12px; }

.row { display: flex; gap: 8px; margin-bottom: 8px; align-items: center; }
.row label { color: var(--muted); font-size: 12px; }

/* Deliberately unskippable destructive-action confirmation — shared by
   every widget with a delete action, no "don't ask again" affordance. */
.confirm-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,0.45);
  display: flex; align-items: center; justify-content: center;
}
.confirm-box {
  background: var(--bg); color: var(--fg); border-radius: var(--radius);
  box-shadow: var(--shadow-md); padding: 16px; width: 260px;
}
.confirm-box .row label { flex: 0 0 auto; }
.confirm-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 12px; }
"""

# The MCP Apps postMessage handshake (spec 2026-01-26,
# https://apps.extensions.modelcontextprotocol.io) plus OpenAI Apps SDK
# feature-detection — identical logic every widget previously duplicated.
# Each widget's own <script> now just does: const Bridge = window.__scanovaBridge();
SHARED_BRIDGE_SCRIPT = """
// Override --bg with the host's real chat-surface color (user-supplied,
// not derived from any host API — MCP Apps' hostContext.styles.variables
// would be the "correct" long-term source but isn't confirmed to be
// populated by real hosts yet). Runs synchronously before <body> renders
// (this <script> follows the shared <style> in <head>, both injected
// before window.__scanovaBridge() is ever called), so there's no flash of
// the SHARED_STYLE fallback palette. window.openai presence is the same
// convention check window.__scanovaBridge() uses below, duplicated here
// because this must run before any widget calls that factory function.
(function () {
  var isOpenAI = !!(window.openai && typeof window.openai.callTool === "function");
  var isDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  var bg = isOpenAI
    ? (isDark ? "#000000" : "#fcfbfa")
    : (isDark ? "#151515" : "#fcfbfa");
  document.documentElement.style.setProperty("--bg", bg);
})();

window.__scanovaBridge = function () {
  if (window.openai && typeof window.openai.callTool === "function") {
    return {
      convention: "openai",
      ready: Promise.resolve(),
      getInitialData: () => window.openai.toolOutput || null,
      // window.openai.callTool resolves to {content, structuredContent, _meta} —
      // unwrap structuredContent so callers get the same envelope shape as the
      // postMessage branch's callTool below (and as toolOutput already is).
      callTool: (name, args) =>
        window.openai.callTool(name, args).then((result) => (result && result.structuredContent) || null),
      onToolResult: () => {},
    };
  }

  // Standard MCP Apps postMessage bridge. The host will not render or send
  // anything to this iframe until it receives our ui/notifications/initialized
  // notification, so that handshake must complete before anything else happens.
  let nextId = 0;
  const pending = new Map();
  const toolResultHandlers = [];

  function request(method, params) {
    return new Promise((resolve, reject) => {
      const id = ++nextId;
      pending.set(id, { resolve, reject });
      window.parent.postMessage({ jsonrpc: "2.0", id, method, params: params || {} }, "*");
    });
  }

  function notify(method, params) {
    window.parent.postMessage({ jsonrpc: "2.0", method, params: params || {} }, "*");
  }

  window.addEventListener("message", (event) => {
    const msg = event.data;
    if (!msg || typeof msg !== "object" || msg.jsonrpc !== "2.0") return;

    if (msg.id !== undefined && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      if (msg.error) reject(msg.error); else resolve(msg.result);
      return;
    }

    if (msg.method === "ui/notifications/tool-result") {
      const data = (msg.params && msg.params.structuredContent) || null;
      toolResultHandlers.forEach((cb) => cb(data));
    }
  });

  const ready = request("ui/initialize", {
    capabilities: {},
    appInfo: { name: "scanova-mcp-ui", version: "1.0.0" },
    protocolVersion: "2026-01-26",
    appCapabilities: { experimental: {}, tools: { listChanged: false }, availableDisplayModes: ["inline"] },
  }).then(() => {
    notify("ui/notifications/initialized", {});
  });

  // Tell the host how big this widget actually is — without this, hosts
  // fall back to a small default iframe size and the content has to be
  // scrolled. Report once ready, then on every subsequent content resize.
  function reportSize() {
    notify("ui/notifications/size-changed", {
      width: document.documentElement.scrollWidth,
      height: document.documentElement.scrollHeight,
    });
  }
  ready.then(reportSize);
  if (typeof ResizeObserver !== "undefined") {
    new ResizeObserver(reportSize).observe(document.documentElement);
  }

  return {
    convention: "postMessage",
    ready,
    getInitialData: () => null,
    callTool: (name, args) =>
      request("tools/call", { name, arguments: args }).then(
        (result) => (result && result.structuredContent) || null
      ),
    onToolResult: (cb) => toolResultHandlers.push(cb),
  };
};
"""
