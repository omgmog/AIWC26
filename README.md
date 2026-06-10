# AI vs AI: World Cup 2026 sweepstake

A static page that pits AI models against each other predicting the group
stage of the 2026 World Cup. Each model gets an identical prompt, returns
predictions in a fixed JSON format, and gets scored as the real results
come in.

## Structure

```
index.html                      the whole front end (no build step)
prompt.md                       the brief to paste into each AI
data/
  fixtures.json                 teams, groups, 72 group-stage fixtures
  manifest.json                 which prediction files to load
  results.json                  actual scores, filled in by hand
  predictions/
    claude-fable-5.json         Claude's entry (already submitted)
    _template.json              shape reference for new entries
tools/
  generate_data.py              regenerates fixtures.json and Claude's file
  make_prompt.py                regenerates prompt.md from fixtures.json
  results.py                    set/unset/list results in results.json
```

## Workflow

1. **Collect entries.** Paste the contents of `prompt.md` into each model
   (ChatGPT, Gemini, whatever else). Save each response verbatim as
   `data/predictions/<model-slug>.json` and add the filename to
   `manifest.json`. The page renders however many entries the manifest
   lists; column order follows the manifest.

2. **Validate before trusting.** Models occasionally wrap output in
   markdown fences or miss a fixture. A quick check:

   ```sh
   python3 -c "import json,sys; d=json.load(open(sys.argv[1])); \
     ids={p['fixture_id'] for p in d['predictions']}; \
     print(len(ids), 'fixtures,', 'OK' if len(ids)==72 else 'MISSING SOME')" \
     data/predictions/gpt-whatever.json
   ```

3. **Enter results.** As matches finish, record the 90-minute score with:

   ```sh
   tools/results.py set A1 2 0
   tools/results.py list      # see what's pending
   tools/results.py unset A1  # undo a mistake
   ```

   This writes to `data/results.json` keyed by fixture id. The leaderboard,
   per-fixture colouring, and "next match" widget update on next page load.

4. **Serve it.** `fetch()` is blocked on `file://`, so use any static
   server locally (`python3 -m http.server`) or drop the folder into the
   Jekyll site as-is. No build step, no dependencies beyond one Google
   Font.

## Scoring

3 points for the exact scoreline, 1 point for the correct result with the
wrong score, 0 otherwise. Ties on points break on exact-score count.
Hover a prediction for the model's one-line reasoning.

## Caveats worth knowing

- **Fixture order is the standard round-robin rotation, not verified
  against the official FIFA schedule.** Home/away orientation and the
  pairing on each matchday may differ. Check before circulating the
  prompt, edit `data/fixtures.json` if needed, then rerun
  `tools/make_prompt.py` so every model sees the same orientation.
  Predictions key on fixture id and home/away as listed, so consistency
  matters more than matching FIFA's ordering exactly.
- Dates are only populated for the two confirmed openers (Mexico v South
  Africa on 11 June, USA v Paraguay on 12 June). The `date` and `venue`
  fields exist if you want to backfill them.
- Claude's predictions in `data/predictions/claude-fable-5.json` were
  generated on 10 June 2026 and should be treated as immutable, the same
  as every other entry. If you regenerate them after kick-off you have
  invented sports fraud for robots.
- Groups and teams reflect the completed March 2026 playoffs (Bosnia &
  Herzegovina, Sweden, Türkiye, Czechia via UEFA; DR Congo and Iraq via
  the intercontinental route).

## Extending

- Knockout rounds: add fixtures with new ids (`R32-1` etc.) to
  `fixtures.json` once the bracket is known, rerun `make_prompt.py` for a
  second prompt, and collect a second round of entries. The front end
  groups by the `group` field, so give knockout fixtures a `group` value
  like `R32` and they get their own section for free.
- Confidence is collected but not yet displayed or scored. A Brier score
  column would be a natural follow-up post.
