# Which Pokémon are you?

A short, positive personality quiz for the family. Fifteen questions, no accounts, no server. The
result is the nearest Pokémon in a five-trait space built from the Big Five, never a "type."

Live: https://joshuamatalon.github.io/which-pokemon/

## Attribution

Pokémon names and artwork are the property of Nintendo, Creatures Inc. and Game Freak Inc. Animated
sprites are from Pokémon Showdown. Species data is from PokéAPI (https://pokeapi.co/). This is a fan
project made for one family and has no affiliation with any of the above.

## How it is built

- `scripts/build-corpus.mjs` pulls PokéAPI `pokemon-species` 1 to 1025, plus `pokemon` for types and
  stats and each `evolution-chain` for stage, caching every response under `data/cache/` so a rerun is
  free. It tags every species against `data/lexicon.json` and writes `data/corpus.json`.
- `scripts/fetch-images.mjs` downloads official artwork and Pokémon Showdown animated sprites for the
  pool only, into `web/img/art/` and `web/img/ani/`, verifying file magic bytes.
- `data/profiles/*.json` hold hand-researched profiles for the 149-species screened pool
  (`spec/pool.csv`, `spec/POOL-SCREEN.md`), one file per contiguous id range or gap batch.
  `scripts/build-pool.mjs` merges them with the corpus, drops any profile the screen removed, computes
  each profile's trait vector with `profileVectors()`, and writes `data/pool.json`.
- `data/questions.json` holds the 15 quiz items, checked against the contract with
  `scripts/validate-questions.mjs`.
- `web/` is the static app: vanilla JS, no framework, no build step. `web/app.js` holds the scoring
  engine (`match()`, `resultText()`, etc.) transcribed from `spec/CONTRACT.md`, and it runs both in the
  browser and under Node so `test/check.py` can call it directly.

## Running the corpus scripts

```
node scripts/build-corpus.mjs      # data/corpus.json (cached, safe to rerun)
node scripts/fetch-images.mjs      # web/img/art, web/img/ani
node scripts/build-pool.mjs        # data/pool.json, copies runtime data into web/data/
node scripts/validate-questions.mjs
python scripts/make-og-image.py    # web/img/og.png
```

## Check

`python test/check.py` (built by the enabling position) asserts the contract's acceptance criteria
(spec/CONTRACT.md Q8): schema shape, image validity, the reading-level and keying rules on every item,
score-engine agreement between this repo's JavaScript and an independent Python copy, coverage and
reachability over the pool, lean and stage behaviour, and a live-site mobile run.

## The law

`spec/CONTRACT.md` is authoritative. `spec/RESEARCH-PERSONALITY.md` has the personality-science sources
behind it. `spec/pool.csv` is the 149-species result pool, screened for offence potential
(`spec/POOL-SCREEN.md`). There is no gender or lean filter; every taker's lean is null.
