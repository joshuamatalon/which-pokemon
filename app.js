// Which Pokémon are you? Scoring engine (Q3 of spec/CONTRACT.md) transcribed line by line, plus the
// browser UI. Works both in the browser and under node (guarded on typeof module), so test/check.py
// can run match() and resultText() directly against this file (A9).

const TRAITS = ["O", "C", "E", "A", "S"];
const STAGE_INDEX = { young: 0, evolved: 1, mature: 2 };
const LEAN_SAME = 0.00;
const LEAN_NEUTRAL = 0.08;
const LEAN_OPPOSITE = 0.25;

function round6(x) {
  return Math.floor(x * 1000000 + 0.5);
}
function round4(x) {
  return Math.floor(x * 10000 + 0.5) / 10000;
}

function takerVector(items, choice) {
  const sum = { O: 0, C: 0, E: 0, A: 0, S: 0 };
  const n = { O: 0, C: 0, E: 0, A: 0, S: 0 };
  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    const level = item.answers[choice[i]].level;
    sum[item.trait] = sum[item.trait] + level;
    n[item.trait] = n[item.trait] + 1;
  }
  return TRAITS.map((k) => sum[k] / (3 * n[k]));
}

function leanPenalty(takerLean, memberLean) {
  if (takerLean === null || takerLean === undefined) return 0;
  if (memberLean === takerLean) return LEAN_SAME;
  if (memberLean === "neutral") return LEAN_NEUTRAL;
  return LEAN_OPPOSITE;
}

function stagePenalty(taker, memberStage) {
  return taker.stage_weight * Math.abs(STAGE_INDEX[memberStage] - STAGE_INDEX[taker.stage_target]);
}

function match(t, taker, profiles) {
  let best = null;
  for (const p of profiles) {
    let d2 = 0;
    for (let k = 0; k < TRAITS.length; k++) {
      const diff = t[k] - p.vector[k];
      d2 += diff * diff;
    }
    const d = Math.sqrt(d2);
    const key = round6(d + leanPenalty(taker.lean, p.lean) + stagePenalty(taker, p.stage));
    if (best === null || key < best.key || (key === best.key && p.id < best.id)) {
      best = { id: p.id, key: key };
    }
  }
  return best.id;
}

function resultText(t, taker, member, items, choice, traitsMeta) {
  const scored = [];
  for (let i = 0; i < 15; i++) {
    const level = items[i].answers[choice[i]].level;
    const align = (level / 3) * member.vector[TRAITS.indexOf(items[i].trait)];
    scored.push({ i, level, align, trait: items[i].trait });
  }
  scored.sort((a, b) => {
    if (b.align !== a.align) return b.align - a.align;
    if (Math.abs(b.level) !== Math.abs(a.level)) return Math.abs(b.level) - Math.abs(a.level);
    return a.i - b.i;
  });
  const c1 = scored[0];
  let c2 = null;
  for (let j = 1; j < scored.length; j++) {
    if (scored[j].trait !== c1.trait) {
      c2 = scored[j];
      break;
    }
  }
  const echoOf = (entry) => items[entry.i].answers[choice[entry.i]].echo;
  const lineA = "You said " + echoOf(c1) + ", and " + echoOf(c2) + ".";

  const groups = [c1.trait, c2.trait];
  const whyOrder = [];
  const used = new Set();
  for (const trait of groups) {
    for (const w of member.why) {
      if (w.trait === trait && !used.has(w.text)) {
        whyOrder.push(w);
        used.add(w.text);
      }
    }
  }
  for (const w of member.why) {
    if (!used.has(w.text)) {
      whyOrder.push(w);
      used.add(w.text);
    }
  }
  const linesB = whyOrder.slice(0, 3).map((w) => w.text);

  let kStar = 0;
  for (let k = 1; k < TRAITS.length; k++) {
    if (Math.abs(t[k]) > Math.abs(t[kStar])) kStar = k;
  }
  const traitKey = TRAITS[kStar];
  const poleHigh = t[kStar] >= 0;
  const meta = traitsMeta[traitKey];
  const poleLabel = poleHigh ? meta.high : meta.low;
  const strengthLine = poleHigh ? meta.high_line : meta.low_line;
  const lineC = "Your answers lean most toward " + poleLabel + ". " + strengthLine;

  return { lineA, linesB, lineC };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { TRAITS, STAGE_INDEX, LEAN_SAME, LEAN_NEUTRAL, LEAN_OPPOSITE, round6, round4, takerVector, leanPenalty, stagePenalty, match, resultText };
}

// ---------------------------------------------------------------------------------------------
// Browser UI. Guarded so this file loads cleanly under node for the check's match() import.
// ---------------------------------------------------------------------------------------------
if (typeof document !== "undefined") {
  (function () {
    let questions = null;
    let pool = null;
    let takerKey = null;
    let choice = [];
    let currentIndex = 0;

    const screens = {};
    function showScreen(name) {
      for (const s of Object.values(screens)) s.classList.remove("on");
      screens[name].classList.add("on");
    }

    function findTaker(key) {
      return questions.takers.find((t) => t.key === key);
    }

    async function loadData() {
      const [q, p] = await Promise.all([
        fetch("data/questions.json").then((r) => r.json()),
        fetch("data/pool.json").then((r) => r.json()),
      ]);
      questions = q;
      pool = p;
    }

    function renderNames() {
      const grid = document.getElementById("names-grid");
      grid.innerHTML = "";
      for (const t of questions.takers) {
        const btn = document.createElement("button");
        btn.textContent = t.name;
        btn.addEventListener("click", () => startQuiz(t.key));
        grid.appendChild(btn);
      }
    }

    function startQuiz(key) {
      takerKey = key;
      choice = new Array(15).fill(null);
      currentIndex = 0;
      showScreen("quiz");
      renderQuizItem();
    }

    function renderQuizItem() {
      const item = questions.items[currentIndex];
      const progress = document.getElementById("progress");
      progress.innerHTML = "";
      for (let i = 0; i < 15; i++) {
        const dot = document.createElement("div");
        dot.className = "dot" + (i < currentIndex ? " done" : i === currentIndex ? " current" : "");
        progress.appendChild(dot);
      }
      document.getElementById("stem").textContent = item.stem;
      const answersEl = document.getElementById("answers");
      answersEl.innerHTML = "";
      item.answers.forEach((a, idx) => {
        const btn = document.createElement("button");
        btn.textContent = a.text;
        btn.addEventListener("click", () => selectAnswer(idx));
        answersEl.appendChild(btn);
      });
      document.getElementById("quiz-back").style.visibility = currentIndex === 0 ? "hidden" : "visible";
    }

    function selectAnswer(idx) {
      choice[currentIndex] = idx;
      if (currentIndex < 14) {
        currentIndex += 1;
        renderQuizItem();
      } else {
        finishQuiz();
      }
    }

    function goBack() {
      if (currentIndex > 0) {
        currentIndex -= 1;
        renderQuizItem();
      }
    }

    function finishQuiz() {
      const digits = choice.join("");
      location.hash = `t=${takerKey}&a=${digits}`;
      renderResultFromHash();
    }

    function parseHash() {
      const h = location.hash.replace(/^#/, "");
      const params = new URLSearchParams(h);
      const t = params.get("t");
      const a = params.get("a");
      if (!t || !a || a.length !== 15 || !/^[0-3]{15}$/.test(a)) return null;
      return { takerKey: t, choice: a.split("").map(Number) };
    }

    function renderResultFromHash() {
      const parsed = parseHash();
      if (!parsed) return false;
      const taker = findTaker(parsed.takerKey);
      if (!taker) return false;
      const t = takerVector(questions.items, parsed.choice);
      const memberId = match(t, taker, pool.profiles);
      const member = pool.profiles.find((p) => p.id === memberId);
      const text = resultText(t, taker, member, questions.items, parsed.choice, questions.traits);
      renderResult(member, text, t);
      showScreen("result");
      return true;
    }

    function renderResult(member, text, t) {
      document.getElementById("art-img").src = member.images.art;
      document.getElementById("art-img").alt = member.name + " official artwork";
      document.getElementById("ani-img").src = member.images.ani;
      document.getElementById("ani-img").alt = member.name + " animated sprite";
      document.getElementById("result-name").textContent = "You're a lot like " + member.name + ".";
      document.getElementById("result-genus").textContent = member.genus;

      const lineAEl = document.getElementById("line-a");
      lineAEl.textContent = text.lineA;
      const linesBEl = document.getElementById("lines-b");
      linesBEl.innerHTML = "";
      for (const line of text.linesB) {
        const li = document.createElement("li");
        li.textContent = line;
        linesBEl.appendChild(li);
      }
      document.getElementById("line-c").textContent = text.lineC;

      const barsEl = document.getElementById("bars");
      barsEl.innerHTML = "";
      TRAITS.forEach((k, i) => {
        const meta = questions.traits[k];
        const row = document.createElement("div");
        row.className = "bar-row";
        const labels = document.createElement("div");
        labels.className = "bar-labels";
        labels.innerHTML = `<span>${meta.low}</span><span>${meta.high}</span>`;
        const track = document.createElement("div");
        track.className = "bar-track";
        const dot = document.createElement("div");
        dot.className = "bar-dot";
        const pct = ((t[i] + 1) / 2) * 100;
        dot.style.left = pct + "%";
        track.appendChild(dot);
        row.appendChild(labels);
        row.appendChild(track);
        barsEl.appendChild(row);
      });

      const status = document.getElementById("copy-status");
      status.textContent = "";
    }

    function copyLink() {
      const url = location.href;
      const status = document.getElementById("copy-status");
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard
          .writeText(url)
          .then(() => (status.textContent = "Link copied."))
          .catch(() => (status.textContent = url));
      } else {
        status.textContent = url;
      }
    }

    function takeAgain() {
      history.replaceState(null, "", location.pathname + location.search);
      showScreen("names");
    }

    window.addEventListener("DOMContentLoaded", async () => {
      screens.names = document.getElementById("screen-names");
      screens.quiz = document.getElementById("screen-quiz");
      screens.result = document.getElementById("screen-result");

      await loadData();
      renderNames();

      document.getElementById("quiz-back").addEventListener("click", goBack);
      document.getElementById("copy-link").addEventListener("click", copyLink);
      document.getElementById("take-again").addEventListener("click", takeAgain);

      if (!renderResultFromHash()) {
        showScreen("names");
      }
    });

    window.addEventListener("hashchange", () => {
      renderResultFromHash();
    });
  })();
}
