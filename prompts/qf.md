# World Cup 2026 quarter-finals: prediction request

You previously predicted fixtures for this tournament in earlier rounds;
those rounds are final and scored separately from this one.

As with earlier knockout rounds, you have real results as context below
and should use them. Predict the outcome of the 4 quarter-final fixtures
that follow. Knockout matches cannot end in a draw: if a match is level
after 90 minutes it goes to extra time, and if still level, penalties.
Predict the winner and, separately, your best guess at the 90-minute
scoreline (which may itself be a draw, since that's still possible before
extra time).

Base your prediction on the results below, plus anything else you find
relevant: historical knockout-round pedigree, squad depth and fatigue
five matches into the tournament, and head-to-head history if any exists
between these two opponents.

## Round of 16 results

Scores are 90 minutes; matches level after 90 went to extra time and,
where noted, penalties.

- Paraguay 0-1 France
- Canada 0-3 Morocco
- Brazil 1-2 Norway
- Mexico 2-3 England
- Portugal 0-1 Spain
- United States 1-4 Belgium
- Argentina 3-2 Egypt
- Switzerland 0-0 Colombia (Switzerland win 4-3 on penalties)

## Round of 32 results

- Germany 1-1 Paraguay (Paraguay win 4-3 on penalties)
- France 3-0 Sweden
- South Africa 0-1 Canada
- Netherlands 1-1 Morocco (Morocco win 3-2 on penalties)
- Portugal 2-1 Croatia
- Spain 3-0 Austria
- United States 2-0 Bosnia & Herzegovina
- Belgium 3-2 Senegal
- Brazil 2-1 Japan
- Ivory Coast 1-2 Norway
- Mexico 2-0 Ecuador
- England 2-1 DR Congo
- Argentina 3-2 Cape Verde
- Australia 1-1 Egypt (Egypt win 4-2 on penalties)
- Switzerland 2-0 Algeria
- Colombia 1-0 Ghana

## Final group standings

Played, points, goal difference, goals for-against.

Group A: Mexico 9pts GD+6 (6-0); South Africa 4pts GD-1 (2-3); South Korea 3pts GD-1 (2-3); Czechia 1pt GD-4 (2-6)
Group B: Switzerland 7pts GD+4 (7-3); Canada 4pts GD+5 (8-3); Bosnia & Herzegovina 4pts GD-1 (5-6); Qatar 1pt GD-8 (2-10)
Group C: Brazil 7pts GD+6 (7-1); Morocco 7pts GD+3 (6-3); Scotland 3pts GD-3 (1-4); Haiti 0pts GD-6 (2-8)
Group D: United States 6pts GD+4 (8-4); Australia 4pts GD+0 (2-2); Paraguay 4pts GD-2 (2-4); Türkiye 3pts GD-2 (3-5)
Group E: Germany 6pts GD+6 (10-4); Ivory Coast 6pts GD+2 (4-2); Ecuador 4pts GD+0 (2-2); Curaçao 1pt GD-8 (1-9)
Group F: Netherlands 7pts GD+6 (10-4); Japan 5pts GD+4 (7-3); Sweden 4pts GD+0 (7-7); Tunisia 0pts GD-10 (2-12)
Group G: Belgium 5pts GD+4 (6-2); Egypt 5pts GD+2 (5-3); Iran 3pts GD+0 (3-3); New Zealand 1pt GD-6 (4-10)
Group H: Spain 7pts GD+5 (5-0); Cape Verde 3pts GD+0 (2-2); Uruguay 2pts GD-1 (3-4); Saudi Arabia 2pts GD-4 (1-5)
Group I: France 9pts GD+8 (10-2); Norway 6pts GD+1 (8-7); Senegal 3pts GD+2 (8-6); Iraq 0pts GD-11 (1-12)
Group J: Argentina 9pts GD+7 (8-1); Austria 4pts GD+0 (6-6); Algeria 4pts GD-2 (5-7); Jordan 0pts GD-5 (3-8)
Group K: Colombia 7pts GD+3 (4-1); Portugal 5pts GD+5 (6-1); DR Congo 4pts GD+1 (4-3); Uzbekistan 0pts GD-9 (2-11)
Group L: England 7pts GD+4 (6-2); Croatia 6pts GD+0 (5-5); Ghana 4pts GD+0 (2-2); Panama 0pts GD-4 (0-4)

## Scoring for this round

- 2 points for predicting the correct winner
- +1 additional point if your 90-minute scoreline is also exact
- 0 points for predicting the wrong winner, regardless of scoreline

## Output format

Return ONLY a single JSON object, no markdown fences, no commentary
before or after, matching this schema exactly:

{
  "model": "<your model name and version>",
  "provider": "<your developer>",
  "generated": "<YYYY-MM-DD>",
  "round": "QF",
  "method_notes": "<one or two sentences on your approach for this round, including how you weighted the results above>",
  "predictions": [
    {
      "fixture_id": "<id from the fixture list>",
      "winner": "<team code>",
      "home_score": <integer, 90-minute>,
      "away_score": <integer, 90-minute>,
      "confidence": <0.0–1.0, your probability that the WINNER pick is correct>,
      "reasoning": "<one short sentence>"
    }
  ]
}

Rules:
- Exactly one prediction per fixture, 4 in total
- "winner" must be one of the two team codes in that fixture
- home_score/away_score are still required even if you predict a draw at
  90 minutes (since the winner field captures who you think wins after
  extra time/penalties)
- Integers only for scores

## Fixtures

[
  {"id": "QF-1", "home": "FRA", "away": "MAR"},
  {"id": "QF-2", "home": "ESP", "away": "BEL"},
  {"id": "QF-3", "home": "NOR", "away": "ENG"},
  {"id": "QF-4", "home": "ARG", "away": "SUI"}
]

## Teams

- FRA: France
- MAR: Morocco
- ESP: Spain
- BEL: Belgium
- NOR: Norway
- ENG: England
- ARG: Argentina
- SUI: Switzerland