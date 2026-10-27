const user = requireRole("crew");
const NEXT_STEP = {
  assigned: { status: "en_route", label: "On my way" },
  en_route: { status: "on_scene", label: "Arrived on scene" },
  on_scene: { status: "available", label: "Mission complete" },
};

const map = createMap();
const layer = L.layerGroup().addTo(map);
const $ = (id) => document.getElementById(id);
let myUnit = null;
let route = null;

$("who").textContent = user.name;
$("logout").onclick = logout;

async function act(promise) {
  $("message").textContent = "";
  try {
    await promise;
  } catch (err) {
    $("message").textContent = "Error: " + err.message;
  }
  refresh();
}

const body = (extra = {}) => ({ app_user_id: user.id, ...extra });

function startShift(unitId) {
  act(api(`/units/${unitId}/start-shift`, { method: "POST", body: body() }));
}

function endShift() {
  act(api(`/units/${myUnit.id}/end-shift`, { method: "POST", body: body() }));
}

function setStatus(status) {
  act(api(`/units/${myUnit.id}/status`, { method: "PATCH", body: body({ status }) }));
}

// The browser only reports a position on start and when it changes, so keep the last one
// and send it as soon as we know the unit.
let lastPosition = null;
let sentPosition = null;

function sendPosition() {
  if (!myUnit || !lastPosition || lastPosition === sentPosition) return;
  sentPosition = lastPosition;
  api(`/units/${myUnit.id}/position`, { method: "PATCH", body: body(lastPosition) }).catch(() => {});
}

// Demo: clicking the map moves the vehicle there and stops using the real GPS.
let simulated = false;
map.on("click", (e) => {
  simulated = true;
  lastPosition = { latitude: e.latlng.lat, longitude: e.latlng.lng };
  sendPosition();
  setTimeout(refresh, 300);
});

if (navigator.geolocation) {
  navigator.geolocation.watchPosition(
    (p) => {
      if (simulated) return;
      lastPosition = { latitude: p.coords.latitude, longitude: p.coords.longitude };
      sendPosition();
    },
    (err) => ($("message").textContent = "Location unavailable: " + err.message),
    { enableHighAccuracy: true },
  );
}

function addButton(label, onclick) {
  const b = document.createElement("button");
  b.textContent = label;
  b.onclick = onclick;
  $("content").appendChild(b);
}

async function refresh() {
  try {
    const units = await api(`/units?district_id=${user.district_id}`);
    myUnit = units.find((u) => u.user_id === user.id) || null;
    sendPosition();
    layer.clearLayers();

    if (!myUnit) {
      route = null;
      const free = units.filter((u) => u.user_id === null);
      $("content").innerHTML = "<h2>Choose a vehicle</h2>" + (free.length ? "" : "<p class='muted'>No free vehicles.</p>");
      for (const u of free) addButton(`Start shift — ${u.code} (${u.support_level})`, () => startShift(u.id));
      return;
    }

    dot([myUnit.latitude, myUnit.longitude], UNIT_COLOR[myUnit.status], 9).bindTooltip(myUnit.code).addTo(layer);
    let html = `<h2>${escapeHtml(myUnit.code)}</h2><p>Status: <b>${myUnit.status}</b></p>`;

    if (myUnit.incident_id) {
      const i = await api(`/incidents/${myUnit.incident_id}`);
      dot([i.latitude, i.longitude], SEVERITY_COLOR[i.severity], 11).addTo(layer);
      await loadRoute(i);
      html += `<h2>Mission #${i.id} — severity ${i.severity}</h2>` +
        `<p>${escapeHtml(i.address || `${i.latitude.toFixed(5)}, ${i.longitude.toFixed(5)}`)}</p>` +
        `<p>${escapeHtml(i.victim_name)}<br>${escapeHtml(i.description)}</p>` +
        (route?.seconds != null ? `<p>ETA ${Math.round(route.seconds / 60)} min</p>` : "");
    } else {
      route = null;
      map.setView([myUnit.latitude, myUnit.longitude], 14);
      html += "<p class='muted'>Waiting for a mission.</p>";
    }

    $("content").innerHTML = html;
    const next = NEXT_STEP[myUnit.status];
    if (next) addButton(next.label, () => setStatus(next.status));
    if (myUnit.status === "available") addButton("End shift", endShift);
  } catch (err) {
    $("message").textContent = "Error: " + err.message;
  }
}

async function loadRoute(incident) {
  const key = `${incident.id}:${myUnit.latitude}:${myUnit.longitude}`;
  if (route?.key !== key) {
    const r = await api(`/units/${myUnit.id}/route`).catch(() => null);
    route = { key, seconds: r?.seconds ?? null, line: r?.route ?? null };
    map.fitBounds([[myUnit.latitude, myUnit.longitude], [incident.latitude, incident.longitude]], { padding: [40, 40] });
  }
  if (route.line) L.polyline(route.line, { color: "#1976d2", weight: 5 }).addTo(layer);
}

refresh();
setInterval(refresh, POLL_MS);
