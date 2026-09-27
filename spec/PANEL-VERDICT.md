# PANEL-VERDICT: which-pokemon, independent product verification

Panelist position (CHALLENGE), one-shot, 2026-09-27. Findings committed from my own six live playthroughs,
a full-pool offence sweep, a design-token count and my own `test/check.py` and `prose_check.py` runs,
before reading `DELIVERY.md` or `test/CHECK-RESULT.md`. Section 7 is the post-hoc comparison, added last.

## Verdict: PASS WITH FINDINGS

Nothing found blocks sending the link. `test/check.py` (my own run, same session, live URL) shows 18 PASS,
0 FAIL (0 of them MUST), 2 REPORT-only. The offence screen holds across all 149 shipped profiles by direct
word sweep. Six independent live playthroughs at 390x844 all completed, rendered both images, and produced
positive, specific, non-mocking results. Five ADVISORY findings below are real and worth a look, none of
them rise to something a family member could read as a joke about themselves.

## 1. The six playthroughs (live URL, headless Chromium, 390x844, `spec/panel_play.py`)

| Taker persona | Species | Genus | Shots |
|---|---|---|---|
| Carolyn (calm, orderly, warm grandparent) | Suicune | Aurora Pokémon | `spec/panel-shots/carolyn-result-1.png`, `-2.png` |
| Milo (energetic, curious 8-year-old) | Meloetta | Melody Pokémon | `spec/panel-shots/milo-result-1.png`, `-2.png` |
| Andrew (bold, competitive adult) | Rookidee | Tiny Bird Pokémon | `spec/panel-shots/andrew-result-1.png`, `-2.png` |
| Alex (social, expressive adult) | Espeon | Sun Pokémon | `spec/panel-shots/alex-result-1.png`, `-2.png` |
| Guest, middle-level options every item | Braixen | Fox Pokémon | `spec/panel-shots/guest-result-1.png`, `-2.png` |
| Josh, first button on every screen incl. every answer (index 0 throughout) | Sprigatito | Grass Cat Pokémon | `spec/panel-shots/josh_first-result-1.png`, `-2.png` |

Raw data (choices, echoes, all three reasoning lines, image src, console errors): `spec/panel-shots/results.json`.

For every run: both images rendered (`art_ok`/`ani_ok` true, verified via `naturalWidth > 0`), zero
console/page errors, the reasoning quoted two of the taker's own echoed answers verbatim (not generic),
and the three why-lines were specific to that species (Pokédex facts, named media, or its canon trait), not
interchangeable boilerplate. I read every result for mockery, offence or embarrassment toward the taker (a
child or a parent): none found. Carolyn's Suicune, Alex's Espeon and Milo's Meloetta read as clean fits;
Andrew's Rookidee and the guest's Braixen are discussed under Findings 3 and 4.

**Animation, confirmed not asserted.** I screenshotted each result twice, one second apart, and diffed the
two images with PIL. All six diffs were non-empty and localized to exactly the animated-sprite's bounding
box (e.g. Carolyn: `(295, 414, 476, 567)`), never the static artwork above it. The animated sprite is
genuinely animating, for all six species tested, not a static GIF or a frozen first frame.

## 2. The 149 profiles, offence sweep

I built the Q6 screen-word list (eating/sleeping, size/body, smell/dirt, mind/worth, temper, tears,
age/death, sex/gender — same list `spec/CONTRACT.md` Q6 states) and scanned every profile's `personality`,
`community`, `media` title/note and `why` text (894 strings) for a whole-word, case-insensitive hit.
**Zero hits across all 149 profiles.** I separately read a random sample of 10 of the 37 "mature"-bucket
profiles (the ones nudged toward Carolyn and John) in full: Meganium, Kangaskhan, Milotic, Mewtwo,
Aegislash, Volcarona, Altaria, Empoleon, Suicune, Samurott. Every one reads as dignified, warm and
grandparent-safe; none carries an age joke.

I also ran `prose_check.py` over the same 894-string extract: 0 banned words, 0 em dashes (the two MUST-be-
zero fields in A16). Full output: `spec/panel-shots/pool_text.txt` and the console log below. The tool also
flagged 3 "fragment"-like lines, but those trace to my own extraction script joining a profile's media
`title` directly to its `note` with no punctuation between them (an artifact of how I built the scratch
file, not of the product) — and `personality`/`community`/`media` are not even rendered on the live result
screen (only `why` texts and the generated lines are), so this has no user-facing effect either way.

## 3. ADVISORY: an adult can land on a young-stage, small-genus species

Andrew (adult, `stage_target: evolved`) landed on Rookidee, `stage: young`, genus "Tiny Bird Pokémon". This
is inside the contract's own design: stage is a nudge (weight 0.08 for Andrew), never a filter (Q3, and
A11 explicitly requires every named taker to reach at least 60 pool members, which only works if stage
never hard-excludes). The species itself passed the offence screen and carries no line ban. Reading
"Tiny Bird Pokémon" as a comment on an adult man's own size is a stretch — it is the bird's own size
class, the same construction as "Seed Pokémon" or "Mouse Pokémon" — and the why-text ("bravely challenge
any opponent, no matter how much bigger or stronger they are") reads as a compliment about grit, not a
put-down. I could not construct a plausible offensive reading of this specific result. Flagging only
because the offence screen in `spec/POOL-SCREEN.md` was written species-by-species without testing which
takers can actually reach a "young" member, and this is the first concrete case of it happening to an
adult. Not blocking.

## 4. ADVISORY: one item may skew toward the "kind" answer

`q04` ("You notice a puppy wandering alone near the park. What do you do?") has one answer, "I figure an
adult nearby will handle it" (level -3, the Strong-willed extreme), that reads less warm than the other
three. `spec/RESEARCH-PERSONALITY.md` section 3 names exactly this risk ("people lean toward the answer
that sounds better") and the contract requires all four options be "equally acceptable behaviours" (D4).
The option is still a reasonable, non-mean choice (passing responsibility to a nearby adult is ordinary,
sensible advice for a child to hear), so this is a soft judgement call, not a rule violation, and I would
not fail A6 over it. Worth a second look if the item set is ever revised.

## 5. ADVISORY: two design-standard misses on the rendered page

Measured from computed styles in the browser (`spec/panel_design.py`, `spec/panel-shots/design.json`), not
from the CSS source:

- **Type sizes: exactly 3** (16px, 13px, 28px) across names, quiz and result screens combined. This
  confirms PLAN.md ruling 12's fix landed (the four-size regression, 13/16/20/28, is gone; `h2` and
  `.stem` now render at 16px). No violation here, stated for the record since it was a named prior finding.
- **An untokenized color.** `.names-grid button` and `.answers button` render with `background-color: rgb(255, 255, 255)`
  (pure white), not `var(--paper)` (`#F7F5F0`), the page's own background token. This is a real, if small,
  "ad hoc colour" against DESIGN-STANDARD's rule ("no ad hoc colours, sizes or fonts"; the palette lists
  `paper` as `#F7F5F0`, not `#FFFFFF`). It does not hurt legibility or contrast; it is a second, undeclared
  neutral alongside the declared palette. Fonts stayed at 1 (Segoe UI stack) throughout, well under the
  2-font ceiling.
- **The "How it works" tap target is short.** The `<summary>` element measures 350x19px. The mission
  checklist and DESIGN-STANDARD's house rule both look for tap targets of at least 44px; the CSS's own
  `button { min-height: 44px }` rule is honored everywhere else (names buttons 169x56, answer buttons
  350x52, quiz-back 67x49, result actions 350x49) but a `<summary>` is not a `button` and gets no such
  rule, so its own line-height (19px) is all a tap has to land on. In practice the full 350px-wide row
  still registers a tap because `<summary>` is the whole clickable element, but its vertical target is
  under a third of the stated minimum. Worth a `min-height: 44px` and vertical centering if anyone touches
  `styles.css` again. Not blocking: it is a secondary disclosure control, not part of the 15-question flow
  a child or grandparent must get through unaided.

## 6. My own check runs

`python test/check.py` (live URL, my own invocation, this session):

```
A1   PASS   ids 1..1025 complete; field/type schema OK for 1025 species
A2   PASS   0/1025 species tag() mismatch. REPORT: 81.1% of species have >=1 lexicon match
A3   PASS   seed coverage + no-duplicate check: OK
A4   PASS   149 profiles checked against pool.csv + swaps
A5   PASS   0 why-sentence problems across 149 profiles
A6   PASS   15 items checked
A7   PASS   takers list equals Q7 table exactly
A8   PASS   0 image problems across 149 profiles. REPORT: 0 static fallbacks
A9   PASS   python/js match() agreement on 10000 cases (10 takers x 1000), seed=20260927: 0 disagreements
A10  PASS   seed=20260927 lattice max=1.500 p95=0.996; random(20000,seed=20260927) p95=0.717
A11  PASS   lattice reach counts: alex 149 ... guest 149 (all >= 60)
A12  PASS   seed=20260927 top-member share per taker: all under caps (max 6.92% named, 5.04% guest)
A13  PASS   unit-case py=OK js=OK; questions-null-lean=OK; stub-vs-real(20000x10)=OK, 0 disagreements;
            web: 11 lean-mentioning lines under web/, 0 flagged; index.html gender-word scan: clean
A14  PASS   seed=20260927 target-stage share: todd 76.85%, milo 76.85%, carolyn 50.18%, john 50.18%
A15  PASS   seed=20260927 result-text checks over 2000 draws: 0 problems
A16  PASS   prose_check.py over 1029 strings + index.html: em-dashes/banned/neg-parallel 0; how-it-works 82 words
A17  REPORT seed=20260927 guest retest over 2000 draws: same-Pokemon 6.5%, in-original-top-3 13.6%
A18  REPORT OG tags: title=True image=True. 0/3 heuristic mobile playthroughs completed (SUSPECTED, not CONFIRMED)
     HEURISTIC failures: Locator.click timeout on all 3 attempts against a working button (I clicked the
     same "Alex" button successfully with my own script seconds later, same URL) -- this is check.py's own
     harness being flaky, not a live-site defect. My section 1 above supplies the real evidence A18 wants:
     six completed mobile playthroughs, not three, with screenshots, on this exact URL.
A19  PASS   self-contained calibration: clean pair -> PASS, pair with a duplicated why sentence -> FAIL
A20  PASS   149 pool.csv rows, 149 pool.json profiles checked against 142 screened-out ids
SUMMARY: 18 PASS, 0 FAIL (0 of them MUST), 0 SKIP, 2 REPORT-only
```

Full console capture: `spec/panel-shots/check_output.txt`. `prose_check.py` output over the pool text extract:
`spec/panel-shots/pool_text.txt` produced `words 25017 sentences 1296 ... banned 0 [] ... em-dashes 0`.

`How it works` link (`https://github.com/joshuamatalon/which-pokemon/blob/main/spec/RESEARCH-PERSONALITY.md`)
resolves: `curl -s -o /dev/null -w "%{http_code}"` returned `200`. The toggle text on the live page is the
contract's 81-word reference text verbatim, states the Big Five basis, 15 items at three per trait, and the
nearest-match rule, and makes no measurement claim (checked by eye against Q6's banned-word list).

## 7. Comparison with DELIVERY.md and test/CHECK-RESULT.md (read after committing the above)

No disagreement on anything load-bearing. `DELIVERY.md`'s own "Check tail" reports the identical numbers I
reproduced independently (A10 lattice max 1.500/p95 0.996, A12 percentages, A14 76.85%/50.18%, A17
6.5%/13.6%), which is strong evidence that report was not fabricated. `DELIVERY.md` deviation 8 already
names the same A18 harness flakiness I hit and reaches the same conclusion (site fine, check's own
Playwright selector is the problem) — I confirm that independently rather than taking it on faith, since I
ran the identical `python test/check.py` command myself and watched the same three timeouts, then
immediately drove the same live URL successfully with my own script. `DELIVERY.md`'s "Observe" section
only demonstrates two takers (Milo, Carolyn) with its own ad hoc script; my six playthroughs close that gap
more completely and were run without reading DELIVERY.md first. `test/CHECK-RESULT.md` is stale (it was
written before `DELIVERY.md` landed, while `data/pool.json` was still missing, and says so honestly) — it
is not evidence about the current shipped state and I did not weight it. None of my five ADVISORY findings
(sections 3-5) appear in either upstream document; they are new.

## What would falsify this verdict

A BLOCKING finding would be: a profile string carrying a screen-word hit my sweep missed (I scanned exact
whole-word matches only, not synonyms or non-English text); a playthrough producing a result that reads as
mocking on a wording I didn't consider; `check.py` failing a MUST assertion on a re-run against a changed
live site; or the "How it works" link going stale. I re-ran the sweep and the live check once each in this
session (not repeatedly), so a flake in either is possible but I have no evidence of one.

## Confidence

CONFIRMED for: all six playthroughs completing with no console errors and both images rendering; the
sprite being genuinely animated in all six; zero screen-word hits across 149 profiles; `check.py`'s 18
PASS/0 FAIL/2 REPORT on this session's live run; the How it works link resolving and its text matching the
contract; the type-size count (3) and font count (1) on the rendered page.

SUSPECTED, not confirmed: that no reading of any of the 149 profiles' text could ever land badly for one
of the nine specific family members (I read a 10-species mature sample in full plus the mechanical sweep
across all 149, not every one of the 149 personality/community paragraphs word by word); that the q04
social-desirability observation actually changes any real taker's answer in practice (I judged the wording,
I did not run a live human test).
