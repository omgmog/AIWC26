# World Cup 2026 group stage: prediction request

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

{
  "model": "<your model name and version>",
  "provider": "<your developer>",
  "generated": "<YYYY-MM-DD>",
  "method_notes": "<one or two sentences on your approach>",
  "predictions": [
    {
      "fixture_id": "<id from the fixture list>",
      "home_score": <integer>,
      "away_score": <integer>,
      "confidence": <0.0–1.0, your probability that the RESULT is correct>,
      "reasoning": "<one short sentence>"
    }
  ]
}

Rules:
- Exactly one prediction per fixture, 72 in total, using the ids below
- home_score applies to the "home" team as listed, away_score to "away"
- Integers only for scores; this is the 90-minute result (group stage has
  no extra time)

## Teams

- ALG: Algeria (Group J)
- ARG: Argentina (Group J)
- AUS: Australia (Group D)
- AUT: Austria (Group J)
- BEL: Belgium (Group G)
- BIH: Bosnia & Herzegovina (Group B)
- BRA: Brazil (Group C)
- CAN: Canada (Group B)
- CIV: Ivory Coast (Group E)
- COD: DR Congo (Group K)
- COL: Colombia (Group K)
- CPV: Cape Verde (Group H)
- CRO: Croatia (Group L)
- CUW: Curaçao (Group E)
- CZE: Czechia (Group A)
- ECU: Ecuador (Group E)
- EGY: Egypt (Group G)
- ENG: England (Group L)
- ESP: Spain (Group H)
- FRA: France (Group I)
- GER: Germany (Group E)
- GHA: Ghana (Group L)
- HAI: Haiti (Group C)
- IRN: Iran (Group G)
- IRQ: Iraq (Group I)
- JOR: Jordan (Group J)
- JPN: Japan (Group F)
- KOR: South Korea (Group A)
- KSA: Saudi Arabia (Group H)
- MAR: Morocco (Group C)
- MEX: Mexico (Group A)
- NED: Netherlands (Group F)
- NOR: Norway (Group I)
- NZL: New Zealand (Group G)
- PAN: Panama (Group L)
- PAR: Paraguay (Group D)
- POR: Portugal (Group K)
- QAT: Qatar (Group B)
- RSA: South Africa (Group A)
- SCO: Scotland (Group C)
- SEN: Senegal (Group I)
- SUI: Switzerland (Group B)
- SWE: Sweden (Group F)
- TUN: Tunisia (Group F)
- TUR: Türkiye (Group D)
- URU: Uruguay (Group H)
- USA: United States (Group D)
- UZB: Uzbekistan (Group K)

## Fixtures

[
  {"id": "A1", "group": "A", "home": "MEX", "away": "RSA"},
  {"id": "A2", "group": "A", "home": "KOR", "away": "CZE"},
  {"id": "A3", "group": "A", "home": "MEX", "away": "KOR"},
  {"id": "A4", "group": "A", "home": "CZE", "away": "RSA"},
  {"id": "A5", "group": "A", "home": "CZE", "away": "MEX"},
  {"id": "A6", "group": "A", "home": "RSA", "away": "KOR"},
  {"id": "B1", "group": "B", "home": "CAN", "away": "SUI"},
  {"id": "B2", "group": "B", "home": "QAT", "away": "BIH"},
  {"id": "B3", "group": "B", "home": "CAN", "away": "QAT"},
  {"id": "B4", "group": "B", "home": "BIH", "away": "SUI"},
  {"id": "B5", "group": "B", "home": "BIH", "away": "CAN"},
  {"id": "B6", "group": "B", "home": "SUI", "away": "QAT"},
  {"id": "C1", "group": "C", "home": "BRA", "away": "MAR"},
  {"id": "C2", "group": "C", "home": "HAI", "away": "SCO"},
  {"id": "C3", "group": "C", "home": "BRA", "away": "HAI"},
  {"id": "C4", "group": "C", "home": "SCO", "away": "MAR"},
  {"id": "C5", "group": "C", "home": "SCO", "away": "BRA"},
  {"id": "C6", "group": "C", "home": "MAR", "away": "HAI"},
  {"id": "D1", "group": "D", "home": "USA", "away": "PAR"},
  {"id": "D2", "group": "D", "home": "AUS", "away": "TUR"},
  {"id": "D3", "group": "D", "home": "USA", "away": "AUS"},
  {"id": "D4", "group": "D", "home": "TUR", "away": "PAR"},
  {"id": "D5", "group": "D", "home": "TUR", "away": "USA"},
  {"id": "D6", "group": "D", "home": "PAR", "away": "AUS"},
  {"id": "E1", "group": "E", "home": "GER", "away": "CUW"},
  {"id": "E2", "group": "E", "home": "CIV", "away": "ECU"},
  {"id": "E3", "group": "E", "home": "GER", "away": "CIV"},
  {"id": "E4", "group": "E", "home": "ECU", "away": "CUW"},
  {"id": "E5", "group": "E", "home": "ECU", "away": "GER"},
  {"id": "E6", "group": "E", "home": "CUW", "away": "CIV"},
  {"id": "F1", "group": "F", "home": "NED", "away": "JPN"},
  {"id": "F2", "group": "F", "home": "SWE", "away": "TUN"},
  {"id": "F3", "group": "F", "home": "NED", "away": "SWE"},
  {"id": "F4", "group": "F", "home": "TUN", "away": "JPN"},
  {"id": "F5", "group": "F", "home": "TUN", "away": "NED"},
  {"id": "F6", "group": "F", "home": "JPN", "away": "SWE"},
  {"id": "G1", "group": "G", "home": "BEL", "away": "EGY"},
  {"id": "G2", "group": "G", "home": "IRN", "away": "NZL"},
  {"id": "G3", "group": "G", "home": "BEL", "away": "IRN"},
  {"id": "G4", "group": "G", "home": "NZL", "away": "EGY"},
  {"id": "G5", "group": "G", "home": "NZL", "away": "BEL"},
  {"id": "G6", "group": "G", "home": "EGY", "away": "IRN"},
  {"id": "H1", "group": "H", "home": "ESP", "away": "CPV"},
  {"id": "H2", "group": "H", "home": "KSA", "away": "URU"},
  {"id": "H3", "group": "H", "home": "ESP", "away": "KSA"},
  {"id": "H4", "group": "H", "home": "URU", "away": "CPV"},
  {"id": "H5", "group": "H", "home": "URU", "away": "ESP"},
  {"id": "H6", "group": "H", "home": "CPV", "away": "KSA"},
  {"id": "I1", "group": "I", "home": "FRA", "away": "SEN"},
  {"id": "I2", "group": "I", "home": "IRQ", "away": "NOR"},
  {"id": "I3", "group": "I", "home": "FRA", "away": "IRQ"},
  {"id": "I4", "group": "I", "home": "NOR", "away": "SEN"},
  {"id": "I5", "group": "I", "home": "NOR", "away": "FRA"},
  {"id": "I6", "group": "I", "home": "SEN", "away": "IRQ"},
  {"id": "J1", "group": "J", "home": "ARG", "away": "AUT"},
  {"id": "J2", "group": "J", "home": "ALG", "away": "JOR"},
  {"id": "J3", "group": "J", "home": "ARG", "away": "ALG"},
  {"id": "J4", "group": "J", "home": "JOR", "away": "AUT"},
  {"id": "J5", "group": "J", "home": "JOR", "away": "ARG"},
  {"id": "J6", "group": "J", "home": "AUT", "away": "ALG"},
  {"id": "K1", "group": "K", "home": "POR", "away": "COL"},
  {"id": "K2", "group": "K", "home": "COD", "away": "UZB"},
  {"id": "K3", "group": "K", "home": "POR", "away": "COD"},
  {"id": "K4", "group": "K", "home": "UZB", "away": "COL"},
  {"id": "K5", "group": "K", "home": "UZB", "away": "POR"},
  {"id": "K6", "group": "K", "home": "COL", "away": "COD"},
  {"id": "L1", "group": "L", "home": "ENG", "away": "CRO"},
  {"id": "L2", "group": "L", "home": "PAN", "away": "GHA"},
  {"id": "L3", "group": "L", "home": "ENG", "away": "PAN"},
  {"id": "L4", "group": "L", "home": "GHA", "away": "CRO"},
  {"id": "L5", "group": "L", "home": "GHA", "away": "ENG"},
  {"id": "L6", "group": "L", "home": "CRO", "away": "PAN"}
]
