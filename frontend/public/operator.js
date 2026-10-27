const user = requireRole("operator");
const map = createMap();
const layer = L.layerGroup().addTo(map);
const $ = (id) => document.getElementById(id);
let picked = null;
let pickedMarker = null;
let fitted = false;

$("who").textContent = user.name;
$("logout").onclick = logout;

let searchTimer = null;
$("address").addEventListener("input", () => {
  clearTimeout(searchTimer);
  picked = null;
  $("location").textContent = "No address selected";
  const q = $("address").value.trim();
  if (q.length < 3) return ($("suggestions").innerHTML = "");
  searchTimer = setTimeout(() => search(q), 300);
});

async function search(q) {
  const c = map.getCenter();
  const url = `https://photon.komoot.io/api/?q=${encodeURIComponent(q)}&limit=5&lat=${c.lat}&lon=${c.lng}&bbox=-9.6,36.9,-6.1,42.2`;
  const data = await (await fetch(url)).json();
  $("suggestions").innerHTML = "";
  for (const f of data.features) {
    const p = f.properties;
    const label = [p.name, p.street, p.housenumber, p.city].filter(Boolean).join(", ");
    const li = document.createElement("li");
    li.textContent = label;
    li.onclick = () => {
      const [lon, lat] = f.geometry.coordinates;
      picked = { latitude: lat, longitude: lon };
      $("address").value = label;
      $("location").textContent = label;
      $("suggestions").innerHTML = "";
      if (pickedMarker) pickedMarker.remove();
      pickedMarker = L.marker([lat, lon]).addTo(map);
      map.setView([lat, lon], 15);
    };
    $("suggestions").appendChild(li);
  }
}

$("create").onclick = async () => {
  if (!picked) return ($("message").textContent = "Choose an address from the list first.");
  try {
    const incident = await api("/incidents", {
      method: "POST",
      body: {
        district_id: user.district_id,
        created_by: user.id,
        ...picked,
        address: $("address").value,
        victim_name: $("victim").value || null,
        description: $("description").value || null,
        severity: Number($("severity").value),
      },
    });
    $("message").textContent = `Incident #${incident.id} created.`;
    for (const id of ["address", "victim", "description"]) $(id).value = "";
    if (pickedMarker) pickedMarker.remove();
    picked = pickedMarker = null;
    $("location").textContent = "No address selected";
    refresh();
  } catch (err) {
    $("message").textContent = "Error: " + err.message;
  }
};

async function refresh() {
  try {
    const [incidents, units] = await Promise.all([
      api(`/incidents?district_id=${user.district_id}`),
      api(`/units?district_id=${user.district_id}`),
    ]);
    layer.clearLayers();
    const unitOf = {};
    const points = [];
    for (const u of units) {
      if (u.incident_id) unitOf[u.incident_id] = u.code;
      points.push([u.latitude, u.longitude]);
      dot([u.latitude, u.longitude], UNIT_COLOR[u.status], 7).bindTooltip(`${u.code} — ${u.status}`).addTo(layer);
    }
    $("incidents").innerHTML = "";
    for (const i of incidents) {
      points.push([i.latitude, i.longitude]);
      dot([i.latitude, i.longitude], SEVERITY_COLOR[i.severity], 10)
        .bindTooltip(`#${i.id} sev ${i.severity} — ${i.status}`)
        .addTo(layer);
      const li = document.createElement("li");
      li.innerHTML = `#${i.id} <b>sev ${i.severity}</b> — ${i.status}` +
        (unitOf[i.id] ? ` → ${unitOf[i.id]}` : "") +
        `<br><span class="muted">${escapeHtml(i.address || "")}</span>`;
      $("incidents").appendChild(li);
    }
    if (!fitted && points.length) {
      map.fitBounds(points, { padding: [40, 40] });
      fitted = true;
    }
  } catch (err) {
    $("message").textContent = "Error: " + err.message;
  }
}

refresh();
connectLive(user.district_id, refresh);
