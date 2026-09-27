#!/usr/bin/env python3
"""
test/check.py -- independent instrument for spec/CONTRACT.md, one command, asserts A1 to A20 (Q8).

Amended 2026-09-27 for CONTRACT.md's own amendment (lean void, offence screen, How it works toggle):
A13 was rewritten (lean-is-null + stub-vs-real match() agreement + no lean field under web/ + no
gender word in index.html), A7/Q7_TAKERS now expects null lean for every taker, A4/RESERVE_IDS use the
screened reserve list, A15/A16 add the Q6 screen-word list, A16 adds the How it works checks, and A20
is new (no pool.csv row / pool.json profile / swap / reserve carries a spec/POOL-SCREEN.md removed id).

Usage:
  python test/check.py [--root PATH] [--base-url URL] [--seed N] [--skip-a18]

--root defaults to the project root (parent of test/). Point it at a fixture root
(test/fixtures/good or test/fixtures/known_bad) to run the same checks against synthetic data.
--base-url defaults to the live URL for A18; pass a local http://127.0.0.1:PORT/ to check a
local `python -m http.server` run from web/ instead.

Every assertion prints one line: "A<n> STATUS  summary". STATUS is PASS, FAIL, SKIP or REPORT.
REPORT lines carry a number with no pass mark, as the contract requires for A17 (and sub-metrics
of A2 and A8). SKIP means the input this assertion needs was not present at run time; it is never
counted as a pass. Exit code is nonzero iff any MUST-marked assertion FAILed on data that was
actually present (a SKIP does not fail the run, so an honest "could not run yet" never look like
green).

KNOWN LIMITATIONS -- read before trusting a PASS:
- A9 needs node and web/app.js. This check assumes the app exposes match() (and friends) either
  as ES module named exports, or as top-level function declarations reachable in a non-module
  script's global scope. If the stream ships neither shape (e.g. everything wrapped in a closure
  with no export), the harness cannot reach the function and A9 SKIPs with the node error printed,
  rather than guessing a verdict.
- A9's 1,000-per-taker agreement cases use a SYNTHETIC 15-item quiz built in this file (trait
  cycle O,C,E,A,S x3, levels -3,-1,1,3 in a fixed answer order), not the real data/questions.json.
  That is deliberate: A9 tests whether the two match() implementations compute the same thing,
  which does not depend on item wording; A6 is what checks item content.
- A10 to A14 and A17 (the 20,000-draw and lattice simulations) do not depend on data/questions.json
  either: since every item always offers exactly the four levels -3,-1,1,3 once each (Q2), a
  uniform random choice of answer index is a uniform random draw of level, independent of answer
  order. So these assertions run against whatever pool (data/pool.json, or the fixture pool under
  --root) is loaded, at that pool's real size. Run against a small fixture pool, the coverage /
  reachability / concentration THRESHOLDS in the contract were derived for a 160-member pool and
  are not expected to hold; those lines are labelled FIXTURE-SCALE and are informative only, never
  a false FAIL of a threshold the fixture was never big enough to meet.
- A16 shells out to demandscan's prose_check.py rather than reimplementing its banned-word list,
  per the mission order ("call it, do not reimplement it"). If that script's own banned-word list
  ever drifts from the contract's Q6 list, this check will not notice the drift on its own; A16
  also separately re-checks the Q6-specific words prose_check.py does not carry.
- A18's mobile playthrough cannot know the real app's DOM before the app exists, so it is a
  HEURISTIC: it looks for the first clickable element per screen and clicks it. A green result
  here is SUSPECTED, never CONFIRMED (the panelist's independent product pass is the real check
  of the flow); a SKIP means the heuristic's assumptions did not match what it found, which is not
  evidence the app is broken.
- Euclidean-distance simulations use numpy for speed; round6/round4 are still applied exactly as
  the contract defines them (floor, never a language round()), matching the pure-Python
  scalar path used for A9's tie-break-sensitive comparisons.
- This instrument is calibrated on defects the author thought to construct (A19: a duplicated
  why sentence, and separately a missing image, an em dash, and a changed lean weight, tried by
  hand). A green run on real data is evidence the data agrees with the contract on the axes this
  file checks, not proof of correctness on axes nobody thought to break.
- A13's "no lean field under web/" scan and its localStorage/sessionStorage/cookie scan are exact
  text/regex matches, not a running browser: they can miss a lean written under a different key name,
  or through an obfuscated/minified build. Its "How it works" checks (moved into A16, see below) share
  the same limit. A13's real-vs-stubbed-leanPenalty comparison is, by construction, near-tautological
  once every taker's lean is confirmed null (leanPenalty already short-circuits to 0 on a null taker
  lean) -- its value is as a regression guard against a taker lean silently becoming non-null again or
  the null check being removed, not as a live behavioural test.
- A16's "How it works" extraction (extract_how_it_works) is a HEURISTIC: it does not know the real
  toggle's HTML structure, so it grabs everything between the phrase "how it works" and the next
  closing container/heading tag (or 4000 chars). A None or oddly-sized extract is a prompt to read
  web/index.html by eye, not proof the toggle is missing or wrong.
"""
import argparse, json, math, os, re, subprocess, sys, tempfile, time, unicodedata
from pathlib import Path

import numpy as np

ROOT_DEFAULT = Path(__file__).resolve().parent.parent
TRAITS = ["O", "C", "E", "A", "S"]
STAGE_INDEX = {"young": 0, "evolved": 1, "mature": 2}
LEAN_SAME = 0.00
LEAN_NEUTRAL = 0.08
LEAN_OPPOSITE = 0.25
LEVELS = [-3, -1, 1, 3]
LATTICE_VALS = [s / 9 for s in range(-9, 10, 2)]  # 10 values, -1 .. 1

# ---------------------------------------------------------------- Q3 scoring, byte for byte

def round6(x):
    return math.floor(x * 1_000_000 + 0.5)


def round4(x):
    return math.floor(x * 10_000 + 0.5) / 10_000


def takerVector(items, choice):
    s = {k: 0 for k in TRAITS}
    n = {k: 0 for k in TRAITS}
    for i, item in enumerate(items):
        level = item["answers"][choice[i]]["level"]
        s[item["trait"]] += level
        n[item["trait"]] += 1
    return [s[k] / (3 * n[k]) for k in TRAITS]


def profileVectors(profiles):
    """Mutates profiles in place, writing profile['vector']. profiles: list of dicts with
    'ratings' (dict trait->int -4..4) and 'auto_vector' (list of 5 floats) and 'id'."""
    n = len(profiles)
    for p in profiles:
        p["_raw"] = [0.75 * (p["ratings"][TRAITS[k]] / 4) + 0.25 * p["auto_vector"][k] for k in range(5)]
    for k in range(5):
        order = sorted(range(n), key=lambda pi: (profiles[pi]["_raw"][k], profiles[pi]["id"]))
        pos = 0
        while pos < n:
            end = pos
            while end + 1 < n and profiles[order[end + 1]]["_raw"][k] == profiles[order[pos]]["_raw"][k]:
                end += 1
            rank = (pos + end) / 2
            val = round4(-0.9 + 1.8 * rank / (n - 1)) if n > 1 else 0.0
            for j in range(pos, end + 1):
                profiles[order[j]].setdefault("vector", [0.0] * 5)
                profiles[order[j]]["vector"][k] = val
            pos = end + 1
    for p in profiles:
        p.pop("_raw", None)
    return profiles


def leanPenalty(taker_lean, member_lean):
    if taker_lean is None:
        return 0
    if member_lean == taker_lean:
        return LEAN_SAME
    if member_lean == "neutral":
        return LEAN_NEUTRAL
    return LEAN_OPPOSITE


def stagePenalty(taker, member_stage):
    return taker["stage_weight"] * abs(STAGE_INDEX[member_stage] - STAGE_INDEX[taker["stage_target"]])


def match(t, taker, profiles):
    best = None
    for p in profiles:
        d = math.sqrt(sum((t[k] - p["vector"][k]) ** 2 for k in range(5)))
        # p.get("lean"): lean is optional on a profile since the 2026-09-27 amendment (Q5) and, when taker
        # lean is null (every real taker, since the same amendment), leanPenalty never looks at it anyway.
        key = round6(d + leanPenalty(taker["lean"], p.get("lean")) + stagePenalty(taker, p["stage"]))
        if best is None or key < best["key"] or (key == best["key"] and p["id"] < best["id"]):
            best = {"id": p["id"], "key": key}
    return best["id"]


# ---------------------------------------------------------------- Q5 lexicon tagging

def tokenize(text):
    return re.findall(r"[a-zé]+", text.lower())


def _match_lexicon(tokens, entries):
    singles_exact = set(e for e in entries if " " not in e and not e.endswith("*"))
    prefixes = [e[:-1] for e in entries if " " not in e and e.endswith("*")]
    multi = [e.split(" ") for e in entries if " " in e]
    hits = []
    i, n = 0, len(tokens)
    while i < n:
        consumed = 1
        matched_multi = None
        for parts in multi:
            L = len(parts)
            if tokens[i:i + L] == parts:
                matched_multi = " ".join(parts)
                consumed = L
                break
        if matched_multi:
            hits.append(matched_multi)
        else:
            tok = tokens[i]
            if tok in singles_exact:
                hits.append(tok)
            else:
                for p in prefixes:
                    if tok.startswith(p) and len(tok) >= len(p):
                        hits.append(tok)
                        break
        i += consumed
    return hits


def _unique_in_order(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def tag(flavor_texts, lexicon):
    text = " ".join(flavor_texts)
    tokens = tokenize(text)
    auto = []
    matched = {}
    for k in TRAITS:
        hi = _match_lexicon(tokens, lexicon["traits"][k]["high"])
        lo = _match_lexicon(tokens, lexicon["traits"][k]["low"])
        auto.append(round4((len(hi) - len(lo)) / (len(hi) + len(lo) + 2)))
        matched[k] = {"high": _unique_in_order(hi), "low": _unique_in_order(lo)}
    return auto, matched


# ---------------------------------------------------------------- Q2 reading level

def syllables(word):
    w = re.sub(r"[^a-z]", "", word.lower())
    if len(w) <= 3:
        return 1
    if w.endswith("e") and not w.endswith("le"):
        w = w[:-1]
    runs = re.findall(r"[aeiouy]+", w)
    return max(1, len(runs))


def fk_grade(stem, answers):
    words = stem.split() + [w for a in answers for w in a.split()]
    n_words = len(words)
    n_sent = 1 + len(answers)
    n_syl = sum(syllables(w) for w in words)
    if n_words == 0 or n_sent == 0:
        return 0.0
    return 0.39 * (n_words / n_sent) + 11.8 * (n_syl / n_words) - 15.59


NEGATION_RE = re.compile(r"\b(not|no|never|none|nobody|nothing|nowhere|neither|nor|without)\b|n't\b", re.I)

TOPIC_WORDS = """sick doctor hospital medicine weight diet body fat thin money cost price buy pay rich poor
allowance spend church god pray religion vote election date dating crush boyfriend girlfriend kiss fight
argue argument divorce punish grounded die died death funeral grade grades test homework school class
teacher work job office boss retire scared afraid sad cry lonely worry worried""".split()
TOPIC_RE = re.compile(r"\b(" + "|".join(re.escape(w) for w in TOPIC_WORDS) + r")\b", re.I)

# ---------------------------------------------------------------- Q6 result-text banned lists

Q6_BANNED_WORDS = """lazy weird bossy lonely sad scary creepy old elderly aged fat chubby slow dumb stupid
annoying grumpy cranky weak ugly needy clingy moody stubborn""".split()

BANNED_FRAMINGS = ["your true pokémon", "the real you", "deep down", "secretly", "science says",
                    "scientifically", "proven", "you will always", "you are a type", "personality type",
                    "introvert", "extrovert", "neurotic"]

BARNUM_LINES = ["unused capacity", "untapped potential", "critical of yourself", "at times you",
                 "sometimes you", "you pride yourself", "a great need for",
                 "while you have some personality weaknesses", "you prefer a certain amount of change"]

DASH_RE = re.compile(r"[—–]")  # em dash, en dash

# ---------------------------------------------------------------- Q6 screen words (amendment 2026-09-27)
# A superset the ORIGINAL Q6_BANNED_WORDS does not cover: a line about a species can be turned on the
# taker. Enforced in profile strings (A16) and in the result-text block (A15).

Q6_SCREEN_WORDS = ("""
eat eats eating ate hungry appetite glutton gluttonous devour devours snack snacks food sleep sleeps
sleeping asleep slept nap naps napping doze dozes dozing snooze lazily idle
heavy heavier heaviest weigh weighs weight belly stomach plump pudgy stout portly bulky muscle muscles
muscular bald
smell smells smelly stink stinks stinky stench odor odour sweat slime slimy dirt dirty filth filthy
garbage trash
dim dopey derp derpy clumsy dizzy clown weakest useless worthless pathetic loser pig worm weasel snake
tyrant toxic smug disaster
angry anger angered rage rages raging enraged rampage rampages furious fury violent vicious savage
temper tantrum vengeful grudge
cry cries crying cried tears sob sobs weep weeps
lifespan elder ancient die dies died dead death kill kills killed soul souls curse cursed curses grave
funeral
female male feminine masculine gender girl boy lady gentleman
""").split()

# ---------------------------------------------------------------- Q6 "How it works" (amendment 2026-09-27)

MEASUREMENT_WORDS = """accurate accuracy precise precisely valid validated validity proven scientifically
reliable reliability diagnose diagnosis true real""".split()
SCIENCE_SAYS_RE = re.compile(r"\bscience says\b", re.I)
RESEARCH_NOTE_URL_RE = re.compile(
    r"github\.com/joshuamatalon/which-pokemon/blob/[^\s\"'<>]+/spec/RESEARCH-PERSONALITY\.md", re.I)

# ---------------------------------------------------------------- A13: lean removal (amendment 2026-09-27)

GENDER_WORDS_RE = re.compile(r"\b(gender|feminine|masculine|female|male)\b", re.I)
STORAGE_CALL_RE = re.compile(r"(localStorage|sessionStorage|document\.cookie)[^\n;]{0,120}", re.I)

# ---------------------------------------------------------------- A20: the offence screen (amendment 2026-09-27)
# ids from spec/POOL-SCREEN.md section 8 / CONTRACT.md A20, verbatim.

A20_REMOVED_IDS = set(int(x) for x in """
29,31,32,38,39,40,43,44,50,51,52,54,66,68,79,80,88,89,96,97,98,99,100,101,102,104,105,108,109,110,122,
124,128,129,130,132,134,138,139,140,141,142,143,195,199,202,206,209,210,230,241,248,282,287,289,299,316,
317,321,325,326,345,346,347,348,349,359,398,399,400,408,409,410,411,416,418,425,428,429,431,432,446,463,
476,478,495,498,508,532,560,562,563,564,565,566,567,568,569,576,587,607,609,618,629,630,635,696,697,698,
699,704,706,727,758,763,765,775,778,779,780,816,835,845,849,858,865,866,867,872,877,880,881,882,883,889,
898,909,911,915,977,979,983
""".replace("\n", "").split(",") if x)

# ---------------------------------------------------------------- Q5 seed lexicon (A3 ground truth)

SEED_LEXICON = {
    "O": {
        "high": "curious curiosity intelligen* smart clever wisdom wise knowledge mysteri* mystic* dream* "
                "imagin* future predict* explor* wander* artist music* melod* song songs sing sings singing "
                "danc* beauty beautiful learn* magic* invent* inquisitive".split(),
        "low": "simple plain routine habit habits habitual ordinary familiar instinct instincts instinctive* "
               "practical predictable unchanging traditional tradition humble".split(),
    },
    "C": {
        "high": "careful carefully diligent* trains training disciplin* patient* patience precise* neat "
                "neatly tidy cleans organiz* organis* prepar* build* collect* stores gather* skill* master* "
                "dutiful* responsib* method* perfect*".split(),
        "low": "lazy lazily sleep* naps napping careless* reckless* whim whims whimsical fickle forget* "
               "mischiev* prank* trick* messy clumsy clumsily carefree aimless* idle* lounge* doze dozes "
               "dozing loaf* dawdl* impuls*".split(),
    },
    "E": {
        "high": "playful* lively energetic* excited excitement noisy loud* group* flock* herd* colony "
                "colonies pack packs swarm* play plays playing frolic* crowd* social* chatter* boister* "
                "shout* cheer* perform*".split() + ["show off"],
        "low": "timid* shy* hide hides hiding hidden alone solitar* quiet* silent* rarely reclus* seclu* "
               "nocturnal lurk* unseen reserved lone loner secretive withdrawn".split(),
    },
    "A": {
        "high": "gentle* kind kindly kindness kindhearted friendly affection* loyal* help helps helping "
                "helpful heal heals healing healer care cares caring nurtur* share shares sharing protect* "
                "rescue* sooth* comfort* docile harmless love loves beloved trust* cooperat* compassion* "
                "generous*".split(),
        "low": "fierce* aggress* violent* vicious* territor* ruthless* savage* brutal* hostile challeng* "
               "rival* proud pride selfish* stubborn* arrogan* bully bullies bullying intimidat* merciless* "
               "feisty domineer* belligeren* combative".split(),
    },
    "S": {
        "high": "calm* serene* relaxed relax* unflappable placid* mellow steady steadi* tranquil* peaceful* "
                "unfazed unmoved easygoing leisure* undisturbed poise* levelheaded unhurried".split(),
        "low": "nervous* scared frightened fearful afraid panic* startl* anxi* worr* sensitive moody temper "
               "tempered weep* sulk* upset* agitat* irritab* excitable jumpy trembl* cowardly skittish".split(),
    },
}

# ---------------------------------------------------------------- Q7 takers, exact

# Amendment 2026-09-27 (PLAN.md ruling 9): lean is void, every taker's lean is null. This is the check's
# own ground-truth copy of Q7, not read from data/questions.json (A7 compares the two).
Q7_TAKERS = [
    {"key": "alex", "name": "Alex", "lean": None, "stage_target": "evolved", "stage_weight": 0.08},
    {"key": "melissa", "name": "Melissa", "lean": None, "stage_target": "evolved", "stage_weight": 0.08},
    {"key": "josh", "name": "Josh", "lean": None, "stage_target": "evolved", "stage_weight": 0.08},
    {"key": "carolyn", "name": "Carolyn", "lean": None, "stage_target": "mature", "stage_weight": 0.15},
    {"key": "john", "name": "John", "lean": None, "stage_target": "mature", "stage_weight": 0.15},
    {"key": "andrew", "name": "Andrew", "lean": None, "stage_target": "evolved", "stage_weight": 0.08},
    {"key": "oliver", "name": "Oliver", "lean": None, "stage_target": "young", "stage_weight": 0.08},
    {"key": "todd", "name": "Todd", "lean": None, "stage_target": "young", "stage_weight": 0.15},
    {"key": "milo", "name": "Milo", "lean": None, "stage_target": "young", "stage_weight": 0.15},
    {"key": "guest", "name": "Someone else", "lean": None, "stage_target": "evolved", "stage_weight": 0},
]

# Amended Q4 reserve list (spec/CONTRACT.md, after the 2026-09-27 screen). Pachirisu(417), Mareep(179),
# Electabuzz(125), Hitmontop(237) and Scizor(212) moved INTO the pool and are no longer reserves; Weavile
# (461) and the screened-out reserves (763 Tsareena, 416 Vespiquen, 431 Glameow, 587 Emolga, 230 Kingdra)
# are gone. The live reserve list is Marill, Minun, Mienfoo, Milcery, Togetic, Audino.
RESERVE_IDS = {183, 312, 619, 868, 176, 531}

REQUIRED_Q1_FACETS = {
    "O": {"Intellectual Curiosity", "Aesthetic Sensitivity", "Creative Imagination"},
    "C": {"Organization", "Productiveness", "Responsibility"},
    "E": {"Sociability", "Assertiveness", "Energy Level"},
    "A": {"Compassion", "Respectfulness", "Trust"},
    "S": {"Anxiety", "Emotional Volatility", "Vulnerability"},
}

# ================================================================== loading

def load_json(path):
    if not path.exists():
        return None, "missing: %s" % path
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as e:
        return None, "unreadable JSON %s: %s" % (path, e)


def load_pool_csv(path):
    """spec/pool.csv is real (subsystem output). Returns list of dicts id,name,showdown_id,lean,stage,reason."""
    import csv
    rows = []
    if not path.exists():
        return rows
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            row["id"] = int(row["id"])
            rows.append(row)
    return rows


class R:
    """One assertion's result."""
    def __init__(self, id, status, summary, must=True, detail=None):
        self.id, self.status, self.summary, self.must, self.detail = id, status, summary, must, detail

    def line(self):
        s = "%-4s %-6s %s" % (self.id, self.status, self.summary)
        if self.detail:
            s += "\n" + "\n".join("     " + d for d in (self.detail if isinstance(self.detail, list) else [self.detail]))
        return s


def skip(id, reason, must=True):
    return R(id, "SKIP", reason, must)


# ================================================================== numpy simulation core

def penalty_vector_np(taker, leans, stages):
    n = len(leans)
    if taker["lean"] is None:
        lean_pen = np.zeros(n)
    else:
        leans = np.array(leans)
        same = leans == taker["lean"]
        neutral = leans == "neutral"
        lean_pen = np.where(same, LEAN_SAME, np.where(neutral, LEAN_NEUTRAL, LEAN_OPPOSITE))
    stage_idx = np.array([STAGE_INDEX[s] for s in stages])
    stage_pen = taker["stage_weight"] * np.abs(stage_idx - STAGE_INDEX[taker["stage_target"]])
    return lean_pen + stage_pen


def round6_np(x):
    return np.floor(x * 1_000_000 + 0.5).astype(np.int64)


def winners_for_vectors_np(t_batch, taker, pool_vec, pool_ids, pool_leans, pool_stages, chunk=4000):
    """t_batch: (M,5) array of taker vectors. Returns (winner_ids (M,), min_dist (M,))."""
    penalty = penalty_vector_np(taker, pool_leans, pool_stages)  # (N,)
    ids = np.array(pool_ids)
    M = t_batch.shape[0]
    out_ids = np.empty(M, dtype=np.int64)
    out_dist = np.empty(M, dtype=np.float64)
    for start in range(0, M, chunk):
        chunk_t = t_batch[start:start + chunk]  # (c,5)
        diff = chunk_t[:, None, :] - pool_vec[None, :, :]  # (c,N,5)
        dist = np.sqrt((diff ** 2).sum(axis=2))  # (c,N)
        keys = round6_np(dist + penalty[None, :])
        min_key = keys.min(axis=1)
        is_min = keys == min_key[:, None]
        masked_ids = np.where(is_min, ids[None, :], np.iinfo(np.int64).max)
        win_idx_id = masked_ids.min(axis=1)
        out_ids[start:start + chunk_t.shape[0]] = win_idx_id
        # min pure distance (no penalty) for coverage stats
        out_dist[start:start + chunk_t.shape[0]] = dist.min(axis=1)
    return out_ids, out_dist


def lattice_vectors():
    vals = np.array(LATTICE_VALS)
    grids = np.meshgrid(vals, vals, vals, vals, vals, indexing="ij")
    return np.stack([g.reshape(-1) for g in grids], axis=1)  # (100000,5)


def random_taker_vectors(rng, n):
    draws = rng.choice(LEVELS, size=(n, 5, 3))
    return draws.mean(axis=2) / 3.0


def pool_arrays(profiles):
    vec = np.array([p["vector"] for p in profiles], dtype=np.float64)
    ids = [p["id"] for p in profiles]
    leans = [p.get("lean") for p in profiles]  # optional since the 2026-09-27 amendment; unread when present
    stages = [p["stage"] for p in profiles]
    return vec, ids, leans, stages


def synthetic_items(n=15):
    """15-item shell used ONLY for A9 (cross-language agreement does not depend on wording)."""
    items = []
    for i in range(n):
        trait = TRAITS[i % 5]
        order = [-1, 3, -3, 1] if i % 2 == 0 else [3, -3, 1, -1]
        answers = [{"level": lv, "text": "placeholder %d" % lv, "echo": "you placeholder %d" % lv} for lv in order]
        items.append({"id": "q%02d" % (i + 1), "trait": trait, "answers": answers})
    return items


# ================================================================== A1-A19

def a1_corpus(corpus):
    if corpus is None:
        return skip("A1", "data/corpus.json missing")
    species = corpus.get("species", [])
    if not species:
        return R("A1", "FAIL", "corpus.species is empty")
    ids = [s.get("id") for s in species]
    bits, problems = [], []
    if len(ids) != len(set(ids)):
        problems.append("duplicate ids present")
    if len(species) == 1025:
        if sorted(ids) != list(range(1, 1026)):
            problems.append("1025 species present but ids are not exactly 1..1025")
        else:
            bits.append("ids 1..1025 complete")
    else:
        bits.append("FIXTURE-SCALE: %d species, full 1..1025 completeness not evaluated" % len(species))
    missing_flavor = set(corpus.get("missing_flavor", []))
    req_bool = ["is_legendary", "is_mythical", "is_baby", "in_pool"]
    req_str = ["slug", "name", "genus"]
    for s in species:
        sid = s.get("id")
        for f in req_str:
            if not isinstance(s.get(f), str):
                problems.append("id %s field %s not str" % (sid, f))
        ft = s.get("flavor_texts")
        if not isinstance(ft, list):
            problems.append("id %s flavor_texts not list" % sid)
        elif sid not in missing_flavor and len(ft) == 0:
            problems.append("id %s flavor_texts empty but not listed in missing_flavor" % sid)
        if s.get("habitat") is not None and not isinstance(s.get("habitat"), str):
            problems.append("id %s habitat wrong type" % sid)
        if not isinstance(s.get("gender_rate"), int):
            problems.append("id %s gender_rate not int" % sid)
        if not isinstance(s.get("egg_groups"), list):
            problems.append("id %s egg_groups not list" % sid)
        for f in req_bool:
            if not isinstance(s.get(f), bool):
                problems.append("id %s field %s not bool" % (sid, f))
        if not isinstance(s.get("stage"), int):
            problems.append("id %s stage not int" % sid)
        if not isinstance(s.get("types"), list):
            problems.append("id %s types not list" % sid)
        bs = s.get("base_stats")
        if not (isinstance(bs, dict) and all(k in bs for k in
                ["hp", "attack", "defense", "special_attack", "special_defense", "speed"])):
            problems.append("id %s base_stats malformed" % sid)
        if not isinstance(s.get("height"), int):
            problems.append("id %s height not int" % sid)
        if not isinstance(s.get("weight"), int):
            problems.append("id %s weight not int" % sid)
        gen = s.get("generation")
        if not (isinstance(gen, int) and 1 <= gen <= 9):
            problems.append("id %s generation out of 1..9" % sid)
        av = s.get("auto_vector")
        if not (isinstance(av, list) and len(av) == 5):
            problems.append("id %s auto_vector malformed" % sid)
        mw = s.get("matched_words")
        if not (isinstance(mw, dict) and all(k in mw for k in TRAITS)):
            problems.append("id %s matched_words malformed" % sid)
    status = "FAIL" if problems else "PASS"
    if problems:
        bits.append("%d field/type problems, first 5: %s" % (len(problems), problems[:5]))
    else:
        bits.append("field/type schema OK for %d species" % len(species))
    return R("A1", status, "; ".join(bits))


def a2_tags(corpus, lexicon):
    if corpus is None or lexicon is None:
        return skip("A2", "needs data/corpus.json and data/lexicon.json")
    species = corpus.get("species", [])
    mismatches = []
    any_match = 0
    for s in species:
        auto, matched = tag(s.get("flavor_texts", []), lexicon)
        stored_auto = s.get("auto_vector")
        ok_auto = stored_auto is not None and all(abs(a - b) <= 0.0001 for a, b in zip(auto, stored_auto))
        stored_mw = s.get("matched_words", {})
        ok_mw = all(matched[k]["high"] == stored_mw.get(k, {}).get("high") and
                    matched[k]["low"] == stored_mw.get(k, {}).get("low") for k in TRAITS)
        if not (ok_auto and ok_mw):
            mismatches.append(s.get("id"))
        if any(matched[k]["high"] or matched[k]["low"] for k in TRAITS):
            any_match += 1
    status = "PASS" if not mismatches else "FAIL"
    share = round(100.0 * any_match / len(species), 1) if species else 0.0
    detail = None
    if mismatches:
        detail = "first 10 mismatched ids: %s" % mismatches[:10]
    return R("A2", status, "%d/%d species tag() mismatch. REPORT: %.1f%% of species have >=1 lexicon match" %
              (len(mismatches), len(species), share), detail=detail)


def a3_lexicon(lexicon):
    if lexicon is None:
        return skip("A3", "data/lexicon.json missing")
    problems = []
    all_entries = {}
    for k in TRAITS:
        for pole in ("high", "low"):
            have = set(lexicon.get("traits", {}).get(k, {}).get(pole, []))
            need = set(SEED_LEXICON[k][pole])
            missing = need - have
            if missing:
                problems.append("%s.%s missing seed entries: %s" % (k, pole, sorted(missing)[:8]))
            for e in have:
                all_entries.setdefault(e, []).append("%s.%s" % (k, pole))
    dupes = {e: locs for e, locs in all_entries.items() if len(locs) > 1}
    if dupes:
        problems.append("entries in two lists: %s" % list(dupes.items())[:5])
    status = "FAIL" if problems else "PASS"
    return R("A3", status, "seed coverage + no-duplicate check" + (": OK" if not problems else ""),
              detail=problems or None)


def load_reserve_lookup():
    return RESERVE_IDS


def a4_pool(pool, pool_csv_rows):
    if pool is None:
        return skip("A4", "data/pool.json missing")
    if not pool_csv_rows:
        return skip("A4", "spec/pool.csv missing (should exist, subsystem output)")
    csv_by_id = {r["id"]: r for r in pool_csv_rows}
    swaps = pool.get("swaps", [])
    if len(swaps) > 10:
        return R("A4", "FAIL", "more than 10 swaps recorded (%d)" % len(swaps))
    swap_out = {sw["out_id"] for sw in swaps}
    swap_in = {sw["in_id"]: sw for sw in swaps}
    for sw in swaps:
        if sw["in_id"] not in RESERVE_IDS:
            return R("A4", "FAIL", "swap in_id %s is not on the reserve list" % sw["in_id"])
    profiles = pool.get("profiles", [])
    if not profiles:
        return R("A4", "FAIL", "pool.profiles is empty")
    problems = []
    for p in profiles:
        pid = p.get("id")
        src = swap_in.get(pid)
        if src is not None:
            expect_name, expect_showdown = None, None  # reserve names not cross-checked here (small table)
        elif pid in csv_by_id:
            row = csv_by_id[pid]
            for f in ["name", "showdown_id", "lean", "stage"]:
                if str(p.get(f)) != str(row[f]):
                    problems.append("id %s field %s = %r, pool.csv says %r" % (pid, f, p.get(f), row[f]))
        elif pid not in RESERVE_IDS:
            problems.append("id %s not in pool.csv and not a recorded swap-in" % pid)
        ratings = p.get("ratings", {})
        if not (isinstance(ratings, dict) and all(k in ratings for k in TRAITS) and
                all(isinstance(ratings[k], int) and -4 <= ratings[k] <= 4 for k in TRAITS)):
            problems.append("id %s ratings malformed" % pid)
        rev = p.get("rating_evidence", {})
        if not (isinstance(rev, dict) and all(k in rev and isinstance(rev[k], str) and rev[k] for k in TRAITS)):
            problems.append("id %s rating_evidence incomplete" % pid)
        if not (isinstance(p.get("personality", ""), str) and len(p["personality"].split()) <= 80):
            problems.append("id %s personality missing or over 80 words" % pid)
        if not (isinstance(p.get("community", ""), str) and len(p["community"].split()) <= 50):
            problems.append("id %s community missing or over 50 words" % pid)
        if not (isinstance(p.get("media"), list) and len(p["media"]) >= 1):
            problems.append("id %s media empty" % pid)
        why = p.get("why", [])
        if not (isinstance(why, list) and len(why) >= 3 and len({w.get("trait") for w in why}) >= 2):
            problems.append("id %s why has fewer than 3 entries or fewer than 2 traits" % pid)
        for w in why:
            if not (isinstance(w.get("text", ""), str) and len(w["text"].split()) <= 30):
                problems.append("id %s a why.text is missing or over 30 words" % pid)
        srcs = p.get("sources", [])
        if not (isinstance(srcs, list) and len(srcs) >= 2 and any("pokeapi.co" in s for s in srcs)):
            problems.append("id %s sources needs >=2 URLs incl. a PokeAPI species URL" % pid)
        images = p.get("images", {})
        if not (isinstance(images, dict) and images.get("art") and images.get("ani")):
            problems.append("id %s images.art/ani missing" % pid)
    # ratings spread across the pool
    for k in TRAITS:
        vals = [p["ratings"][k] for p in profiles if isinstance(p.get("ratings", {}).get(k), int)]
        if vals:
            lo_share = sum(1 for v in vals if v <= -1) / len(vals)
            hi_share = sum(1 for v in vals if v >= 1) / len(vals)
            if lo_share < 0.30 or hi_share < 0.30:
                problems.append("trait %s spread: %.0f%% at <=-1, %.0f%% at >=1 (need >=30%% each)" %
                                 (k, lo_share * 100, hi_share * 100))
    # recompute vectors
    calc_profiles = [dict(id=p["id"], ratings=p["ratings"], auto_vector=p.get("auto_vector", [0] * 5))
                      for p in profiles if isinstance(p.get("ratings"), dict) and isinstance(p.get("auto_vector"), list)]
    vec_problems = 0
    if len(calc_profiles) == len(profiles) and profiles:
        profileVectors(calc_profiles)
        by_id = {p["id"]: p for p in calc_profiles}
        for p in profiles:
            calc = by_id.get(p["id"])
            stored = p.get("vector")
            if calc is None or not (isinstance(stored, list) and len(stored) == 5 and
                                     all(abs(a - b) <= 0.0001 for a, b in zip(calc["vector"], stored))):
                vec_problems += 1
        if vec_problems:
            problems.append("%d/%d profile vectors do not match profileVectors() recomputation" %
                             (vec_problems, len(profiles)))
    else:
        problems.append("could not recompute vectors: some profiles missing ratings/auto_vector")
    status = "FAIL" if problems else "PASS"
    scale = "" if len(profiles) >= 100 else " FIXTURE-SCALE: only %d profiles, pool-wide floors (126/60/42/25) not evaluated" % len(profiles)
    return R("A4", status, "%d profiles checked against pool.csv + swaps%s" % (len(profiles), scale),
              detail=problems[:12] or None)


def a5_why(pool, corpus):
    if pool is None:
        return skip("A5", "data/pool.json missing")
    profiles = pool.get("profiles", [])
    if not profiles:
        return R("A5", "FAIL", "no profiles to check")
    corpus_by_id = {}
    if corpus:
        corpus_by_id = {s["id"]: s for s in corpus.get("species", [])}
    seen_texts = {}
    problems = []
    for p in profiles:
        for w in p.get("why", []):
            norm = re.sub(r"\s+", " ", w.get("text", "").strip().lower())
            if norm in seen_texts and seen_texts[norm] != p["id"]:
                problems.append("why text reused between id %s and id %s: %r" % (seen_texts[norm], p["id"], norm[:60]))
            else:
                seen_texts[norm] = p["id"]
            anchor = (w.get("anchor") or "").lower()
            text = (w.get("text") or "").lower()
            if not anchor or anchor not in text:
                problems.append("id %s anchor %r not found in its own why.text" % (p["id"], anchor))
                continue
            hay = [p.get("genus", ""), p.get("name", "")]
            hay += [m.get("title", "") for m in p.get("media", [])]
            cs = corpus_by_id.get(p["id"])
            if cs:
                hay += cs.get("flavor_texts", []) + [cs.get("genus", "")]
            hay_l = " | ".join(hay).lower()
            if anchor not in hay_l:
                problems.append("id %s anchor %r not found in flavor_texts/genus/name/media" % (p["id"], anchor))
    status = "FAIL" if problems else "PASS"
    return R("A5", status, "%d why-sentence problems across %d profiles" % (len(problems), len(profiles)),
              detail=problems[:12] or None)


def a6_items(questions, pool_names=None):
    if questions is None:
        return skip("A6", "data/questions.json missing")
    items = questions.get("items", [])
    if not items:
        return R("A6", "FAIL", "questions.items is empty")
    problems, bits = [], []
    if len(items) != 15:
        bits.append("FIXTURE-SCALE: %d items, exact-15 MUST expected to fail here" % len(items))
    ids_expected = ["q%02d" % (i + 1) for i in range(len(items))]
    if [it.get("id") for it in items] != ids_expected:
        problems.append("ids are not q01..q%02d in order" % len(items))
    trait_cycle_ok = all(items[i].get("trait") == TRAITS[i % 5] for i in range(len(items)))
    if not trait_cycle_ok:
        problems.append("trait cycle O,C,E,A,S is not followed in id order")
    facets_by_trait = {}
    flavour_count = 0
    level3_positions = [0, 0, 0, 0]
    nonmonotone = 0
    names_l = set(n.lower() for n in (pool_names or [])) | {"pokémon", "pokemon"}
    for it in items:
        trait, facet = it.get("trait"), it.get("facet")
        facets_by_trait.setdefault(trait, set()).add(facet)
        if it.get("flavour"):
            flavour_count += 1
        answers = it.get("answers", [])
        levels = [a.get("level") for a in answers]
        if sorted(levels) != [-3, -1, 1, 3]:
            problems.append("%s answers levels != {-3,-1,1,3} once each: %r" % (it.get("id"), levels))
            continue
        pos3 = levels.index(3)
        level3_positions[pos3] += 1
        asc = all(levels[i] <= levels[i + 1] for i in range(3))
        desc = all(levels[i] >= levels[i + 1] for i in range(3))
        if not (asc or desc):
            nonmonotone += 1
        stem = it.get("stem", "")
        if len(stem.split()) > 16:
            problems.append("%s stem over 16 words" % it["id"])
        answer_texts = [a.get("text", "") for a in answers]
        lens = [len(t.split()) for t in answer_texts]
        if any(l > 10 for l in lens):
            problems.append("%s an answer is over 10 words" % it["id"])
        if lens and (max(lens) - min(lens)) > 4:
            problems.append("%s longest/shortest answer differ by more than 4 words" % it["id"])
        grade = fk_grade(stem, answer_texts)
        if grade > 4.0 + 1e-9:
            problems.append("%s Flesch-Kincaid grade %.2f > 4.0" % (it["id"], grade))
        for w in (stem.split() + [x for t in answer_texts for x in t.split()]):
            plain = re.sub(r"[^A-Za-zé]", "", w)
            if plain.lower() in names_l:
                continue
            if syllables(w) >= 4:
                problems.append("%s long word (4+ syllables): %r" % (it["id"], w))
        whole_text = " ".join([stem] + answer_texts)
        if TOPIC_RE.search(whole_text):
            problems.append("%s contains a D8 topic word: %s" % (it["id"], TOPIC_RE.search(whole_text).group(0)))
        if NEGATION_RE.search(whole_text):
            problems.append("%s contains negation" % it["id"])
        for a in answers:
            echo = a.get("echo", "")
            if not echo.lower().startswith("you"):
                problems.append("%s echo does not start with 'you': %r" % (it["id"], echo))
            if len(echo.split()) > 12:
                problems.append("%s echo over 12 words" % it["id"])
            if NEGATION_RE.search(echo):
                problems.append("%s echo contains negation" % it["id"])
        if it.get("source_instrument") != "IPIP" or not it.get("source_item") or it.get("source_key") not in ("+", "-"):
            problems.append("%s IPIP source fields incomplete" % it["id"])
    for trait, facets in facets_by_trait.items():
        if trait in REQUIRED_Q1_FACETS and len(facets) < min(3, len(REQUIRED_Q1_FACETS[trait])):
            problems.append("trait %s items do not sample 3 different facets: %s" % (trait, facets))
    if flavour_count > 4:
        problems.append("%d flavoured stems, at most 4 allowed" % flavour_count)
    if len(items) == 15:
        if sum(1 for c in level3_positions if c >= 3) < 4:
            problems.append("D5 position balance: level-3 answer does not appear >=3x in each of the 4 positions: %s" % level3_positions)
        if nonmonotone < 10:
            problems.append("D5: only %d/%d items are non-monotone (need >=10)" % (nonmonotone, len(items)))
    else:
        bits.append("FIXTURE-SCALE: D5 position-balance/non-monotone counts (%s, nonmonotone=%d) not evaluated against pool-wide floors" %
                     (level3_positions, nonmonotone))
    status = "FAIL" if problems else "PASS"
    return R("A6", status, "; ".join(bits) or ("%d items checked" % len(items)), detail=problems[:15] or None)


def a7_takers(questions):
    if questions is None:
        return skip("A7", "data/questions.json missing")
    takers = questions.get("takers", [])
    ok = takers == Q7_TAKERS
    detail = None
    if not ok:
        detail = ["got: %r" % takers, "want: %r" % Q7_TAKERS]
    return R("A7", "PASS" if ok else "FAIL", "takers list equals Q7 table exactly" if ok else "takers list differs from Q7 table", detail=detail)


def a8_images(pool, web_dir):
    if pool is None:
        return skip("A8", "data/pool.json missing")
    profiles = pool.get("profiles", [])
    if not profiles:
        return R("A8", "FAIL", "no profiles to check")
    try:
        from PIL import Image
    except ImportError:
        return skip("A8", "Pillow not importable")
    problems, fallback_count = [], 0
    for p in profiles:
        images = p.get("images", {})
        art_path = web_dir / images.get("art", "___missing___")
        ani_path = web_dir / images.get("ani", "___missing___")
        if not art_path.exists():
            problems.append("id %s art missing: %s" % (p["id"], art_path))
        else:
            try:
                with Image.open(art_path) as im:
                    if im.format != "PNG":
                        problems.append("id %s art is not a PNG (%s)" % (p["id"], im.format))
            except Exception as e:
                problems.append("id %s art unreadable: %s" % (p["id"], e))
        if images.get("ani_static_fallback"):
            fallback_count += 1
            expect_fmt = "PNG"
        else:
            expect_fmt = "GIF"
        if not ani_path.exists():
            problems.append("id %s ani missing: %s" % (p["id"], ani_path))
        else:
            try:
                with Image.open(ani_path) as im:
                    if im.format != expect_fmt:
                        problems.append("id %s ani is %s, expected %s" % (p["id"], im.format, expect_fmt))
            except Exception as e:
                problems.append("id %s ani unreadable: %s" % (p["id"], e))
    status = "FAIL" if problems else "PASS"
    return R("A8", status, "%d image problems across %d profiles. REPORT: %d static fallbacks" %
              (len(problems), len(profiles), fallback_count),
              detail=problems[:12] or None)


def find_node():
    import shutil
    return shutil.which("node")


def a9_cross_language(profiles_for_test, node_path, app_js_path, seed, tmp_dir):
    if node_path is None:
        return skip("A9", "node not found on PATH")
    if app_js_path is None or not Path(app_js_path).exists():
        return skip("A9", "app.js not found at %s" % app_js_path)
    if not profiles_for_test:
        return skip("A9", "no usable pool profiles yet (data/pool.json missing or not all profiles have a vector/lean/stage)")
    rng = np.random.default_rng(seed)
    items = synthetic_items()
    flat_taker_keys, flat_t, py_ids = [], [], []
    for taker in Q7_TAKERS:
        n = 1000
        choices = rng.integers(0, 4, size=(n, 15))
        for row in choices:
            t = takerVector(items, [int(x) for x in row])
            wid = match(t, taker, profiles_for_test)
            flat_taker_keys.append(taker["key"])
            flat_t.append(t)
            py_ids.append(wid)
    node_input = {"profiles": profiles_for_test,
                  "cases": [{"t": t, "taker": next(tk for tk in Q7_TAKERS if tk["key"] == k)}
                            for t, k in zip(flat_t, flat_taker_keys)]}
    input_path = tmp_dir / "a9_input.json"
    input_path.write_text(json.dumps(node_input), encoding="utf-8")
    harness_path = tmp_dir / "a9_harness.mjs"
    harness_path.write_text(A9_HARNESS_JS, encoding="utf-8")
    try:
        proc = subprocess.run([node_path, str(harness_path), str(Path(app_js_path).resolve()), str(input_path)],
                               capture_output=True, text=True, timeout=120)
    except Exception as e:
        return skip("A9", "node harness failed to run: %s" % e)
    if proc.returncode != 0:
        return skip("A9", "node harness exited %d: %s" % (proc.returncode, (proc.stderr or proc.stdout)[:400]))
    try:
        js_ids = json.loads(proc.stdout)
    except Exception:
        return skip("A9", "node harness did not print JSON: %s" % proc.stdout[:400])
    if isinstance(js_ids, dict) and js_ids.get("error"):
        return skip("A9", "node harness: %s" % js_ids["error"])
    if len(js_ids) != len(py_ids):
        return R("A9", "FAIL", "node returned %d winners, expected %d" % (len(js_ids), len(py_ids)))
    disagreements = [(k, a, b) for k, a, b in zip(flat_taker_keys, py_ids, js_ids) if a != b]
    # determinism: recompute python twice on a slice, and re-invoke node on a slice
    det_py_ok = py_ids[:20] == [match(t, next(tk for tk in Q7_TAKERS if tk["key"] == k), profiles_for_test)
                                  for t, k in zip(flat_t[:20], flat_taker_keys[:20])]
    status = "PASS" if not disagreements and det_py_ok else "FAIL"
    detail = None
    if disagreements:
        detail = ["seed=%d first 5 disagreements (taker, python_id, js_id): %s" % (seed, disagreements[:5])]
    return R("A9", status, "python/js match() agreement on %d cases (10 takers x 1000), seed=%d: %d disagreements; determinism %s" %
              (len(py_ids), seed, len(disagreements), "OK" if det_py_ok else "BROKEN"), detail=detail)


A9_HARNESS_JS = r"""
import { pathToFileURL } from 'node:url';
import fs from 'node:fs';
import vm from 'node:vm';

const [, , appPathArg, inputPathArg] = process.argv;

async function resolveMatchFn() {
  try {
    const mod = await import(pathToFileURL(appPathArg).href);
    if (typeof mod.match === 'function') return mod.match;
    if (mod.default && typeof mod.default.match === 'function') return mod.default.match;
  } catch (e) {
    // fall through to vm attempt
  }
  try {
    const src = fs.readFileSync(appPathArg, 'utf8');
    const sandbox = { console, module: { exports: {} }, exports: {} };
    vm.createContext(sandbox);
    vm.runInContext(src, sandbox, { timeout: 10000 });
    if (typeof sandbox.match === 'function') return sandbox.match;
    if (sandbox.module.exports && typeof sandbox.module.exports.match === 'function') return sandbox.module.exports.match;
  } catch (e) {
    console.log(JSON.stringify({ error: 'vm fallback failed: ' + String(e) }));
    process.exit(3);
  }
  return null;
}

const matchFn = await resolveMatchFn();
if (typeof matchFn !== 'function') {
  console.log(JSON.stringify({ error: 'no match() export or global found in app.js' }));
  process.exit(3);
}
const input = JSON.parse(fs.readFileSync(inputPathArg, 'utf8'));
const out = input.cases.map(c => matchFn(c.t, c.taker, input.profiles));
console.log(JSON.stringify(out));
"""


def nearest_distances_np(t_batch, pool_vec, chunk=4000):
    M = t_batch.shape[0]
    out = np.empty(M)
    for start in range(0, M, chunk):
        chunk_t = t_batch[start:start + chunk]
        diff = chunk_t[:, None, :] - pool_vec[None, :, :]
        dist = np.sqrt((diff ** 2).sum(axis=2))
        out[start:start + chunk_t.shape[0]] = dist.min(axis=1)
    return out


def a10_coverage(pool_vec, seed):
    if pool_vec is None or len(pool_vec) == 0:
        return skip("A10", "no pool vectors available")
    latt = lattice_vectors()
    d_latt = nearest_distances_np(latt, pool_vec)
    max_d, p95_latt = float(d_latt.max()), float(np.percentile(d_latt, 95))
    rng = np.random.default_rng(seed)
    rand_t = random_taker_vectors(rng, 20000)
    d_rand = nearest_distances_np(rand_t, pool_vec)
    p95_rand = float(np.percentile(d_rand, 95))
    n = len(pool_vec)
    evaluate = n >= 100
    problems = []
    if evaluate:
        if max_d > 1.60 + 1e-9:
            problems.append("lattice max %.3f > 1.60" % max_d)
        if p95_latt > 1.00 + 1e-9:
            problems.append("lattice p95 %.3f > 1.00" % p95_latt)
        if p95_rand > 0.75 + 1e-9:
            problems.append("random(20000) p95 %.3f > 0.75" % p95_rand)
    status = ("FAIL" if problems else "PASS") if evaluate else "REPORT"
    scale = "" if evaluate else " FIXTURE-SCALE (%d members): thresholds not evaluated, numbers only" % n
    return R("A10", status, "seed=%d lattice max=%.3f p95=%.3f; random(20000,seed=%d) p95=%.3f%s" %
              (seed, max_d, p95_latt, seed, p95_rand, scale), must=evaluate, detail=problems or None)


def a11_reachability(profiles, pool_vec, pool_ids, pool_leans, pool_stages):
    if not profiles:
        return skip("A11", "no pool profiles available")
    latt = lattice_vectors()
    reach = {}
    for taker in Q7_TAKERS:
        wids, _ = winners_for_vectors_np(latt, taker, pool_vec, pool_ids, pool_leans, pool_stages)
        reach[taker["key"]] = len(set(wids.tolist()))
    n = len(pool_ids)
    evaluate = n >= 60
    problems = []
    if evaluate:
        if reach["guest"] < n:
            problems.append("guest reaches %d/%d members, needs all" % (reach["guest"], n))
        for taker in Q7_TAKERS:
            if taker["key"] != "guest" and reach[taker["key"]] < 60:
                problems.append("%s reaches only %d members, needs >=60" % (taker["key"], reach[taker["key"]]))
    status = ("FAIL" if problems else "PASS") if evaluate else "REPORT"
    scale = "" if evaluate else " FIXTURE-SCALE (%d members): >=60/all thresholds not evaluated" % n
    return R("A11", status, "lattice reach counts: %s%s" % (reach, scale), must=evaluate, detail=problems or None)


def a12_concentration(profiles, pool_vec, pool_ids, pool_leans, pool_stages, seed):
    if not profiles:
        return skip("A12", "no pool profiles available")
    rng = np.random.default_rng(seed)
    rand_t = random_taker_vectors(rng, 20000)
    n = len(pool_ids)
    problems, shares = [], {}
    for taker in Q7_TAKERS:
        wids, _ = winners_for_vectors_np(rand_t, taker, pool_vec, pool_ids, pool_leans, pool_stages)
        vals, counts = np.unique(wids, return_counts=True)
        top_share = float(counts.max()) / len(wids)
        shares[taker["key"]] = round(top_share * 100, 2)
        limit = 0.06 if taker["key"] == "guest" else 0.16
        if n >= 60 and top_share > limit + 1e-9:
            problems.append("%s top member share %.2f%% > %.0f%%" % (taker["key"], top_share * 100, limit * 100))
    evaluate = n >= 60
    status = ("FAIL" if problems else "PASS") if evaluate else "REPORT"
    scale = "" if evaluate else " FIXTURE-SCALE (%d members): 6%%/16%% caps not evaluated" % n
    return R("A12", status, "seed=%d top-member share per taker (pct): %s%s" % (seed, shares, scale),
              must=evaluate, detail=problems or None)


def scan_web_lean_lines(web_dir):
    """Every line under web_dir (js/mjs/json/html) that contains '.lean' or 'lean:' or a JSON '"lean"'
    key -- the property/key, never the prose phrase 'Your answers lean most toward'. Returns
    (relpath, lineno, line) tuples. Ground truth is the raw file text; this is exact substring/regex
    matching, not a heuristic."""
    hits = []
    if not web_dir.exists():
        return hits
    for path in sorted(web_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in (".js", ".mjs", ".json", ".html"):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if "lean most toward" in line.lower():
                continue
            if (".lean" in line) or ("lean:" in line.lower()) or ('"lean"' in line):
                hits.append((str(path.relative_to(web_dir.parent)), i, line.strip()[:160]))
    return hits


def lean_line_is_ok(line):
    """A13: each flagged line MUST be the leanPenalty call/definition in match(), or a taker row whose
    lean is null. Anything else (e.g. a profile literal carrying a real lean value) is a violation."""
    low = line.lower()
    if "leanpenalty" in low:
        return True
    if re.search(r'"lean"\s*:\s*null', low) or re.search(r"\blean\s*:\s*null\b", low):
        return True
    return False


def visible_text(html):
    """Crude visible-text extractor: drop <script>/<style> bodies, then all remaining tags. A16/A13 use
    this for word scans that must not fire on markup or script identifiers; it is not a DOM renderer."""
    html = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<style.*?</style>", " ", html, flags=re.S | re.I)
    return re.sub(r"<[^>]+>", " ", html)


def scan_storage_for_lean_gender(web_dir):
    """HEURISTIC: a regex over localStorage/sessionStorage/document.cookie call sites looking for 'lean'
    or 'gender' nearby on the same line. Cannot see runtime values, only source text; a SKIP-free empty
    result here is not proof nothing is ever stored, only that no such call SITE mentions those words."""
    hits = []
    if not web_dir.exists():
        return hits
    for path in web_dir.rglob("*.js"):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in STORAGE_CALL_RE.finditer(text):
            snippet = m.group(0)
            if re.search(r"lean|gender", snippet, re.I):
                hits.append((str(path.relative_to(web_dir.parent)), snippet[:150]))
    return hits


def run_node_match_once(node_path, app_js_path, node_input, tmp_dir, tag):
    """Minimal one-shot invocation of the A9 node harness for a small, explicit case list (used by A13's
    transcription-fidelity check, not the bulk A9 agreement run)."""
    input_path = tmp_dir / ("%s_input.json" % tag)
    input_path.write_text(json.dumps(node_input), encoding="utf-8")
    harness_path = tmp_dir / ("%s_harness.mjs" % tag)
    harness_path.write_text(A9_HARNESS_JS, encoding="utf-8")
    proc = subprocess.run([node_path, str(harness_path), str(Path(app_js_path).resolve()), str(input_path)],
                           capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError("node exited %d: %s" % (proc.returncode, (proc.stderr or proc.stdout)[:300]))
    out = json.loads(proc.stdout)
    if isinstance(out, dict) and out.get("error"):
        raise RuntimeError(out["error"])
    return out


def a13_lean(profiles, pool_vec, pool_ids, pool_leans, pool_stages, questions, web_dir, node_path,
             app_js_path, seed, tmp_dir):
    """Rewritten 2026-09-27 (CONTRACT.md A13, amendment 4): lean is void. Every taker's lean MUST be
    null, stubbing leanPenalty to 0 MUST change no winner, no pool data under web/ MUST carry a lean
    field, and web/index.html's visible text MUST carry no gender word. Four independent checks, all
    MUST, combined into one assertion because they are all "is lean really gone" questions."""
    problems = []

    # ---- (1) transcription-fidelity unit case. Every real taker.lean is null now, so leanPenalty is
    # dead code in production and neither A9 nor a real-data run can exercise LEAN_OPPOSITE/NEUTRAL/SAME
    # by accident (this is exactly why the known-bad fixture's changed LEAN_OPPOSITE would otherwise slip
    # through unnoticed post-amendment). This calls match() directly with a synthetic NON-null-lean taker
    # to prove the constants are still transcribed correctly, in Python and -- if node/app.js are present
    # -- in the app's own JavaScript.
    taker_unit = {"lean": "feminine", "stage_target": "evolved", "stage_weight": 0}

    def unit_case_py(same_dist):
        t = [0, 0, 0, 0, 0]
        opp = {"id": 1, "vector": [0, 0, 0, 0, 0], "lean": "masculine", "stage": "evolved"}
        same = {"id": 2, "vector": [same_dist, 0, 0, 0, 0], "lean": "feminine", "stage": "evolved"}
        return match(t, taker_unit, [opp, same])

    u_024, u_026 = unit_case_py(0.24), unit_case_py(0.26)
    unit_ok = (u_024 == 2) and (u_026 == 1)
    if not unit_ok:
        problems.append("python leanPenalty transcription unit case failed: dist 0.24 winner=%s (want 2), "
                         "dist 0.26 winner=%s (want 1)" % (u_024, u_026))

    js_unit_note = "SKIPPED (node or app.js not available)"
    if node_path and app_js_path and Path(app_js_path).exists():
        base_profiles = [{"id": 1, "vector": [0, 0, 0, 0, 0], "lean": "masculine", "stage": "evolved"},
                          {"id": 2, "vector": [0.24, 0, 0, 0, 0], "lean": "feminine", "stage": "evolved"}]
        case_024 = {"profiles": base_profiles, "cases": [{"t": [0, 0, 0, 0, 0], "taker": taker_unit}]}
        case_026 = json.loads(json.dumps(case_024))
        case_026["profiles"][1]["vector"][0] = 0.26
        try:
            js_024 = run_node_match_once(node_path, app_js_path, case_024, tmp_dir, "a13_024")
            js_026 = run_node_match_once(node_path, app_js_path, case_026, tmp_dir, "a13_026")
            if js_024 == [2] and js_026 == [1]:
                js_unit_note = "OK (matches python: 0.24->2, 0.26->1)"
            else:
                js_unit_note = "MISMATCH: got %r/%r, want [2]/[1]" % (js_024, js_026)
                problems.append("JS leanPenalty transcription unit case: %s" % js_unit_note)
        except Exception as e:
            js_unit_note = "node harness error: %s" % e

    # ---- (2) every taker's lean is null, in data/questions.json and in this check's own Q7 copy.
    non_null_q = []
    if questions is not None:
        non_null_q = [t.get("key") for t in questions.get("takers", []) if t.get("lean") is not None]
        if non_null_q:
            problems.append("data/questions.json takers with non-null lean: %s" % non_null_q)
    non_null_const = [t["key"] for t in Q7_TAKERS if t["lean"] is not None]
    if non_null_const:
        problems.append("check.py's own Q7_TAKERS copy has non-null lean (fix the check): %s" % non_null_const)

    # ---- (3) over 20,000 random draws for every taker, match() with the real (but, per (2), always-null-
    # taker-lean) leanPenalty gives the same winner as a copy of match() whose leanPenalty is stubbed to
    # return 0 unconditionally. Vectorised the same way as A10-A14's other simulations.
    stub_note = "SKIPPED, no real pool profiles available"
    if profiles and pool_vec is not None and len(pool_vec):
        rng = np.random.default_rng(seed)
        n_draws = 20000
        rand_t = random_taker_vectors(rng, n_draws)
        ids_arr = np.array(pool_ids)
        stage_idx_pool = np.array([STAGE_INDEX[s] for s in pool_stages])
        per_taker_mismatch, total_mismatch = {}, 0
        for taker in Q7_TAKERS:
            real_ids, _ = winners_for_vectors_np(rand_t, taker, pool_vec, pool_ids, pool_leans, pool_stages)
            stage_pen = taker["stage_weight"] * np.abs(stage_idx_pool - STAGE_INDEX[taker["stage_target"]])
            stub_ids = np.empty(n_draws, dtype=np.int64)
            for start in range(0, n_draws, 4000):
                chunk_t = rand_t[start:start + 4000]
                diff = chunk_t[:, None, :] - pool_vec[None, :, :]
                dist = np.sqrt((diff ** 2).sum(axis=2))
                keys = round6_np(dist + stage_pen[None, :])  # leanPenalty stubbed to 0, term omitted entirely
                min_key = keys.min(axis=1)
                is_min = keys == min_key[:, None]
                masked = np.where(is_min, ids_arr[None, :], np.iinfo(np.int64).max)
                stub_ids[start:start + chunk_t.shape[0]] = masked.min(axis=1)
            mism = int((real_ids != stub_ids).sum())
            per_taker_mismatch[taker["key"]] = mism
            total_mismatch += mism
        if total_mismatch:
            problems.append("real match() vs leanPenalty-stubbed-to-0 match() disagree on %d/%d draws: %s" %
                             (total_mismatch, n_draws * len(Q7_TAKERS), per_taker_mismatch))
            stub_note = "MISMATCH: %s" % per_taker_mismatch
        else:
            stub_note = "OK: 0 disagreements over %d draws x %d takers" % (n_draws, len(Q7_TAKERS))

    # ---- (4) web/ carries no lean field on pool data, no gender word in index.html's visible text, and
    # (heuristic) writes nothing lean/gender-shaped to storage.
    web_bits = []
    if web_dir.exists():
        lean_lines = scan_web_lean_lines(web_dir)
        bad_lines = [(f, n, l) for f, n, l in lean_lines if not lean_line_is_ok(l)]
        if bad_lines:
            problems.append("%d line(s) under web/ mention .lean/lean:/\"lean\" outside leanPenalty() or a "
                             "null taker row: %s" % (len(bad_lines), bad_lines[:8]))
        web_bits.append("%d lean-mentioning line(s) under web/, %d flagged" % (len(lean_lines), len(bad_lines)))

        idx_html = web_dir / "index.html"
        if idx_html.exists():
            html_text = idx_html.read_text(encoding="utf-8", errors="ignore")
            gender_hits = sorted(set(m.group(0).lower() for m in GENDER_WORDS_RE.finditer(visible_text(html_text))))
            if gender_hits:
                problems.append("web/index.html visible text contains gender word(s): %s" % gender_hits)
            web_bits.append("index.html gender-word scan: %s" % (gender_hits or "clean"))
        else:
            web_bits.append("web/index.html not present yet")

        storage_hits = scan_storage_for_lean_gender(web_dir)
        if storage_hits:
            problems.append("HEURISTIC (SUSPECTED, source-text regex only): possible lean/gender written "
                             "to storage: %s" % storage_hits[:5])
        web_bits.append("storage-write heuristic scan: %d hit(s)" % len(storage_hits))
    else:
        web_bits.append("web/ not present yet")

    status = "FAIL" if problems else "PASS"
    summary = ("unit-case py=%s js=%s; questions-null-lean=%s check-const-null-lean=%s; "
               "stub-vs-real(20000x10)=%s; web: %s" % (
                   "OK" if unit_ok else "BROKEN", js_unit_note,
                   "OK" if not non_null_q else "BAD:%s" % non_null_q,
                   "OK" if not non_null_const else "BAD:%s" % non_null_const,
                   stub_note, "; ".join(web_bits)))
    return R("A13", status, summary, must=True, detail=problems[:15] or None)


def a14_stage(profiles, pool_vec, pool_ids, pool_leans, pool_stages, seed):
    if not profiles:
        return skip("A14", "no pool profiles available")
    rng = np.random.default_rng(seed)
    rand_t = random_taker_vectors(rng, 20000)
    n = len(pool_ids)
    id_to_stage = dict(zip(pool_ids, pool_stages))
    problems, shares = {}, {}
    for key, want_stage, min_share in (("todd", "young", 0.40), ("milo", "young", 0.40),
                                        ("carolyn", "mature", 0.40), ("john", "mature", 0.40)):
        taker = next(t for t in Q7_TAKERS if t["key"] == key)
        wids, _ = winners_for_vectors_np(rand_t, taker, pool_vec, pool_ids, pool_leans, pool_stages)
        result_stages = np.array([id_to_stage[i] for i in wids])
        share = float((result_stages == want_stage).mean())
        shares[key] = share
        if n >= 40 and share < min_share - 1e-9:
            problems.setdefault("fail", []).append("%s %s-share %.3f < %.0f%%" % (key, want_stage, share, min_share * 100))
    evaluate = n >= 40
    fails = problems.get("fail", [])
    status = ("FAIL" if fails else "PASS") if evaluate else "REPORT"
    scale = "" if evaluate else " FIXTURE-SCALE (%d members): 40%% thresholds not evaluated" % n
    return R("A14", status, "seed=%d target-stage share: %s%s" %
              (seed, {k: round(v * 100, 2) for k, v in shares.items()}, scale), must=evaluate, detail=fails or None)


def a15_result_text(profiles, questions, seed):
    if not profiles:
        return skip("A15", "no pool profiles available")
    items = questions.get("items") if questions else None
    if not items or len(items) != 15:
        items = synthetic_items()
        note = " (synthetic 15-item shape; data/questions.json not ready or not 15 items)"
    else:
        note = ""
    rng = np.random.default_rng(seed)
    problems, checked = [], 0
    for taker in Q7_TAKERS:
        for _ in range(200):  # 200 x 10 takers = 2000, matches the contract's 2,000-draw spec
            choice = rng.integers(0, 4, size=len(items)).tolist()
            t = takerVector(items, choice)
            member_id = match(t, taker, profiles)
            member = next(p for p in profiles if p["id"] == member_id)
            scored = []
            for i, it in enumerate(items):
                level = it["answers"][choice[i]]["level"]
                k = TRAITS.index(it["trait"])
                align = (level / 3.0) * member["vector"][k]
                scored.append((align, abs(level), i, level, it["trait"], it["answers"][choice[i]].get("echo", "")))
            scored.sort(key=lambda x: (-x[0], -x[1], x[2]))
            c1 = scored[0]
            c2 = next((s for s in scored[1:] if s[4] != c1[4]), None)
            if c2 is None:
                continue
            echo1, echo2 = c1[5], c2[5]
            line_a = "You said %s, and %s." % (echo1, echo2)
            why_pool = member.get("why", [])
            ordered = [w for w in why_pool if w.get("trait") == c1[4]] + \
                      [w for w in why_pool if w.get("trait") == c2[4] and w.get("trait") != c1[4]] + \
                      [w for w in why_pool if w.get("trait") not in (c1[4], c2[4])]
            seen_txt, lines_b = set(), []
            for w in ordered:
                if w["text"] not in seen_txt:
                    lines_b.append(w["text"])
                    seen_txt.add(w["text"])
                if len(lines_b) == 3:
                    break
            k_star = max(range(5), key=lambda k: (abs(t[k]), -k))
            block_text = " ".join([line_a] + lines_b)
            checked += 1
            if echo1 not in block_text or echo2 not in block_text:
                problems.append("echoes not verbatim in block (taker %s)" % taker["key"])
            if len(block_text.split()) > 110:
                problems.append("block over 110 words (taker %s)" % taker["key"])
            low = block_text.lower()
            for w in Q6_BANNED_WORDS:
                if re.search(r"\b" + re.escape(w) + r"\b", low):
                    problems.append("banned word %r (taker %s)" % (w, taker["key"]))
            for fr in BANNED_FRAMINGS:
                if fr in low:
                    problems.append("banned framing %r (taker %s)" % (fr, taker["key"]))
            for bl in BARNUM_LINES:
                if bl in low:
                    problems.append("Barnum line %r (taker %s)" % (bl, taker["key"]))
            if DASH_RE.search(block_text):
                problems.append("em/en dash in block (taker %s)" % taker["key"])
            for w in Q6_SCREEN_WORDS:  # amendment 2026-09-27: a species-turned-on-the-taker word
                if re.search(r"\b" + re.escape(w) + r"\b", low):
                    problems.append("Q6 screen word %r in block (taker %s)" % (w, taker["key"]))
    status = "FAIL" if problems else "PASS"
    return R("A15", status, "seed=%d result-text checks over %d draws%s: %d problems" %
              (seed, checked, note, len(problems)), detail=list(dict.fromkeys(problems))[:12] or None)


def extract_how_it_works(html_text):
    """HEURISTIC extractor: find the first 'how it works' occurrence, take the HTML up to the next
    closing container / heading tag (or a 4000-char cap), strip tags, and drop the heading phrase
    itself. The real toggle markup was not known at build time, so this cannot be a DOM-exact reader;
    a None return or an odd word count is a prompt for the panelist to look at the actual page, not
    proof the toggle is missing."""
    idx = html_text.lower().find("how it works")
    if idx == -1:
        return None
    rest = html_text[idx:]
    end = len(rest)
    for marker in ("</details>", "</section>", "<h1", "<h2", "<h3"):
        pos = rest.lower().find(marker, len("how it works"))
        if pos != -1:
            end = min(end, pos)
    end = min(end, 4000)
    block_html = rest[:end]
    text = re.sub(r"<[^>]+>", " ", block_html)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^how it works\W*", "", text, flags=re.I).strip()
    return text, block_html


def a16_prose(questions, pool, web_dir, tmp_dir):
    texts = []
    if questions:
        for it in questions.get("items", []):
            texts.append(it.get("stem", ""))
            for a in it.get("answers", []):
                texts.append(a.get("text", ""))
                texts.append(a.get("echo", ""))
    profile_texts = []
    if pool:
        for p in pool.get("profiles", []):
            profile_texts.append(p.get("personality", ""))
            profile_texts.append(p.get("community", ""))
            for m in p.get("media", []):
                profile_texts.append(m.get("note", ""))
            for w in p.get("why", []):
                profile_texts.append(w.get("text", ""))
    texts += profile_texts
    html_path = web_dir / "index.html"
    if not texts and not html_path.exists():
        return skip("A16", "no human-read strings yet (questions.json, pool.json, web/index.html all missing)")
    txt_path = tmp_dir / "a16_strings.txt"
    txt_path.write_text("\n\n".join(t for t in texts if t), encoding="utf-8")
    targets = [str(txt_path)]
    if html_path.exists():
        targets.append(str(html_path))
    prose_check_path = Path("C:/Users/joshu/demandscan/bids/samples/tools/prose_check.py")
    if not prose_check_path.exists():
        return skip("A16", "prose_check.py not found at %s" % prose_check_path)
    proc = subprocess.run([sys.executable, str(prose_check_path)] + targets, capture_output=True, text=True, timeout=60)
    out = proc.stdout
    banned_total = sum(int(m) for m in re.findall(r"banned (\d+)", out))
    em_total = sum(int(m) for m in re.findall(r"em-dashes (\d+)", out))
    negpar_total = sum(int(m) for m in re.findall(r"neg-parallel (\d+)", out))
    combined = "\n".join(t for t in texts if t)
    html_text = None
    if html_path.exists():
        html_text = html_path.read_text(encoding="utf-8", errors="ignore")
        combined += "\n" + html_text
    q6_hits = sorted({w for w in Q6_BANNED_WORDS if re.search(r"\b" + re.escape(w) + r"\b", combined, re.I)})
    # amendment 2026-09-27: the new Q6 screen-word list, checked against PROFILE strings only (item
    # stems/echoes are covered separately in A6/A15's own word lists; the contract names profile
    # personality/community/media-note/why text specifically for this list).
    combined_profile = "\n".join(t for t in profile_texts if t)
    q6_screen_hits = sorted({w for w in Q6_SCREEN_WORDS
                              if re.search(r"\b" + re.escape(w) + r"\b", combined_profile, re.I)})
    problems = []
    if em_total:
        problems.append("%d em/en dash occurrences (prose_check)" % em_total)
    if banned_total:
        problems.append("%d prose_check banned-word hits" % banned_total)
    if negpar_total:
        problems.append("%d 'not X but Y' shapes" % negpar_total)
    if q6_hits:
        problems.append("Q6-specific banned words prose_check does not carry: %s" % q6_hits)
    if q6_screen_hits:
        problems.append("Q6 screen words present in profile personality/community/media/why text: %s" % q6_screen_hits)

    # amendment 2026-09-27 (ruling 11): the How it works text, HEURISTIC extraction from index.html.
    how_bits = ["how-it-works: not found in web/index.html yet"]
    if html_text is not None:
        extracted = extract_how_it_works(html_text)
        if extracted is None:
            problems.append("web/index.html has no \"How it works\" text yet")
        else:
            hiw_text, hiw_html = extracted
            n_words = len(hiw_text.split())
            how_bits = ["how-it-works HEURISTIC extract: %d words" % n_words]
            if n_words == 0:
                problems.append("How it works text extracted empty (HEURISTIC extractor -- verify by eye)")
            elif n_words > 90:
                problems.append("How it works text is %d words, over the 90-word cap (HEURISTIC extract, "
                                 "verify by eye)" % n_words)
            if "big five" not in hiw_text.lower():
                problems.append("How it works text does not contain \"Big Five\"")
            if not re.search(r"\b15\b", hiw_text):
                problems.append("How it works text does not contain \"15\"")
            if not RESEARCH_NOTE_URL_RE.search(hiw_html):
                problems.append("How it works text/link does not link spec/RESEARCH-PERSONALITY.md on GitHub")
            meas_hits = sorted({w for w in MEASUREMENT_WORDS
                                 if re.search(r"\b" + re.escape(w) + r"\b", hiw_text, re.I)})
            if SCIENCE_SAYS_RE.search(hiw_text):
                meas_hits.append("science says")
            if meas_hits:
                problems.append("How it works text contains measurement-claim word(s): %s" % meas_hits)
    status = "FAIL" if problems else "PASS"
    return R("A16", status, "prose_check.py over %d strings%s: em-dashes/banned/neg-parallel must be 0; %s" %
              (len(texts), " + index.html" if html_path.exists() else "", "; ".join(how_bits)),
              detail=(problems + [out[:1200]]) if problems else None)


def a17_retest(profiles, seed):
    if not profiles:
        return skip("A17", "no pool profiles available", must=False)
    rng = np.random.default_rng(seed)
    items = synthetic_items()
    guest = next(t for t in Q7_TAKERS if t["key"] == "guest")
    n, same, top3 = 2000, 0, 0
    for _ in range(n):
        choice = rng.integers(0, 4, size=15)
        t0 = takerVector(items, choice.tolist())
        keyed = sorted(profiles, key=lambda p: (
            round6(math.sqrt(sum((t0[k] - p["vector"][k]) ** 2 for k in range(5))) +
                   leanPenalty(guest["lean"], p["lean"]) + stagePenalty(guest, p["stage"])), p["id"]))
        top3_ids = {keyed[i]["id"] for i in range(min(3, len(keyed)))}
        w0 = keyed[0]["id"]
        choice2 = choice.copy()
        for i in range(15):
            if rng.random() < 0.3:
                step = 1 if rng.random() < 0.5 else -1
                nv = int(choice2[i]) + step
                if nv < 0:
                    nv = 1
                if nv > 3:
                    nv = 2
                choice2[i] = nv
        t1 = takerVector(items, choice2.tolist())
        w1 = match(t1, guest, profiles)
        if w1 == w0:
            same += 1
        if w1 in top3_ids:
            top3 += 1
    return R("A17", "REPORT", "seed=%d guest retest over %d draws (synthetic item shape): same-Pokemon %.1f%%, "
              "in-original-top-3 %.1f%% -- report only, no pass mark" % (seed, n, 100 * same / n, 100 * top3 / n), must=False)


def a18_live(base_url, do_skip, tmp_dir):
    if do_skip:
        return skip("A18", "--skip-a18 set")
    import urllib.request
    try:
        req = urllib.request.Request(base_url, headers={"User-Agent": "which-pokemon-check/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html_text = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return skip("A18", "could not fetch %s: %s" % (base_url, e))
    has_og_title = re.search(r'property=["\']og:title["\']', html_text) is not None
    has_og_image = re.search(r'property=["\']og:image["\']', html_text) is not None
    problems = []
    if not has_og_title:
        problems.append("missing og:title meta tag")
    if not has_og_image:
        problems.append("missing og:image meta tag")
    shots_done, heuristic_notes = [], []
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for taker_name in ["Milo", "Alex", "Someone else"]:
                ctx = browser.new_context(viewport={"width": 390, "height": 844})
                page = ctx.new_page()
                try:
                    page.goto(base_url, timeout=20000)
                    page.get_by_text(taker_name, exact=False).first.click(timeout=5000)
                    for _ in range(15):
                        page.locator("button, [role=button], a").first.click(timeout=5000)
                        page.wait_for_timeout(150)
                    shot = tmp_dir / ("a18-%s.png" % taker_name.replace(" ", "_"))
                    page.screenshot(path=str(shot))
                    shots_done.append(str(shot))
                except Exception as e:
                    heuristic_notes.append("HEURISTIC (SUSPECTED): flow for %s did not complete: %s" % (taker_name, str(e)[:150]))
                ctx.close()
            browser.close()
    except Exception as e:
        heuristic_notes.append("HEURISTIC (SUSPECTED): playwright run failed: %s" % str(e)[:200])
    status = "FAIL" if (not has_og_title or not has_og_image) else ("REPORT" if heuristic_notes else "PASS")
    return R("A18", status, "OG tags: title=%s image=%s. %d/3 heuristic mobile playthroughs completed (SUSPECTED not CONFIRMED)." %
              (has_og_title, has_og_image, len(shots_done)), must=True, detail=(problems + heuristic_notes) or None)


def a19_calibration():
    good = [
        {"id": 1, "name": "A", "genus": "Calm Test Pokemon", "lean": "neutral", "stage": "young",
         "ratings": {"O": 0, "C": 0, "E": 0, "A": 0, "S": 0}, "auto_vector": [0, 0, 0, 0, 0],
         "why": [{"text": "It is calm and steady in tests.", "trait": "S", "anchor": "calm"}],
         "media": [{"title": "Test show"}]},
        {"id": 2, "name": "B", "genus": "Curious Test Pokemon", "lean": "neutral", "stage": "young",
         "ratings": {"O": 0, "C": 0, "E": 0, "A": 0, "S": 0}, "auto_vector": [0, 0, 0, 0, 0],
         "why": [{"text": "It is bold and curious in tests.", "trait": "O", "anchor": "curious"}],
         "media": [{"title": "Test show"}]},
    ]
    clean_result = a5_why({"profiles": json.loads(json.dumps(good))}, None)
    broken = json.loads(json.dumps(good))
    broken[1]["why"][0]["text"] = broken[0]["why"][0]["text"]  # deliberately duplicate a why sentence
    broken_result = a5_why({"profiles": broken}, None)
    ok = clean_result.status == "PASS" and broken_result.status == "FAIL"
    return R("A19", "PASS" if ok else "FAIL",
              "self-contained calibration: clean pair -> %s, pair with a duplicated why sentence -> %s "
              "(must be PASS then FAIL for this check to count as calibrated)" % (clean_result.status, broken_result.status))


def a20_screen(pool_csv_rows, pool):
    """New 2026-09-27 (CONTRACT.md A20 / spec/POOL-SCREEN.md section 8): no row of spec/pool.csv, no
    profile in data/pool.json, no recorded swap's in_id and no Q4 reserve carries a screened-out id."""
    if not pool_csv_rows:
        return skip("A20", "spec/pool.csv missing")
    problems = []
    csv_bad = sorted(r["id"] for r in pool_csv_rows if r["id"] in A20_REMOVED_IDS)
    if csv_bad:
        problems.append("spec/pool.csv rows carry screened-out id(s): %s" % csv_bad)
    if pool:
        profiles = pool.get("profiles", [])
        prof_bad = sorted(p.get("id") for p in profiles if p.get("id") in A20_REMOVED_IDS)
        if prof_bad:
            problems.append("data/pool.json profiles carry screened-out id(s): %s" % prof_bad)
        swaps = pool.get("swaps", [])
        swap_bad = sorted(sw.get("in_id") for sw in swaps if sw.get("in_id") in A20_REMOVED_IDS)
        if swap_bad:
            problems.append("data/pool.json swaps carry a screened-out in_id: %s" % swap_bad)
    reserve_bad = sorted(i for i in RESERVE_IDS if i in A20_REMOVED_IDS)
    if reserve_bad:
        problems.append("check.py's own RESERVE_IDS constant carries a screened-out id (fix the check): %s" % reserve_bad)
    status = "FAIL" if problems else "PASS"
    return R("A20", status, "%d pool.csv rows, %d pool.json profiles checked against %d screened-out ids" %
              (len(pool_csv_rows), len(pool.get("profiles", [])) if pool else 0, len(A20_REMOVED_IDS)),
              detail=problems or None)


# ================================================================== main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT_DEFAULT))
    ap.add_argument("--base-url", default="https://joshuamatalon.github.io/which-pokemon/")
    ap.add_argument("--seed", type=int, default=20260927)
    ap.add_argument("--skip-a18", action="store_true")
    args = ap.parse_args()

    root = Path(args.root)
    data_dir, web_dir = root / "data", root / "web"
    corpus, corpus_err = load_json(data_dir / "corpus.json")
    pool, pool_err = load_json(data_dir / "pool.json")
    questions, questions_err = load_json(data_dir / "questions.json")
    lexicon, lexicon_err = load_json(data_dir / "lexicon.json")
    pool_csv_rows = load_pool_csv(ROOT_DEFAULT / "spec" / "pool.csv")

    print("=== which-pokemon check.py ===")
    print("root=%s  base-url=%s  seed=%d  python=%s  numpy=%s" %
          (root, args.base_url, args.seed, sys.version.split()[0], np.__version__))
    node_path = find_node()
    if node_path:
        try:
            nv = subprocess.run([node_path, "--version"], capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            nv = "?"
        print("node=%s (%s)" % (node_path, nv))
    else:
        print("node=NOT FOUND on PATH")
    for name, err in (("corpus.json", corpus_err), ("pool.json", pool_err),
                       ("questions.json", questions_err), ("lexicon.json", lexicon_err)):
        print(("loaded data/%s" % name) if err is None else ("data/%s: %s" % (name, err)))
    print()

    with tempfile.TemporaryDirectory(prefix="which_pokemon_check_") as tmp:
        tmp_dir = Path(tmp)

        # profiles used by simulation assertions: real pool.json if it has vectors, else empty.
        # lean is optional on a profile since the 2026-09-27 amendment (Q5) and unread when present, so
        # it is no longer part of this filter (a profile missing "lean" entirely is expected, not broken).
        sim_profiles = []
        if pool and pool.get("profiles"):
            sim_profiles = [p for p in pool["profiles"]
                             if isinstance(p.get("vector"), list) and len(p["vector"]) == 5
                             and p.get("stage") in STAGE_INDEX]
        pool_vec = pool_ids = pool_leans = pool_stages = None
        if sim_profiles:
            pool_vec, pool_ids, pool_leans, pool_stages = pool_arrays(sim_profiles)

        app_js_path = web_dir / "app.js"

        results = [
            a1_corpus(corpus),
            a2_tags(corpus, lexicon),
            a3_lexicon(lexicon),
            a4_pool(pool, pool_csv_rows),
            a5_why(pool, corpus),
            a6_items(questions, pool_names=[p.get("name") for p in (pool or {}).get("profiles", [])] if pool else None),
            a7_takers(questions),
            a8_images(pool, web_dir),
            a9_cross_language(sim_profiles, node_path, app_js_path if app_js_path.exists() else None, args.seed, tmp_dir),
            a10_coverage(pool_vec, args.seed),
            a11_reachability(sim_profiles, pool_vec, pool_ids, pool_leans, pool_stages),
            a12_concentration(sim_profiles, pool_vec, pool_ids, pool_leans, pool_stages, args.seed),
            a13_lean(sim_profiles, pool_vec, pool_ids, pool_leans, pool_stages, questions, web_dir,
                     node_path, app_js_path if app_js_path.exists() else None, args.seed, tmp_dir),
            a14_stage(sim_profiles, pool_vec, pool_ids, pool_leans, pool_stages, args.seed),
            a15_result_text(sim_profiles, questions, args.seed),
            a16_prose(questions, pool, web_dir, tmp_dir),
            a17_retest(sim_profiles, args.seed),
            a18_live(args.base_url, args.skip_a18, tmp_dir),
            a19_calibration(),
            a20_screen(pool_csv_rows, pool),
        ]

        for r in results:
            print(r.line())

        must_fails = [r for r in results if r.status == "FAIL" and r.must]
        skips = [r for r in results if r.status == "SKIP"]
        reports = [r for r in results if r.status == "REPORT"]
        print()
        print("SUMMARY: %d PASS, %d FAIL (%d of them MUST), %d SKIP, %d REPORT-only" %
              (sum(1 for r in results if r.status == "PASS"), sum(1 for r in results if r.status == "FAIL"),
               len(must_fails), len(skips), len(reports)))
        if skips:
            print("SKIPPED (not evidence of failure, evidence of missing input): %s" % [r.id for r in skips])
        if must_fails:
            print("FAILED (MUST): %s" % [r.id for r in must_fails])
            return 1
        return 0


if __name__ == "__main__":
    sys.exit(main())

