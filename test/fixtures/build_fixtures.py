"""Builds test/fixtures/good (a small, schema-shaped pool+corpus+app.js) and test/fixtures/known_bad
(a clone of good/ with four deliberate defects) so test/check.py has something to run every
pool-dependent assertion against before the stream's data/pool.json and web/app.js land, and so
A19's calibration claim is backed by more than the one self-contained unit test inside check.py.
This script is a one-time fixture builder, not part of the check itself.
"""
import json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "test"))
import check as C  # noqa: E402

GOOD = ROOT / "test" / "fixtures" / "good"
BAD = ROOT / "test" / "fixtures" / "known_bad"

# ids chosen from the REAL spec/pool.csv, spanning several stages. Rebuilt 2026-09-27: the amended pool
# screen (spec/POOL-SCREEN.md) removed Nidoran-female (29) and Nidoran-male (32) from the pool (their
# names carry a sex, and lean no longer filters anyone away from them), so this fixture substitutes
# Butterfree (12) and Alakazam (65), both still KEEP in the screened spec/pool.csv, none of the ten ids
# below appear in check.py's A20_REMOVED_IDS.
IDS = [1, 3, 6, 12, 30, 35, 58, 59, 65, 9]
RATINGS = {
    1: {"O": -1, "C": 1, "E": 0, "A": 2, "S": 1},
    3: {"O": 1, "C": 1, "E": -1, "A": 2, "S": 3},
    6: {"O": 1, "C": -1, "E": 2, "A": -2, "S": -1},
    12: {"O": -2, "C": 1, "E": -1, "A": 2, "S": -1},
    30: {"O": -1, "C": 2, "E": 0, "A": 3, "S": 1},
    35: {"O": 1, "C": -1, "E": 3, "A": -1, "S": -2},
    58: {"O": -1, "C": -1, "E": 2, "A": -1, "S": -2},
    59: {"O": 1, "C": 2, "E": -1, "A": 1, "S": 3},
    65: {"O": -2, "C": -1, "E": 1, "A": -1, "S": -1},
    9: {"O": 1, "C": 3, "E": -2, "A": 2, "S": 2},
}


def load_pool_csv_rows():
    rows = C.load_pool_csv(ROOT / "spec" / "pool.csv")
    return {r["id"]: r for r in rows}


# Rebuilt 2026-09-27: this fixture used to copy the REAL, in-flight data/questions.json verbatim. That
# broke calibration the moment the real file's own content (item q10's answer/echo text uses the word
# "stomach", one of the new Q6 screen words -- a genuine stream-side issue, reported separately, not a
# check bug) leaked into what is supposed to be a clean "good" baseline. A calibration fixture must not
# depend on the correctness of the thing being judged, so this now builds a small, self-contained,
# schema-valid 15-item quiz by hand, independent of the real file.

FACET_ORDER = {
    "O": ["Intellectual Curiosity", "Aesthetic Sensitivity", "Creative Imagination"],
    "C": ["Organization", "Productiveness", "Responsibility"],
    "E": ["Sociability", "Assertiveness", "Energy Level"],
    "A": ["Compassion", "Respectfulness", "Trust"],
    "S": ["Anxiety", "Emotional Volatility", "Vulnerability"],
}
STEMS = {
    "O": "You have a free afternoon. What do you do?",
    "C": "You are getting ready for a trip. What do you do?",
    "E": "A friend invites you to a party. What do you do?",
    "A": "Your group needs help with a project. What do you do?",
    "S": "Plans change at the last minute. What do you do?",
}
# level -> answer text, one set per trait; all short, plain, no D8 topic word, no negation.
ANSWER_TEXT = {
    "O": {3: "I try a brand new idea.", 1: "I mix in something new today.",
          -1: "I pick something a little familiar.", -3: "I pick a plan that always works."},
    "C": {3: "I make a full list first.", 1: "I jot a quick short list.",
          -1: "I pack a little and wing it.", -3: "I just grab what I need."},
    "E": {3: "I invite everyone I can find.", 1: "I join in with a few people.",
          -1: "I stay near people I know well.", -3: "I find a quiet spot alone."},
    "A": {3: "I put the group first every time.", 1: "I offer to help where I can.",
          -1: "I share my own view first.", -3: "I say exactly what I think."},
    "S": {3: "I stay calm through it all.", 1: "I take a breath and carry on.",
          -1: "I feel it but keep moving.", -3: "I feel it right away, strongly."},
}
# level-3 position per item index (0..3), chosen so each of the 4 positions gets >=3 across 15 items
# (D5), and every one of the four orders below is non-monotone (D5's >=10-non-monotone floor).
ORDER_BY_POS = {
    0: [3, -1, -3, 1],
    1: [-1, 3, 1, -3],
    2: [-3, 1, 3, -1],
    3: [1, -3, -1, 3],
}


def echo_of(text):
    body = text.strip().rstrip(".")
    if body.lower().startswith("i "):
        body = body[2:]
    return "you'd " + body


def build_fixture_questions():
    items = []
    for i in range(15):
        trait = C.TRAITS[i % 5]
        facet = FACET_ORDER[trait][i // 5]
        pos = i % 4
        levels = ORDER_BY_POS[pos]
        answers = [{"text": ANSWER_TEXT[trait][lv], "level": lv, "echo": echo_of(ANSWER_TEXT[trait][lv])}
                   for lv in levels]
        items.append({
            "id": "q%02d" % (i + 1), "trait": trait, "facet": facet, "flavour": False,
            "source_instrument": "IPIP", "source_item": "Fixture placeholder IPIP source item.", "source_key": "+",
            "stem": STEMS[trait], "answers": answers,
        })
    traits_meta = {
        "O": {"name": "Imagination", "high": "Curious", "low": "Down-to-earth",
              "high_line": "You like new ideas and want to know how things work.",
              "low_line": "You trust what works and keep your feet on the ground."},
        "C": {"name": "Planning", "high": "Planner", "low": "Go-with-the-flow",
              "high_line": "You like a plan, and you finish what you start.",
              "low_line": "You adapt fast and enjoy whatever comes up."},
        "E": {"name": "Social energy", "high": "Outgoing", "low": "Low-key",
              "high_line": "You get energy from people and like being in the mix.",
              "low_line": "You recharge in calm places and notice what others miss."},
        "A": {"name": "Getting along", "high": "Team player", "low": "Strong-willed",
              "high_line": "You look out for others and help a group get along.",
              "low_line": "You say what you think and stand up for it."},
        "S": {"name": "Steadiness", "high": "Steady", "low": "Sensitive",
              "high_line": "You stay calm when plans change.",
              "low_line": "You feel things deeply and notice changes early."},
    }
    return {"version": 1, "traits": traits_meta, "takers": C.Q7_TAKERS, "items": items}


def main():
    real_corpus = json.loads((ROOT / "data" / "corpus.json").read_text(encoding="utf-8"))
    real_lexicon = json.loads((ROOT / "data" / "lexicon.json").read_text(encoding="utf-8"))
    species_by_id = {s["id"]: s for s in real_corpus["species"]}
    csv_by_id = load_pool_csv_rows()

    (GOOD / "data").mkdir(parents=True, exist_ok=True)
    (GOOD / "web" / "img" / "art").mkdir(parents=True, exist_ok=True)
    (GOOD / "web" / "img" / "ani").mkdir(parents=True, exist_ok=True)

    # --- fixture corpus.json: real per-id entries for the chosen ids only
    sub_species = [species_by_id[i] for i in IDS]
    fixture_corpus = {"version": 1, "source": real_corpus["source"], "pulled": real_corpus["pulled"],
                       "count": len(sub_species), "missing_flavor": [], "species": sub_species}
    (GOOD / "data" / "corpus.json").write_text(json.dumps(fixture_corpus, ensure_ascii=False, indent=1), encoding="utf-8")

    # --- lexicon: reuse the REAL, already-landed file as-is (read-only copy; not the object of this
    # amendment and not implicated in the q10/"stomach" issue above)
    shutil.copy(ROOT / "data" / "lexicon.json", GOOD / "data" / "lexicon.json")
    # --- questions: hand-built fixture-only quiz (see build_fixture_questions() docstring above)
    fixture_questions = build_fixture_questions()
    (GOOD / "data" / "questions.json").write_text(
        json.dumps(fixture_questions, ensure_ascii=False, indent=1), encoding="utf-8")

    # --- fixture pool.json
    profiles = []
    for pid in IDS:
        row = csv_by_id[pid]
        sp = species_by_id[pid]
        auto, _ = C.tag(sp["flavor_texts"], real_lexicon)
        profiles.append({
            "id": pid, "name": row["name"], "showdown_id": row["showdown_id"], "genus": sp["genus"],
            "lean": row["lean"], "stage": row["stage"], "ratings": RATINGS[pid],
            "rating_evidence": {k: "Fixture evidence sentence for %s." % k for k in C.TRAITS},
            "auto_vector": auto,
            "personality": "Fixture personality sentence about %s for instrument calibration only." % row["name"],
            "media": [{"title": "%s appears in the games" % row["name"], "note": "Fixture note."}],
            "community": "Fixture community sentence about %s." % row["name"],
            "why": [
                {"text": "The %s is known for being steady in canon." % row["name"], "trait": "S", "anchor": row["name"]},
                {"text": "Its %s genus fits %s well." % (sp["genus"], row["name"]), "trait": "O", "anchor": sp["genus"]},
                {"text": "Fans of %s note its friendly reputation." % row["name"], "trait": "A", "anchor": row["name"]},
            ],
            "sources": ["https://pokeapi.co/api/v2/pokemon-species/%d/" % pid,
                        "https://bulbapedia.bulbagarden.net/wiki/%s_(Pok%%C3%%A9mon)" % row["name"]],
            "images": {"art": "img/art/%d.png" % pid, "ani": "img/ani/%s.gif" % row["showdown_id"],
                       "ani_static_fallback": False},
        })
    C.profileVectors(profiles)
    fixture_pool = {"version": 1, "traits": C.TRAITS, "swaps": [], "profiles": profiles}
    (GOOD / "data" / "pool.json").write_text(json.dumps(fixture_pool, ensure_ascii=False, indent=1), encoding="utf-8")

    # --- tiny valid images for every profile
    from PIL import Image
    for p in profiles:
        Image.new("RGBA", (4, 4), (10, 20, 30, 255)).save(GOOD / "web" / "img" / "art" / ("%d.png" % p["id"]))
        Image.new("P", (4, 4)).save(GOOD / "web" / "img" / "ani" / ("%s.gif" % p["showdown_id"]))

    # --- app.js: ES module mirror of Q3, for A9
    app_js = APP_JS_TEMPLATE
    (GOOD / "web" / "app.js").write_text(app_js, encoding="utf-8")
    # index.html: fixture page plus the contract's own 81-word "How it works" reference text (Q6,
    # amendment 2026-09-27), inside a <details> toggle so extract_how_it_works() finds a closing marker.
    (GOOD / "web" / "index.html").write_text(HOW_IT_WORKS_HTML, encoding="utf-8")

    # ================= known_bad: clone of good/ with four deliberate defects =================
    if BAD.exists():
        shutil.rmtree(BAD)
    shutil.copytree(GOOD, BAD)

    bad_pool = json.loads((BAD / "data" / "pool.json").read_text(encoding="utf-8"))
    # defect 1: duplicate a why sentence across two profiles (breaks A5)
    bad_pool["profiles"][1]["why"][0]["text"] = bad_pool["profiles"][0]["why"][0]["text"]
    # defect 2: an em dash in a why sentence (breaks A16)
    bad_pool["profiles"][2]["why"][1]["text"] = "It stands out — a fixture defect on purpose."
    (BAD / "data" / "pool.json").write_text(json.dumps(bad_pool, ensure_ascii=False, indent=1), encoding="utf-8")
    # defect 3: missing image for one profile (breaks A8)
    missing_art = BAD / "web" / "img" / "art" / ("%d.png" % profiles[3]["id"])
    if missing_art.exists():
        missing_art.unlink()
    # defect 4: a changed lean weight in the copied match() (breaks A9 and/or A13)
    bad_js = app_js.replace("const LEAN_OPPOSITE = 0.25;", "const LEAN_OPPOSITE = 0.50;")
    assert bad_js != app_js, "lean-weight substitution did not match app.js text"
    (BAD / "web" / "app.js").write_text(bad_js, encoding="utf-8")

    print("built", GOOD, "and", BAD, "with", len(profiles), "profiles")


HOW_IT_WORKS_HTML = """<!doctype html><html><head><title>fixture</title></head><body><main>
<p>fixture page, no banned words here.</p>
<details><summary>How it works</summary>
<p>The quiz is built on the Big Five, the trait model most personality research uses. The five traits here
are Imagination, Planning, Social energy, Getting along and Steadiness. There are 15 questions. Each trait
gets three of them. Your answers place you on all five traits, and your Pokemon is the one whose trait
profile sits nearest to yours. It is a game drawn from that
<a href="https://github.com/joshuamatalon/which-pokemon/blob/main/spec/RESEARCH-PERSONALITY.md">research note</a>
and makes no claim to measure you.</p>
</details>
</main></body></html>"""

APP_JS_TEMPLATE = r"""// Fixture-only ES module mirror of spec/CONTRACT.md Q3, for test/check.py A9.
export const TRAITS = ["O", "C", "E", "A", "S"];
const STAGE_INDEX = { young: 0, evolved: 1, mature: 2 };
const LEAN_SAME = 0.00;
const LEAN_NEUTRAL = 0.08;
const LEAN_OPPOSITE = 0.25;

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
"""

if __name__ == "__main__":
    main()
