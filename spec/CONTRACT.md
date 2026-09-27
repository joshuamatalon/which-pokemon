# CONTRACT: Which Pokémon are you?

Subsystem DEFINE, 2026-09-27. This file is the interface every later position builds and checks against.
Every statement here is a rule. "MUST" marks a rule the check enforces; the rest are rules the panelist
judges. The evidence behind each rule is in `spec/RESEARCH-PERSONALITY.md`, and its decisions D1 to D12
are inherited below word for word. The pool is `spec/pool.csv`.

Paths are relative to the project root `C:/Users/joshu/Pokemon/which-pokemon/`.

Amended 2026-09-27 after Josh's correction (PLAN.md rulings 9 to 12). The CHANGES section at the end lists
every rule that moved.

## Decisions inherited from the research note

D1. The trait model is the Big Five, scored as five continuous dimensions from -1 to 1. Negative
Emotionality is reversed and named Steadiness, so both poles of every trait have a positive label.
HEXACO Honesty-Humility is not measured.

D2. The quiz has 15 items, three per trait, and each trait's three items sample three different BFI-2
facets.

D3. Every item is a single-trait graded choice: one everyday situation and four fully labelled behaviour
options at levels -3, -1, 1 and 3 of that one trait. No agree-or-disagree scale, no midpoint, no
multi-trait ipsative blocks.

D4. No item or option uses negation, and all four options of an item must be equally acceptable
behaviours.

D5. Keying balance comes from option order. The top-level option sits in each of the four display
positions at least three times across the 15 items, and at least ten items show their options in a
non-monotone order.

D6. Every item is written for an 8-year-old reader and must make sense unchanged to a 70-year-old.
Readability limits are set in the contract.

D7. Every item names a public-domain IPIP source item and a BFI-2 facet. At most four stems use Pokémon
flavour, and no item needs Pokémon knowledge.

D8. Topics that are too personal are banned: health, the body, money, sex, religion, politics, family
conflict, grief, school or work performance, and fears or sadness.

D9. The result is the nearest pool member in trait space, never a type. The result screen also shows the
taker's five trait positions.

D10. The result text never claims permanence, truth or scientific certainty, and presents the match as a
reading of today's answers.

D11. Every result quotes two of the taker's own answers, and every profile sentence carries a
species-specific anchor. Stock Barnum lines are banned, and no profile sentence is reused.

D12. The quiz makes no claim of validated measurement. Its expected instability on retakes is stated in
the contract and is not hidden from the check.

## Q1. The traits

Vector order is fixed everywhere as `[O, C, E, A, S]`.

| Key | Shown as | High pole (+1) | Low pole (-1) | Definition | Facets sampled (one item each) | Source |
|---|---|---|---|---|---|---|
| O | Imagination | Curious | Down-to-earth | Openness: interest in ideas, beauty and new experience, against a preference for the familiar and practical | Intellectual Curiosity, Aesthetic Sensitivity, Creative Imagination | BFI-2 [8], Goldberg [1] |
| C | Planning | Planner | Go-with-the-flow | Conscientiousness: order, persistence and follow-through, against flexibility and spontaneity | Organization, Productiveness, Responsibility | BFI-2 [8] |
| E | Social energy | Outgoing | Low-key | Extraversion: drawing energy from people and activity, against recharging in calm and quiet | Sociability, Assertiveness, Energy Level | BFI-2 [8] |
| A | Getting along | Team player | Strong-willed | Agreeableness: putting harmony and others' needs first, against saying what you think and holding your ground | Compassion, Respectfulness, Trust | BFI-2 [8] |
| S | Steadiness | Steady | Sensitive | Negative Emotionality reversed: staying level when things change, against feeling things strongly and noticing early | Anxiety, Emotional Volatility, Vulnerability (IPIP-NEO N6) | BFI-2 [8], IPIP |

The BFI-2 Depression facet is not sampled (D8). Vulnerability from the IPIP-NEO takes its place, and its
item MUST be about being rushed or under time pressure.

Each pole has one fixed strength line. The result shows only the line for the taker's strongest pole
(Q6), so the line always follows from the answers.

| Pole | Strength line (exact text) |
|---|---|
| O high, Curious | You like new ideas and want to know how things work. |
| O low, Down-to-earth | You trust what works and keep your feet on the ground. |
| C high, Planner | You like a plan, and you finish what you start. |
| C low, Go-with-the-flow | You adapt fast and enjoy whatever comes up. |
| E high, Outgoing | You get energy from people and like being in the mix. |
| E low, Low-key | You recharge in calm places and notice what others miss. |
| A high, Team player | You look out for others and help a group get along. |
| A low, Strong-willed | You say what you think and stand up for it. |
| S high, Steady | You stay calm when plans change. |
| S low, Sensitive | You feel things deeply and notice changes early. |

## Q2. Items

Format and count.

- The quiz MUST have exactly 15 items, ids `q01` to `q15`, shown in id order.
- Traits MUST run in the cycle O, C, E, A, S three times, so no two neighbouring items share a trait.
- Each trait's three items MUST name three different facets from the Q1 table.
- Each item MUST have exactly four answers whose `level` values are -3, -1, 1 and 3, one of each.
- Answer display order is the array order in `data/questions.json`, fixed for every taker. It MUST
  satisfy D5: the level-3 answer appears in each of positions 1 to 4 at least three times across the
  quiz, and at least ten items are non-monotone (their levels in display order are neither ascending nor
  descending).
- Every answer MUST describe something the taker does, in first person ("I pack..."), in one short
  sentence.

Keying balance. Agree-or-disagree acquiescence has nothing to act on in this format, so balance is
carried by option order (D5) and by the stems: in each trait, at most two of the three stems may invite
the high pole first by their wording. The panelist judges the stems; the check enforces D5.

Reading level. The check MUST enforce these limits, and the writer aims lower.

- Stem at most 16 words; each answer at most 10 words; within one item the longest answer is at most 4
  words longer than the shortest.
- Flesch-Kincaid grade of the item (stem plus its four answers, each answer counted as one sentence) at
  most 4.0.
- No word of four or more syllables, except "Pokémon" and Pokémon names.
- Syllable rule used by the check and by any writer's own tool: lowercase the word and keep letters only;
  a word of three letters or fewer has one syllable; otherwise drop one trailing "e" unless the word ends
  in "le", then count runs of the letters a, e, i, o, u, y; the minimum is one.
- Flesch-Kincaid grade = 0.39 × (words ÷ sentences) + 11.8 × (syllables ÷ words) − 15.59.

The "not too personal" rule.

- No stem or answer may touch the D8 topics. The check MUST reject any item containing these words, case
  insensitive, whole word: sick, doctor, hospital, medicine, weight, diet, body, fat, thin, money, cost,
  price, buy, pay, rich, poor, allowance, spend, church, god, pray, religion, vote, election, date,
  dating, crush, boyfriend, girlfriend, kiss, fight, argue, argument, divorce, punish, grounded, die,
  died, death, funeral, grade, grades, test, homework, school, class, teacher, work, job, office, boss,
  retire, scared, afraid, sad, cry, lonely, worry, worried.
- No negation (D4). The check MUST reject any stem, answer or echo matching
  `\b(not|no|never|none|nobody|nothing|nowhere|neither|nor|without)\b|n't\b`, case insensitive.
- Every stem MUST read the same for an 8-year-old and a 70-year-old: no school, work, retirement,
  grandchildren or parenting setting. Allowed ground: a free afternoon, a trip, a board game, a new
  place, a surprise, a shared project, a party, a walk, a rainy day, cooking together, a puzzle, a pet,
  meeting someone new.
- At most four items may set the stem in a Pokémon world (`flavour: true`). A flavoured stem still asks
  what the taker would really do, and no item needs Pokémon knowledge.

Each item names its evidence (D7): `source_instrument` is "IPIP", `source_item` is the text of a
public-domain IPIP item from https://ipip.ori.org whose content the four answers express at four levels,
and `source_key` is "+" or "-" as IPIP keys it.

Worked example (Conscientiousness, Organization facet; source item IPIP "Like order", keyed +):

```json
{
  "id": "q02", "trait": "C", "facet": "Organization", "flavour": false,
  "source_instrument": "IPIP", "source_item": "Like order.", "source_key": "+",
  "stem": "You are going on a trip tomorrow. What do you do tonight?",
  "answers": [
    {"text": "I pack some things and finish in the morning.", "level": -1, "echo": "you'd pack some things and finish in the morning"},
    {"text": "I pack my bag and check it twice.",             "level": 3,  "echo": "you'd pack your bag and check it twice"},
    {"text": "I grab what I need on the way out.",            "level": -3, "echo": "you'd grab what you need on the way out"},
    {"text": "I make a short list and pack most of it.",      "level": 1,  "echo": "you'd make a short list and pack most of it"}
  ]
}
```

Its display order is -1, 3, -3, 1, which is non-monotone, and all four answers describe a likeable
person.

## Q3. Scoring

The web app and `test/check.py` MUST implement this exactly. A JavaScript author transcribes it line by
line; the check runs an independent Python copy against the app's JavaScript (Q8, A9).

Constants.

```
TRAITS          = ["O", "C", "E", "A", "S"]
STAGE_INDEX     = { "young": 0, "evolved": 1, "mature": 2 }
LEAN_SAME       = 0.00      // UNUSED since 2026-09-27: every taker's lean is null
LEAN_NEUTRAL    = 0.08      // UNUSED since 2026-09-27
LEAN_OPPOSITE   = 0.25      // UNUSED since 2026-09-27
round6(x)       = floor(x * 1000000 + 0.5)       // integer key; floor, never a language round()
round4(x)       = floor(x * 10000 + 0.5) / 10000
```

Taker vector. `choice[i]` is the display index (0 to 3) the taker tapped for `items[i]`.

```
function takerVector(items, choice):
    sum = {O: 0, C: 0, E: 0, A: 0, S: 0}
    n   = {O: 0, C: 0, E: 0, A: 0, S: 0}
    for i in 0 .. items.length - 1:
        item  = items[i]
        level = item.answers[choice[i]].level          // -3, -1, 1 or 3
        sum[item.trait] = sum[item.trait] + level
        n[item.trait]   = n[item.trait] + 1
    return [ sum[k] / (3 * n[k]) for k in TRAITS ]     // each value in [-1, 1], a multiple of 1/9
```

Profile vector. The build script computes it once and writes it into `data/pool.json`; the app only
reads it. `ratings[k]` is the researcher's integer rating from -4 to 4 (Q5), and `auto_vector` comes from
the corpus.

```
function profileVectors(profiles):                       // all pool members at once
    N = profiles.length
    for each profile p, for each trait index k:
        raw[p][k] = 0.75 * (p.ratings[TRAITS[k]] / 4) + 0.25 * p.auto_vector[k]
    for each trait index k:
        order = profiles sorted by (raw[p][k] ascending, p.id ascending)
        pos = 0
        while pos < N:
            end = pos
            while end + 1 < N and raw[order[end + 1]][k] == raw[order[pos]][k]:
                end = end + 1
            rank = (pos + end) / 2                        // tied profiles share the average rank
            for j in pos .. end:
                order[j].vector[k] = round4(-0.9 + 1.8 * rank / (N - 1))
            pos = end + 1
```

The rank step spreads every trait evenly across the pool, the way norms spread raw test scores. A
Pokémon's position is relative to the other pool members, which keeps the pool from bunching on the
friendly, steady side where most canon sits.

Lean and stage. The lean penalty is void (amendment 2026-09-27, ruling 9). Every taker's lean is null,
so `leanPenalty` returns 0 on its first line for every call. The function and its call in `match()` stay
in the pseudocode so the JavaScript and Python copies remain line-for-line transcriptions. Nothing in the
app stores, sends or shows a gender, and nothing reads a pool member's lean except this dead call.

```
function leanPenalty(takerLean, memberLean):             // takerLean is always null (void since 2026-09-27)
    if takerLean == null:        return 0
    if memberLean == takerLean:  return LEAN_SAME
    if memberLean == "neutral":  return LEAN_NEUTRAL
    return LEAN_OPPOSITE

function stagePenalty(taker, memberStage):
    return taker.stage_weight * abs(STAGE_INDEX[memberStage] - STAGE_INDEX[taker.stage_target])
```

Match, tie-break and determinism.

```
function match(t, taker, profiles):                      // t = takerVector(...)
    best = null
    for p in profiles:
        d = sqrt( sum over k of (t[k] - p.vector[k])^2 )  // Euclidean distance
        key = round6(d + leanPenalty(taker.lean, p.lean) + stagePenalty(taker, p.stage))
        if best == null or key < best.key or (key == best.key and p.id < best.id):
            best = {id: p.id, key: key}
    return best.id
```

The metric is plain Euclidean distance over the five traits. The score is rounded to an integer key
before comparison, so float noise in the last bits cannot change a result between JavaScript and Python.
Equal keys go to the lower national Pokédex id. The same taker and the same 15 choices always give the same
Pokémon; nothing random, time-based or order-of-load dependent enters the function.

Why these weights. One answer moved by one step changes that trait's score by 2/9, about 0.22, and moves
the distance by at most that much. For scale, the median distance from a quiz taker to the nearest member
was about 0.59 in the calibration simulation. The lean weights that used to sit on this scale are void
(amendment 2026-09-27), and the lean figures from the first simulation no longer apply.

The stage nudge uses the same scale. A weight of 0.15 per stage step is about two thirds of one answer
step, and 0.08 is about a third. Children and grandparents get the stronger nudge; adults and Oliver get
the lighter one (Q7). In the simulation the nudge put children on a young member and grandparents on a
mature member in about 55% to 75% of random answer sets.

The share link carries the inputs, never the result. Its form is
`https://joshuamatalon.github.io/which-pokemon/#t=<taker_key>&a=<15 digits, each 0 to 3>`, and opening
it recomputes the match with `match()`.

## Q4. The pool

`spec/pool.csv` holds 149 base species with columns `id,name,showdown_id,lean,stage,reason`. The `lean`
column is a record of the old rule and nothing more. No build script, app file or check reads it
(amendment 2026-09-27, ruling 9).

| Stage | Young | Evolved | Mature | Total |
|---|---|---|---|---|
| members | 60 | 52 | 37 | 149 |

The mature bucket holds 37 members, above the floor of 25, and the panelist reads every one of them for age
jokes.

Selection order. Recognisability came first: most starters from all nine generations, the best-known
final starters, Pikachu and the Eevee family, anime partners, and most of the Pokémon of the Year 2020
top 30. Coverage came second: each row's reason ends with a short trait sketch, and the rows were chosen so
every pole of every trait has several clear examples. The offence screen came third and overrides both.
The rows it removed and the rows it added are listed in `spec/POOL-SCREEN.md`.

Lean rules. Void since 2026-09-27. Rows written before the amendment still start their reason with
`Lean by <basis>:`, and rows added by the screen mark that text "(record only)". A new row needs no lean.

Stage rules. young: a first stage (baby forms not counted) or a small single-stage species with a youthful canon. evolved: a middle
or final form in its prime. mature: a final form or legendary whose canon is wise, calm or protective.
Baby Pokémon (PokéAPI `is_baby`) are excluded, which removed Riolu, Pichu and Togepi from consideration.

Offence screen. This replaces the old exclusion table and replaces the lean as the pool's safeguard. The
family taking the quiz spans ages 8 to over 60, and a result must never read as a joke about the person.

- A species is OUT if its name, its genus, its Pokédex text, its design or its common community read makes
  a plausible joke about the taker's looks, weight, age, intelligence, hygiene, laziness, attractiveness,
  temper or worth. The genus counts because the result screen shows it.
- It is OUT when the joke is central: it sits in the name or genus, in most of its Pokédex lines, in its
  design, or in its best-known community read.
- It stays with line bans when the joke sits in a minority of Pokédex lines and the common read is warm.
  A profile writer MUST NOT use a banned subject in any profile string. The Q6 screen words enforce most
  of them mechanically, and the panelist reads for the rest.
- A species is OUT if a sexual meme attaches to it that a 13-year-old in the family is likely to know.
- A species is OUT if its name states a sex, because no lean filter now keeps it from any taker.
- A species is OUT if its Pokédex centres on taking lives, souls or children, or on grief and death.
- Calls that could go either way are marked "judgement" below, so the panelist can overrule them.

Every species screened out, with its reason, is listed in `spec/POOL-SCREEN.md`, and A20 holds their ids.
That file is part of this contract.

Decision for every pool member. The screen read each species' name, genus and every English Pokédex line
in `data/corpus.json` (a word scan for the screen categories, then a reading of every hit), plus its design
and community read.

| id | Name | Stage | Decision and line bans |
|---|---|---|---|
| 1 | Bulbasaur | young | KEEP. Line ban: napping. |
| 3 | Venusaur | mature | KEEP. No read in any screen category. |
| 4 | Charmander | young | KEEP. Line ban: its flame weakening when it is unwell. |
| 6 | Charizard | evolved | KEEP. Proud, and Ash's Charizard is loved for it. Line ban: fury. |
| 7 | Squirtle | young | KEEP. No read in any screen category. |
| 9 | Blastoise | mature | KEEP. Line ban: making itself heavy. |
| 12 | Butterfree | evolved | KEEP. No read in any screen category. |
| 25 | Pikachu | young | KEEP. Line ban: sleep. |
| 26 | Raichu | evolved | KEEP. No read in any screen category. |
| 30 | Nidorina | evolved | KEEP. No read in any screen category. |
| 35 | Clefairy | young | KEEP. Round and pink, but the genus is Fairy and the read is moon-dance magic. |
| 36 | Clefable | evolved | KEEP. No read in any screen category. |
| 37 | Vulpix | young | KEEP. No read in any screen category. |
| 58 | Growlithe | young | KEEP. Line ban: smell; use its loyalty. |
| 59 | Arcanine | mature | KEEP. No read in any screen category. |
| 65 | Alakazam | mature | KEEP, judgement. The read is genius. Line ban: its head growing heavier with age, and death; three of 22 Pokédex lines say so. |
| 77 | Ponyta | young | ADDED. No read in any screen category. |
| 78 | Rapidash | evolved | ADDED. No read in any screen category. |
| 94 | Gengar | evolved | KEEP, judgement. The read is a grinning prankster. Line ban: curses, stealing lives, frightening children; about half its Pokédex lines are dark. |
| 106 | Hitmonlee | evolved | KEEP. No read in any screen category. |
| 107 | Hitmonchan | evolved | KEEP. No read in any screen category. |
| 113 | Chansey | evolved | KEEP. Nurse Joy's partner; the read is kindness. Line ban: eggs as food. |
| 115 | Kangaskhan | mature | KEEP. The read is a protective parent. Line ban: rage, death. |
| 125 | Electabuzz | evolved | ADDED. Line ban: eating electricity, blackouts. |
| 131 | Lapras | mature | KEEP. Line ban: being hunted. |
| 133 | Eevee | young | KEEP. No read in any screen category. |
| 135 | Jolteon | evolved | KEEP. Line ban: its Pokédex says it easily becomes sad or angry; use its speed and sensitivity. |
| 136 | Flareon | evolved | KEEP. No read in any screen category. |
| 147 | Dratini | young | KEEP. Line ban: weakness. |
| 149 | Dragonite | mature | KEEP. The rounded design has an affectionate read, and the genus is Dragon. Line ban: body shape. |
| 150 | Mewtwo | mature | KEEP. The read is the antihero who chose peace. Line ban: vicious, savage, lab-made. |
| 151 | Mew | young | KEEP. No read in any screen category. |
| 152 | Chikorita | young | KEEP. No read in any screen category. |
| 154 | Meganium | mature | KEEP. No read in any screen category. |
| 155 | Cyndaquil | young | KEEP. Timid is a Sensitive-pole fact, stated warmly. |
| 157 | Typhlosion | evolved | KEEP. Line ban: rage. |
| 158 | Totodile | young | KEEP, judgement. Genus Big Jaw names a crocodile's jaw; the read is Ash's dancing Totodile. |
| 164 | Noctowl | mature | KEEP. The read is wisdom. Line ban: any age wording. |
| 179 | Mareep | young | ADDED. No read in any screen category. |
| 181 | Ampharos | mature | KEEP. No read in any screen category. |
| 196 | Espeon | evolved | KEEP. No read in any screen category. |
| 197 | Umbreon | evolved | KEEP. Line ban: its poisonous sweat. |
| 212 | Scizor | evolved | ADDED. Line ban: weight. |
| 237 | Hitmontop | evolved | ADDED. No read in any screen category. |
| 242 | Blissey | mature | KEEP. The read is kindness. Line ban: eggs as food. |
| 245 | Suicune | mature | KEEP. No read in any screen category. |
| 249 | Lugia | mature | KEEP. Line ban: sleep. |
| 250 | Ho-Oh | mature | KEEP. No read in any screen category. |
| 251 | Celebi | young | KEEP. No read in any screen category. |
| 252 | Treecko | young | KEEP. No read in any screen category. |
| 254 | Sceptile | evolved | KEEP. No read in any screen category. |
| 255 | Torchic | young | KEEP. No read in any screen category. |
| 257 | Blaziken | evolved | KEEP. No read in any screen category. |
| 258 | Mudkip | young | KEEP. Mud is its habitat; the meme is old and friendly. |
| 260 | Swampert | evolved | KEEP. No read in any screen category. |
| 280 | Ralts | young | KEEP. No read in any screen category. |
| 281 | Kirlia | evolved | KEEP. No read in any screen category. |
| 300 | Skitty | young | KEEP. Line ban: chasing its own tail, dizziness. |
| 311 | Plusle | young | ADDED. Line ban: crying. |
| 330 | Flygon | evolved | KEEP. No read in any screen category. |
| 333 | Swablu | young | ADDED. Line ban: dirt; use its love of clean things. |
| 334 | Altaria | mature | KEEP. No read in any screen category. |
| 350 | Milotic | mature | KEEP. Line ban: Feebas or any looks transformation. |
| 376 | Metagross | mature | KEEP. No read in any screen category. |
| 380 | Latias | evolved | KEEP. No read in any screen category. |
| 381 | Latios | evolved | KEEP. No read in any screen category. |
| 384 | Rayquaza | mature | KEEP. No read in any screen category. |
| 385 | Jirachi | young | KEEP. Line ban: its thousand-year sleep. |
| 387 | Turtwig | young | KEEP. Line ban: slow, heavy. |
| 389 | Torterra | mature | KEEP. Line ban: slow, heavy. |
| 390 | Chimchar | young | KEEP. Line ban: sleep. |
| 392 | Infernape | evolved | KEEP. No read in any screen category. |
| 393 | Piplup | young | KEEP. Pride is its affectionate read. Line ban: falling over, refusing help. |
| 395 | Empoleon | mature | KEEP. No read in any screen category. |
| 403 | Shinx | young | ADDED. Line ban: muscles. |
| 405 | Luxray | evolved | KEEP. Line ban: sleep. |
| 417 | Pachirisu | young | ADDED. No read in any screen category. |
| 427 | Buneary | young | KEEP. Its evolution Lopunny stays excluded. Line ban: its ears showing it is unwell. |
| 445 | Garchomp | evolved | KEEP. No read in any screen category. |
| 448 | Lucario | evolved | KEEP, judgement. The 2020 runner-up; the furry joke targets fans, not the taker, and carries no adult copypasta. |
| 468 | Togekiss | mature | KEEP. No read in any screen category. |
| 470 | Leafeon | evolved | KEEP. Line ban: smell. |
| 471 | Glaceon | evolved | KEEP. No read in any screen category. |
| 475 | Gallade | mature | KEEP. No read in any screen category. |
| 479 | Rotom | young | KEEP. No read in any screen category. |
| 488 | Cresselia | mature | KEEP. Line ban: sleep; use good dreams. |
| 490 | Manaphy | young | ADDED. No read in any screen category. |
| 492 | Shaymin | young | ADDED. No read in any screen category. |
| 494 | Victini | young | ADDED. No read in any screen category. |
| 497 | Serperior | mature | KEEP. Genus Regal. Line ban: smug. |
| 501 | Oshawott | young | KEEP. No read in any screen category. |
| 503 | Samurott | mature | KEEP. No read in any screen category. |
| 542 | Leavanny | mature | KEEP. No read in any screen category. |
| 547 | Whimsicott | evolved | KEEP. No read in any screen category. |
| 548 | Petilil | young | KEEP. Line ban: the elderly, fatigue, medicine. |
| 549 | Lilligant | evolved | KEEP. No read in any screen category. |
| 570 | Zorua | young | KEEP. No read in any screen category. |
| 571 | Zoroark | evolved | KEEP. Line ban: death, loneliness. |
| 572 | Minccino | young | KEEP. Line ban: dirt; use its tidiness. |
| 573 | Cinccino | evolved | KEEP. No read in any screen category. |
| 585 | Deerling | young | ADDED. No read in any screen category. |
| 586 | Sawsbuck | mature | ADDED. No read in any screen category. |
| 610 | Axew | young | ADDED. Line ban: eating berries. |
| 627 | Rufflet | young | KEEP. No read in any screen category. |
| 628 | Braviary | evolved | KEEP. No read in any screen category. |
| 637 | Volcarona | mature | KEEP. No read in any screen category. |
| 648 | Meloetta | evolved | KEEP. No read in any screen category. |
| 650 | Chespin | young | KEEP. Line ban: food. |
| 653 | Fennekin | young | KEEP. Line ban: eating twigs. |
| 654 | Braixen | evolved | KEEP. Some adult fan art exists; the mainstream read is Serena's partner. |
| 655 | Delphox | mature | KEEP. Some adult fan art exists; the mainstream read is a fire sorceress. |
| 656 | Froakie | young | KEEP. No read in any screen category. |
| 658 | Greninja | evolved | KEEP. No read in any screen category. |
| 669 | Flabébé | young | KEEP. No read in any screen category. |
| 671 | Florges | mature | KEEP. No read in any screen category. |
| 681 | Aegislash | mature | KEEP. Line ban: the king it drained of life. |
| 700 | Sylveon | evolved | KEEP. No read in any screen category. |
| 701 | Hawlucha | evolved | KEEP. No read in any screen category. |
| 722 | Rowlet | young | KEEP, judgement. Ash's Rowlet sleeps a lot, but its Pokédex does not. Line ban: sleep, naps. |
| 724 | Decidueye | mature | KEEP. No read in any screen category. |
| 725 | Litten | young | KEEP. No read in any screen category. |
| 728 | Popplio | young | KEEP, judgement. Its 2016 reveal drew clown jokes that have faded. Line ban: clown. |
| 730 | Primarina | mature | KEEP. No read in any screen category. |
| 741 | Oricorio | evolved | KEEP. No read in any screen category. |
| 742 | Cutiefly | young | KEEP. The name is a compliment. |
| 744 | Rockruff | young | KEEP. Line ban: trainers abandoning it. |
| 745 | Lycanroc | evolved | KEEP. No read in any screen category. |
| 761 | Bounsweet | young | KEEP. Line ban: its sweet sweat. |
| 764 | Comfey | evolved | KEEP. No read in any screen category. |
| 810 | Grookey | young | KEEP. No read in any screen category. |
| 813 | Scorbunny | young | KEEP. No read in any screen category. |
| 815 | Cinderace | evolved | KEEP. No read in any screen category. |
| 818 | Inteleon | evolved | KEEP. No read in any screen category. |
| 821 | Rookidee | young | ADDED. No read in any screen category. |
| 823 | Corviknight | mature | KEEP. No read in any screen category. |
| 831 | Wooloo | young | KEEP. Line ban: tumbling, sheep-follower wording. |
| 836 | Boltund | evolved | ADDED. No read in any screen category. |
| 856 | Hatenna | young | KEEP. No read in any screen category. |
| 869 | Alcremie | evolved | KEEP. No read in any screen category. |
| 873 | Frosmoth | mature | KEEP. No read in any screen category. |
| 887 | Dragapult | evolved | KEEP. No read in any screen category. |
| 888 | Zacian | mature | ADDED. Line ban: slumber, elder sister. |
| 891 | Kubfu | young | KEEP. No read in any screen category. |
| 892 | Urshifu | evolved | KEEP. No read in any screen category. |
| 906 | Sprigatito | young | KEEP. No read in any screen category. |
| 908 | Meowscarada | evolved | KEEP. Some adult fan art exists; the mainstream read is a stage magician. |
| 912 | Quaxly | young | KEEP. No read in any screen category. |
| 957 | Tinkatink | young | KEEP. Line ban: eating metal. |
| 959 | Tinkaton | evolved | KEEP, judgement. The Corviknight-bonking meme is affectionate awe. |

Reserve list. The stream MAY swap at most 10 pool rows for reserve species, and only when a coverage,
reachability or concentration assertion in Q8 fails with the real vectors. Each swap MUST keep the pool
between 140 and 170 rows and the mature bucket at 25 or more, MUST be recorded in `data/pool.json` under
`swaps` as `{out_id, in_id, reason}`, and the replacement MUST follow every profile rule. Every reserve
passed the offence screen, and every reserve has a Showdown animated sprite, checked 2026-09-27.

| id | name | showdown_id | lean (record) | stage | Trait sketch and screen note |
|---|---|---|---|---|---|
| 183 | Marill | marill | neutral | young | Cheerful, playful. Line ban: eating. |
| 312 | Minun | minun | neutral | young | Outgoing, team player; cheers on its partners. |
| 619 | Mienfoo | mienfoo | neutral | young | Disciplined, strong-willed; trains in the mountains. |
| 868 | Milcery | milcery | feminine | young | Warm, generous; brings good fortune to sweet shops. Line ban: its body being cream. |
| 176 | Togetic | togetic | neutral | evolved | Kind, hopeful; shares happiness with kind people. |
| 531 | Audino | audino | neutral | evolved | Caring, attentive; reads feelings through its ear feelers. |

Profile workers claim contiguous row ranges of `spec/pool.csv` by id, never by name (ruling 7).

## Q5. Data schemas

All three files are UTF-8 without a byte-order mark. Numbers are JSON numbers; vectors are rounded with
round4.

### `data/lexicon.json`

```json
{
  "version": 1,
  "match": "a token matches an entry exactly, or starts with it when the entry ends in *",
  "traits": {
    "O": {"high": ["..."], "low": ["..."]},
    "C": {"high": ["..."], "low": ["..."]},
    "E": {"high": ["..."], "low": ["..."]},
    "A": {"high": ["..."], "low": ["..."]},
    "S": {"high": ["..."], "low": ["..."]}
  }
}
```

The lexicon MUST contain every seed entry below. The stream MAY add entries and MUST NOT remove any. No
entry may appear in two lists. Low-pole lists for O will match rarely, because the Pokédex seldom
describes a Pokémon as conventional; that is a property of the text, and the check reports it.

| List | Seed entries |
|---|---|
| O high | curious, curiosity, intelligen\*, smart, clever, wisdom, wise, knowledge, mysteri\*, mystic\*, dream\*, imagin\*, future, predict\*, explor\*, wander\*, artist, music\*, melod\*, song, songs, sing, sings, singing, danc\*, beauty, beautiful, learn\*, magic\*, invent\*, inquisitive |
| O low | simple, plain, routine, habit, habits, habitual, ordinary, familiar, instinct, instincts, instinctive\*, practical, predictable, unchanging, traditional, tradition, humble |
| C high | careful, carefully, diligent\*, trains, training, disciplin\*, patient\*, patience, precise\*, neat, neatly, tidy, cleans, organiz\*, organis\*, prepar\*, build\*, collect\*, stores, gather\*, skill\*, master\*, dutiful\*, responsib\*, method\*, perfect\* |
| C low | lazy, lazily, sleep\*, naps, napping, careless\*, reckless\*, whim, whims, whimsical, fickle, forget\*, mischiev\*, prank\*, trick\*, messy, clumsy, clumsily, carefree, aimless\*, idle\*, lounge\*, doze, dozes, dozing, loaf\*, dawdl\*, impuls\* |
| E high | playful\*, lively, energetic\*, excited, excitement, noisy, loud\*, group\*, flock\*, herd\*, colony, colonies, pack, packs, swarm\*, play, plays, playing, frolic\*, crowd\*, social\*, chatter\*, boister\*, shout\*, cheer\*, show off, perform\* |
| E low | timid\*, shy\*, hide, hides, hiding, hidden, alone, solitar\*, quiet\*, silent\*, rarely, reclus\*, seclu\*, nocturnal, lurk\*, unseen, reserved, lone, loner, secretive, withdrawn |
| A high | gentle\*, kind, kindly, kindness, kindhearted, friendly, affection\*, loyal\*, help, helps, helping, helpful, heal, heals, healing, healer, care, cares, caring, nurtur\*, share, shares, sharing, protect\*, rescue\*, sooth\*, comfort\*, docile, harmless, love, loves, beloved, trust\*, cooperat\*, compassion\*, generous\* |
| A low | fierce\*, aggress\*, violent\*, vicious\*, territor\*, ruthless\*, savage\*, brutal\*, hostile, challeng\*, rival\*, proud, pride, selfish\*, stubborn\*, arrogan\*, bully, bullies, bullying, intimidat\*, merciless\*, feisty, domineer\*, belligeren\*, combative |
| S high | calm\*, serene\*, relaxed, relax\*, unflappable, placid\*, mellow, steady, steadi\*, tranquil\*, peaceful\*, unfazed, unmoved, easygoing, leisure\*, undisturbed, poise\*, levelheaded, unhurried |
| S low | nervous\*, scared, frightened, fearful, afraid, panic\*, startl\*, anxi\*, worr\*, sensitive, moody, temper, tempered, weep\*, sulk\*, upset\*, agitat\*, irritab\*, excitable, jumpy, trembl\*, cowardly, skittish |

Entries were chosen to avoid common Pokédex words with other meanings: "secretes", "composed of",
"psychic power", "clean water" and "legendary" are all frequent and say nothing about temperament, so they
are left out. `show off` is a two-word entry and matches the two
tokens in sequence.

Tagging algorithm (the check recomputes it and MUST match the stored values).

```
function tag(flavor_texts, lexicon):
    text   = join(flavor_texts, " ")
    tokens = split lowercase(text) on every character that is not a letter a-z or é
    for each trait k:
        hi = list of tokens (and two-token phrases) matching any entry in lexicon[k].high, in text order
        lo = same for lexicon[k].low
        auto[k] = round4( (len(hi) - len(lo)) / (len(hi) + len(lo) + 2) )
        matched_words[k] = { "high": unique(hi) in first-seen order, "low": unique(lo) in first-seen order }
    return auto (ordered as TRAITS), matched_words
```

The +2 in the denominator keeps a species with one stray match near zero. Base stats are stored in the
corpus but do not enter `auto_vector`: a base stat is a game-balance number, and no study links it to
temperament. This is a deviation from PLAN.md, which said "plus stats".

### `data/corpus.json`

```json
{
  "version": 1,
  "source": "https://pokeapi.co/api/v2/",
  "pulled": "YYYY-MM-DD",
  "count": 1025,
  "missing_flavor": [],
  "species": [
    {
      "id": 1,
      "slug": "bulbasaur",
      "name": "Bulbasaur",
      "genus": "Seed Pokémon",
      "flavor_texts": ["A strange seed was planted on its back at birth..."],
      "color": "green",
      "shape": "quadruped",
      "habitat": "grassland",
      "gender_rate": 1,
      "egg_groups": ["monster", "plant"],
      "is_legendary": false,
      "is_mythical": false,
      "is_baby": false,
      "stage": 1,
      "types": ["grass", "poison"],
      "base_stats": {"hp": 45, "attack": 49, "defense": 49, "special_attack": 65, "special_defense": 65, "speed": 45},
      "height": 7,
      "weight": 69,
      "generation": 1,
      "auto_vector": [0.0, 0.0, 0.0, 0.0, 0.0],
      "matched_words": {"O": {"high": [], "low": []}, "C": {"high": [], "low": []}, "E": {"high": [], "low": []}, "A": {"high": [], "low": []}, "S": {"high": [], "low": []}},
      "in_pool": true
    }
  ]
}
```

Field rules. `species` holds ids 1 to 1025, each once, in id order. `flavor_texts` holds every English
flavor text PokéAPI lists, with form feeds, soft hyphens and runs of whitespace turned into single
spaces, then deduplicated in first-seen order. Any species with no English text is listed in
`missing_flavor`. `habitat` is null where PokéAPI has none. `stage` here is evolution depth (1 for no
pre-evolution, 2 for one, 3 for two, counting baby forms); it is not the pool's life stage. `types`,
`base_stats`, `height` (decimetres) and `weight` (hectograms) come from the default form at
`/pokemon/<id>`. `generation` is an integer from 1 to 9.

### `data/pool.json`

```json
{
  "version": 1,
  "traits": ["O", "C", "E", "A", "S"],
  "swaps": [],
  "profiles": [
    {
      "id": 113,
      "name": "Chansey",
      "showdown_id": "chansey",
      "genus": "Egg Pokémon",
      "stage": "evolved",
      "ratings": {"O": 0, "C": 2, "E": 1, "A": 4, "S": 2},
      "rating_evidence": {"O": "...", "C": "...", "E": "...", "A": "...", "S": "..."},
      "auto_vector": [0.0, 0.0, 0.0, 0.0, 0.0],
      "vector": [0.0, 0.0, 0.0, 0.0, 0.0],
      "personality": "Two to four sentences drawn from canon.",
      "media": [{"title": "Pokémon: Indigo League, Nurse Joy's partner", "note": "One sentence."}],
      "community": "One or two sentences on how fans see it, with its source in sources.",
      "why": [
        {"text": "One sentence about this species.", "trait": "A", "anchor": "egg", "source": "https://..."}
      ],
      "sources": ["https://pokeapi.co/api/v2/pokemon-species/113/", "https://bulbapedia.bulbagarden.net/wiki/Chansey_(Pok%C3%A9mon)"],
      "images": {"art": "img/art/113.png", "ani": "img/ani/chansey.gif", "ani_static_fallback": false}
    }
  ]
}
```

Profile rules (the check enforces each MUST).

- `id`, `name`, `showdown_id` and `stage` MUST equal the pool.csv row, or the reserve row for a recorded
  swap. `genus` and `auto_vector` MUST equal the corpus entry. `lean` is optional in `data/pool.json`;
  when present it equals the csv and nothing reads it. Any pool data shipped under `web/` MUST carry no
  `lean` field (amendment 2026-09-27).
- `ratings` MUST be integers from -4 to 4. Each rating MUST have a one-sentence `rating_evidence` that
  names a Pokédex line or a media moment.
- Across the pool, each trait's ratings MUST have at least 30% at -1 or below and at least 30% at 1 or
  above. The low poles are positive labels, so this asks for honest spread and costs no flattery.
- `vector` MUST equal `profileVectors()` recomputed from `ratings` and `auto_vector`, within 0.0001.
- `personality` is at most 80 words; `community` is at most 50 words; `media` has at least one named
  appearance.
- `why` MUST have at least three entries covering at least two different traits. Each `text` is one
  sentence of at most 30 words, written about the Pokémon in the third person, positive, and true to the
  cited source. Each `anchor` MUST appear in its `text` and in that species' corpus `flavor_texts`,
  `genus` or `name`, or in one of its `media` titles, case insensitive.
- No `why` text may appear in two profiles, after lowercasing and collapsing whitespace.
- `sources` MUST hold at least two URLs, one of them the PokéAPI species URL.
- `images.art` and `images.ani` are paths under `web/`. When Showdown has no animated sprite,
  `ani_static_fallback` is true and `ani` points at a PNG.

Rating anchors, so every worker uses the same scale. A rating of 4 or -4 means the Pokémon is a textbook
case of that pole.

| Trait | -4 looks like | +4 looks like |
|---|---|---|
| O | Machamp, Tauros: practical, sticks to what works | Mew, Alakazam: endlessly curious, full of ideas |
| C | Whimsicott, Jigglypuff: follows the moment | Metagross, Quaxly: precise, tidy, finishes the job |
| E | Clefable, Hatenna: keeps away from crowds | Jigglypuff, Hawlucha: performs for everyone |
| A | Tyranitar, Incineroar: challenges anyone, holds its ground | Chansey, Blissey: puts others first |
| S | Sobble, Cyndaquil: startles and feels things fast | Lapras, Torterra: unshaken by anything |

### `data/questions.json`

```json
{
  "version": 1,
  "traits": {
    "O": {"name": "Imagination", "high": "Curious", "low": "Down-to-earth",
          "high_line": "You like new ideas and want to know how things work.",
          "low_line": "You trust what works and keep your feet on the ground."}
  },
  "takers": [
    {"key": "alex", "name": "Alex", "lean": null, "stage_target": "evolved", "stage_weight": 0.08}
  ],
  "items": [ "15 items in the shape of the Q2 worked example" ]
}
```

`traits` holds all five keys with the Q1 names, pole labels and exact strength lines. `takers` holds the
ten rows of Q7 in the Q7 order. `items` follow Q2. Each `echo` MUST start with "you", be at most 12
words, contain no negation, and rewrite its answer in the second person.

## Q6. Result text

The result screen shows, in this order: the official artwork, the animated sprite, the Pokémon's name and
genus, the reasoning block, the five trait bars, a copy-link button and a take-again button. Nothing else.

Reasoning block, built deterministically.

```
function resultText(t, taker, member, items, choice, traitsMeta):
    scored = []
    for i in 0 .. 14:
        level = items[i].answers[choice[i]].level
        align = (level / 3) * member.vector[index of items[i].trait in TRAITS]
        scored.append({i, level, align, trait: items[i].trait})
    sort scored by (align descending, abs(level) descending, i ascending)
    c1 = scored[0]
    c2 = first entry after c1 in scored whose trait != c1.trait
    lineA = "You said " + echo(c1) + ", and " + echo(c2) + "."
    whyOrder = member.why entries with trait == c1.trait, then trait == c2.trait, then the rest,
               each group in stored order, without repeats
    linesB = first 3 texts of whyOrder
    kStar = index of the largest abs(t[k]); ties go to the earlier trait in TRAITS
    pole  = t[kStar] >= 0 ? high : low
    lineC = "Your answers lean most toward " + pole label + ". " + pole strength line
    return lineA, linesB, lineC
```

Rules.

- The block MUST quote both echoes verbatim and MUST be at most 110 words across lines A, B and C.
- Every sentence is positive and specific. It either restates the taker's own answers or states a sourced
  fact about the species.
- The match is framed as today's reading: "You're a lot like {Name}" is the heading form. Banned framings:
  "your true Pokémon", "the real you", "deep down", "secretly", "science says", "scientifically",
  "proven", "you will always", "you are a type", "personality type", "introvert", "extrovert",
  "neurotic", any comparison with another family member, and any mention of age, the body, health, money,
  religion, sex or family conflict.
- Banned words, whole word and case insensitive, in every human-read string (results, profiles, items,
  echoes, interface text): lazy,
  weird, bossy, lonely, sad, scary, creepy, old, elderly, aged, fat, chubby, slow, dumb, stupid, annoying,
  grumpy, cranky, weak, ugly, needy, clingy, moody, stubborn, and every banned word of `prose_check.py`.
- Banned Barnum lines, case insensitive: "unused capacity", "untapped potential", "critical of yourself",
  "at times you", "sometimes you", "you pride yourself", "a great need for", "while you have some
  personality weaknesses", "you prefer a certain amount of change".
- Tone: warm, plain, spoken. Species are "it" unless the source names a specific character. No
  exclamation marks after the heading, no emoji, no em dashes or en dashes anywhere.
- The five trait bars show the pole labels at each end and a dot at the taker's position. They show no
  numbers.

Screen words (amendment 2026-09-27). A sentence about a species can be turned on the taker. A line about
eating a lot, sleeping all day, being dim or smelling is out even for a species that stays. These words,
whole word and case insensitive, MUST NOT appear in any profile string (`personality`, `community`,
`media` notes, `why` texts) or in the reasoning block:

- eating and sleeping: eat, eats, eating, ate, hungry, appetite, glutton, gluttonous, devour, devours,
  snack, snacks, food, sleep, sleeps, sleeping, asleep, slept, nap, naps, napping, doze, dozes, dozing,
  snooze, lazily, idle
- size and body: heavy, heavier, heaviest, weigh, weighs, weight, belly, stomach, plump, pudgy, stout,
  portly, bulky, muscle, muscles, muscular, bald
- smell and dirt: smell, smells, smelly, stink, stinks, stinky, stench, odor, odour, sweat, slime, slimy,
  dirt, dirty, filth, filthy, garbage, trash
- mind and worth: dim, dopey, derp, derpy, clumsy, dizzy, clown, weakest, useless, worthless, pathetic,
  loser, pig, worm, weasel, snake, tyrant, toxic, smug, disaster
- temper: angry, anger, angered, rage, rages, raging, enraged, rampage, rampages, furious, fury,
  violent, vicious, savage, temper, tantrum, vengeful, grudge
- tears: cry, cries, crying, cried, tears, sob, sobs, weep, weeps
- age and death: lifespan, elder, ancient, die, dies, died, dead, death, kill, kills, killed, soul,
  souls, curse, cursed, curses, grave, funeral
- sex and gender: female, male, feminine, masculine, gender, girl, boy, lady, gentleman

The words "ancient" and "elder" are banned because a grandparent reads them next to their own name. The
species-level line bans in Q4 cover what this list cannot catch.

How it works (amendment 2026-09-27, ruling 11). The names screen carries one collapsed toggle labelled
"How it works". Opening it shows a short text that follows these rules.

- At most 90 words, plain and spoken, passing `prose_check.py` with no em dash, banned word or "not X but
  Y" shape.
- It states that the quiz is built on the Big Five, the five traits by their Q1 display names, that there
  are 15 questions with three per trait, and that the result is the Pokémon whose trait profile sits
  nearest to the taker's answers.
- It links the research note in the public repo at
  `https://github.com/joshuamatalon/which-pokemon/blob/main/spec/RESEARCH-PERSONALITY.md`. The stream MUST
  publish `spec/` to the repo and confirm the link resolves; if the default branch is not `main`, the link
  uses the real branch name.
- It makes no claim of measurement. None of these words may appear in it, whole word and case insensitive:
  accurate, accuracy, precise, precisely, valid, validated, validity, proven, scientifically, reliable,
  reliability, diagnose, diagnosis, true, real, "science says".
- It never mentions a gender, a lean or any family member.

Reference text, 81 words, which the stream MAY use as written:

> The quiz is built on the Big Five, the trait model most personality research uses. The five traits here
> are Imagination, Planning, Social energy, Getting along and Steadiness. There are 15 questions. Each trait
> gets three of them. Your answers place you on all five traits, and your Pokémon is the one whose trait
> profile sits nearest to yours. It is a game drawn from that research and makes no claim to measure you.
> The sources are in the research note.

The words "the research note" are the link.

## Q7. The takers

The first screen asks who is taking the quiz. Stage is never shown to the taker. Every taker's `lean` in
`data/questions.json` is null (amendment 2026-09-27, ruling 9), and the app has no lean column, field or
setting a person can see.

| Order | key | Name | stage_target | stage_weight | Life-stage note |
|---|---|---|---|---|---|
| 1 | alex | Alex | evolved | 0.08 | Adult; Josh's sister, five years older than Josh |
| 2 | melissa | Melissa | evolved | 0.08 | Adult; Josh's sister, 13 years older than Josh |
| 3 | josh | Josh | evolved | 0.08 | Adult |
| 4 | carolyn | Carolyn | mature | 0.15 | Grandmother; Josh's mother |
| 5 | john | John | mature | 0.15 | Grandfather; Josh's father |
| 6 | andrew | Andrew | evolved | 0.08 | Adult; Alex's husband |
| 7 | oliver | Oliver | young | 0.08 | Age 13; lighter nudge so an evolved match stays easy to reach |
| 8 | todd | Todd | young | 0.15 | Age 10 |
| 9 | milo | Milo | young | 0.15 | Age 8; the items are written for him |
| 10 | guest | Someone else | evolved | 0 | No stage nudge |

Each row in `data/questions.json` keeps a `lean` key whose value is null, so `match()` stays a faithful
transcription. The stage nudge stays, as a nudge.

## Q8. Acceptance: what `test/check.py` MUST assert

Random draws use a fixed seed that the check prints. "Random answer set" means each of the 15 choices
drawn uniformly from 0 to 3. "The lattice" means every taker vector the quiz can produce: each trait
takes the ten values -1, -7/9, ..., 7/9, 1, giving 100,000 vectors.

A1. `data/corpus.json` has 1,025 species, ids 1 to 1025 once each, every Q5 field with the right type,
and a non-empty `flavor_texts` for every id not in `missing_flavor`.

A2. For every species, `auto_vector` and `matched_words` equal `tag()` recomputed from `flavor_texts`
and `data/lexicon.json`, within 0.0001. The check reports the share of species with at least one match.

A3. `data/lexicon.json` holds every seed entry of Q5, and no entry sits in two lists.

A4. `data/pool.json` matches pool.csv plus recorded swaps (at most 10, each from the reserve list), passes
every profile MUST in Q5, and its vectors equal `profileVectors()` within 0.0001.

A5. No `why` text repeats across profiles, and every `anchor` rule holds.

A6. `data/questions.json` passes every item MUST in Q2 and Q5: count, trait cycle, facets, levels, D5
position balance, word limits, Flesch-Kincaid at most 4.0 by the Q2 syllable rule, long-word rule,
negation regex, banned-topic words, at most four flavoured stems, echo rules, and IPIP source fields.

A7. `takers` equals the Q7 table exactly, and every taker's `lean` is null.

A8. For every pool member, `web/img/art/<id>.png` is a valid PNG and `web/img/ani/<showdown_id>.gif` is
a valid GIF, or a recorded static fallback that is a valid PNG. The check reports the fallback count.

A9. The check's Python `match()` and the web app's JavaScript `match()` (run under node) agree on the
winner for at least 1,000 random answer sets for every taker. Running the same inputs twice gives the
same winner.

A10. Coverage, pure trait distance to the nearest pool member with no penalties: over the lattice, the
maximum is at most 1.60 and the 95th percentile at most 1.00; over 20,000 random answer sets, the 95th
percentile is at most 0.75. The calibration simulation gave 1.40 to 1.52, 0.92 to 0.94, and 0.67 to 0.69.

A11. Reachability over the lattice: the guest reaches every pool member, and every named taker reaches at
least 60 members.

A12. Concentration over 20,000 random answer sets: no member takes more than 6% of guest results or more
than 16% of any named taker's results.

A13. Lean is void (rewritten 2026-09-27). Every taker in `data/questions.json` has `lean` null. Over
20,000 random answer sets for every taker, `match()` gives the same winner as a copy of `match()` whose
`leanPenalty` returns 0 for every input, in the Python copy and in the app's JavaScript. No pool data
under `web/` carries a `lean` field. The app writes nothing to localStorage, sessionStorage or cookies
that holds a lean or a gender. The visible text of `web/index.html` contains none of the words gender,
feminine, masculine, female or male, whole word and case insensitive. The check prints every line under
`web/` that contains `.lean` or `lean:` (the property, not the word in "Your answers lean most toward"),
and each such line MUST be the `leanPenalty` call in `match()` or a taker row whose `lean` is null.

A14. Stage behaviour over 20,000 random answer sets: Todd and Milo get a young member at least 40% of the
time, and Carolyn and John get a mature member at least 40% of the time.

A15. Result text over 2,000 random answer sets for every taker: both echoes appear verbatim, the block is
at most 110 words, and no banned word, framing, Barnum line, em dash or en dash appears. No Q6 screen
word appears in the block.

A16. `prose_check.py` runs over every human-read string (item stems, answers, echoes, profile
`personality`, `community` and `why`, and the visible text of `web/index.html`). Em dashes, banned words
and "not X but Y" shapes MUST be zero; the other counts are reported. No Q6 screen word appears in any
profile `personality`, `community`, `media` note or `why` text. The How it works text exists on the names
screen, holds at most 90 words, contains "Big Five" and "15", links the research-note URL of Q6, contains
none of the Q6 measurement words, and passes `prose_check.py`.

A17. The check reports, with no pass mark, the retest rates from a model where each answer moves one step
up or down with probability 0.3 (reflected at the ends): the share of retakes with the same Pokémon and
the share landing in the first result's top three.

A18. The live URL serves the app with Open Graph title and image tags, and a mobile-width run completes
the quiz for three takers with screenshots.

A19. The check is calibrated on a deliberately broken pool entry, and that entry fails at least one
assertion.

A20. No row of `spec/pool.csv`, no profile in `data/pool.json`, no recorded swap's `in_id` and no Q4
reserve carries an id from the screened-out list below (added 2026-09-27). The list is the one in
`spec/POOL-SCREEN.md` section 8, and the two MUST match.

```
29,31,32,38,39,40,43,44,50,51,52,54,66,68,79,80,88,89,96,97,98,99,100,101,102,104,105,108,109,110,122,124,128,129,130,132,134,138,139,140,141,142,143,195,199,202,206,209,210,230,241,248,282,287,289,299,316,317,321,325,326,345,346,347,348,349,359,398,399,400,408,409,410,411,416,418,425,428,429,431,432,446,463,476,478,495,498,508,532,560,562,563,564,565,566,567,568,569,576,587,607,609,618,629,630,635,696,697,698,699,704,706,727,758,763,765,775,778,779,780,816,835,845,849,858,865,866,867,872,877,880,881,882,883,889,898,909,911,915,977,979,983
```

## Q9. Forced choice or Likert

The quiz uses neither classic form. Every item is a single-trait graded choice (D3): one situation and
four concrete behaviour options, each scoring the same trait at a different level. The reasons, from the
research note, are these. Likert agreement invites acquiescence, which is largest in children, and its
usual fix, reversed items, is what young children misread. Classic forced choice across traits is
ipsative, which distorts profiles and cannot be repaired at 15 items without a fitted model. The graded
format has no agreement step, needs no negation, stays normative, and is how game-like personality
measures work. This keeps the plan's "scenario-style forced choice" in spirit, since the taker picks one
option, and drops the ipsative form the literature rules out.

## Q10. Limits on validity loss from rewording

The quiz is a new instrument built from validated content, and its own validity is unmeasured (D12). Six
rules hold the loss down, and A6 checks the first four.

1. Every item cites a public-domain IPIP source item and a BFI-2 facet, and its four answers express that
   item's content at four levels.
2. Each trait's three items sample three different facets.
3. Stems are real, everyday situations; at most four carry Pokémon flavour, and none needs Pokémon
   knowledge.
4. Each item scores one trait only, so no answer can leak into a neighbouring trait's score.
5. The panelist reads every item for content drift into a neighbouring trait and for an answer that is
   plainly better than the others.
6. The result never claims measurement (D10), and the trait bars carry no numbers.

## Q11. Child reliability

Milo is eight, Todd ten and Oliver thirteen. The literature expects noisier answers at those ages, and
the simulation shows that noise changes the single nearest Pokémon more than it changes the traits. The
contract handles it with these rules.

1. One quiz for everyone, written for the youngest reader (Q2 reading limits), with no negation, no
   agreement scale, no midpoint and four labelled options, which removes the failure modes found in
   children [10, 11, 12].
2. Children keep their own answers; their vectors are not shrunk toward the middle. Shrinking would hand
   every child a middling Pokémon, which is less true to their answers and less fun.
3. The result shows the trait bars, which are the stable part, next to the Pokémon.
4. The result presents the match as today's reading (D10) and quotes the answers behind it, so a
   different match on a later retake reads as a different set of answers, not a broken quiz.
5. A17 reports the retake rates, so the instability is on record.
6. Oliver's stage nudge is lighter (Q7), because at 13 a young-only result can feel babyish.

## Deviations from PLAN.md and the rulings

- Item format: the plan's "scenario-style forced-choice items" became single-trait graded choice, because
  multi-trait forced choice is ipsative at this length (Q9).
- Lean is void (amendment 2026-09-27, ruling 9). PLAN.md's "women get more feminine Pokémon, men more
  masculine" no longer holds, by Josh's own later ruling. The offence screen in Q4 takes its place.
- `auto_vector` uses the Pokédex lexicon only; base stats are stored and left out (Q5).
- The pool holds 149 species after the 2026-09-27 screen, within the 140 to 170 band; the plan said
  about 150.
- Retake stability: the quiz will often give a different Pokémon on a retake weeks later, for adults too.
  The plan's "precise and accurate" holds as determinism (same answers, same Pokémon) and as fidelity to
  the answers, not as stability across weeks. The contract states this openly (D12, A17).

## References

Numbers in square brackets refer to the source list in `spec/RESEARCH-PERSONALITY.md`.

## CHANGES (2026-09-27)

Josh's sister objected to the gender rule, and Josh ruled that it goes. He also ruled that no one may get a
Pokémon that could read as offensive or upsetting, and that the science must be visible. Subsystem DEFINE
applied four amendments in place. Everything not listed here stands as written.

1. Q3, lean void. Every taker's lean is null, so `leanPenalty` returns 0 on every call. The function and
   its call in `match()` stay for transcription fidelity. The three LEAN constants are marked unused. The
   lean part of "Why these weights" and the lean simulation figures are withdrawn. Nothing in the app
   stores, sends or shows a gender.
2. Q4, offence screen. The old exclusion table is replaced by the screen rule and a decision, with line
   bans, for every one of the 149 pool members. `spec/POOL-SCREEN.md` lists every species screened out and
   every species added, with reasons, and is part of the contract. The pool went from 160 rows to 149.
3. Q6, How it works. The names screen carries a collapsed "How it works" toggle of at most 90 words. It
   states the Big Five basis, the 15 items with three per trait and the nearest-match rule, links the
   research note, and makes no claim of measurement. A reference text is given.
4. Q7 and Q8, takers and checks. The Q7 table has no lean column, and every taker's `lean` is null. A13 now
   asserts that lean is null for every taker and that stubbing `leanPenalty` to 0 changes no result. A20 is
   new and asserts that no pool member, profile, swap or reserve carries a screened-out id.

Rules the amendments forced to change beyond those four.

- Q4 counts. The lean-by-stage table became a stage-only table: 60 young, 52 evolved, 37 mature.
- Q4 lean rules. They are void. The `lean` column stays in `spec/pool.csv` as a record, and nothing reads
  it.
- Q4 selection order. The Pokémon of the Year sentence no longer claims 29 of the top 30, because the
  screen removed several of them.
- Q4 reserve list. It was rebuilt from screened species. Pachirisu, Mareep, Electabuzz, Hitmontop and
  Scizor moved into the pool, and Tsareena, Vespiquen, Glameow, Emolga and Kingdra failed the screen.
  Weavile left without a screen verdict. The swap rule now protects the 140 to 170 band and the mature
  floor of 25, in place of the lean floors.
- Q5 profile rules. `lean` is optional in `data/pool.json` and is never read. Pool data shipped under
  `web/` MUST carry no `lean` field. The Chansey example lost its `lean` line, and the Alex taker example
  shows `"lean": null`.
- Q5 rating anchors. The table still names Jigglypuff, Tyranitar, Incineroar, Machamp, Tauros and Sobble.
  These are points on a rating scale for profile writers and are never shown to a taker, so the table stays
  as written. Screened-out species remain valid anchors.
- Q6 screen words. A new list of words MUST NOT appear in any profile string or reasoning block. It covers
  eating, sleeping, size, smell, mind and worth, temper, tears, age and death, and sex or gender. This
  enforces the rule that a why-sentence cannot be turned on the taker.
- A7 now also asserts a null lean. A15 and A16 now also enforce the screen words, and A16 checks the How it
  works text.
- Deviations. The lean bullet now records that the lean is void, and the pool bullet states 149.

What the next positions must act on. The stream must drop profiles for the 30 removed ids, write profiles
for the 19 added ids from their sketches in `spec/POOL-SCREEN.md`, set every taker's `lean` to null,
strip `lean` from shipped pool data, add the How it works toggle, and rewrite any profile sentence that
hits a screen word or a Q4 line ban. The enabling agent must add A20, rewrite A13, and extend A7, A15 and
A16. Profile workers that started from the 160-row csv are working on a stale pool.
