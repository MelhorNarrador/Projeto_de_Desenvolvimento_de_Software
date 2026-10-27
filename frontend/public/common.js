const SEVERITY_COLOR = { 1: "#d32f2f", 2: "#f57c00", 3: "#fbc02d", 4: "#388e3c", 5: "#1976d2" };
const UNIT_COLOR = { available: "#388e3c", assigned: "#f57c00", en_route: "#f57c00", on_scene: "#d32f2f", unavailable: "#9e9e9e" };
const POLL_MS = 30000; // safety net only: changes arrive over the WebSocket

function session() {
  try {
    return JSON.parse(localStorage.getItem("kairos_session"));
  } catch {
    return null;
  }
}

function logout() {
  localStorage.removeItem("kairos_session");
  location.href = "index.html";
}

function requireRole(role) {
  const s = session();
  if (!s || s.user.role !== role) logout();
  return s.user;
}

async function api(path, options = {}) {
  const token = session()?.access_token;
  const response = await fetch("/api" + path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: "Bearer " + token } : {}) },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  const data = await response.json().catch(() => null);
  if (response.status === 401 && token) logout();
  if (!response.ok) throw new Error(typeof data?.detail === "string" ? data.detail : response.statusText);
  return data;
}
//------------------NOT AI WRITEN ------------------
function connectLive(districtId, onChange) {
  let timer = null;
  const changed = () => {
    clearTimeout(timer);
    timer = setTimeout(onChange, 200);
  };
  const open = () => {
    const proto = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${proto}://${location.host}/api/ws?district_id=${districtId}`);
    ws.onopen = changed;
    ws.onmessage = changed;
    ws.onclose = () => setTimeout(open, 2000);
  };
  open();
  setInterval(onChange, POLL_MS);
}
//---------------------------------------------------

function createMap() {
  const map = L.map("map").setView([39.5, -8.0], 7);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);
  return map;
}

function dot(latlng, color, radius = 8) {
  return L.circleMarker(latlng, { radius, color: "#222", weight: 1, fillColor: color, fillOpacity: 0.9 });
}

function escapeHtml(text) {
  return String(text ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}
