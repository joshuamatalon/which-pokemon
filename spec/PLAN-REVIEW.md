# Plan review — which-pokemon

Reviewer: panelist (plan review), one-shot. Reviewed against `PLAN.md` as written 2026-09-27.

VERDICT: APPROVE WITH CHANGES

## Findings

1. BLOCKING — the gender rule is stated as a raw binary ("Women get more feminine Pokémon, men more
   masculine") with no fallback named for anyone who does not fit that binary. Nine specific named people
   are listed and none currently needs a fallback, but the CONTRACT (task 1) must state the rule as a
   default nudge inside a filter that already allows neutral, not a hard partition, and must say what
   happens if that ever stops being true. As written, "filtered by lean" in the Matching section reads
   as a hard filter (women: feminine or neutral; men: masculine or neutral), which forecloses, say, a
   father matched best by his trait vector to a feminine-leaning Pokémon. A hard filter is also how this
   becomes the facade risk Josh should not want: a result determined by gender before the quiz answers
   are even scored. Recommend: lean should nudge distance (small penalty for the disfavored lean, not
   exclusion), so the trait match still wins when it clearly should, and the CONTRACT must justify the
   exact weight given to lean versus trait distance in the scoring formula (question 3 in the contract
   list already asks for the lean filter and tie-break, but must also require this justification).

2. BLOCKING — the plan hands the personality-science research to the DEFINE position (subsystem, task 1),
   correctly, but the budget for it ("at least eight cited primary or review sources") is not enough of a
   brief on its own. The RESEARCH note must explicitly answer, and the CONTRACT must inherit answers to:
   why forced-choice over Likert for a mixed 8-to-60-plus family audience, what the literature says about
   validity loss when a validated short instrument (TIPI, BFI-10, Mini-IPIP) is reworded into
   Pokémon-flavored items, and what happens to test-retest reliability at 12-15 items for an 8-year-old
   reader. Without those three answers written down, "the trait model comes from the research" is a claim
   the CONTRACT cannot be checked against, only trusted. This is fixable by adding those three questions
   to the eight already listed under "Questions the CONTRACT must answer" (making it eleven), not by
   redoing the decomposition.

3. ADVISORY — the ~150-of-1,025 pool narrowing is stated honestly (line 43-49 says so directly, and gives
   a real reason: a ~12-15 item quiz cannot discriminate 1,025 outcomes and a bad-fit obscure result reads
   as a miss for a family member). That is the correct call and the correct amount of pool for nine takers
   plus reruns. The risk is not the number, it is coverage: nothing in the plan requires the pool to
   actually cover the trait space the nine people are likely to land in before the pool is finalized. Add
   one line to the CONTRACT acceptance criteria (already implied by "coverage of the trait space" but not
   checkable) requiring that the pool's trait vectors, plotted against the taker vectors from the eight
   named adults' expected profiles, have no taker further than some stated distance from their nearest
   pool member. Otherwise "about 150" is asserted, not demonstrated.

4. ADVISORY — the eight contract questions are close to right and cover the mechanically necessary ground
   (traits, items, scoring, pool, schema, result text, names, acceptance). Missing: a ninth question on
   what happens on a genuine near-tie between two very different pool members (the plan says "tie-break"
   exists in question 3 but does not ask the CONTRACT to state whether the tie-break is deterministic
   given identical answers across repeat takers, e.g. two children answering identically). Also missing:
   an explicit question about minimum distance from EVERY pool member (the "unreachable outcome" case) —
   what the app does if the taker's vector sits equidistant from three pool members or if a profile is
   simply never the nearest match for any plausible answer combination. Recommend folding this into
   question 8 acceptance criteria: check.py must assert every pool member is reachable by at least one
   simulated answer combination, which the enabling position's 20k-answer simulation (task 3) can already
   produce as a side effect, so no new artifact is needed, only a named assertion.

5. ADVISORY — facade risks are mostly designed out: profile text is hand-researched, corpus tags are
   checkable, scoring is deterministic, the enabling position runs a 20k-answer simulation and a
   known-bad calibration. The one facade risk not covered anywhere is generic Barnum flattery inside the
   handwritten "three positive why sentences" per pool profile — nothing enforces that those sentences
   are specific to that species rather than generically flattering (a sentence like "you bring energy to
   every room" fits nearly any result). Recommend the CONTRACT's result-text rules (question 6) require
   each profile's why-sentences to reference something species-specific (a stat, a canon trait, a named
   media appearance), and the check.py prose pass should grep pool.json for sentence reuse across
   profiles as a cheap facade test.

6. ADVISORY — the nine named people are handled reasonably: ages given for the three children (13, 10, 8)
   support the "reading level an 8-year-old can follow" requirement in the trait-model ruling, and stage
   nudges (children toward youthful stages, adults toward evolved, grandparents toward mature) are a
   sound design answer to "never offensive." One gap: Carolyn and John are "60s or older" per this task's
   own framing, but the plan's stage nudge only names three buckets (youthful, evolved, mature/wise) with
   no named rule distinguishing a grandparent from a plain adult beyond "mature or wise" — that is fine as
   a design choice but the CONTRACT should confirm mature/wise pool members exist and are not, themselves,
   a small or unflattering subset (an unintentional joke about being old is exactly the "mocking" failure
   Josh named). This is a check, not a redesign.

7. ADVISORY — one-shot with 8 profile workers for PRODUCE is a reasonable scale call: ~150 profiles at
   ~20 each per worker is bounded, parallel, and each worker's artifact (a slice of pool.json) is
   independently checkable against the CONTRACT's profile schema. The risk is not the worker count, it is
   that the plan does not say who reconciles overlapping or duplicate research (e.g., two workers both
   independently profiling a starter that appears in two different "recognisability" buckets). This is
   a one-line addition to the PRODUCE task, not a decomposition change: workers claim non-overlapping id
   ranges from `spec/pool.csv`, which task 1 already produces before task 2 starts, so the ordering
   already prevents the collision — flagging only because the plan does not say so explicitly and a
   future reader could assign ranges by name instead of id and collide.

8. ADVISORY — decomposition otherwise serves Josh's intent well: research is DEFINE-position and gates
   PRODUCE (correct ordering, the trait model cannot be invented ad hoc by whichever worker gets to it
   first), the corpus/pool split correctly separates "read everything" from "produce curated results,"
   and the enabling position's calibration-on-known-bad plus 20k-answer simulation is the right shape of
   check for a matching function that must never look hardcoded. The "3D animated sprite (the Champions
   Lab kind)" language matches what champions-lab actually ships (Showdown's animated sprite set, which
   for Gen 6+ species are renders of the 3D in-game models); this is not a bait-and-switch as long as the
   pool skews toward Gen 6+ species where that holds, worth a one-line CONTRACT note but not blocking.

## What was checked

Read `PLAN.md` in full. Confirmed `data/` and `test/` are still empty (nothing pre-built ahead of review).
Read `champions-lab/README.md` to check the "3D animated sprite" claim against what that project actually
serves (Showdown sprite collection, MIT-licensed, confirms the source is real and matches the plan's
description). Did not read DESIGN-STANDARD.md or WRITING-STANDARD.md line by line; the plan's design
section (Champions Lab tokens, 4px grid, prose_check.py) names concrete, checkable artifacts rather than
adjectives, which is the signal that matters for a plan review — deferred deep design-standard comparison
to the product-verification panelist pass (task 4), which reviews the live rendered app.

## Why APPROVE WITH CHANGES and not REJECT

The decomposition, ordering, and budget are sound and nothing here requires re-cutting tasks. Findings 1
and 2 are BLOCKING because they are cheap to fix now (add clauses to the CONTRACT's question list and the
RESEARCH brief) and expensive to discover after 150 profiles and a live URL exist. Findings 3 through 8
are ADVISORY: real, worth the subsystem and stream positions reading before they start, but none of them
invalidates the plan's shape.
