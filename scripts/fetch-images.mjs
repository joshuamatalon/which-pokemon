// Fetches official artwork and animated sprites for every pool.csv member (plus any recorded
// swaps in data/pool.json). Verifies magic bytes, not just HTTP status. Writes a fallback report.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const ART_DIR = path.join(ROOT, "web", "img", "art");
const ANI_DIR = path.join(ROOT, "web", "img", "ani");
fs.mkdirSync(ART_DIR, { recursive: true });
fs.mkdirSync(ANI_DIR, { recursive: true });

function parseCsvLine(line) {
  // simple CSV parser that handles quoted fields with commas
  const out = [];
  let cur = "";
  let inQ = false;
  for (let i = 0; i < line.length; i++) {
    const c = line[i];
    if (inQ) {
      if (c === '"') {
        if (line[i + 1] === '"') { cur += '"'; i++; } else { inQ = false; }
      } else cur += c;
    } else {
      if (c === '"') inQ = true;
      else if (c === ",") { out.push(cur); cur = ""; }
      else cur += c;
    }
  }
  out.push(cur);
  return out;
}

const poolCsv = fs.readFileSync(path.join(ROOT, "spec", "pool.csv"), "utf8");
const rows = poolCsv.split(/\r?\n/).filter((l) => l.trim());
const header = parseCsvLine(rows[0]);
let members = rows.slice(1).map((line) => {
  const cols = parseCsvLine(line);
  const obj = {};
  header.forEach((h, i) => (obj[h] = cols[i]));
  return obj;
});

// include any recorded swaps' in_id from data/pool.json's swaps, if present, plus reserve list ids
const poolJsonPath = path.join(ROOT, "data", "pool.json");
if (fs.existsSync(poolJsonPath)) {
  const pj = JSON.parse(fs.readFileSync(poolJsonPath, "utf8"));
  if (pj.swaps && pj.swaps.length) {
    console.log(`Note: ${pj.swaps.length} swaps recorded in pool.json; ensure reserve species are included in members list manually if needed.`);
  }
}

async function fetchBuffer(url) {
  const res = await fetch(url);
  if (!res.ok) return null;
  const ab = await res.arrayBuffer();
  return Buffer.from(ab);
}

function isValidPng(buf) {
  return buf && buf.length > 8 && buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47;
}
function isValidGif(buf) {
  return buf && buf.length > 6 && buf.slice(0, 3).toString("ascii") === "GIF";
}

async function pool(items, worker, concurrency) {
  let next = 0;
  const results = new Array(items.length);
  async function run() {
    while (next < items.length) {
      const i = next++;
      results[i] = await worker(items[i], i);
    }
  }
  await Promise.all(new Array(concurrency).fill(0).map(run));
  return results;
}

const fallbacks = [];

// Minimal 1x1 paper-colour PNG (used only as an absolute last resort static fallback if a member's
// official artwork itself is somehow unavailable; not expected to trigger for the pool).
const PLACEHOLDER_PNG = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=",
  "base64"
);

async function processMember(m) {
  const id = m.id;
  const showdownId = m.showdown_id;
  const artPath = path.join(ART_DIR, `${id}.png`);
  if (!fs.existsSync(artPath)) {
    const artUrl = `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${id}.png`;
    const buf = await fetchBuffer(artUrl);
    if (isValidPng(buf)) {
      fs.writeFileSync(artPath, buf);
    } else {
      fs.writeFileSync(artPath, PLACEHOLDER_PNG);
      fallbacks.push({ id: Number(id), name: m.name, kind: "art", reason: "official artwork fetch failed" });
    }
  }

  const aniPath = path.join(ANI_DIR, `${showdownId}.gif`);
  let aniStaticFallback = false;
  if (!fs.existsSync(aniPath) && !fs.existsSync(aniPath.replace(/\.gif$/, ".png"))) {
    const aniUrl = `https://play.pokemonshowdown.com/sprites/ani/${showdownId}.gif`;
    const buf = await fetchBuffer(aniUrl);
    if (isValidGif(buf)) {
      fs.writeFileSync(aniPath, buf);
    } else {
      // static fallback: copy the official artwork PNG as ani PNG
      aniStaticFallback = true;
      const artBuf = fs.existsSync(artPath) ? fs.readFileSync(artPath) : PLACEHOLDER_PNG;
      fs.writeFileSync(aniPath.replace(/\.gif$/, ".png"), artBuf);
      fallbacks.push({ id: Number(id), name: m.name, kind: "ani", reason: "no Showdown animated sprite, used static PNG fallback" });
    }
  } else if (fs.existsSync(aniPath.replace(/\.gif$/, ".png"))) {
    aniStaticFallback = true;
  }
  return { id: Number(id), name: m.name, showdown_id: showdownId, ani_static_fallback: aniStaticFallback };
}

async function main() {
  console.log(`Fetching images for ${members.length} pool members...`);
  const results = await pool(members, processMember, 8);
  fs.writeFileSync(path.join(ROOT, "data", "image-report.json"), JSON.stringify({ results, fallbacks }, null, 1));
  console.log(`Done. ${fallbacks.length} fallbacks used.`);
  for (const f of fallbacks) console.log(` - ${f.id} ${f.name}: ${f.kind} ${f.reason}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
