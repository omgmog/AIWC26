#!/usr/bin/env python3
"""Record group-stage results in data/results.json as the tournament unfolds.

Usage:
  tools/results.py set <fixture_id> <home_score> <away_score>
  tools/results.py set <fixture_id> <CODE>=<score> <CODE>=<score>
  tools/results.py unset <fixture_id>
  tools/results.py list

The first form of "set" is canonical home-first, matching fixtures.json and
the scoring prompt. The second form (CODE=score) is orientation-proof: the
two team codes can be given in either order.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_data"
FIXTURES = DATA / "fixtures.json"
RESULTS = DATA / "results.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, doc):
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def cmd_set(args):
    if len(args) != 3:
        sys.exit(
            "usage: results.py set <fixture_id> <home_score> <away_score>\n"
            "   or: results.py set <fixture_id> <CODE>=<score> <CODE>=<score>"
        )
    fid, a, b = args
    fixtures = load(FIXTURES)
    fixture = next((f for f in fixtures["fixtures"] if f["id"] == fid), None)
    if fixture is None:
        sys.exit(f"unknown fixture id: {fid}")

    if "=" in a or "=" in b:
        scores = {}
        for arg in (a, b):
            code, sep, score_raw = arg.partition("=")
            if not sep:
                sys.exit(f"invalid CODE=score argument: {arg}")
            if code not in (fixture["home"], fixture["away"]):
                sys.exit(f"{code} is not a team in fixture {fid}")
            try:
                scores[code] = int(score_raw)
            except ValueError:
                sys.exit("scores must be integers")
        if set(scores) != {fixture["home"], fixture["away"]}:
            sys.exit(f"expected scores for both {fixture['home']} and {fixture['away']}")
        home, away = scores[fixture["home"]], scores[fixture["away"]]
    else:
        try:
            home, away = int(a), int(b)
        except ValueError:
            sys.exit("scores must be integers")

    if home < 0 or away < 0:
        sys.exit("scores must be non-negative")
    doc = load(RESULTS)
    doc["results"][fid] = {"home_score": home, "away_score": away}
    save(RESULTS, doc)
    print(f"{fid}: {home}-{away} saved")


def cmd_unset(args):
    if len(args) != 1:
        sys.exit("usage: results.py unset <fixture_id>")
    fid = args[0]
    doc = load(RESULTS)
    if doc["results"].pop(fid, None) is None:
        sys.exit(f"no result recorded for {fid}")
    save(RESULTS, doc)
    print(f"{fid}: result removed")


def cmd_list(_args):
    fixtures = load(FIXTURES)
    teams = fixtures["teams"]
    results = load(RESULTS)["results"]
    for f in fixtures["fixtures"]:
        fid = f["id"]
        home_code, away_code = f["home"], f["away"]
        res = results.get(fid)

        actual_home = f.get("actual_home")
        if actual_home and actual_home != home_code:
            home_code, away_code = away_code, home_code
            if res:
                res = {"home_score": res["away_score"], "away_score": res["home_score"]}

        home, away = teams[home_code]["name"], teams[away_code]["name"]
        if res:
            print(f"{fid:4} {home} {res['home_score']}-{res['away_score']} {away}")
        else:
            print(f"{fid:4} {home} v {away}  (pending)")


COMMANDS = {"set": cmd_set, "unset": cmd_unset, "list": cmd_list}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        sys.exit(f"usage: results.py <{'|'.join(COMMANDS)}> [args...]")
    COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    main()
