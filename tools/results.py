#!/usr/bin/env python3
"""Record match results in data/results.json as the tournament unfolds.

Usage:
  tools/results.py set <fixture_id> <home_score> <away_score>
  tools/results.py set <fixture_id> <CODE>=<score> <CODE>=<score>

  Knockout fixtures (stage != group) also need a winner. If the 90-minute
  score is level, add how it was decided and (for penalties) the shootout
  score:
  tools/results.py set <fixture_id> <home_score> <away_score> winner=<CODE>
  tools/results.py set <fixture_id> <home_score> <away_score> winner=<CODE> decided=aet
  tools/results.py set <fixture_id> <home_score> <away_score> winner=<CODE> decided=pens pens=<h>-<a>

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
    if len(args) < 3:
        sys.exit(
            "usage: results.py set <fixture_id> <home_score> <away_score> [winner=<CODE>] [decided=aet|pens] [pens=<h>-<a>]\n"
            "   or: results.py set <fixture_id> <CODE>=<score> <CODE>=<score> [winner=<CODE>] [decided=aet|pens] [pens=<h>-<a>]"
        )
    fid, a, b, *extra = args
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

    extras = {}
    for arg in extra:
        key, sep, value = arg.partition("=")
        if not sep or key not in ("winner", "decided", "pens"):
            sys.exit(f"invalid argument: {arg}")
        extras[key] = value

    entry = {"home_score": home, "away_score": away}

    if fixture["stage"] == "group":
        if extras:
            sys.exit(f"fixture {fid} is a group-stage fixture and doesn't take {', '.join(extras)}")
    else:
        winner = extras.get("winner")
        if winner is None:
            if home != away:
                winner = fixture["home"] if home > away else fixture["away"]
            else:
                sys.exit(f"fixture {fid} is level after 90 minutes; pass winner=<CODE>")
        if winner not in (fixture["home"], fixture["away"]):
            sys.exit(f"winner must be {fixture['home']} or {fixture['away']}, got {winner!r}")
        entry["winner"] = winner

        if home == away:
            decided = extras.get("decided", "aet")
            if decided not in ("aet", "pens"):
                sys.exit("decided must be 'aet' or 'pens'")
            if decided == "pens":
                entry["decided"] = "pens"
                pens = extras.get("pens")
                if not pens:
                    sys.exit("decided=pens requires pens=<home>-<away>, e.g. pens=4-3")
                ph, sep, pa = pens.partition("-")
                if not sep:
                    sys.exit("pens must be in <home>-<away> form, e.g. pens=4-3")
                try:
                    ph, pa = int(ph), int(pa)
                except ValueError:
                    sys.exit("pens scores must be integers")
                if ph == pa:
                    sys.exit("pens scores can't be tied")
                if (ph > pa and winner != fixture["home"]) or (pa > ph and winner != fixture["away"]):
                    sys.exit("winner doesn't match the pens scoreline")
                entry["pens"] = {"home_score": ph, "away_score": pa}
        elif "decided" in extras or "pens" in extras:
            sys.exit(f"fixture {fid} wasn't level after 90 minutes; decided/pens don't apply")

    doc = load(RESULTS)
    doc["results"][fid] = entry
    save(RESULTS, doc)
    if "winner" not in entry:
        suffix = ""
    elif home == away:
        decided = entry.get("decided", "aet")
        pens = f" {entry['pens']['home_score']}-{entry['pens']['away_score']}" if "pens" in entry else ""
        suffix = f" ({decided}{pens}, {entry['winner']} won)"
    else:
        suffix = f" ({entry['winner']} won)"
    print(f"{fid}: {home}-{away}{suffix} saved")


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
                res = {**res, "home_score": res["away_score"], "away_score": res["home_score"]}
                if "pens" in res:
                    res["pens"] = {"home_score": res["pens"]["away_score"], "away_score": res["pens"]["home_score"]}

        home, away = teams[home_code]["name"], teams[away_code]["name"]
        if not res:
            print(f"{fid:4} {home} v {away}  (pending)")
        elif "winner" not in res:
            print(f"{fid:4} {home} {res['home_score']}-{res['away_score']} {away}")
        else:
            winner_name = teams[res["winner"]]["name"]
            if res["home_score"] == res["away_score"]:
                decided = res.get("decided", "aet")
                pens = f" {res['pens']['home_score']}-{res['pens']['away_score']}" if "pens" in res else ""
                print(f"{fid:4} {home} {res['home_score']}-{res['away_score']} {away}  ({decided}{pens}, {winner_name} won)")
            else:
                print(f"{fid:4} {home} {res['home_score']}-{res['away_score']} {away}  ({winner_name} won)")


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
        fifa_swapped = fifa_home != fixture["home"]

        # Orient scores to our fixture's home/away
        if not fifa_swapped:
            home_score, away_score = fifa_home_score, fifa_away_score
        else:
            home_score, away_score = fifa_away_score, fifa_home_score

        new_entry = {"home_score": home_score, "away_score": away_score}

        if fixture["stage"] != "group":
            winner_id = match.get("Winner")
            if winner_id is not None:
                winner_id = str(winner_id)
                if winner_id == str(match["Home"]["IdTeam"]):
                    new_entry["winner"] = fifa_home if not fifa_swapped else fifa_away
                elif winner_id == str(match["Away"]["IdTeam"]):
                    new_entry["winner"] = fifa_away if not fifa_swapped else fifa_home

            if "winner" in new_entry and home_score == away_score:
                home_pens = match.get("HomeTeamPenaltyScore")
                away_pens = match.get("AwayTeamPenaltyScore")
                if home_pens is not None and away_pens is not None:
                    new_entry["decided"] = "pens"
                    if not fifa_swapped:
                        new_entry["pens"] = {"home_score": home_pens, "away_score": away_pens}
                    else:
                        new_entry["pens"] = {"home_score": away_pens, "away_score": home_pens}
                else:
                    new_entry["decided"] = "aet"

        existing = results.get(fid)

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
