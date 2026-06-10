#!/usr/bin/env python3
"""Generate fixtures.json and Claude's predictions for the WC2026 group stage.

Fixture ordering within each group follows the standard round-robin rotation:
  MD1: T1 v T2, T3 v T4
  MD2: T1 v T3, T4 v T2
  MD3: T4 v T1, T2 v T3
Verify home/away order against the official FIFA schedule before circulating
prompt.md to other models -- fixtures.json is the single source of truth.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_data"

# (code, name) in pot order as drawn
GROUPS = {
    "A": [("MEX", "Mexico"), ("RSA", "South Africa"), ("KOR", "South Korea"), ("CZE", "Czechia")],
    "B": [("CAN", "Canada"), ("SUI", "Switzerland"), ("QAT", "Qatar"), ("BIH", "Bosnia & Herzegovina")],
    "C": [("BRA", "Brazil"), ("MAR", "Morocco"), ("HAI", "Haiti"), ("SCO", "Scotland")],
    "D": [("USA", "United States"), ("PAR", "Paraguay"), ("AUS", "Australia"), ("TUR", "Türkiye")],
    "E": [("GER", "Germany"), ("CUW", "Curaçao"), ("CIV", "Ivory Coast"), ("ECU", "Ecuador")],
    "F": [("NED", "Netherlands"), ("JPN", "Japan"), ("SWE", "Sweden"), ("TUN", "Tunisia")],
    "G": [("BEL", "Belgium"), ("EGY", "Egypt"), ("IRN", "Iran"), ("NZL", "New Zealand")],
    "H": [("ESP", "Spain"), ("CPV", "Cape Verde"), ("KSA", "Saudi Arabia"), ("URU", "Uruguay")],
    "I": [("FRA", "France"), ("SEN", "Senegal"), ("IRQ", "Iraq"), ("NOR", "Norway")],
    "J": [("ARG", "Argentina"), ("AUT", "Austria"), ("ALG", "Algeria"), ("JOR", "Jordan")],
    "K": [("POR", "Portugal"), ("COL", "Colombia"), ("COD", "DR Congo"), ("UZB", "Uzbekistan")],
    "L": [("ENG", "England"), ("CRO", "Croatia"), ("PAN", "Panama"), ("GHA", "Ghana")],
}

ROTATION = [  # (home_idx, away_idx, matchday)
    (0, 1, 1), (2, 3, 1),
    (0, 2, 2), (3, 1, 2),
    (3, 0, 3), (1, 2, 3),
]

KNOWN_DATES = {"A1": "2026-06-11", "D1": "2026-06-12"}

teams = {}
fixtures = []
for g, members in GROUPS.items():
    for code, name in members:
        teams[code] = {"name": name, "group": g}
    for n, (h, a, md) in enumerate(ROTATION, start=1):
        fid = f"{g}{n}"
        fixtures.append({
            "id": fid,
            "group": g,
            "matchday": md,
            "home": members[h][0],
            "away": members[a][0],
            "date": KNOWN_DATES.get(fid),
            "venue": None,
        })

fixtures_doc = {
    "tournament": "FIFA World Cup 2026",
    "stage": "Group stage",
    "note": ("Fixture order within each group uses the standard round-robin "
             "rotation. Verify home/away order and dates against the official "
             "schedule; edit here, then regenerate prompt.md with make_prompt.py."),
    "teams": teams,
    "fixtures": fixtures,
}
(DATA / "fixtures.json").write_text(json.dumps(fixtures_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# --- Claude's predictions -------------------------------------------------
# (fixture_id): (home_score, away_score, confidence, reasoning)
P = {
    "A1": (2, 0, 0.65, "Opening match at the Azteca; altitude and occasion favour Mexico heavily."),
    "A2": (1, 1, 0.40, "Korea's attack vs Czech organisation; evenly matched on recent form."),
    "A3": (2, 1, 0.50, "Mexico's home support edges a tight game against Son-less-but-deep Korea."),
    "A4": (1, 0, 0.40, "Czechia arrive battle-hardened from the playoffs; South Africa struggle for goals."),
    "A5": (0, 1, 0.40, "Mexico top the group; Czechia likely already through and rotated."),
    "A6": (0, 2, 0.50, "Korea's quality should tell against a limited South Africa side."),
    "B1": (1, 1, 0.40, "Switzerland's tournament pedigree against Canadian home energy; a draw is the value pick."),
    "B2": (0, 1, 0.40, "Bosnia's playoff momentum and Dzeko's swansong against a fading Qatar."),
    "B3": (2, 0, 0.55, "Canada at home with Davies fit should handle Qatar comfortably."),
    "B4": (0, 2, 0.50, "Swiss tournament know-how against a Bosnia side that peaks emotionally early."),
    "B5": (1, 1, 0.35, "Both may need a point; cagey draw suits the script."),
    "B6": (3, 0, 0.55, "Switzerland routinely dispatch sides at Qatar's level in group stages."),
    "C1": (2, 1, 0.45, "Heavyweight opener; Brazil's depth edges Morocco's structure."),
    "C2": (0, 1, 0.40, "Scotland's set-piece threat against a debutant-level Haiti defence."),
    "C3": (3, 0, 0.65, "Class gap; Brazil should win at a canter."),
    "C4": (0, 2, 0.50, "Morocco's midfield control smothers Scotland as it did better sides in 2022."),
    "C5": (0, 2, 0.55, "Brazil too strong; Scotland's hopes rest on third place."),
    "C6": (3, 0, 0.60, "Morocco close out top-two with a comfortable win."),
    "D1": (1, 0, 0.45, "Host pressure but home crowd at SoFi; Paraguay are obdurate but blunt."),
    "D2": (1, 1, 0.40, "Türkiye's flair against Australia's organisation; share of the spoils."),
    "D3": (2, 1, 0.50, "USA's athleticism wears Australia down late."),
    "D4": (1, 1, 0.35, "Two contrasting styles cancel out."),
    "D5": (1, 2, 0.40, "Marquee group game; USA's home support shades a Türkiye side prone to chaos."),
    "D6": (1, 0, 0.35, "Paraguay grind out the narrowest of wins; Australia exit on goal difference."),
    "E1": (3, 0, 0.70, "Germany against the smallest nation ever at a World Cup; ruthless expected."),
    "E2": (1, 1, 0.40, "Ivory Coast's physicality against Ecuador's altitude-hardened press."),
    "E3": (2, 1, 0.50, "Germany win but Ivory Coast will trouble their high line."),
    "E4": (2, 0, 0.55, "Ecuador's young core too athletic for Curaçao."),
    "E5": (1, 1, 0.40, "Ecuador have made a habit of frustrating elite sides; Germany already through."),
    "E6": (0, 2, 0.55, "Ivory Coast seal progression against the debutants."),
    "F1": (2, 1, 0.45, "Two genuine dark horses; Dutch physical edge in a high-quality opener."),
    "F2": (1, 0, 0.40, "Sweden's playoff-forged momentum and Isak against Tunisia's low block."),
    "F3": (2, 0, 0.45, "Netherlands' control should blunt Sweden's transitions."),
    "F4": (0, 2, 0.55, "Japan's pressing dismantles Tunisia; quietly one of the best sides here."),
    "F5": (0, 3, 0.55, "Netherlands finish the group strongly against eliminated opposition."),
    "F6": (2, 1, 0.45, "Japan edge a meaningful game for top spot; both likely through."),
    "G1": (2, 1, 0.50, "Belgium's new generation against Salah's Egypt; quality edges experience."),
    "G2": (2, 0, 0.55, "Iran's tournament streetwise game too much for New Zealand."),
    "G3": (2, 0, 0.50, "Belgium control possession; Iran dangerous only on the break."),
    "G4": (0, 2, 0.55, "Egypt's quality tells against the OFC qualifiers."),
    "G5": (0, 3, 0.60, "Belgium stroll; New Zealand's tournament likely already over."),
    "G6": (1, 1, 0.35, "Both may go through with a draw; expect exactly that."),
    "H1": (4, 0, 0.65, "Spain at full strength against debutants; Yamal showcase expected."),
    "H2": (0, 2, 0.55, "Uruguay's experience and nous against a limited Saudi side."),
    "H3": (3, 0, 0.60, "Spain's press suffocates Saudi Arabia's build-up."),
    "H4": (2, 0, 0.55, "Uruguay too streetwise for Cape Verde."),
    "H5": (0, 2, 0.50, "The group's marquee game; Spain's midfield should dominate."),
    "H6": (1, 1, 0.35, "Dead rubber energy; Cape Verde's pace against Saudi possession."),
    "I1": (2, 1, 0.50, "France against Senegal is a genuine contest, but Mbappé settles it."),
    "I2": (0, 2, 0.55, "Norway's Haaland-Ødegaard axis far too much for Iraq."),
    "I3": (3, 0, 0.65, "France ease past the playoff qualifiers."),
    "I4": (2, 1, 0.40, "The game of the group; Haaland edges Senegal's physical defence."),
    "I5": (1, 2, 0.40, "France win a heavyweight clash; Norway fine with second."),
    "I6": (2, 0, 0.55, "Senegal take third-place points with room to spare."),
    "J1": (2, 0, 0.55, "Defending champions open against Austria's press; Argentina's control prevails."),
    "J2": (1, 0, 0.40, "Algeria's experience edges debutants Jordan."),
    "J3": (2, 0, 0.55, "Argentina handle Algeria's counters; Messi's last group stage."),
    "J4": (0, 2, 0.50, "Austria's Rangnick-drilled press overwhelms Jordan."),
    "J5": (0, 3, 0.65, "Argentina cruise against the group's weakest side."),
    "J6": (1, 1, 0.35, "Second place possibly settled elsewhere; tense draw."),
    "K1": (2, 1, 0.45, "Ronaldo's final World Cup opener; Portugal's depth edges Colombia's flair."),
    "K2": (1, 1, 0.35, "DR Congo's playoff fairytale against Uzbekistan's organised debut."),
    "K3": (3, 0, 0.60, "Portugal's quality gap shows."),
    "K4": (0, 2, 0.50, "Colombia's class tells against Uzbekistan."),
    "K5": (0, 2, 0.55, "Portugal top the group; Uzbekistan's tournament effectively over."),
    "K6": (2, 0, 0.50, "Colombia seal second; James pulls the strings."),
    "L1": (2, 1, 0.45, "The only all-UEFA heavyweight group tie; England's depth edges an ageing Croatia."),
    "L2": (1, 1, 0.35, "Panama's organisation against Ghana's chaos; low-scoring draw."),
    "L3": (3, 0, 0.60, "England should be ruthless against Panama."),
    "L4": (0, 2, 0.50, "Croatia's midfield controls Ghana's transitions."),
    "L5": (0, 2, 0.55, "England close out top spot; Ghana need a miracle."),
    "L6": (2, 0, 0.50, "Croatia take second comfortably."),
}

assert set(P) == {f["id"] for f in fixtures}, "prediction coverage mismatch"

claude_doc = {
    "model": "Claude Fable 5",
    "provider": "Anthropic",
    "generated": "2026-06-10",
    "method_notes": ("Weighted blend of FIFA ranking (Apr 2026), qualifying and recent "
                     "tournament form, squad depth and key-player club seasons, plus "
                     "host/venue effects. Scores are modal outcomes, not expected goals."),
    "predictions": [
        {"fixture_id": fid, "home_score": h, "away_score": a,
         "confidence": c, "reasoning": r}
        for fid, (h, a, c, r) in sorted(P.items())
    ],
}
(DATA / "predictions" / "claude-fable-5.json").write_text(
    json.dumps(claude_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"fixtures: {len(fixtures)}  predictions: {len(claude_doc['predictions'])}")
