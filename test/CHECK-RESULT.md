# CHECK-RESULT: which-pokemon (amended contract, 2026-09-27)

Enabling position (INSTRUMENT), second pass. This supersedes the first enabling agent's CHECK-RESULT.md
now that spec/CONTRACT.md carries its 2026-09-27 CHANGES section (lean void, offence screen, How it
works toggle). One command:

```
python test/check.py [--root PATH] [--base-url URL] [--seed N] [--skip-a18]
```

Default `--root` is the project root; it reads `data/corpus.json`, `data/pool.json`,
`data/questions.json`, `data/lexicon.json`, `spec/pool.csv` and `web/app.js`/`web/index.html` under that
root and prints one line per assertion (A1 to A20), then a summary and a nonzero exit code iff a
MUST-marked assertion FAILed on data that was actually present. A missing input SKIPs, it never reads as
a pass. A pass here means the data agrees with the contract on the axes this file checks -- see "What
this instrument did not check" at the end before treating a green run as proof of anything else.

## (0) What changed in test/check.py for the amendment

- **A13, rewritten.** The old A13 measured a feminine/masculine result split; that concept is gone. The
  new A13 checks four things in one assertion, all MUST: (1) a transcription-fidelity unit case --
  `leanPenalty`'s constants (LEAN_SAME/NEUTRAL/OPPOSITE) are still correct in both the Python copy and,
  via a small node-harness call, the app's own JavaScript `match()`, using a synthetic NON-null-lean
  taker (this exists because every REAL taker's lean is null now, so a broken constant is otherwise
  invisible to any real-data run -- see the note below on why this matters); (2) every taker's lean is
  null, in `data/questions.json` and in check.py's own Q7 copy; (3) over 20,000 random draws per taker,
  the real `match()` (whose leanPenalty already returns 0 for a null taker lean) agrees with a copy of
  `match()` with leanPenalty stubbed to return 0 unconditionally -- 0 disagreements expected always,
  since (2) makes it near-tautological, but it is a real regression guard against the null check quietly
  breaking; (4) no line under `web/` mentions `.lean`/`lean:`/`"lean"` outside `leanPenalty()` itself or a
  taker row whose lean is null, `web/index.html`'s visible text carries no gender word, and a HEURISTIC
  regex scan finds no `localStorage`/`sessionStorage`/`document.cookie` call site mentioning lean or
  gender. CONTRACT.md's own text sizes the stub comparison at "20,000 random answer sets for every
  taker"; the mission order that spawned this pass paraphrased it as "2,000" -- I followed the contract,
  since that is the definition this check answers to, not the paraphrase. Flagging the discrepancy here
  rather than picking silently.
- **A7** now runs against a Q7_TAKERS constant with every `lean` set to `None` (previously feminine/
  masculine per taker); the comparison logic (`takers == Q7_TAKERS`) is unchanged.
- **RESERVE_IDS** updated to the amended Q4 reserve list (Marill 183, Minun 312, Mienfoo 619, Milcery
  868, Togetic 176, Audino 531). The old set included ids the 2026-09-27 screen dropped from the
  reserve (Tsareena 763, Vespiquen 416, Glameow 431, Emolga 587, Kingdra 230) and ids that moved INTO the
  pool itself (Pachirisu 417, Mareep 179, Electabuzz 125, Hitmontop 237, Scizor 212) -- keeping the old
  set would have made A4 wrongly accept a swap-in that is no longer a reserve, or wrongly reject one of
  the new pool members if it were later swapped back out.
- **A4** needed no code change: it already reads the live `spec/pool.csv`, so it automatically sees the
  screened (149-row) pool now that subsystem-2 rewrote that file in place.
- **A20, new.** No row of `spec/pool.csv`, no profile in `data/pool.json`, no swap `in_id` and no id in
  check.py's own `RESERVE_IDS` may be one of the 142 ids in `spec/POOL-SCREEN.md` section 8 / CONTRACT.md
  A20's list (copied verbatim into `A20_REMOVED_IDS`).
- **A15** adds the Q6 screen-word list (a superset of the pre-existing Q6_BANNED_WORDS) to its scan of
  the reasoning block.
- **A16** now also collects profile `media` notes (a schema field the original A16 omitted), checks the
  new Q6 screen-word list against profile personality/community/media/why text specifically, and adds a
  HEURISTIC extraction of the "How it works" toggle text from `web/index.html` -- word count <=90,
  contains "Big Five" and "15", links `spec/RESEARCH-PERSONALITY.md` on GitHub, and carries none of the
  Q6 measurement-claim words.
- **`pool_arrays()` and `match()`** now use `p.get("lean")` instead of `p["lean"]`, since lean is optional
  on a profile per the amended Q5 and a profile omitting it entirely is now expected, not malformed.
- **`main()`'s sim_profiles filter** no longer requires a profile to carry a valid lean value (it used to
  require `p.get("lean") in ("feminine","masculine","neutral")`, which would have silently excluded every
  real profile the moment the stream stopped writing that optional field).

## (a) Calibration on a known-bad

Two layers, both required before this instrument counted as calibrated for this pass.

**A19, self-contained, unchanged in behaviour, runs on every invocation:**

```
A19  PASS   self-contained calibration: clean pair -> PASS, pair with a duplicated why sentence -> FAIL
```

**A20, ad hoc probe (not wired into the fixtures, done once by hand to confirm the new assertion can
fail before trusting a real-data PASS from it):** injecting a screened-out id (29, Nidoran-female) into a
copy of the real `spec/pool.csv` rows and calling `a20_screen()` directly:

```
clean: PASS 149 pool.csv rows, 0 pool.json profiles checked against 142 screened-out ids
dirty: FAIL 150 pool.csv rows, 0 pool.json profiles checked against 142 screened-out ids
       ['spec/pool.csv rows carry screened-out id(s): [29]']
```

**Full known-bad fixture, `test/fixtures/known_bad/` (rebuilt this pass, see below), a byte-for-byte
clone of `test/fixtures/good/` with four planted defects:**

1. A `why` sentence on one profile overwritten with another profile's `why` sentence (duplicate).
2. An em dash inserted into a different profile's `why` sentence.
3. The art PNG for one profile's id deleted from disk.
4. `LEAN_OPPOSITE` changed from `0.25` to `0.50` in the fixture's copied JS `match()`.

Command: `python test/check.py --root test/fixtures/known_bad --skip-a18`. Real result, exit code 1:

```
A5   FAIL   3 why-sentence problems across 10 profiles
A8   FAIL   1 image problems across 10 profiles. REPORT: 0 static fallbacks
A13  FAIL   ... JS leanPenalty transcription unit case: MISMATCH: got [2]/[2], want [2]/[1]
A15  FAIL   seed=20260927 result-text checks over 2000 draws: 241 problems (em/en dash, all 10 takers)
A16  FAIL   prose_check.py ...: 1 em/en dash occurrences (prose_check)
SUMMARY: 9 PASS, 5 FAIL (5 of them MUST), 1 SKIP, 5 REPORT-only
FAILED (MUST): ['A5', 'A8', 'A13', 'A15', 'A16']
```

Full transcript: `test/.run_known_bad.txt`. This is the important result of this pass's calibration work:
**defect 4 (the changed LEAN_OPPOSITE constant) would have gone completely uncaught under the amended
contract** if A13 were only rewritten to check the new null-lean/stub/web-scan properties, because every
real taker's lean is null now and `leanPenalty` never reaches that constant in production. The old A13's
"unit case" (calling `match()` with a synthetic non-null-lean taker) is the only thing that can still see
a broken constant, so I kept it and extended it to also probe the JS side via the node harness -- which
is what caught defect 4 above (`js=MISMATCH`). Without that extension, the known-bad fixture would have
passed A13 clean despite carrying a real, deliberately-planted defect, which would have meant reporting a
calibrated instrument that was not actually calibrated against its own fixture. This is the specific,
unplanned finding referenced by the doctrine's "never observed reporting FAILURE is not an instrument"
bar for this pass.

**The same command against the rebuilt `test/fixtures/good/`** is clean:

```
SUMMARY: 14 PASS, 0 FAIL (0 of them MUST), 1 SKIP, 5 REPORT-only
SKIPPED (not evidence of failure, evidence of missing input): ['A18']
```

Full transcript: `test/.run_good.txt`.

**Why the fixtures needed rebuilding, not just re-running.** Two of the original fixture's ten pool ids
(29 Nidoran-female, 32 Nidoran-male) are now on the A20 screened-out list, since their names state a sex
and the lean filter that used to gate them away from any taker no longer exists -- so the ORIGINAL good
fixture would fail the new A20 by construction, which is not a defect, just a stale choice of ids. I
substituted Butterfree (12) and Alakazam (65), both still KEEP rows in the screened `spec/pool.csv`.
Separately, the original fixture copied the REAL, in-flight `data/questions.json` verbatim to save
effort; that stopped being safe the moment the real file's own content turned out to contain a genuine
issue against the new contract (item q10's answer/echo text reads "I feel my stomach flip...", and
"stomach" is one of the new Q6 screen words -- see the note below, this is a real stream-side finding,
not a fixture bug). A calibration baseline that inherits defects from the thing it is meant to judge
stops being independent, so `test/fixtures/build_fixtures.py` now builds a small, hand-authored,
schema-valid 15-item quiz and a valid "How it works" `web/index.html` (the contract's own 81-word
reference text) for the good fixture, instead of copying the real files. I did not touch the real
`data/questions.json` -- that belongs to the stream, and it is reported below and directly to stream-2,
not silently patched around.

**A real-content finding for stream-2 (not a check defect):** `data/questions.json` item `q10`'s answer
at level -1 reads "I feel my stomach flip and thoughts race a while." and its echo repeats "stomach"
verbatim. "stomach" is on the new Q6 screen-word list (size and body). Since the reasoning block quotes
echoes verbatim (Q6's `resultText()`), this item will make "stomach" appear in a live result screen for
whichever taker draws it, which A15 will flag against the real pool the moment `data/pool.json` lands
(it already flags it against the fixture's borrowed-real-item test run before the fixture was rewritten,
see above). This was reported to stream-2 directly; it is not fixed in `data/questions.json` here, since
that file is outside this position's boundary (test/ only).

## (b) Run against the real data

`DELIVERY.md` had not been written by the 40-minute polling deadline (poll `test/.poll2.sh` was started
in the background and had not found the file by the time this report closed). Per the mission's fallback,
this is the real check run against whatever was actually on disk, with `--skip-a18`, honestly reporting
which inputs were present.

Command: `python test/check.py --skip-a18 --seed 20260927` (real project root, no `--root`). Real result,
exit code 0:

```
node=C:\Users\joshu\scoop\apps\nodejs-lts\current\node.EXE (v24.18.0)
loaded data/corpus.json
data/pool.json: missing: C:\Users\joshu\Pokemon\which-pokemon\data\pool.json
loaded data/questions.json
loaded data/lexicon.json

A1   PASS   ids 1..1025 complete; field/type schema OK for 1025 species
A2   PASS   0/1025 species tag() mismatch. REPORT: 81.1% of species have >=1 lexicon match
A3   PASS   seed coverage + no-duplicate check: OK
A4   SKIP   data/pool.json missing
A5   SKIP   data/pool.json missing
A6   PASS   15 items checked
A7   PASS   takers list equals Q7 table exactly
A8   SKIP   data/pool.json missing
A9   SKIP   no usable pool profiles yet (data/pool.json missing or not all profiles have a vector/lean/stage)
A10  SKIP   no pool vectors available
A11  SKIP   no pool profiles available
A12  SKIP   no pool profiles available
A13  PASS   unit-case py=OK js=OK (matches python: 0.24->2, 0.26->1); questions-null-lean=OK
            check-const-null-lean=OK; stub-vs-real(20000x10)=SKIPPED, no real pool profiles available;
            web: 1 lean-mentioning line(s) under web/, 0 flagged; index.html gender-word scan: clean;
            storage-write heuristic scan: 0 hit(s)
A14  SKIP   no pool profiles available
A15  SKIP   no pool profiles available
A16  PASS   prose_check.py over 135 strings + index.html: em-dashes/banned/neg-parallel must be 0;
            how-it-works HEURISTIC extract: 82 words
A17  SKIP   no pool profiles available
A18  SKIP   --skip-a18 set
A19  PASS   self-contained calibration: clean pair -> PASS, pair with a duplicated why sentence -> FAIL
A20  PASS   149 pool.csv rows, 0 pool.json profiles checked against 142 screened-out ids

SUMMARY: 9 PASS, 0 FAIL (0 of them MUST), 11 SKIP, 0 REPORT-only
SKIPPED (not evidence of failure, evidence of missing input): ['A4', 'A5', 'A8', 'A9', 'A10', 'A11',
    'A12', 'A14', 'A15', 'A17', 'A18']
```

Full transcript: `test/.run_real.txt`. Real-data verdicts, everything that could run against what had
actually landed:

- **A1 PASS** on the real 1,025-species corpus, unchanged from the first pass.
- **A2 PASS**, **A3 PASS**: unchanged, corpus tagging and lexicon coverage still hold.
- **A6 PASS**: the real 15 items still pass every item MUST.
- **A7 PASS**: `takers` in the real `data/questions.json` equals the amended Q7 table exactly -- every
  taker's `lean` is already `None` in the live file, confirmed directly (not just via A7's equality
  check): `[('alex', None), ('melissa', None), ..., ('guest', None)]`.
- **A13 PASS**: both unit cases (Python and, via node, the real `web/app.js`) confirm `leanPenalty`'s
  constants still transcribe correctly; the real `data/questions.json` takers are confirmed null; the
  20,000-draw stub-vs-real comparison SKIPPED (honestly -- there is no real pool yet to draw against);
  the web scan found exactly one `.lean`/`lean:` line under `web/` and it was the `leanPenalty()` call
  itself in `web/app.js` (flagged 0 as a violation); `web/index.html`'s visible text carries no gender
  word; the storage heuristic found nothing.
- **A16 PASS**: `web/index.html` already carries a "How it works" section -- the HEURISTIC extractor
  pulled an 82-word block that satisfied every check (Big Five, 15, the research-note link, no
  measurement word). This is new since the first enabling pass, when the toggle did not exist yet; it is
  reported here as SUSPECTED-not-CONFIRMED per the extractor's own heuristic-extraction caveat, since the
  real toggle's markup was not known when the extractor was written -- the panelist should read the
  actual rendered toggle by eye to confirm the extract matches what a user sees.
- **A20 PASS**: the real, screened `spec/pool.csv` (149 rows) carries none of the 142 screened-out ids.
- **A19 PASS**: see (a) above.

Assertions A4, A5, A8, A9, A10, A11, A12, A14, A15 and A17 all SKIPPED, honestly, for the single reason
`data/pool.json` did not exist at run time. `data/profiles/` held seven worker shards (`1-59.json`,
`65-152.json`, `280-405.json`, `427-549.json`, `570-700.json`, `701-815.json`, `816-959.json`) at the time
this report closed, so the stream was progressing, not stalled, but had not merged them into
`data/pool.json` or written `DELIVERY.md`.

**Polling.** Per the mission order, a background poll (`test/.poll2.sh`, up to 40 minutes, 2-minute
intervals, no bare sleep chain) was started to wait for `DELIVERY.md`. This report closed before that
poll's deadline because the session was required to hand back before the wait completed; the poll's own
process is not guaranteed to survive past this handback. **`DELIVERY.md` had not landed as of this
report, and A4, A5, A8, A9, A10, A11, A12, A14, A15 and A17's real-data verdicts are UNKNOWN as of this
report -- they did not run against real data.** Everything in section (b) above is what DID run.
Whoever next runs the instrument should re-run `python test/check.py` (no `--root`, no `--skip-a18` if
the site is live) once `data/pool.json` exists and `DELIVERY.md` has landed, and treat that as the
authoritative real-data verdict, superseding the SKIP lines above.

## (c) File evidence: mtime and byte size at judgment time (2026-09-27 14:54 -0400)

| File | Present | Bytes | mtime |
|---|---|---|---|
| `data/pool.json` | NO, still absent when this report closed | - | - |
| `data/questions.json` | yes | 14,436 | 2026-09-27 14:47:19 -0400 |
| `web/app.js` | yes | 10,740 | 2026-09-27 14:13:11 -0400 |

The judged `check.py` build for every run in this file: `test/check.py`, rewritten this pass for the
amended contract, no further edits after `test/.run_real.txt` was produced (frozen before the real run,
per the mission order's boundary rule). At the moment this report closed: 60,742 bytes, mtime
2026-09-27 (this session). `test/fixtures/build_fixtures.py` was rebuilt in the same pass, before any
fixture run in section (a).

## What this instrument did not check

- A18 (live URL OG tags + mobile playthrough) was not run (`--skip-a18`); DELIVERY.md and a live deploy
  had not landed.
- A4, A5, A8, A9, A10-A15 and A17's real-pool thresholds have not been evaluated against the real pool,
  because `data/pool.json` does not exist yet. The fixture-scale numbers in `test/.run_good.txt` are
  informative only.
- A13's "no lean field under web/" scan, its storage-write scan, and A16's "How it works" extraction are
  all HEURISTIC (exact-text/regex or crude-tag-strip based, not a running browser or DOM parser). A green
  result on these is SUSPECTED, not CONFIRMED; the panelist's independent read of the live page is the
  real check.
- A13's stub-vs-real match() comparison is close to tautological once every taker's lean is confirmed
  null (which it is, per A7 and A13's own check) -- its value is as a regression guard, not as a live
  behavioural distinction, and is reported as such above.
- This instrument is calibrated on defects the author thought to construct (A19's duplicated why
  sentence; the known-bad fixture's missing image, em dash, and changed lean weight; an ad hoc A20 probe
  with an injected screened-out id). A green run on real data is evidence the data agrees with the
  contract on the axes this file checks, not proof of correctness on axes nobody thought to break.
- The one real-content finding this pass turned up (`data/questions.json` q10's "stomach") was found
  by accident, via the fixture rebuild, not by a dedicated real-data run (since `data/pool.json` was not
  ready to drive A15 against the real pool). It is reported to stream-2 directly and will re-surface in
  A15 once `data/pool.json` lands, unless fixed first.
