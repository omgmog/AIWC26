#!/usr/bin/env python3
"""Ranking Bot: a deterministic baseline entry for the AIWC26 sweepstake.

One rule, two parameters, no football knowledge:
  - if the teams are within DRAW_THRESHOLD places of each other in the
    FIFA world ranking, predict 1-1
  - otherwise the higher-ranked team wins 2-1

Rankings are the FIFA Men's World Ranking of 1 April 2026, the last
official update before the tournament. Source noted below; top 20
cross-checked against Wikipedia's table of the same release.

Run from the repo root:  python3 tools/ranking_bot.py
Writes _data/predictions/ranking-bot.json
"""
import json
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

fx = json.loads((DATA / "fixtures.json").read_text(encoding="utf-8"))
missing = set(fx["teams"]) - set(FIFA_RANK)
assert not missing, f"teams missing a ranking: {missing}"

predictions = []
for f in fx["fixtures"]:
    rh, ra = FIFA_RANK[f["home"]], FIFA_RANK[f["away"]]
    gap = abs(rh - ra)
    if gap < DRAW_THRESHOLD:
        h, a = 1, 1
        verdict = "draw"
    elif rh < ra:
        h, a = 2, 1
        verdict = f"{f['home']} win"
    else:
        h, a = 1, 2
        verdict = f"{f['away']} win"
    predictions.append({
        "fixture_id": f["id"],
        "home_score": h,
        "away_score": a,
        "confidence": 0.5,
        "reasoning": f"{f['home']} ranked {rh}, {f['away']} ranked {ra}, gap {gap}: {verdict}.",
    })

doc = {
    "model": "Ranking Bot",
    "provider": "FIFA rankings + one rule",
    "generated": "2026-06-10",
    "method_notes": (f"Deterministic baseline. FIFA World Ranking of 1 Apr 2026; "
                     f"teams within {DRAW_THRESHOLD} places of each other draw 1-1, "
                     f"otherwise the higher-ranked team wins 2-1. No model, no judgement."),
    "predictions": predictions,
}
out = DATA / "predictions" / "ranking-bot.json"
out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

draws = sum(1 for p in predictions if p["home_score"] == p["away_score"])
print(f"wrote {out.relative_to(ROOT)}: {len(predictions)} predictions, "
      f"{draws} draws ({draws/len(predictions):.0%})")
