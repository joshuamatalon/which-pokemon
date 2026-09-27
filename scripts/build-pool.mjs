// Merges the 8 worker profile files with spec/pool.csv and data/corpus.json, computes
// profileVectors(), attaches image paths, and writes data/pool.json. Also copies the runtime
// data files (pool.json, questions.json) into web/data/ so the static site can fetch them.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { profileVectors, TRAITS } from "./lib.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

function parseCsvLine(line) {
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
const csvRows = rows.slice(1).map((line) => {
  const cols = parseCsvLine(line);
  const obj = {};
  header.forEach((h, i) => (obj[h] = cols[i]));
  obj.id = Number(obj.id);
  return obj;
});
const csvById = new Map(csvRows.map((r) => [r.id, r]));

const profilesDir = path.join(ROOT, "data", "profiles");
const files = fs.readdirSync(profilesDir).filter((f) => f.endsWith(".json"));
console.log(`Found ${files.length} worker profile files:`, files);

let allProfiles = [];
const errors = [];
for (const f of files) {
  const arr = JSON.parse(fs.readFileSync(path.join(profilesDir, f), "utf8"));
  if (!Array.isArray(arr)) { errors.push(`${f} is not an array`); continue; }
  for (const p of arr) allProfiles.push(p);
}

// Screen: keep only ids that are in the amended (149-row) spec/pool.csv. Older shards were written
// against the pre-screen 160-row pool and still carry the 30 removed ids; those are dropped here,
// silently as far as errors go (recorded in DELIVERY.md by the stream, not an error condition) since
// dropping a screened-out profile is expected, not a defect. A profile id NOT in the screened csv and
// NOT in the known-screened-out A20 list would still be worth flagging, so we only stay silent for
// ids that pool.csv's own screen removed.
const A20 = new Set([29,31,32,38,39,40,43,44,50,51,52,54,66,68,79,80,88,89,96,97,98,99,100,101,102,104,105,108,109,110,122,124,128,129,130,132,134,138,139,140,141,142,143,195,199,202,206,209,210,230,241,248,282,287,289,299,316,317,321,325,326,345,346,347,348,349,359,398,399,400,408,409,410,411,416,418,425,428,429,431,432,446,463,476,478,495,498,508,532,560,562,563,564,565,566,567,568,569,576,587,607,609,618,629,630,635,696,697,698,699,704,706,727,758,763,765,775,778,779,780,816,835,845,849,858,865,866,867,872,877,880,881,882,883,889,898,909,911,915,977,979,983]);

const droppedScreened = [];
let profiles = [];
const seenIds = new Set();
for (const p of allProfiles) {
  if (!csvById.has(p.id)) {
    if (A20.has(p.id)) {
      droppedScreened.push(p.id);
      continue; // legitimately screened out, drop silently from the shipped pool
    }
    errors.push(`profile id ${p.id} not in pool.csv and not in the A20 screened-out list -- unexplained`);
    continue;
  }
  if (seenIds.has(p.id)) { errors.push(`duplicate profile id ${p.id}`); continue; }
  seenIds.add(p.id);
  profiles.push(p);
}
if (droppedScreened.length) {
  console.log(`Dropped ${droppedScreened.length} screened-out profile(s) from old shards: ${droppedScreened.sort((a,b)=>a-b).join(", ")}`);
}

// dedupe / sanity
for (const p of profiles) {
  const csv = csvById.get(p.id);
  if (p.name !== csv.name) errors.push(`id ${p.id} name mismatch: profile="${p.name}" csv="${csv.name}"`);
  if (p.showdown_id !== csv.showdown_id) errors.push(`id ${p.id} showdown_id mismatch: profile="${p.showdown_id}" csv="${csv.showdown_id}"`);
  if (p.stage !== csv.stage) errors.push(`id ${p.id} stage mismatch: profile="${p.stage}" csv="${csv.stage}"`);
  // Q5: lean is OPTIONAL in data/pool.json and, when present, MUST equal the csv record (nothing
  // reads it there -- test/check.py's a17 retest simulation still indexes p["lean"] as a stub, so we
  // keep it as a harmless record rather than deleting it). It is stripped only from the web/ copy below.
  p.lean = csv.lean;
}
for (const csv of csvRows) {
  if (!seenIds.has(csv.id)) errors.push(`missing profile for pool.csv id ${csv.id} (${csv.name})`);
}

if (errors.length) {
  console.log(`${errors.length} ERRORS before merge:`);
  errors.forEach((e) => console.log(" - " + e));
}

// attach auto_vector from corpus
const corpus = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "corpus.json"), "utf8"));
const corpusById = new Map(corpus.species.map((s) => [s.id, s]));

for (const p of profiles) {
  const c = corpusById.get(p.id);
  if (!c) { errors.push(`no corpus entry for id ${p.id}`); continue; }
  p.auto_vector = c.auto_vector;
  if (!p.genus) p.genus = c.genus;
  else if (p.genus !== c.genus) {
    console.log(`note: id ${p.id} genus differs, profile="${p.genus}" corpus="${c.genus}" -- using corpus genus (contract requires genus MUST equal corpus entry)`);
    p.genus = c.genus;
  }
}

// attach images
const ART_DIR = path.join(ROOT, "web", "img", "art");
const ANI_DIR = path.join(ROOT, "web", "img", "ani");
for (const p of profiles) {
  p.images = { art: `img/art/${p.id}.png`, ani: `img/ani/${p.showdown_id}.gif`, ani_static_fallback: false };
  const gifPath = path.join(ANI_DIR, `${p.showdown_id}.gif`);
  const pngFallback = path.join(ANI_DIR, `${p.showdown_id}.png`);
  if (!fs.existsSync(gifPath) && fs.existsSync(pngFallback)) {
    p.images.ani = `img/ani/${p.showdown_id}.png`;
    p.images.ani_static_fallback = true;
  }
  if (!fs.existsSync(path.join(ART_DIR, `${p.id}.png`))) {
    errors.push(`missing art image for id ${p.id}`);
  }
}

// order profiles by id ascending for determinism
profiles.sort((a, b) => a.id - b.id);

// compute profileVectors (mutates profiles, adding .vector)
profileVectors(profiles);

// Contract Q5: each trait's ratings MUST have at least 30% at -1 or below and at least 30% at 1 or above.
const N = profiles.length;
for (const k of TRAITS) {
  const lo = profiles.filter((p) => p.ratings[k] <= -1).length;
  const hi = profiles.filter((p) => p.ratings[k] >= 1).length;
  const loPct = ((lo / N) * 100).toFixed(1);
  const hiPct = ((hi / N) * 100).toFixed(1);
  const ok = lo / N >= 0.3 && hi / N >= 0.3;
  console.log(`Rating spread ${k}: ${loPct}% at or below -1, ${hiPct}% at or above 1${ok ? "" : "  <-- FAILS 30% floor"}`);
  if (!ok) errors.push(`trait ${k} rating spread fails the 30% floor: ${loPct}% low, ${hiPct}% high`);
}

if (errors.length) {
  console.log(`\n${errors.length} TOTAL ERRORS. Writing pool.json anyway for inspection; fix before shipping.`);
  fs.writeFileSync(path.join(ROOT, "data", "pool-errors.json"), JSON.stringify(errors, null, 1));
}

const poolJson = {
  version: 1,
  traits: TRAITS,
  swaps: [],
  profiles,
};

fs.writeFileSync(path.join(ROOT, "data", "pool.json"), JSON.stringify(poolJson));
console.log(`Wrote data/pool.json with ${profiles.length} profiles.`);

// Copy runtime data into web/data/. Amendment 2026-09-27: "Any pool data shipped under web/ MUST
// carry no lean field" -- data/pool.json itself may keep it as a harmless record (Q5), but the web/
// copy strips it so no shipped file, script, or app code can read a taker's or a match's lean.
fs.mkdirSync(path.join(ROOT, "web", "data"), { recursive: true });
const webPoolJson = {
  ...poolJson,
  profiles: profiles.map(({ lean, ...rest }) => rest),
};
fs.writeFileSync(path.join(ROOT, "web", "data", "pool.json"), JSON.stringify(webPoolJson));
fs.copyFileSync(path.join(ROOT, "data", "questions.json"), path.join(ROOT, "web", "data", "questions.json"));
console.log("Wrote web/data/pool.json (lean stripped) and copied questions.json into web/data/.");
