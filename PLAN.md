# PLAN: Which Pokémon are you? (family personality quiz)

Lead plan, 2026-09-27. Scale: NORMAL with a heavy PRODUCE step, run in one-shot mode (doctrine §4.2).
Project root: `C:/Users/joshu/Pokemon/which-pokemon/`. Public repo `joshuamatalon/which-pokemon`, served
from `web/` on GitHub Pages at `https://joshuamatalon.github.io/which-pokemon/`.

## What Josh asked for (his words, condensed)

1. Pull the ENTIRE Pokémon corpus. Read the Pokédex entries, look at the pictures, research each one's
   personality, show and media appearances, and how the community sees it.
2. Research real personality quizzes, the scientific studies behind them, and the field of personality
   assessment. That research decides the quiz's foundation (added mid-turn, 13:23).
3. Build a professional web app: a brief personality quiz, quick and easy, precise and accurate, with
   questions that are enjoyable and thought provoking but not too personal.
4. It matches the taker with THEIR Pokémon. The end screen shows a 2D image and a 3D animated sprite (the
   Champions Lab kind), explains the reasoning, and gives positive insight. Never offensive, never mocking.
5. It asks who is taking it: Alex, Melissa, Josh, Carolyn, John, Andrew, Oliver, Todd, Milo.
   Alex (sister, 5 years older than Josh), Melissa (sister, 13 years older), Andrew (Alex's husband),
   their children Oliver 13, Todd 10, Milo 8, and Carolyn and John (Josh's parents). Women get more
   feminine Pokémon, men more masculine.
6. Follow the design document (`demandscan/bids/samples/DESIGN-STANDARD.md`): minimalism, aesthetics,
   no visual clutter. Mobile first. A GitHub Pages link he can paste into iMessage.

## Decomposition (five positions, one-shot)

| # | Position | Produces | Path |
|---|---|---|---|
| 0 | panelist (plan review) | verdict on this plan | `spec/PLAN-REVIEW.md` |
| 1 | subsystem DEFINE | personality-science research note, the contract (trait model, item spec, scoring, pool criteria and pool list, profile schema, gender and age rules, result-text rules) | `spec/RESEARCH-PERSONALITY.md`, `spec/CONTRACT.md`, `spec/pool.csv` |
| 2 | stream PRODUCE | corpus pull, corpus tagging, pool profiles (workers), questions, the web app, deploy | `scripts/`, `data/corpus.json`, `data/pool.json`, `data/questions.json`, `web/`, live URL |
| 3 | enabling INSTRUMENT | `test/check.py`: schema, images, prose check, 20k-answer simulation, live-site mobile run with screenshots; calibrated on a known-bad | `test/check.py`, `test/CHECK-RESULT.md`, `test/shots/` |
| 4 | panelist (product) | independent verification of the live quiz as three takers, tone and design audit | `spec/PANEL-VERDICT.md` |
| 5 | integrator CONFIRM | seams: contract vs data vs app vs check vs live URL; final reconciled report | `spec/CONFIRM.md` |

## Design decisions the lead is making now (RULINGS, so nothing waits on Josh)

- **Corpus = all 1,025 species from PokéAPI** (`pokemon-species` 1..1025, verified 2026-09-27): every
  English flavor text ever printed (deduped), genus, colour, shape, habitat, gender rate, egg groups,
  legendary/mythical/baby flags, evolution stage, types, base stats, height, weight, generation. Every
  species gets a machine-derived trait vector from its flavor text (a lexicon per trait) plus stats. That
  is how "read the Pokédex entries" becomes checkable: `data/corpus.json` carries the vector and the
  matched lexicon words for every species.
- **Result pool = a curated subset, about 150 species,** chosen for recognisability (starters and their
  lines, mascots, the 2020 Pokémon of the Year vote, anime regulars), coverage of the trait space, and
  balance of feminine, masculine and neutral leans. Each pool member gets a hand-researched profile
  (personality, anime and media appearances, community perception, lean, stage, trait vector, three
  positive "why" sentences). Reason: a quiz of about a dozen questions cannot discriminate 1,025 outcomes,
  and a grandparent matched to an obscure species reads as a miss. The whole corpus is still pulled,
  read and tagged, and the corpus tags seed the pool vectors. This narrowing is stated to Josh.
- **Trait model comes from the DEFINE research**, expected to be the Big Five with brief-instrument item
  design (TIPI, BFI-10, Mini-IPIP as precedents), scenario-style forced-choice items, balanced keying,
  reading level a capable 8-year-old can follow, about 12 to 15 items, every trait covered by at least two
  items. Type-based quizzes (MBTI style) and Barnum-style flattery are to be avoided on the evidence.
  The subsystem may replace this with a better-supported model if the literature says so.
- **Matching** = nearest pool member in the trait space, filtered by the taker's lean (women: feminine or
  neutral; men: masculine or neutral) and nudged by life stage (children toward youthful stages, adults
  toward evolved, grandparents toward mature or wise). A guest option ("someone else") exists with no
  lean filter. Deterministic: same answers, same result.
- **Result screen**: official artwork (2D), Showdown animated sprite (3D), name and genus, the reasoning
  built from the taker's actual answers plus the profile's sentences, a "copy link" that shares the result,
  and "take it again". Positive, specific, never generic.
- **Design**: the Champions Lab token set (paper, ink, muted, rule, soft, data, accent; three sizes; one
  font stack; 4 px grid), one job per screen, big tap targets, no chrome. Open Graph tags so the iMessage
  preview shows a title and image.
- **Images self-hosted** for the pool only: `web/img/art/<id>.png` (PokéAPI official artwork) and
  `web/img/ani/<showdown-id>.gif` (Showdown `ani`). Attribution in the footer. Nothing hotlinked.
- **Prose**: every human-read string passes `demandscan/bids/samples/tools/prose_check.py`. No em dashes.

## What is NOT being built

- No accounts, no server, no analytics, no database. Static files only.
- No results for all 1,025 species. The pool is the outcome set; the corpus is the evidence layer.
- No Mega, regional or alternate forms in the pool. Base species only.
- No compatibility, couples or "who in the family are you most like" features.
- No sound, no confetti, no animation beyond the sprite itself and screen transitions.
- No editing of Champions Lab. Its CSS tokens are copied, not linked.

## Budget

- Subsystem: one pass, research with at least eight cited primary or review sources, stops when the
  contract answers every question in the item list below.
- Stream: up to 8 workers for profiles (about 20 species each). Stops when `test/check.py` (once it
  exists) or its own smoke run shows the live URL serving a complete quiz. Cap: 3 deploy attempts.
- Enabling: one instrument, calibrated on one deliberately broken pool entry. Stops when the known-bad
  fails and the real data is judged, either way.
- Panelist and integrator: one pass each.

## Questions the CONTRACT must answer

1. Which traits, with definitions, poles, and the source that supports them.
2. Item format, count, answer count, keying balance, reading level, and the rule for "not too personal".
3. Scoring: how answers become a taker vector, how a profile vector is expressed, the distance metric, the
   lean filter, the stage nudge, the tie-break, and determinism.
4. The pool: the list of species with lean (feminine / masculine / neutral), stage (young / evolved /
   mature), and the selection reason, in `spec/pool.csv`.
5. Profile schema (`data/pool.json` shape) and the corpus schema (`data/corpus.json` shape).
6. Result-text rules: what the reasoning must cite (at least two of the taker's own answers), tone rules,
   banned framings, length.
7. The names list and each person's lean and stage.
8. Acceptance: what `test/check.py` must assert for the deliverable to count as done.

## Lead rulings after the plan review (2026-09-27 13:30, spec/PLAN-REVIEW.md)

1. Lean is a distance PENALTY, never an exclusion. Josh wrote "more feminine" and "more masculine", which is
   a nudge. The contract states the penalty weight and justifies it against trait distance, so a decisive
   trait fit can still cross leans. The pool must contain no species whose cross-lean result would read as
   a joke about the taker; the contract lists the exclusions it applied.
2. The research note answers, in its own words with sources: (a) forced-choice versus Likert for a mixed
   audience from age 8 to over 60; (b) what validity is lost when a validated brief instrument is reworded
   into Pokémon-flavoured scenario items, and how the contract limits that loss; (c) test-retest
   reliability at 12 to 15 items for a child reader. Three more questions for the contract, eleven total.
3. Coverage is demonstrated, not asserted: the contract states a maximum distance from any plausible taker
   vector to its nearest pool member, and the check asserts it.
4. The tie-break is deterministic and stated. Every pool member must be reachable by some answer set.
5. Every why-sentence in a profile names something specific to that species (a Pokédex fact, a canon
   trait, a named media appearance). The check flags a sentence reused across profiles.
6. The mature bucket must be a real, flattering set of at least 25 species. No species that reads as a joke
   about age.
7. Profile workers claim contiguous row ranges of spec/pool.csv by id, never by name.
8. Showdown's animated set renders the 3D game models for every species it covers, Gen 1 included, so the
   "3D sprite" claim holds across the pool. The stream records any species that fell back to a static
   image.

## Josh's correction (2026-09-27 14:18) and the lead rulings from it

Josh: "This will be grounded in factual analysis and science not just a buzzfeed slop article." And, after
his sister objected to the gender rule: "make sure no one gets a Pokemon that could be viewed as offensive
or upsetting. Like my mother or sisters getting Purugly. Remove the gender thing so none is limited in
that way."

9. Lean is REMOVED. Every taker's lean is null, the lean penalty is never applied, and the app never
   stores or shows a gender. Ruling 1 and the lean rows in the contract are void. The lean column may stay
   in pool.csv as a record but nothing reads it.
10. The pool is screened for offence potential in place of the lean. A species is OUT if its name, its
    Pokédex text, its design, or its common community read makes a plausible joke about the taker's
    looks, weight, age, intelligence, hygiene, laziness, attractiveness, temper, or worth (Purugly, Jynx,
    Grimer and Muk, Trubbish and Garbodor, Snorlax, Slaking, Bidoof, Magikarp, Stunfisk, Bruxish, Gulpin,
    Swalot, Koffing and Weezing are the shape of it; the DEFINE agent decides each species and writes the
    reason). Swap in reserves so coverage still holds. Stage nudges stay, as nudges.
11. The science is visible: the app carries a short "How it works" toggle (reference behind a toggle, per
    the design standard) that states the Big Five basis, the 15-item three-per-trait design, the nearest
    match rule, and links the research note in the repo. No claims of measurement.
12. Two lead findings from opening the artifacts go on the fix list: the stylesheet uses four type sizes
    (13, 16, 20, 28) where the standard allows three; two item stems repeat ("You have an open afternoon").
