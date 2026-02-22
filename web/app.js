const listEl = document.getElementById("list");
const detailEl = document.getElementById("detail");
const topicEl = document.getElementById("topic");
const searchEl = document.getElementById("search");
const reloadEl = document.getElementById("reload");

async function getJson(url, opts) {
  const res = await fetch(url, opts);
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
}

function renderList(items) {
  listEl.innerHTML = "";
  for (const item of items) {
    const li = document.createElement("li");
    li.innerHTML = `<strong>${item.title || "(untitled)"}</strong><div class="meta">${item.topic} | #${item.id}</div>`;
    li.onclick = () => loadDetail(item.id);
    listEl.appendChild(li);
  }
}

function safeJson(text) {
  try {
    return JSON.parse(text || "[]");
  } catch {
    return [];
  }
}

async function loadDetail(id) {
  const data = await getJson(`/api/fatawa/${id}`);
  const refs = safeJson(data.quran_references_json);
  const feedback = data.feedback || [];
  detailEl.innerHTML = `
    <h2>${data.title || "(untitled)"}</h2>
    <p class="meta">${data.topic} | ${data.madhhab || "unknown madhhab"} | <a href="${data.url}" target="_blank">source</a></p>
    <h3>Question Summary</h3>
    <p>${data.question_summary || ""}</p>
    <h3>Draft Fatwa</h3>
    <p>${data.draft_fatwa_text || ""}</p>
    <h3>Quran References</h3>
    <p>${refs.join(", ")}</p>
    <h3>Feedback</h3>
    <ul>${feedback.map((x) => `<li>${x.comment}</li>`).join("")}</ul>
    <h3>Add Feedback</h3>
    <textarea id="fb-text" placeholder="Refinement note..."></textarea>
    <button id="fb-send">Submit</button>
  `;
  document.getElementById("fb-send").onclick = async () => {
    const comment = document.getElementById("fb-text").value.trim();
    if (!comment) {
      return;
    }
    await getJson("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fatwa_id: id, comment }),
    });
    await loadDetail(id);
  };
}

async function loadTopics() {
  const data = await getJson("/api/topics");
  topicEl.innerHTML = `<option value="">All topics</option>`;
  for (const t of data.topics) {
    const opt = document.createElement("option");
    opt.value = t.topic;
    opt.textContent = `${t.topic} (${t.count})`;
    topicEl.appendChild(opt);
  }
}

async function loadList() {
  const topic = topicEl.value;
  const q = searchEl.value.trim();
  const params = new URLSearchParams();
  if (topic) params.set("topic", topic);
  if (q) params.set("q", q);
  params.set("limit", "80");
  const data = await getJson(`/api/fatawa?${params.toString()}`);
  renderList(data.items || []);
}

reloadEl.onclick = () => loadList();
topicEl.onchange = () => loadList();
searchEl.onkeydown = (e) => {
  if (e.key === "Enter") loadList();
};

loadTopics().then(loadList);
