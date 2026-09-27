# CONFIRM: which-pokemon, integrator seam report

Integrator position (CONFIRM), one-shot, 2026-09-27. Everything below is something I ran, diffed, hashed
or grepped myself this session, against the live URL and the repo at HEAD, not a summary of what other
agents reported.

## CONFIRMED

1. **Pool identity.** `data/pool.json` has 149 profiles; `spec/pool.csv` has 149 rows. Their id sets are
   identical (checked as sets, no missing or extra ids either direction). None of the 149 ids appears in
   the 142-id POOL-SCREEN removed list from `spec/CONTRACT.md` A20 (checked by set intersection, empty).
   `web/data/pool.json` also has 149 profiles with the same id set as `data/pool.json`, and zero profiles
   under `web/` carry a `lean` field, while `data/pool.json` does carry `lean` on its rows (allowed, since
   the contract calls it optional and unread there).

2. **Q3/Q6 transcription.** I read `spec/CONTRACT.md`'s `takerVector`, `leanPenalty`, `stagePenalty`,
   `match` and `resultText` pseudocode next to `web/app.js` line by line. Every function is a faithful,
   unmodified transcription: same constants, same tie-break (`round6` key, then lower id), same sort order
   in `resultText` (align descending, then `abs(level)` descending, then index). No divergence found.

3. **Corpus-to-profile pipeline.** `scripts/lib.mjs` line 105 computes
   `raw = 0.75 * (rating/4) + 0.25 * auto_vector`, matching Q3 exactly. I did not just spot-check two
   species: I recomputed the entire pipeline (the 0.75/0.25 blend, then the rank-based spread across the
   pool) from `data/pool.json`'s own `ratings` and `auto_vector` fields for all 149 profiles in a script,
   and compared against the stored `vector` field. Zero mismatches across all 149. Pikachu and Chansey by
   hand: Pikachu's stored `auto_vector` (`[0.5, 0.4286, 0, 0, 0]`) equals its corpus entry exactly; same for
   Chansey (`[0, 0.3333, -0.3333, 0.8667, 0]`). The corpus tagging is load-bearing, not decorative.

4. **Live equals HEAD.** I downloaded the live `app.js`, `styles.css` and `data/pool.json` with `curl` and
   hashed them with sha256, then hashed the same three files in the working tree. All three pairs match
   byte for byte:
   `app.js` `b122bebd...0a8b0`, `styles.css` `5497b7ec...6dfd6`, `data/pool.json` `55ac1703...81240b0a1a65`.
   The live site is the exact build in this checkout, including the stream-3 stylesheet fix.

5. **My own check.py run**, live URL, seed 20260927, this session:
   `18 PASS, 0 FAIL (0 of them MUST), 0 SKIP, 2 REPORT-only` (A17, A18). Identical to the numbers in
   `spec/PANEL-VERDICT.md` and `DELIVERY.md`'s check tail, including A10's coverage figures, A12's
   concentration shares, A14's stage shares (Todd/Milo 76.85% young, Carolyn/John 50.18% mature, both well
   above the 40% floor), and A17's retest numbers. `test/CHECK-RESULT.md` is genuinely stale: it says so
   itself (`data/pool.json` "NO, still absent when this report closed"), predates the amended pool
   entirely, and I did not weight it. A18's mobile-playthrough sub-check failed all three attempts in my
   run too (`Locator.click: Timeout... locator resolved to <button>Alex</bu`, the same wrong-button race the
   panelist hit), which check.py's own status logic downgrades to REPORT rather than FAIL even though the
   assertion is marked `must=True` in code (see OPEN, item 2).

6. **Panel advisories.** Of `spec/PANEL-VERDICT.md`'s five ADVISORY findings, two (the untokenized
   `#fff` on `.names-grid button`/`.answers button`, and the 19px-tall `<summary>` tap target) are resolved:
   `web/styles.css` now defines `--card: #FFFFFF` and uses it there, and `.how-it-works summary` has
   `min-height: 44px; display: flex; align-items: center;`, exactly as `DELIVERY.md`'s stream-3 section
   describes, and this is the same `styles.css` the live site serves (confirmed by the hash match in item
   4). The other two (Andrew reaching a young-stage member; one item's answer reading slightly less warm)
   are open by the panelist's own design judgement, not by neglect: see OPEN below.

7. **Gender removal.** Every one of the 10 rows in `web/data/questions.json`'s `takers` array has
   `"lean": null` (checked programmatically, all 10). A grep for `gender|feminine|masculine|female|male`
   across every `.js`, `.html`, `.json` and `.css` file under `web/` returns zero hits. `leanPenalty`'s
   first line returns 0 whenever `takerLean` is null, which it always is, so the function is dead code kept
   only for transcription fidelity, exactly as the contract's CHANGES section describes.

8. **Q7 table.** `web/data/questions.json`'s takers match the Q7 table exactly on `key`, `name`,
   `stage_target` and `stage_weight` for all 10 rows, checked by direct comparison. My own check.py run's
   A14 line shows the stage nudge working as intended: Todd and Milo land on a young member about 77% of
   the time, Carolyn and John land on a mature member about 50% of the time, both comfortably clearing the
   contract's 40% floor.

9. The one real defect `test/CHECK-RESULT.md` flagged before delivery, a "stomach" screen-word hit in an
   early `questions.json` draft, is gone from the shipped `web/data/questions.json` (grepped directly,
   zero hits), consistent with A15 and A16 both reporting zero problems in my own run.

## OPEN

1. **Task-tracker gap, not a content defect.** `spec/PANEL-VERDICT.md` is a complete, 180-line, dated
   artifact (mtime 15:28) that reads as task #5's finished product, but task #5 itself still shows
   `pending` with no owner in the tracker, and task #6 (mine) is formally `blockedBy: #5`. I could still
   claim and work #6, so this did not block my own pass, but the lead should close #5 once it looks at
   `spec/PANEL-VERDICT.md`, since nothing about the artifact itself is incomplete.

2. **A18's live-quiz check is weaker than a plain reading of Q8.** Contract Q8 A18 says a mobile-width run
   must complete the quiz for three takers with screenshots. `test/check.py`'s A18 marks itself `must=True`
   but its status logic only fails on missing Open Graph tags; a 0-for-3 playthrough result (which is what
   both the panelist and I independently got, same failure mode both times) still reports as REPORT, not
   FAIL. That means a real future regression that broke the live quiz's clickability could still show a
   green summary line from this check alone. Today the gap is covered by the panelist's six independently
   completed live playthroughs with screenshots and diffed animation frames, not by the automated gate.
   Worth a look if `test/check.py` is ever revisited, not blocking this delivery.

3. **Two ADVISORY findings stand open by judgement, not by a missed fix.** Andrew, an adult, can land on
   Rookidee (young-stage, genus "Tiny Bird Pokémon") because stage is a nudge, never a filter, by the
   contract's own design (needed so every named taker can reach at least 60 pool members). The panelist
   read the actual result text and found no plausible offensive reading. Separately, item q04's "an adult
   nearby will handle it" answer may read as slightly less warm than its three siblings; the panelist judged
   it a reasonable, non-mean choice, not a rule violation. I re-read both writeups and found no basis to
   overturn either judgement call myself.

4. **Retest instability is real and worth stating plainly, since Josh asked for "precise and accurate."**
   My own run, matching the panelist's and DELIVERY.md's: if the same person retakes the quiz, only 6.5% of
   retakes return the same Pokémon, and 13.6% land in the original result's top three. The contract treats
   "precise and accurate" as determinism for identical answers, not stability across retakes, and states
   this as a deliberate deviation from PLAN.md's wording. That is a real, not cosmetic, gap between Josh's
   phrase and what ships, and it should reach him in plain terms rather than being absorbed into "PASS."

5. **Manual deploy path.** The live site is served from a `gh-pages` branch built by `git subtree split`
   and force-pushed by hand, not by the GitHub Actions workflow the plan called for, because the OAuth
   token lacks the `workflow` scope and only Josh can grant it interactively. Any future edit to `web/`
   needs that same manual re-deploy step (confirmed by reading `DELIVERY.md`'s own account of the stream-3
   redeploy, which used the identical branch-split method a second time).

6. **Depth limit on my own verification.** I re-ran `python test/check.py` once and trust its own
   arithmetic for the 20,000-draw Monte Carlo assertions (A10 through A15); I did not reimplement those
   simulations a third time by hand. That is a real bound on how deep my own confirmation goes on those
   specific figures, separate from the A9 cross-language agreement check, which is a direct Python/JS
   comparison I did verify the logic of by reading both `match()` implementations myself.

## Summary for Josh

The quiz is live at https://joshuamatalon.github.io/which-pokemon/. It reads the full Pokédex, all 1,025
species, and tags each one from its own official game text, but the quiz can only hand back one of 149
hand-researched Pokémon, not all 1,025, because 15 questions cannot tell apart a thousand outcomes and a
random obscure match would just feel like a miss. The gender rule you asked to remove is gone. No answer
ever sets or reads a gender or a lean, and I checked the code myself to confirm that path is dead. In its
place, every one of the 149 finalists was read one by one and screened for anything that could land as a
joke about someone's looks, age, weight or intelligence, so a Purugly or a Snorlax simply is not in the set
your family can land on. One number worth knowing: if the same person takes the quiz twice, only about
6.5% of retakes give back the same Pokémon, and about 13.6% land in that person's first top three, so the
result is best read as today's snapshot rather than a fixed label.
