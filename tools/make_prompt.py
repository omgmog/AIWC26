#!/usr/bin/env python3
"""Emit prompt.md from data/fixtures.json so every model receives an
identical brief with identical fixture ids and home/away orientation."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
doc = json.loads((ROOT / "data" / "fixtures.json").read_text(encoding="utf-8"))
teams, fixtures = doc["teams"], doc["fixtures"]

lines = []
for f in fixtures:
    lines.append(f'  {{"id": "{f["id"]}", "group": "{f["group"]}", '
                 f'"home": "{f["home"]}", "away": "{f["away"]}"}}')
fixture_block = "[\n" + ",\n".join(lines) + "\n]"

team_block = "\n".join(
    f'- {code}: {t["name"]} (Group {t["group"]})' for code, t in sorted(teams.items())
)

prompt = f"""# World Cup 2026 group stage: prediction request

You are one of several AI models taking part in a sweepstake predicting the
group stage of the 2026 FIFA World Cup (USA/Canada/Mexico, 11–27 June 2026).
Your predictions will be published alongside those of other models and scored
against the real results.

## Your task

Predict the full-time score of all 72 group-stage fixtures listed below.

Base your predictions on, at minimum:

1. Historical World Cup performance of each nation
2. Recent competitive form: qualifying campaigns, the 2024–26 continental
   tournaments (Euros, Copa América, AFCON, Asian Cup), and Nations League
3. Squad composition for this tournament, including how key players have
   performed for their clubs in the 2025–26 season
4. Contextual factors: host advantage (Mexico, USA, Canada), venue altitude
   and climate, playoff-route fatigue or momentum, managerial changes

Predict the single most likely scoreline (the mode), not an average. Be
willing to predict draws and upsets where the evidence supports them — a
slate of safe favourite wins scores poorly if the tournament misbehaves.

## Scoring (how you will be judged)

- 3 points for the exact scoreline
- 1 point for the correct result (win/draw/loss) with the wrong score
- 0 points otherwise

## Output format

Return ONLY a single JSON object, no markdown fences, no commentary before or
after, matching this schema exactly:

{{
  "model": "<your model name and version>",
  "provider": "<your developer>",
  "generated": "<YYYY-MM-DD>",
  "method_notes": "<one or two sentences on your approach>",
  "predictions": [
    {{
      "fixture_id": "<id from the fixture list>",
      "home_score": <integer>,
      "away_score": <integer>,
      "confidence": <0.0–1.0, your probability that the RESULT is correct>,
      "reasoning": "<one short sentence>"
    }}
  ]
}}

Rules:
- Exactly one prediction per fixture, 72 in total, using the ids below
- home_score applies to the "home" team as listed, away_score to "away"
- Integers only for scores; this is the 90-minute result (group stage has
  no extra time)

## Teams

{team_block}

## Fixtures

{fixture_block}
"""

(ROOT / "prompt.md").write_text(prompt, encoding="utf-8")
print(f"prompt.md written ({len(prompt)} chars, {len(fixtures)} fixtures)")
