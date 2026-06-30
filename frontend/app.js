// Frontend → backend nginx proxy üzərindən (/api → backend:8000).
const API = "/api";

const $ = (sel) => document.querySelector(sel);
const runBtn = $("#run");
const statusEl = $("#status");

runBtn.addEventListener("click", runAudit);

async function runAudit() {
  const content = $("#content").value.trim();
  const contentType = $("#content-type").value;

  if (content.length < 10) {
    showStatus("Ən azı 10 simvol mətn daxil et.");
    return;
  }

  setLoading(true);
  showStatus("5 persona mətni qiymətləndirir... (free-tier model bir az çəkə bilər)");

  try {
    const resp = await fetch(`${API}/audit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content, content_type: contentType }),
    });
    if (!resp.ok) {
      const err = await resp.text();
      throw new Error(`Server xətası (${resp.status}): ${err}`);
    }
    const data = await resp.json();
    render(data);
    showStatus("");
  } catch (e) {
    showStatus(`Xəta: ${e.message}`);
  } finally {
    setLoading(false);
  }
}

function setLoading(loading) {
  runBtn.disabled = loading;
  runBtn.textContent = loading ? "Audit gedir..." : "Audit et";
}

function showStatus(msg) {
  statusEl.textContent = msg;
  statusEl.hidden = !msg;
}

function scoreClass(score) {
  if (score === null || score === undefined) return "";
  if (score >= 67) return "high";
  if (score >= 34) return "mid";
  return "low";
}

function render(data) {
  $("#results").hidden = false;
  renderCards(data.persona_reactions || []);
  renderSynthesis(data.synthesis || {});
  $("#results").scrollIntoView({ behavior: "smooth" });
}

function renderCards(reactions) {
  const wrap = $("#cards");
  wrap.innerHTML = "";
  for (const r of reactions) {
    const card = document.createElement("div");
    card.className = "card" + (r.ok ? "" : " failed");

    if (!r.ok) {
      card.innerHTML = `
        <div class="card-head"><h3>${esc(r.persona_name)}</h3></div>
        <p class="reaction">Bu persona texniki səbəbdən reaksiya vermədi.</p>`;
      wrap.appendChild(card);
      continue;
    }

    const score = r.etibar_skoru;
    card.innerHTML = `
      <div class="card-head">
        <h3>${esc(r.persona_name)}</h3>
        <span class="score ${scoreClass(score)}">${score ?? "—"}/100</span>
      </div>
      <p class="reaction">${esc(r.umumi_reaksiya)}</p>
      ${listBlock("Narahatlıqlar", r.narahatliqlar)}
      ${listBlock("Pozitiv", r.diqqet_ceken_pozitiv)}
      ${r.qerar ? `<span class="decision">${esc(r.qerar)}</span>` : ""}
    `;
    wrap.appendChild(card);
  }
}

function listBlock(label, items) {
  if (!items || !items.length) return "";
  const lis = items.map((i) => `<li>${esc(i)}</li>`).join("");
  return `<div class="section-label">${label}</div><ul class="tag-list">${lis}</ul>`;
}

function renderSynthesis(s) {
  const wrap = $("#synthesis");
  const patterns = (s.ortaq_patternler || [])
    .map((p) => `<div class="pattern"><strong>${esc(p.necə_persona || "")}</strong> — ${esc(p.pattern || "")}</div>`)
    .join("");
  const fixes = (s.prioritetli_düzelişler || [])
    .map((f) => `<div class="fix">
        <span class="prio ${esc(f.prioritet || "")}">${esc(f.prioritet || "")}</span>
        <strong> ${esc(f.problem || "")}</strong><br/>${esc(f.tövsiyə || "")}
      </div>`)
    .join("");
  const alts = (s.persona_üçün_alternativ || [])
    .map((a) => `<div class="alt"><strong>${esc(a.persona || "")}:</strong> ${esc(a.uyğunlaşdırılmış_mətn || "")}</div>`)
    .join("");

  wrap.innerHTML = `
    <div class="synth-block">
      <div class="section-label">Ümumi qiymət</div>
      <p>${esc(s.umumi_qiymet || "")}</p>
    </div>
    ${patterns ? `<div class="synth-block"><div class="section-label">Ortaq pattern-lər</div>${patterns}</div>` : ""}
    ${fixes ? `<div class="synth-block"><div class="section-label">Prioritetli düzəlişlər</div>${fixes}</div>` : ""}
    ${alts ? `<div class="synth-block"><div class="section-label">Persona üçün alternativ</div>${alts}</div>` : ""}
  `;
}

function esc(str) {
  return String(str ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}
