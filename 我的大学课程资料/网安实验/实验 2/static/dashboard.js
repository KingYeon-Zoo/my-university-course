const byId = (id) => document.getElementById(id);

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function endpoint(ip, port) {
  if (!ip) return "-";
  return port ? `${ip}:${port}` : ip;
}

function render(data) {
  byId("total").textContent = data.total;
  byId("blocked").textContent = data.blocked;
  byId("eve-path").textContent = data.eve_path;
  byId("source").textContent = data.events[0]?.src_ip || "-";
  byId("updated").textContent = `最后刷新：${new Date().toLocaleTimeString()}`;

  if (!data.events.length) {
    byId("events").innerHTML =
      '<tr><td colspan="6" class="empty">暂无告警，请在 Mac 上运行攻击模拟器。</td></tr>';
    return;
  }

  byId("events").innerHTML = data.events.map((event) => {
    const badgeClass = event.blocked ? "blocked" : "allowed";
    return `
      <tr>
        <td>${escapeHtml(event.timestamp)}</td>
        <td><span class="badge ${badgeClass}">${escapeHtml(event.action)}</span></td>
        <td>${escapeHtml(event.signature)}</td>
        <td>${escapeHtml(endpoint(event.src_ip, event.src_port))}</td>
        <td>${escapeHtml(endpoint(event.dest_ip, event.dest_port))}</td>
        <td>${escapeHtml(event.category)}</td>
      </tr>`;
  }).join("");
}

async function refresh() {
  try {
    const response = await fetch("/api/alerts", { cache: "no-store" });
    render(await response.json());
  } catch (error) {
    byId("updated").textContent = `读取失败：${error}`;
  }
}

refresh();
setInterval(refresh, 1000);

