# AI vs AI: World Cup 2026 sweepstake

A page that pits AI models against each other predicting the group stage of
the 2026 World Cup. Each model gets an identical prompt, returns predictions
in a fixed JSON format, and gets scored as the real results come in. The
site is a Jekyll build: the leaderboard, scoring and every fixture table are
rendered into the HTML at build time, so the page is fully readable with
JavaScript disabled. Client-side JS is only used for the header clock and
the group filter buttons.

## Structure

```
index.html                      front matter + includes for the page body
_layouts/default.html           page chrome: head, styles, header, footer, JS
_includes/                       leaderboard, methods, group nav, fixtures
_plugins/
  scoring_data.rb                computes leaderboard + per-fixture scoring
  copy_data.rb                   publishes _data/ as /data/ in the built site
prompt.md                        the brief to paste into each AI
_data/
  fixtures.json                  teams, groups, 72 group-stage fixtures
  manifest.json                  which prediction files to load
  results.json                   actual scores, filled in by hand
  predictions/
    claude-fable-5.json           Claude's entry (already submitted)
    ...
tools/
  generate_data.py               regenerates fixtures.json and Claude's file
  make_prompt.py                 regenerates prompt.md from fixtures.json
  results.py                     set/unset/list results in results.json
```

`_data/` is also published verbatim at `/AIWC26/data/...` (via
`_plugins/copy_data.rb`), so `fixtures.json`, `manifest.json`,
`results.json` and every file in `predictions/` remain available at their
original URLs as the project's public API and audit trail.

## Workflow

1. **Collect entries.** Paste the contents of `prompt.md` into each model
   (ChatGPT, Gemini, whatever else). Save each response verbatim as
   `_data/predictions/<model-slug>.json` and add the filename to
   `manifest.json`. The page renders however many entries the manifest
   lists; column order follows the manifest.

2. **Validate before trusting.** Models occasionally wrap output in
   markdown fences or miss a fixture. A quick check:

   ```sh
   python3 -c "import json,sys; d=json.load(open(sys.argv[1])); \
     ids={p['fixture_id'] for p in d['predictions']}; \
     print(len(ids), 'fixtures,', 'OK' if len(ids)==72 else 'MISSING SOME')" \
     _data/predictions/gpt-whatever.json
   ```

3. **Enter results, commit, push.** As matches finish, record the
   90-minute score with:

   ```sh
   tools/results.py set A1 2 0
   tools/results.py list      # see what's pending
   tools/results.py unset A1  # undo a mistake
   ```

   This writes to `_data/results.json` keyed by fixture id. Commit and push
   to `main` — the GitHub Actions workflow rebuilds the site with Jekyll and
   redeploys to Pages. The leaderboard, per-fixture colouring, and "next
   match" widget all update as part of that build. That's the whole update
   loop.

## Building locally

```sh
bundle install
bundle exec jekyll serve --baseurl ""
```

`bundle exec jekyll build` requires the plugins in `_plugins/`, which is why
the deploy workflow runs a plain Jekyll build with Bundler rather than the
`github-pages` gem (which runs in safe mode and ignores plugins).

## Scoring

3 points for the exact scoreline, 1 point for the correct result with the
wrong score, 0 otherwise. Ties on points break on exact-score count.
Hover a prediction for the model's one-line reasoning.

## Caveats worth knowing

- **Fixture order is the standard round-robin rotation, not verified
  against the official FIFA schedule.** Home/away orientation and the
  pairing on each matchday may differ. Check before circulating the
  prompt, edit `_data/fixtures.json` if needed, then rerun
  `tools/make_prompt.py` so every model sees the same orientation.
  Predictions key on fixture id and home/away as listed, so consistency
  matters more than matching FIFA's ordering exactly.
- Dates are only populated for the two confirmed openers (Mexico v South
  Africa on 11 June, USA v Paraguay on 12 June). The `date` and `venue`
  fields exist if you want to backfill them.
- Claude's predictions in `_data/predictions/claude-fable-5.json` were
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
