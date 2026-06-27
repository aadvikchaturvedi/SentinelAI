// ============================================================
//  NOC Copilot — Frontend JS
// ============================================================

const API = "http://localhost:8000";

// ---- CLOCK ----
function updateClock() {
  document.getElementById("clock").textContent = new Date().toUTCString().slice(0, 25);
}
setInterval(updateClock, 1000);
updateClock();

// ---- STATUS CHECK ----
async function checkStatus() {
  try {
    const res = await fetch(`${API}/api/status`);
    const data = await res.json();
    const dot = document.getElementById("status-dot");
    const txt = document.getElementById("status-text");
    dot.className = "dot green";
    txt.textContent = "System Online";
  } catch {
    document.getElementById("status-dot").className = "dot red";
    document.getElementById("status-text").textContent = "Backend Offline";
  }
}
setInterval(checkStatus, 5000);
checkStatus();

// ---- TOPOLOGY ----
async function loadTopology(alertedLocations = []) {
  try {
    const res = await fetch(`${API}/api/graph`);
    const data = await res.json();
    const grid = document.getElementById("topo-grid");
    grid.innerHTML = "";

    const icons = { datacenter: "🏢", hub: "🔌", branch: "🖥️" };

    data.nodes.forEach(node => {
      const status = alertedLocations.includes(node.id) ? "critical" : "healthy";
      const div = document.createElement("div");
      div.className = `topo-node ${status}`;
      div.innerHTML = `
        <span class="topo-icon">${icons[node.type] || "📡"}</span>
        <span class="topo-name">${node.id}</span>
        <span class="topo-type">${node.type.toUpperCase()}</span>
      `;
      grid.appendChild(div);
    });
  } catch (e) {
    document.getElementById("topo-grid").innerHTML = `<span class="placeholder">Topology unavailable</span>`;
  }
}
loadTopology();

// ---- TELEMETRY ----
async function fetchTelemetry() {
  try {
    const res = await fetch(`${API}/api/telemetry`);
    const data = await res.json();
    renderTelemetry(data.telemetry);
  } catch {
    document.getElementById("telemetry-panel").innerHTML = `<span class="placeholder">Telemetry unavailable</span>`;
  }
}

function telemetryClass(metric, value) {
  const rules = {
    latency_ms:          [30, 80],
    packet_loss_pct:     [0.5, 3],
    cpu_pct:             [60, 85],
    bandwidth_mbps:      [70, 30],  // inverted — lower is worse
    jitter_ms:           [5, 20],
  };
  if (!rules[metric]) return "";
  const [warn, crit] = rules[metric];
  const inverted = metric === "bandwidth_mbps";
  if (inverted) {
    if (value <= crit) return "val-critical";
    if (value <= warn) return "val-warning";
    return "val-normal";
  }
  if (value >= crit) return "val-critical";
  if (value >= warn) return "val-warning";
  return "val-normal";
}

function renderTelemetry(snapshots) {
  const panel = document.getElementById("telemetry-panel");
  let html = `<table class="tele-table">
    <tr>
      <th>Location</th><th>Latency</th><th>BW (Mbps)</th>
      <th>Loss%</th><th>CPU%</th><th>Jitter</th>
    </tr>`;
  snapshots.forEach(s => {
    html += `<tr>
      <td><strong>${s.location}</strong></td>
      <td class="${telemetryClass('latency_ms', s.latency_ms)}">${s.latency_ms}ms</td>
      <td class="${telemetryClass('bandwidth_mbps', s.bandwidth_mbps)}">${s.bandwidth_mbps}</td>
      <td class="${telemetryClass('packet_loss_pct', s.packet_loss_pct)}">${s.packet_loss_pct}%</td>
      <td class="${telemetryClass('cpu_pct', s.cpu_pct)}">${s.cpu_pct}%</td>
      <td class="${telemetryClass('jitter_ms', s.jitter_ms)}">${s.jitter_ms}ms</td>
    </tr>`;
  });
  html += "</table>";
  panel.innerHTML = html;
}

// ---- PREDICTIONS ----
async function runPredict() {
  document.getElementById("predictions-panel").innerHTML = `<span class="placeholder">Running pipeline...</span>`;
  document.getElementById("worker-panel").innerHTML = `<span class="placeholder">Analyzing...</span>`;

  try {
    const res = await fetch(`${API}/api/predict`);
    const data = await res.json();

    if (data.status === "healthy" || !data.predictions.length) {
      document.getElementById("predictions-panel").innerHTML = `<span class="placeholder" style="color:var(--green)">✅ No active failures detected</span>`;
      document.getElementById("worker-panel").innerHTML = `<span class="placeholder" style="color:var(--green)">All workers normal</span>`;
      document.getElementById("impact-panel").innerHTML = `<span class="placeholder">No active failure</span>`;
      loadTopology([]);
      return;
    }

    const alertedLocations = data.predictions.map(p => p.location);
    loadTopology(alertedLocations);

    // Render predictions
    let html = "";
    data.predictions.slice(0, 3).forEach(pred => {
      const sev = (pred.llm?.severity || "medium").toLowerCase();
      const actions = (pred.llm?.recommended_actions || []).slice(0, 3);
      html += `<div class="prediction-card ${sev}">
        <div class="pred-title">⚠ ${pred.failure}</div>
        <div class="pred-meta">
          <span><strong>${pred.confidence}%</strong> confidence</span>
          <span>Impact in <strong>${pred.time_to_impact}</strong></span>
          <span>@ <strong>${pred.location}</strong></span>
        </div>
        ${pred.llm?.explanation ? `<div class="pred-explanation">${pred.llm.explanation}</div>` : ""}
        ${actions.length ? `<ul class="pred-actions">${actions.map(a => `<li>${a}</li>`).join("")}</ul>` : ""}
      </div>`;
    });
    document.getElementById("predictions-panel").innerHTML = html;

    // Render workers from first prediction
    if (data.predictions[0]?.signal_outputs) {
      renderWorkers(data.predictions[0].signal_outputs);
    }

    // Render impact
    const top = data.predictions[0];
    renderImpact(top);

  } catch (e) {
    document.getElementById("predictions-panel").innerHTML = `<span class="placeholder" style="color:var(--red)">Prediction error: ${e.message}</span>`;
  }
}

function renderWorkers(workers) {
  let html = `<div class="worker-list">`;
  workers.forEach(w => {
    const sev = (w.severity || "None").toLowerCase();
    html += `<div class="worker-row">
      <span class="worker-name">${w.worker}</span>
      <span class="worker-pred">${w.prediction}</span>
      <span class="badge badge-${sev}">${w.severity}</span>
    </div>`;
  });
  html += "</div>";
  document.getElementById("worker-panel").innerHTML = html;
}

function renderImpact(pred) {
  const graph = pred.graph || {};
  const sites = graph.affected_sites || [];
  const apps  = graph.affected_apps  || [];
  const reroute = graph.reroute || "N/A";

  let siteHtml = sites.map(s => `<span class="impact-tag">${s}</span>`).join("");
  let appHtml  = apps.map(a  => `<span class="impact-tag app">${a}</span>`).join("");

  document.getElementById("impact-panel").innerHTML = `
    <div style="margin-bottom:8px"><span class="placeholder">Affected Sites</span></div>
    <div class="impact-row">${siteHtml || "<span class='placeholder'>None</span>"}</div>
    <div style="margin:8px 0 4px"><span class="placeholder">Affected Applications</span></div>
    <div class="impact-row">${appHtml || "<span class='placeholder'>None</span>"}</div>
    <div style="margin-top:8px;font-size:11px;color:var(--muted)">Impact Score: <strong style="color:var(--yellow)">${graph.impact_score || 0}/100</strong></div>
  `;

  document.getElementById("reroute-panel").innerHTML = `
    <div style="font-size:12px;color:var(--muted);margin-bottom:8px">Current path → Recommended alternate</div>
    <div style="font-size:16px;font-weight:700;color:var(--green)">→ ${reroute}</div>
    <div style="margin-top:8px;font-size:11px;color:var(--muted)">Graph engine recommendation (deterministic)</div>
  `;
}

// ---- CHAT ----
async function sendChat() {
  const input = document.getElementById("chat-input");
  const question = input.value.trim();
  if (!question) return;
  input.value = "";
  appendMessage("user", question);

  try {
    const res = await fetch(`${API}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();
    appendMessage("copilot", data.answer);
  } catch {
    appendMessage("copilot", "Copilot unavailable — check if Ollama is running.");
  }
}

function askQuick(q) {
  document.getElementById("chat-input").value = q;
  sendChat();
}

function appendMessage(role, text) {
  const msgs = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = `chat-bubble ${role}`;
  div.textContent = text;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}

// ---- FAULT INJECTION ----
async function injectFault(faultType, location) {
  try {
    const res = await fetch(`${API}/api/inject_fault`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fault_type: faultType, location }),
    });
    const data = await res.json();
    document.getElementById("fault-status").textContent =
      `✓ Injected: ${faultType} @ ${location}`;
    setTimeout(runPredict, 500);
  } catch {
    document.getElementById("fault-status").textContent = "Injection failed — backend offline";
  }
}

async function clearAllFaults() {
  const locations = ["Hub", "Branch1", "Branch2", "Branch3", "Datacenter"];
  for (const loc of locations) {
    await fetch(`${API}/api/clear_fault`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ location: loc }),
    });
  }
  document.getElementById("fault-status").textContent = "✓ All faults cleared";
  setTimeout(runPredict, 500);
}

// ---- AUTO REFRESH ----
setInterval(fetchTelemetry, 5000);
fetchTelemetry();

// Auto-run prediction every 15 seconds
setInterval(runPredict, 15000);