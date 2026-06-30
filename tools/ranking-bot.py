#!/usr/bin/env python3
"""Ranking Bot: a deterministic baseline entry for the AIWC26 sweepstake.

One rule, two parameters, no football knowledge:
  - if the teams are within DRAW_THRESHOLD places of each other in the
    FIFA world ranking, predict 1-1 (knockout rounds: the higher-ranked
    side is picked as the deterministic tie-break winner)
  - otherwise the higher-ranked team wins 2-1

Rankings are the FIFA Men's World Ranking of 1 April 2026, the last
official update before the tournament. Source noted below; top 20
cross-checked against Wikipedia's table of the same release.

Run from the repo root for the group stage: python3 tools/ranking-bot.py
Writes _data/predictions/ranking-bot.json

For a later stage, pass its key, e.g.:    python3 tools/ranking-bot.py r32
Writes _data/predictions/r32/ranking-bot.json, adding the "winner" field
knockout rounds need since they can't end level.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_data"

DRAW_THRESHOLD = 10

# FIFA Men's World Ranking, 1 April 2026.
FIFA_RANK = {
    "FRA": 1,  "ESP": 2,  "ARG": 3,  "ENG": 4,  "POR": 5,  "BRA": 6,
    "NED": 7,  "MAR": 8,  "BEL": 9,  "GER": 10, "CRO": 11, "COL": 13,
    "SEN": 14, "MEX": 15, "USA": 16, "URU": 17, "JPN": 18, "SUI": 19,
    "IRN": 21, "TUR": 22, "ECU": 23, "AUT": 24, "KOR": 25, "AUS": 27,
    "ALG": 28, "EGY": 29, "CAN": 30, "NOR": 31, "PAN": 33, "CIV": 34,
    "SWE": 38, "PAR": 40, "CZE": 41, "SCO": 43, "TUN": 44, "COD": 46,
    "UZB": 50, "QAT": 55, "IRQ": 57, "RSA": 60, "KSA": 61, "JOR": 63,
    "BIH": 65, "CPV": 69, "GHA": 74, "CUW": 82, "HAI": 83, "NZL": 85,
}

stage = sys.argv[1] if len(sys.argv) > 1 else "group"

fx = json.loads((DATA / "fixtures.json").read_text(encoding="utf-8"))
missing = set(fx["teams"]) - set(FIFA_RANK)
assert not missing, f"teams missing a ranking: {missing}"

stage_fixtures = [f for f in fx["fixtures"] if f["stage"] == stage]
assert stage_fixtures, f"no fixtures tagged stage={stage!r}"
knockout = stage != "group"

predictions = []
for f in stage_fixtures:
    rh, ra = FIFA_RANK[f["home"]], FIFA_RANK[f["away"]]
    gap = abs(rh - ra)
    if gap < DRAW_THRESHOLD:
        h, a = 1, 1
        verdict = "draw"
        winner = f["home"] if rh < ra else f["away"]
    elif rh < ra:
        h, a = 2, 1
        verdict = f"{f['home']} win"
        winner = f["home"]
    else:
        h, a = 1, 2
        verdict = f"{f['away']} win"
        winner = f["away"]

    reasoning = f"{f['home']} ranked {rh}, {f['away']} ranked {ra}, gap {gap}: {verdict}."
    if knockout and verdict == "draw":
        reasoning += f" Tie-break: higher-ranked {winner} progresses."

    prediction = {
        "fixture_id": f["id"],
        "home_score": h,
        "away_score": a,
        "confidence": 0.5,
        "reasoning": reasoning,
    }
    if knockout:
        prediction = {**{"winner": winner}, **prediction}
    predictions.append(prediction)

method_notes = (f"Deterministic baseline. FIFA World Ranking of 1 Apr 2026; "
                 f"teams within {DRAW_THRESHOLD} places of each other draw 1-1, "
                 f"otherwise the higher-ranked team wins 2-1. No model, no judgement.")
if knockout:
    method_notes += " For the winner pick, a drawn scoreline goes to the higher-ranked side."

doc = {
    "model": "Ranking Bot",
    "provider": "FIFA rankings + one rule",
    "generated": "2026-06-10",
    "method_notes": method_notes,
    "predictions": predictions,
}
if knockout:
    doc["round"] = stage.upper()

out_dir = DATA / "predictions" if stage == "group" else DATA / "predictions" / stage
out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / "ranking-bot.json"
out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

draws = sum(1 for p in predictions if p["home_score"] == p["away_score"])
print(f"wrote {out.relative_to(ROOT)}: {len(predictions)} predictions, "
      f"{draws} draws ({draws/len(predictions):.0%})")
