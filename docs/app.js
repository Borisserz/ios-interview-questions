/* Study app: filters on #/, one-card drill on #/drill, done on #/done. */

const app = document.getElementById("app");
let DATA = { topics: [], cards: [], paths: [] };
const DEFAULT_CAP = 12;
const SIZE_KEY = "session-size";
const SPEAK_SECONDS = 60;
const GRADE_KEY = "grades:v1";
const GRADE_ORDER = ["known", "shaky", "blank"];
const GRADE_LABEL = { known: "Known", shaky: "Shaky", blank: "Blank" };

let keyHandler = null;
let timerId = null;

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

function splitGist(text) {
  const raw = String(text || "").trim();
  if (!raw) return { gist: "", rest: "" };
  const parts = raw.split(/\n\s*\n/);
  return { gist: parts[0], rest: parts.slice(1).join("\n\n") };
}

function isPractice(card) {
  return card.kind === "Practice" || Boolean(card.practice);
}

function loadGrades() {
  try {
    const parsed = JSON.parse(localStorage.getItem(GRADE_KEY) || "{}");
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch {
    return {};
  }
}

function saveGrade(slug, grade) {
  const grades = loadGrades();
  grades[slug] = { grade, at: Date.now() };
  localStorage.setItem(GRADE_KEY, JSON.stringify(grades));
}

function storedCap() {
  const n = Number.parseInt(localStorage.getItem(SIZE_KEY) || "", 10);
  return Number.isFinite(n) && n >= 1 ? n : DEFAULT_CAP;
}

function rememberCap(n) {
  localStorage.setItem(SIZE_KEY, String(n));
}

function parseCap(raw, max) {
  const n = Number.parseInt(raw, 10);
  const size = Number.isFinite(n) && n >= 1 ? n : storedCap();
  return Math.min(size, Math.max(1, max));
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
    path: query.get("path") || "",
    session: Math.max(0, Number.parseInt(query.get("session") || "0", 10) || 0),
    review: query.get("review") || "",
    cap: query.get("cap") || String(storedCap()),
    index: Math.max(0, Number.parseInt(query.get("i") || "0", 10) || 0),
  };
}

function matchesTopic(card, topicId) {
  if (topicId === "practice") return isPractice(card);
  if (topicId === "frequent") return Boolean(card.frequent);
  if (topicId === "all") return true;
  if (isPractice(card)) return false;
  return card.topicId === topicId;
}

function pathSession(filters) {
  const path = (DATA.paths || []).find((item) => item.id === filters.path);
  if (!path || !path.sessions.length) return null;
  return path.sessions[filters.session] || path.sessions[0];
}

function filterCards(filters) {
  if (filters.path) {
    const session = pathSession(filters);
    if (!session) return [];
    const bySlug = Object.fromEntries(DATA.cards.map((card) => [card.slug, card]));
    return session.slugs
      .map((slug) => bySlug[slug])
      .filter(Boolean)
      .filter((card) => filters.level === "all" || card.level === filters.level);
  }
  return DATA.cards.filter((card) => {
    if (!matchesTopic(card, filters.topic)) return false;
    if (filters.level !== "all" && card.level !== filters.level) return false;
    return true;
  });
}

function sessionKey(filters) {
  return `deck:${filters.path || filters.topic}:${filters.session}:${filters.level}:${filters.order}`;
}

function orderCards(cards, filters) {
  const copy = cards.slice();
  if (filters.path && filters.order === "sequential") return copy;
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
  let cards = orderCards(filterCards(filters), filters);
  if (!filters.path && filters.cap) {
    cards = cards.slice(0, parseCap(filters.cap, cards.length));
  }
  if (filters.review === "blanks") {
    const grades = loadGrades();
    cards = cards.filter((card) => (grades[card.slug]?.grade || "blank") === "blank");
  }
  return cards;
}

function href(path, filters, index) {
  const query = new URLSearchParams({
    topic: filters.topic || "all",
    level: filters.level || "all",
    order: filters.order || "sequential",
  });
  if (filters.open) query.set("open", filters.open);
  if (filters.path) {
    query.set("path", filters.path);
    query.set("session", String(filters.session || 0));
  }
  if (filters.review) query.set("review", filters.review);
  if (filters.cap) query.set("cap", String(filters.cap));
  if (typeof index === "number") query.set("i", String(index));
  return `#${path}?${query}`;
}

function homeHref(filters) {
  return href("/", {
    ...filters,
    review: "",
    open: filters.path
      ? ""
      : filters.open || (filters.topic !== "all" ? filters.topic : ""),
  });
}

function cardsInTopic(topicId, filters) {
  return orderCards(
    DATA.cards.filter((card) => {
      if (!matchesTopic(card, topicId)) return false;
      if (filters.level !== "all" && card.level !== filters.level) return false;
      return true;
    }),
    { ...filters, topic: topicId, path: "" }
  );
}

function topicCounts(level) {
  const counts = { all: 0, practice: 0, frequent: 0 };
  for (const topic of DATA.topics) counts[topic.id] = 0;
  for (const card of DATA.cards) {
    if (level !== "all" && card.level !== level) continue;
    counts.all += 1;
    if (isPractice(card)) {
      counts.practice += 1;
    } else {
      counts[card.topicId] = (counts[card.topicId] || 0) + 1;
    }
    if (card.frequent) counts.frequent += 1;
  }
  return counts;
}

function originLabel(topicId, card) {
  if (topicId === "frequent" || topicId === "practice") {
    return `${card.topic} · ${card.level}`;
  }
  return card.level;
}

function gradeMark(slug, grades) {
  const grade = grades[slug]?.grade;
  if (!grade) return "";
  return `<span class="grade-mark" data-grade="${escapeHtml(grade)}" title="${escapeHtml(GRADE_LABEL[grade] || grade)}"></span>`;
}

function startLabel(filters, selected, size) {
  if (filters.path) {
    const session = pathSession(filters);
    return session ? `${selected.length} cards` : "0 cards";
  }
  if (size < selected.length) return `of ${selected.length}`;
  return `${selected.length} cards`;
}

function renderHome(filters) {
  const counts = topicCounts(filters.level);
  const selected = filterCards(filters);
  const size = parseCap(filters.cap, selected.length || 1);
  const grades = loadGrades();
  const session = pathSession(filters);
  const choice = (name, value, label) => {
    const checked = filters[name] === value ? " checked" : "";
    return `<label class="choice"><input type="radio" name="${name}" value="${escapeHtml(value)}"${checked}>${escapeHtml(label)}</label>`;
  };
  const topicBlocks = DATA.topics
    .map((topic) => {
      const questions = cardsInTopic(topic.id, filters);
      const open =
        !filters.path && (filters.open === topic.id || (!filters.open && filters.topic === topic.id))
          ? " open"
          : "";
      const items = questions
        .map((card, index) => {
          const drill = href(
            "/drill",
            { ...filters, topic: topic.id, open: topic.id, path: "", cap: "" },
            index
          );
          return `<li>
            <a class="question-link" href="${drill}">
              <span class="question-title">${gradeMark(card.slug, grades)}${escapeHtml(card.title)}</span>
              <span class="question-level">${escapeHtml(originLabel(topic.id, card))}</span>
            </a>
          </li>`;
        })
        .join("");
      const count = topic.id === "practice" ? counts.practice : questions.length;
      return `<details class="topic-block" name="topic" data-topic="${escapeHtml(topic.id)}"${open}>
        <summary>
          <span class="topic-name">${escapeHtml(topic.label)}</span>
          <span class="topic-count">${count}</span>
        </summary>
        <ol class="question-index">${items || "<li class=\"empty\">No cards for these filters.</li>"}</ol>
      </details>`;
    })
    .join("");
  const pathBlocks = (DATA.paths || [])
    .map((path) => {
      const open = filters.path === path.id ? " open" : "";
      const items = path.sessions
        .map((item, index) => {
          const drill = href(
            "/drill",
            { ...filters, path: path.id, session: index, topic: "all", open: "", cap: "" },
            0
          );
          return `<li>
            <a class="question-link" href="${drill}">
              <span class="question-title">${escapeHtml(item.title)}</span>
              <span class="question-level">${item.slugs.length} cards</span>
            </a>
          </li>`;
        })
        .join("");
      return `<details class="topic-block" data-path="${escapeHtml(path.id)}"${open}>
        <summary>
          <span class="topic-name">${escapeHtml(path.label)}</span>
          <span class="topic-count">${path.sessions.length} sessions</span>
        </summary>
        <ol class="question-index">${items}</ol>
      </details>`;
    })
    .join("");
  const lede = session
    ? `${escapeHtml(session.title)}. Speak, reveal, mark.`
    : "Pick a list. Speak. Reveal. Mark Known, Shaky, or Blank.";
  app.innerHTML = `
    <form class="filters" id="filters">
      <div class="toolbar">
        <p class="lede">${lede}</p>
        <div class="toolbar-controls">
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
          <div class="field">
            <span class="field-label">Session</span>
            <div class="start-bar">
              ${
                filters.path
                  ? ""
                  : `<label class="session-size"><input type="number" name="cap" min="1" max="${selected.length || 1}" value="${size}"></label>`
              }
              <p class="start-count">${startLabel(filters, selected, size)}</p>
              <button class="btn" type="submit" ${selected.length ? "" : "disabled"}>Begin</button>
            </div>
          </div>
        </div>
      </div>
      <div class="field">
        <span class="field-label">Paths</span>
        <div class="topic-index path-index">${pathBlocks}</div>
      </div>
      <div class="field">
        <span class="field-label">Topics</span>
        <div class="topic-index">${topicBlocks}</div>
      </div>
    </form>`;
  const form = document.getElementById("filters");
  form.addEventListener("change", (event) => {
    if (event.target.name === "cap") {
      const next = parseCap(event.target.value, selected.length || 1);
      rememberCap(next);
      location.hash = href("/", { ...filters, cap: String(next) });
      return;
    }
    if (event.target.name !== "level" && event.target.name !== "order") return;
    location.hash = href("/", {
      ...filters,
      level: form.level.value,
      order: form.order.value,
    });
  });
  form.querySelectorAll(".topic-block[data-topic]").forEach((block) => {
    block.addEventListener("toggle", () => {
      const topicId = block.dataset.topic;
      if (block.open) {
        if (filters.open === topicId && filters.topic === topicId && !filters.path) return;
        location.hash = href("/", { ...filters, topic: topicId, open: topicId, path: "" });
        return;
      }
      if (filters.open === topicId && !filters.path) {
        location.hash = href("/", { ...filters, topic: "all", open: "" });
      }
    });
  });
  form.querySelectorAll(".topic-block[data-path]").forEach((block) => {
    block.addEventListener("toggle", () => {
      const pathId = block.dataset.path;
      if (block.open) {
        if (filters.path === pathId) return;
        location.hash = href("/", {
          ...filters,
          path: pathId,
          session: 0,
          topic: "all",
          open: "",
        });
        return;
      }
      if (filters.path === pathId) {
        location.hash = href("/", { ...filters, path: "", session: 0 });
      }
    });
  });
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (filters.order === "random") sessionStorage.removeItem(sessionKey(filters));
    if (!selected.length) return;
    const next = parseCap(form.cap ? form.cap.value : filters.cap, selected.length || 1);
    rememberCap(next);
    location.hash = href(
      "/drill",
      { ...filters, cap: filters.path ? "" : String(next), review: "" },
      0
    );
  });
}

function renderRevealBody(card) {
  if (isPractice(card)) {
    const follow = card["follow-ups"]
      ? `<div class="follow"><h3>Cover these</h3>${renderMarkdown(card["follow-ups"])}</div>`
      : "";
    return `<div class="gist"><p>Scope it out loud. Then check the prompt.</p></div>${renderMarkdown(card.prompt)}${follow}`;
  }
  const { gist, rest } = splitGist(card.answer);
  const gistHtml = gist ? `<div class="gist">${renderMarkdown(gist)}</div>` : "";
  const follow = card["follow-ups"]
    ? `<div class="follow"><h3>Then they usually ask</h3>${renderMarkdown(card["follow-ups"])}</div>`
    : "";
  return `${gistHtml}${renderMarkdown(rest)}${renderMarkdown(card.example)}${follow}`;
}

function stopTimer() {
  if (timerId) {
    clearInterval(timerId);
    timerId = null;
  }
}

function startTimer(node) {
  stopTimer();
  const started = Date.now();
  const tick = () => {
    const left = Math.max(0, SPEAK_SECONDS - Math.floor((Date.now() - started) / 1000));
    node.textContent = `${left}s`;
    node.classList.toggle("timer-low", left <= 10);
    if (left === 0) stopTimer();
  };
  tick();
  timerId = setInterval(tick, 250);
}

function unbindKeys() {
  if (!keyHandler) return;
  window.removeEventListener("keydown", keyHandler);
  keyHandler = null;
}

function bindKeys({ onReveal, onGrade, onNext, revealed }) {
  unbindKeys();
  keyHandler = (event) => {
    if (event.metaKey || event.ctrlKey || event.altKey) return;
    const tag = event.target.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
    if (event.key === " " && !revealed()) {
      event.preventDefault();
      onReveal();
      return;
    }
    if (!revealed()) return;
    if (event.key === "1") {
      event.preventDefault();
      onGrade("known");
      return;
    }
    if (event.key === "2") {
      event.preventDefault();
      onGrade("shaky");
      return;
    }
    if (event.key === "3") {
      event.preventDefault();
      onGrade("blank");
      return;
    }
    if (event.key === "ArrowRight" || event.key === "n") {
      event.preventDefault();
      onNext();
    }
  };
  window.addEventListener("keydown", keyHandler);
}

function renderDrill(filters) {
  const cards = deck(filters);
  if (!cards.length) {
    location.hash = href("/", filters);
    return;
  }
  const index = Math.min(filters.index, cards.length - 1);
  const card = cards[index];
  const revealLabel = isPractice(card) ? "Show prompt" : "Reveal";
  const hint = isPractice(card)
    ? "Talk the design. Then open the prompt."
    : "60 seconds. Then reveal.";
  const nextIndex = index + 1;
  const nextHref =
    nextIndex >= cards.length
      ? href("/done", filters)
      : href("/drill", filters, nextIndex);
  const grades = GRADE_ORDER.map(
    (grade) =>
      `<button class="grade" type="button" data-grade="${grade}">${GRADE_LABEL[grade]} <span>${GRADE_ORDER.indexOf(grade) + 1}</span></button>`
  ).join("");
  app.innerHTML = `
    <article class="sheet">
      <p class="sheet-nav"><a class="back" href="${homeHref(filters)}">Back</a></p>
      <p class="sheet-meta">
        <span>${index + 1} / ${cards.length}</span>
        <span class="timer" id="timer">${SPEAK_SECONDS}s</span>
        <span>${escapeHtml(card.topic)}</span>
        <span>${escapeHtml(card.level)}</span>
        <span>${escapeHtml(card.freq)}</span>
        ${isPractice(card) ? "<span>Practice</span>" : ""}
      </p>
      <h1 class="sheet-title">${escapeHtml(card.title)}</h1>
      <p class="hint">${hint}</p>
      <div class="reveal" id="answer" hidden>
        <div class="prose">${renderRevealBody(card)}</div>
        <div class="grades" id="grades">${grades}</div>
      </div>
      <div class="deck-actions">
        <button class="btn" type="button" id="reveal">${revealLabel}</button>
        <a class="btn btn-ghost" id="next" href="${nextHref}" hidden>Next</a>
        <p class="keys">Space reveal · 1 2 3 grade · → next</p>
      </div>
    </article>`;
  const answer = document.getElementById("answer");
  const reveal = document.getElementById("reveal");
  const next = document.getElementById("next");
  const timer = document.getElementById("timer");
  let shown = false;
  const showAnswer = () => {
    if (shown) return;
    shown = true;
    stopTimer();
    answer.hidden = false;
    reveal.hidden = true;
    next.hidden = false;
    next.focus();
  };
  const gradeCard = (grade) => {
    showAnswer();
    saveGrade(card.slug, grade);
    location.hash = nextHref;
  };
  reveal.addEventListener("click", showAnswer);
  document.getElementById("grades").addEventListener("click", (event) => {
    const button = event.target.closest("[data-grade]");
    if (!button) return;
    gradeCard(button.dataset.grade);
  });
  startTimer(timer);
  bindKeys({
    onReveal: showAnswer,
    onGrade: gradeCard,
    onNext: () => {
      showAnswer();
      location.hash = nextHref;
    },
    revealed: () => shown,
  });
}

function tallyGrades(cards) {
  const grades = loadGrades();
  const tally = { known: 0, shaky: 0, blank: 0 };
  for (const card of cards) {
    const grade = grades[card.slug]?.grade || "blank";
    tally[grade] = (tally[grade] || 0) + 1;
  }
  return tally;
}

function renderDone(filters) {
  const cards = deck({ ...filters, review: "" });
  const tally = tallyGrades(cards);
  const blanks = deck({ ...filters, review: "blanks" });
  const retry = blanks.length
    ? `<a class="btn" href="${href("/drill", { ...filters, review: "blanks" }, 0)}">Retry blanks (${blanks.length})</a>`
    : "";
  app.innerHTML = `
    <section class="done">
      <h2>${cards.length} cards.</h2>
      <p class="done-stats">
        <span data-grade="known">${tally.known} known</span>
        <span data-grade="shaky">${tally.shaky} shaky</span>
        <span data-grade="blank">${tally.blank} blank</span>
      </p>
      <p>Say the blanks again, or change the list.</p>
      <div class="deck-actions">
        ${retry}
        <a class="btn btn-ghost" href="${href("/drill", { ...filters, review: "" }, 0)}">Again</a>
        <a class="btn btn-ghost" href="${homeHref(filters)}">Back</a>
      </div>
    </section>`;
}

function clearSessionUi() {
  unbindKeys();
  stopTimer();
}

function render() {
  clearSessionUi();
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
    if (!DATA.paths) DATA.paths = [];
    render();
    window.addEventListener("hashchange", render);
  } catch (error) {
    app.innerHTML = `<p class="err">${escapeHtml(error.message)}. Serve this folder over HTTP: <code>python3 -m http.server</code> from <code>docs/</code>.</p>`;
  }
}

boot();
