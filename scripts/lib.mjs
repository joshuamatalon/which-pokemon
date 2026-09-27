// Shared helpers for corpus/pool build scripts. Pure functions, no I/O.

export const TRAITS = ["O", "C", "E", "A", "S"];

export function round6(x) {
  return Math.floor(x * 1000000 + 0.5);
}

export function round4(x) {
  return Math.floor(x * 10000 + 0.5) / 10000;
}

function normalizeWhitespace(s) {
  return s
    .replace(/\f/g, " ")
    .replace(/­/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

export function cleanFlavorText(raw) {
  return normalizeWhitespace(raw);
}

function matchesEntry(token, entry) {
  if (entry.endsWith("*")) {
    return token.startsWith(entry.slice(0, -1));
  }
  return token === entry;
}

// tag(): implements the contract's Q5 tagging algorithm exactly.
export function tag(flavorTexts, lexicon) {
  const text = flavorTexts.join(" ").toLowerCase();
  const tokens = text.split(/[^a-zé]+/).filter((t) => t.length > 0);

  const auto = {};
  const matchedWords = {};

  for (const k of TRAITS) {
    const highEntries = lexicon.traits[k].high;
    const lowEntries = lexicon.traits[k].low;
    // single-word and two-word entries
    const highSingle = highEntries.filter((e) => !e.includes(" "));
    const highPhrase = highEntries.filter((e) => e.includes(" "));
    const lowSingle = lowEntries.filter((e) => !e.includes(" "));
    const lowPhrase = lowEntries.filter((e) => e.includes(" "));

    const hi = [];
    const lo = [];

    let i = 0;
    while (i < tokens.length) {
      let matched = false;
      if (i + 1 < tokens.length) {
        const phrase = tokens[i] + " " + tokens[i + 1];
        if (highPhrase.includes(phrase)) {
          hi.push(phrase);
          i += 2;
          matched = true;
        } else if (lowPhrase.includes(phrase)) {
          lo.push(phrase);
          i += 2;
          matched = true;
        }
      }
      if (matched) continue;
      const tok = tokens[i];
      if (highSingle.some((e) => matchesEntry(tok, e))) {
        hi.push(tok);
      } else if (lowSingle.some((e) => matchesEntry(tok, e))) {
        lo.push(tok);
      }
      i += 1;
    }

    auto[k] = round4((hi.length - lo.length) / (hi.length + lo.length + 2));
    matchedWords[k] = {
      high: uniqueInOrder(hi),
      low: uniqueInOrder(lo),
    };
  }

  return {
    auto_vector: TRAITS.map((k) => auto[k]),
    matched_words: matchedWords,
  };
}

function uniqueInOrder(arr) {
  const seen = new Set();
  const out = [];
  for (const x of arr) {
    if (!seen.has(x)) {
      seen.add(x);
      out.push(x);
    }
  }
  return out;
}

// profileVectors(): implements the contract's Q3 profile-vector algorithm exactly.
export function profileVectors(profiles) {
  const N = profiles.length;
  const raw = profiles.map((p) => TRAITS.map((k, idx) => 0.75 * (p.ratings[k] / 4) + 0.25 * p.auto_vector[idx]));

  for (let k = 0; k < TRAITS.length; k++) {
    const order = profiles
      .map((p, idx) => idx)
      .sort((a, b) => {
        if (raw[a][k] !== raw[b][k]) return raw[a][k] - raw[b][k];
        return profiles[a].id - profiles[b].id;
      });
    let pos = 0;
    while (pos < N) {
      let end = pos;
      while (end + 1 < N && raw[order[end + 1]][k] === raw[order[pos]][k]) {
        end += 1;
      }
      const rank = (pos + end) / 2;
      const value = round4(-0.9 + (1.8 * rank) / (N - 1));
      for (let j = pos; j <= end; j++) {
        const pIdx = order[j];
        if (!profiles[pIdx].vector) profiles[pIdx].vector = [0, 0, 0, 0, 0];
        profiles[pIdx].vector[k] = value;
      }
      pos = end + 1;
    }
  }
  return profiles;
}
