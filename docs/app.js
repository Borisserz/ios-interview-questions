/* Study app: filters on #/, one-card drill on #/drill, done on #/done. */

const app = document.getElementById("app");
let DATA = { topics: [], cards: [] };

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char];
  });
}

function inlineMarkdown(text) {
  return escapeHtml(text)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}

function blockMarkdown(text) {
  const lines = text.split("\n");
  const out = [];
  const list = [];
  const flushList = () => {
    if (!list.length) return;
    out.push(`<ul>${list.map((item) => `<li>${inlineMarkdown(item)}</li>`).join("")}</ul>`);
    list.length = 0;
  };
  for (const line of lines) {
    const item = line.match(/^\s*[-*]\s+(.*)$/);
    if (item) {
      list.push(item[1]);
      continue;
    }
    flushList();
    if (!line.trim()) continue;
    out.push(`<p>${inlineMarkdown(line)}</p>`);
  }
  flushList();
  return out.join("");
}

function renderMarkdown(source) {
  if (!source) return "";
  const chunks = [];
  const fence = /```(\w*)\n([\s\S]*?)```/g;
  let last = 0;
  let match;
  while ((match = fence.exec(source))) {
    chunks.push(blockMarkdown(source.slice(last, match.index)));
    chunks.push(
      `<pre><code>${escapeHtml(match[2].replace(/\n$/, ""))}</code></pre>`
    );
    last = match.index + match[0].length;
  }
  chunks.push(blockMarkdown(source.slice(last)));
  return chunks.join("");
}

function parseRoute() {
  const raw = (location.hash || "#/").slice(1);
  const qIndex = raw.indexOf("?");
  const path = (qIndex === -1 ? raw : raw.slice(0, qIndex)) || "/";
  const query = new URLSearchParams(qIndex === -1 ? "" : raw.slice(qIndex + 1));
  return { path, query };
}

function readFilters(query) {
  return {
    topic: query.get("topic") || "all",
    level: query.get("level") || "all",
    order: query.get("order") || "sequential",
    open: query.get("open") || "",
    index: Math.max(0, Number.parseInt(query.get("i") || "0", 10) || 0),
  };
}

function matchesTopic(card, topicId) {
  if (topicId === "all") return true;
  if (topicId === "frequent") return Boolean(card.frequent);
  return card.topicId === topicId;
}

function filterCards(filters) {
  return DATA.cards.filter((card) => {
    if (!matchesTopic(card, filters.topic)) return false;
    if (filters.level !== "all" && card.level !== filters.level) return false;
    return true;
  });
}

function sessionKey(filters) {
  return `deck:${filters.topic}:${filters.level}:${filters.order}`;
}

function orderCards(cards, filters) {
  const copy = cards.slice();
  if (filters.topic === "frequent" && filters.order === "sequential") {
    copy.sort((a, b) => (a.frequentRank ?? 999) - (b.frequentRank ?? 999));
    return copy;
  }
  if (filters.order === "level") {
    const rank = { Junior: 0, Mid: 1, Senior: 2 };
    copy.sort((a, b) => (rank[a.level] ?? 9) - (rank[b.level] ?? 9));
    return copy;
  }
  if (filters.order === "random") {
    const key = sessionKey(filters);
    const stored = sessionStorage.getItem(key);
    if (stored) {
      const slugs = JSON.parse(stored);
      const bySlug = Object.fromEntries(copy.map((card) => [card.slug, card]));
      return slugs.map((slug) => bySlug[slug]).filter(Boolean);
    }
    for (let i = copy.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    sessionStorage.setItem(key, JSON.stringify(copy.map((card) => card.slug)));
    return copy;
  }
  return copy;
}

function deck(filters) {
  return orderCards(filterCards(filters), filters);
}

function href(path, filters, index) {
  const query = new URLSearchParams({
    topic: filters.topic || "all",
    level: filters.level || "all",
    order: filters.order || "sequential",
  });
  if (filters.open) query.set("open", filters.open);
  if (typeof index === "number") query.set("i", String(index));
  return `#${path}?${query}`;
}

function homeHref(filters) {
  return href("/", { ...filters, open: filters.open || (filters.topic !== "all" ? filters.topic : "") });
}

function cardsInTopic(topicId, filters) {
  return orderCards(
    DATA.cards.filter((card) => {
      if (!matchesTopic(card, topicId)) return false;
      if (filters.level !== "all" && card.level !== filters.level) return false;
      return true;
    }),
    { ...filters, topic: topicId }
  );
}

function topicCounts(level) {
  const counts = { all: 0 };
  for (const topic of DATA.topics) counts[topic.id] = 0;
  for (const card of DATA.cards) {
    if (level !== "all" && card.level !== level) continue;
    counts.all += 1;
    counts[card.topicId] = (counts[card.topicId] || 0) + 1;
    if (card.frequent) counts.frequent = (counts.frequent || 0) + 1;
  }
  return counts;
}

function renderHome(filters) {
  const counts = topicCounts(filters.level);
  const selected = filterCards(filters);
  const choice = (name, value, label) => {
    const checked = filters[name] === value ? " checked" : "";
    return `<label class="choice"><input type="radio" name="${name}" value="${escapeHtml(value)}"${checked}>${escapeHtml(label)}</label>`;
  };
  const topicBlocks = DATA.topics
    .map((topic) => {
      const questions = cardsInTopic(topic.id, filters);
      const open = filters.open === topic.id ? " open" : "";
      const items = questions
        .map((card, index) => {
          const drill = href(
            "/drill",
            { ...filters, topic: topic.id, open: topic.id },
            index
          );
          return `<li>
            <a class="question-link" href="${drill}">
              <span class="question-title">${escapeHtml(card.title)}</span>
              <span class="question-level">${escapeHtml(topic.id === "frequent" ? `${card.topic} · ${card.level}` : card.level)}</span>
            </a>
          </li>`;
        })
        .join("");
      return `<details class="topic-block" name="topic" data-topic="${escapeHtml(topic.id)}"${open}>
        <summary>
          <span class="topic-name">${escapeHtml(topic.label)}</span>
          <span class="topic-count">${questions.length}</span>
        </summary>
        <ol class="question-index">${items || "<li class=\"empty\">No cards for these filters.</li>"}</ol>
      </details>`;
    })
    .join("");
  app.innerHTML = `
    <form class="filters" id="filters">
      <div class="toolbar">
        <p class="lede">Pick a list. Speak the answer. Then reveal.</p>
        <div class="field">
          <span class="field-label">Level</span>
          <div class="choice-row">
            ${choice("level", "all", "All")}
            ${choice("level", "Junior", "Junior")}
            ${choice("level", "Mid", "Mid")}
            ${choice("level", "Senior", "Senior")}
          </div>
        </div>
        <div class="field">
          <span class="field-label">Order</span>
          <div class="choice-row">
            ${choice("order", "sequential", "In order")}
            ${choice("order", "level", "By level")}
            ${choice("order", "random", "Random")}
          </div>
        </div>
        <div class="start-bar">
          <p class="start-count">${selected.length} cards</p>
          <button class="btn" type="submit" ${selected.length ? "" : "disabled"}>Begin</button>
        </div>
      </div>
      <div class="field">
        <span class="field-label">Topics</span>
        <div class="topic-index">${topicBlocks}</div>
      </div>
    </form>`;
  const form = document.getElementById("filters");
  form.addEventListener("change", (event) => {
    if (event.target.name !== "level" && event.target.name !== "order") return;
    location.hash = href("/", {
      ...filters,
      level: form.level.value,
      order: form.order.value,
    });
  });
  form.querySelectorAll(".topic-block").forEach((block) => {
    block.addEventListener("toggle", () => {
      const topicId = block.dataset.topic;
      if (block.open) {
        if (filters.open === topicId && filters.topic === topicId) return;
        location.hash = href("/", { ...filters, topic: topicId, open: topicId });
        return;
      }
      if (filters.open === topicId) {
        location.hash = href("/", { ...filters, topic: "all", open: "" });
      }
    });
  });
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (filters.order === "random") sessionStorage.removeItem(sessionKey(filters));
    if (!selected.length) return;
    location.hash = href("/drill", filters, 0);
  });
}

function renderDrill(filters) {
  const cards = deck(filters);
  if (!cards.length) {
    location.hash = href("/", filters);
    return;
  }
  const index = Math.min(filters.index, cards.length - 1);
  const card = cards[index];
  const body =
    card.kind === "Practice"
      ? renderMarkdown(card.prompt)
      : `${renderMarkdown(card.answer)}${renderMarkdown(card.example)}`;
  const follow = card["follow-ups"]
    ? `<div class="follow"><h3>Then they usually ask</h3>${renderMarkdown(card["follow-ups"])}</div>`
    : "";
  const revealLabel = card.kind === "Practice" ? "Show prompt" : "Reveal";
  const nextIndex = index + 1;
  const nextHref =
    nextIndex >= cards.length
      ? href("/done", filters)
      : href("/drill", filters, nextIndex);
  app.innerHTML = `
    <article class="sheet">
      <p class="sheet-nav"><a class="back" href="${homeHref(filters)}">Back</a></p>
      <p class="sheet-meta">
        <span>${index + 1} / ${cards.length}</span>
        <span>${escapeHtml(card.topic)}</span>
        <span>${escapeHtml(card.level)}</span>
        <span>${escapeHtml(card.freq)}</span>
        ${card.kind === "Practice" ? "<span>Practice</span>" : ""}
      </p>
      <h1 class="sheet-title">${escapeHtml(card.title)}</h1>
      <p class="hint">Say it, then reveal.</p>
      <div class="reveal" id="answer" hidden>
        <div class="prose">${body}${follow}</div>
      </div>
      <div class="deck-actions">
        <button class="btn" type="button" id="reveal">${revealLabel}</button>
        <a class="btn btn-ghost" id="next" href="${nextHref}" hidden>Next</a>
      </div>
    </article>`;
  const answer = document.getElementById("answer");
  const reveal = document.getElementById("reveal");
  const next = document.getElementById("next");
  reveal.addEventListener("click", () => {
    answer.hidden = false;
    reveal.hidden = true;
    next.hidden = false;
    next.focus();
  });
}

function renderDone(filters) {
  const cards = deck(filters);
  app.innerHTML = `
    <section class="done">
      <h2>${cards.length} cards.</h2>
      <p>Say them again, or change the list.</p>
      <div class="deck-actions">
        <a class="btn" href="${href("/drill", filters, 0)}">Again</a>
        <a class="btn btn-ghost" href="${homeHref(filters)}">Back</a>
      </div>
    </section>`;
}

function render() {
  const { path, query } = parseRoute();
  const filters = readFilters(query);
  if (path.startsWith("/drill")) {
    renderDrill(filters);
    return;
  }
  if (path.startsWith("/done")) {
    renderDone(filters);
    return;
  }
  renderHome(filters);
}

async function boot() {
  try {
    const response = await fetch("./data/cards.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`Could not load cards.json (${response.status})`);
    DATA = await response.json();
    render();
    window.addEventListener("hashchange", render);
  } catch (error) {
    app.innerHTML = `<p class="err">${escapeHtml(error.message)}. Serve this folder over HTTP: <code>python3 -m http.server</code> from <code>docs/</code>.</p>`;
  }
}

boot();
