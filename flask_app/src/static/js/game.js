const TICK_MS = 30000;

async function moveTo(location) {
  const res  = await fetch("/move", {
    method:  "POST",
    headers: {"Content-Type": "application/json"},
    body:    JSON.stringify({location}),
  });
  const data = await res.json();
  if (data.ok) {
    addLog(`Вы перешли в: ${data.location.name}`);
    updateLocation(data.location, data.npcs);
  } else {
    addLog(data.error);
  }
}

function updateLocation(loc, npcs) {
  document.querySelector("h5.text-warning").textContent = loc.name;
  document.querySelector("p.text-muted.fst-italic").textContent = loc.description;

  const exits = document.getElementById("exits");
  exits.innerHTML = "";
  (loc.connected_to || []).forEach(exit => {
    const btn = document.createElement("button");
    btn.className   = "btn btn-sm btn-outline-warning";
    btn.textContent = exit;
    btn.onclick     = () => moveTo(exit);
    exits.appendChild(btn);
  });

  const npcList = document.getElementById("npc-list");
  npcList.innerHTML = "";
  if (!npcs.length) {
    npcList.innerHTML = '<small class="text-muted">Никого нет.</small>';
    return;
  }
  npcs.forEach(npc => {
    const d = document.createElement("div");
    d.className = "d-flex align-items-center justify-content-between mb-1";
    d.innerHTML = `<span>${npc.name} <small class="text-muted">(${npc.state})</small></span>`;
    if (npc.state !== "sleeping") {
      const a = document.createElement("a");
      a.href      = `/dialogue/${npc.id}`;
      a.className = "btn btn-sm btn-outline-light";
      a.textContent = "Говорить";
      d.appendChild(a);
    }
    npcList.appendChild(d);
  });
}

async function tick() {
  const res  = await fetch("/tick", {method: "POST"});
  const data = await res.json();
  document.getElementById("wd").textContent = data.day;
  document.getElementById("wh").textContent = String(data.hour).padStart(2, "0");
  document.getElementById("wt").textContent = data.time_label;
}

function addLog(msg) {
  const log  = document.getElementById("game-log");
  const p    = document.createElement("p");
  p.className = "mb-0";
  p.textContent = msg;
  log.appendChild(p);
  log.scrollTop = log.scrollHeight;
}

setInterval(tick, TICK_MS);