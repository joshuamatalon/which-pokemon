// Pulls PokéAPI pokemon-species 1..1025 plus pokemon (types/stats) and evolution-chain (stage),
// caches everything on disk under data/cache/ so a rerun is free, and writes data/corpus.json.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { tag, cleanFlavorText } from "./lib.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const CACHE = path.join(ROOT, "data", "cache");
const N = 1025;
const CONCURRENCY = 8;
const RETRY = 4;

for (const sub of ["species", "pokemon", "evochain"]) {
  fs.mkdirSync(path.join(CACHE, sub), { recursive: true });
}

const lexicon = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "lexicon.json"), "utf8"));

async function fetchJsonCached(url, cachePath) {
  if (fs.existsSync(cachePath)) {
    return JSON.parse(fs.readFileSync(cachePath, "utf8"));
  }
  let lastErr;
  for (let attempt = 0; attempt < RETRY; attempt++) {
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
      const json = await res.json();
      fs.writeFileSync(cachePath, JSON.stringify(json));
      return json;
    } catch (e) {
      lastErr = e;
      await new Promise((r) => setTimeout(r, 300 * (attempt + 1)));
    }
  }
  throw lastErr;
}

async function pool(items, worker, concurrency) {
  const results = new Array(items.length);
  let next = 0;
  async function run() {
    while (next < items.length) {
      const i = next++;
      results[i] = await worker(items[i], i);
    }
  }
  await Promise.all(new Array(concurrency).fill(0).map(run));
  return results;
}

const GEN_MAP = {
  "generation-i": 1, "generation-ii": 2, "generation-iii": 3, "generation-iv": 4,
  "generation-v": 5, "generation-vi": 6, "generation-vii": 7, "generation-viii": 8, "generation-ix": 9,
};

function evolutionDepth(chainRoot, targetName) {
  // BFS over the chain tree; depth 1 = root.
  const queue = [{ node: chainRoot, depth: 1 }];
  while (queue.length) {
    const { node, depth } = queue.shift();
    if (node.species.name === targetName) return depth;
    for (const child of node.evolves_to || []) {
      queue.push({ node: child, depth: depth + 1 });
    }
  }
  return 1;
}

async function main() {
  const ids = Array.from({ length: N }, (_, i) => i + 1);
  console.log(`Fetching ${N} species...`);

  const speciesRaw = await pool(
    ids,
    async (id) => {
      const cp = path.join(CACHE, "species", `${id}.json`);
      return fetchJsonCached(`https://pokeapi.co/api/v2/pokemon-species/${id}/`, cp);
    },
    CONCURRENCY
  );
  console.log(`Species fetched. Fetching ${N} pokemon (types/stats)...`);

  const pokemonRaw = await pool(
    ids,
    async (id) => {
      const cp = path.join(CACHE, "pokemon", `${id}.json`);
      return fetchJsonCached(`https://pokeapi.co/api/v2/pokemon/${id}/`, cp);
    },
    CONCURRENCY
  );
  console.log("Pokemon fetched. Fetching evolution chains (deduped)...");

  const chainUrls = [...new Set(speciesRaw.map((s) => s.evolution_chain?.url).filter(Boolean))];
  const chainByUrl = new Map();
  await pool(
    chainUrls,
    async (url) => {
      const chainId = url.split("/").filter(Boolean).pop();
      const cp = path.join(CACHE, "evochain", `${chainId}.json`);
      const data = await fetchJsonCached(url, cp);
      chainByUrl.set(url, data);
    },
    CONCURRENCY
  );
  console.log(`Evolution chains fetched: ${chainUrls.length}. Assembling corpus...`);

  const missing_flavor = [];
  const species = [];

  for (let idx = 0; idx < N; idx++) {
    const sp = speciesRaw[idx];
    const pk = pokemonRaw[idx];
    const id = sp.id;

    const nameEntry = sp.names.find((n) => n.language.name === "en");
    const name = nameEntry ? nameEntry.name : sp.name;
    const genusEntry = sp.genera.find((g) => g.language.name === "en");
    const genus = genusEntry ? genusEntry.genus : "";

    const rawTexts = sp.flavor_text_entries.filter((f) => f.language.name === "en").map((f) => cleanFlavorText(f.flavor_text));
    const seen = new Set();
    const flavor_texts = [];
    for (const t of rawTexts) {
      const key = t.toLowerCase();
      if (!seen.has(key)) {
        seen.add(key);
        flavor_texts.push(t);
      }
    }
    if (flavor_texts.length === 0) missing_flavor.push(id);

    const chainUrl = sp.evolution_chain?.url;
    const chainData = chainUrl ? chainByUrl.get(chainUrl) : null;
    const stage = chainData ? evolutionDepth(chainData.chain, sp.name) : 1;

    const statMap = {};
    for (const s of pk.stats) statMap[s.stat.name] = s.base_stat;

    const { auto_vector, matched_words } = tag(flavor_texts.length ? flavor_texts : [""], lexicon);

    species.push({
      id,
      slug: sp.name,
      name,
      genus,
      flavor_texts,
      color: sp.color ? sp.color.name : null,
      shape: sp.shape ? sp.shape.name : null,
      habitat: sp.habitat ? sp.habitat.name : null,
      gender_rate: sp.gender_rate,
      egg_groups: sp.egg_groups.map((g) => g.name),
      is_legendary: sp.is_legendary,
      is_mythical: sp.is_mythical,
      is_baby: sp.is_baby,
      stage,
      types: pk.types.sort((a, b) => a.slot - b.slot).map((t) => t.type.name),
      base_stats: {
        hp: statMap["hp"], attack: statMap["attack"], defense: statMap["defense"],
        special_attack: statMap["special-attack"], special_defense: statMap["special-defense"], speed: statMap["speed"],
      },
      height: pk.height,
      weight: pk.weight,
      generation: GEN_MAP[sp.generation.name] || 1,
      auto_vector,
      matched_words,
      in_pool: false,
    });
  }

  // mark in_pool from spec/pool.csv
  const poolCsv = fs.readFileSync(path.join(ROOT, "spec", "pool.csv"), "utf8");
  const poolIds = new Set(
    poolCsv
      .split(/\r?\n/)
      .slice(1)
      .filter((l) => l.trim())
      .map((l) => parseInt(l.split(",")[0], 10))
  );
  for (const s of species) {
    if (poolIds.has(s.id)) s.in_pool = true;
  }

  const corpus = {
    version: 1,
    source: "https://pokeapi.co/api/v2/",
    pulled: new Date().toISOString().slice(0, 10),
    count: species.length,
    missing_flavor,
    species,
  };

  fs.writeFileSync(path.join(ROOT, "data", "corpus.json"), JSON.stringify(corpus));
  console.log(`Wrote data/corpus.json with ${species.length} species, ${missing_flavor.length} missing flavor text.`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
