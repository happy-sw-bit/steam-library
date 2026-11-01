"""Export the Steam library for Steam DLC Watch.

Calls IPlayerService/GetOwnedGames with the key from STEAM_API_KEY and writes
library.json in the same shape the DLC Watch page saves: every game played
for more than an hour, plus totals for the whole library. The key is never
written to disk.
"""
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request

THRESHOLD = 60  # minutes; games over one hour are watched
OUT = os.environ.get("LIBRARY_OUT", "library.json")


def fetch(key, steamid):
    q = urllib.parse.urlencode({
        "key": key,
        "steamid": steamid,
        "include_appinfo": 1,
        "include_played_free_games": 1,
        "format": "json",
    })
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?" + q
    req = urllib.request.Request(url, headers={"User-Agent": "steam-dlc-watch export"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def build(resp, now):
    games = (resp or {}).get("response", {}).get("games")
    if not isinstance(games, list) or not games:
        raise SystemExit("Steam returned no games. Check STEAM_API_KEY, STEAM_ID and that game details are public.")
    played, never, under = [], 0, 0
    for g in games:
        if not isinstance(g.get("appid"), int):
            continue
        m = int(g.get("playtime_forever") or 0)
        if not m:
            never += 1
        elif m <= THRESHOLD:
            under += 1
        if m > THRESHOLD:
            row = {"a": g["appid"], "n": str(g.get("name") or f"App {g['appid']}")[:200], "m": m}
            lp = int(g.get("rtime_last_played") or 0)
            if lp > 0:
                row["l"] = lp
            ic = str(g.get("img_icon_url") or "")
            if len(ic) == 40 and all(c in "0123456789abcdef" for c in ic):
                row["i"] = ic
            w = int(g.get("playtime_2weeks") or 0)
            if w > 0:
                row["w"] = w
            played.append(row)
    played.sort(key=lambda x: -x["m"])
    return {
        "updatedAt": now,
        "source": "github",
        "thresholdMinutes": THRESHOLD,
        "totalGames": len(games),
        "neverPlayed": never,
        "underHour": under,
        "games": played,
    }


def main():
    key = os.environ.get("STEAM_API_KEY", "").strip()
    steamid = os.environ.get("STEAM_ID", "").strip()
    if not key or not steamid:
        sys.exit("STEAM_API_KEY and STEAM_ID must be set.")
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    lib = build(fetch(key, steamid), now)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(lib, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(lib['games'])} of {lib['totalGames']} games over {THRESHOLD} minutes")


if __name__ == "__main__":
    main()
