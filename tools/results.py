#!/usr/bin/env python3
"""Record group-stage results in data/results.json as the tournament unfolds.

Usage:
  tools/results.py set <fixture_id> <home_score> <away_score>
  tools/results.py set <fixture_id> <CODE>=<score> <CODE>=<score>
  tools/results.py unset <fixture_id>
  tools/results.py list
  tools/results.py sync [--dry-run]
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_data"
FIXTURES = DATA / "fixtures.json"
RESULTS = DATA / "results.json"

FIFA_API = (
    "https://api.fifa.com/api/v3/calendar/matches"
    "?language=en&count=500&idSeason=285023"
)


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


def fetch_fifa_results():
    req = urllib.request.Request(FIFA_API, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def cmd_sync(args):
    dry_run = "--dry-run" in args

    fixtures = load(FIXTURES)
    # Build lookup: frozenset({home, away}) -> fixture
    by_teams = {frozenset([f["home"], f["away"]]): f for f in fixtures["fixtures"]}

    print("Fetching from FIFA API...", flush=True)
    data = fetch_fifa_results()

    doc = load(RESULTS)
    results = doc["results"]

    added, updated, skipped = [], [], []

    for match in data["Results"]:
        if not match.get("Home") or not match.get("Away"):
            continue
        if match.get("HomeTeamScore") is None or match.get("AwayTeamScore") is None:
            continue

        fifa_home = match["Home"]["Abbreviation"]
        fifa_away = match["Away"]["Abbreviation"]
        fifa_home_score = match["HomeTeamScore"]
        fifa_away_score = match["AwayTeamScore"]

        key = frozenset([fifa_home, fifa_away])
        fixture = by_teams.get(key)
        if fixture is None:
            continue  # knockout or unknown

        fid = fixture["id"]

        # Orient scores to our fixture's home/away
        if fifa_home == fixture["home"]:
            home_score, away_score = fifa_home_score, fifa_away_score
        else:
            home_score, away_score = fifa_away_score, fifa_home_score

        existing = results.get(fid)
        new_entry = {"home_score": home_score, "away_score": away_score}

        if existing == new_entry:
            skipped.append(fid)
        elif existing is None:
            added.append(fid)
            if not dry_run:
                results[fid] = new_entry
            print(f"  ADD  {fid}: {home_score}-{away_score}")
        else:
            updated.append(fid)
            if not dry_run:
                results[fid] = new_entry
            print(f"  UPD  {fid}: {existing['home_score']}-{existing['away_score']} -> {home_score}-{away_score}")

    if not dry_run and (added or updated):
        save(RESULTS, doc)

    print(
        f"\n{'[dry-run] ' if dry_run else ''}"
        f"{len(added)} added, {len(updated)} updated, {len(skipped)} unchanged"
    )


COMMANDS = {"set": cmd_set, "unset": cmd_unset, "list": cmd_list, "sync": cmd_sync}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        sys.exit(f"usage: results.py <{'|'.join(COMMANDS)}> [args...]")
    COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    main()
