// Fixture-only ES module mirror of spec/CONTRACT.md Q3, for test/check.py A9.
export const TRAITS = ["O", "C", "E", "A", "S"];
const STAGE_INDEX = { young: 0, evolved: 1, mature: 2 };
const LEAN_SAME = 0.00;
const LEAN_NEUTRAL = 0.08;
const LEAN_OPPOSITE = 0.50;

function round6(x) { return Math.floor(x * 1000000 + 0.5); }
export function round4(x) { return Math.floor(x * 10000 + 0.5) / 10000; }

export function takerVector(items, choice) {
  const sum = { O: 0, C: 0, E: 0, A: 0, S: 0 };
  const n = { O: 0, C: 0, E: 0, A: 0, S: 0 };
  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    const level = item.answers[choice[i]].level;
    sum[item.trait] += level;
    n[item.trait] += 1;
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

export function match(t, taker, profiles) {
  let best = null;
  for (const p of profiles) {
    let d = 0;
    for (let k = 0; k < 5; k++) d += (t[k] - p.vector[k]) * (t[k] - p.vector[k]);
    d = Math.sqrt(d);
    const key = round6(d + leanPenalty(taker.lean, p.lean) + stagePenalty(taker, p.stage));
    if (best === null || key < best.key || (key === best.key && p.id < best.id)) {
      best = { id: p.id, key };
    }
  }
  return best.id;
}
