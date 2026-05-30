import json
import os
import time
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import HTTPException

BACKEND_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = BACKEND_DIR.parent

load_dotenv(ROOT_DIR / ".env")
load_dotenv(BACKEND_DIR / ".env", override=True)

BASE_URL = "https://v3.football.api-sports.io"

LEAGUES = {
    "Premier League": 39,
    "La Liga": 140,
    "Serie A": 135,
    "Bundesliga": 78,
    "Ligue 1": 61,
    "UEFA Champions League": 2,
}
FINISHED_STATUSES = {"FT", "AET", "PEN"}
CACHE_TTL_SECONDS = 60
CACHE_DIR = BACKEND_DIR / ".cache"
STALE_MATCHES_CACHE_FILE = CACHE_DIR / "api_football_matches.json"
STALE_DETAILS_CACHE_FILE = CACHE_DIR / "api_football_match_details.json"
_matches_cache = {}
_match_details_cache = {}
_season_fixtures_cache = {}


def get_headers():
    load_dotenv(BACKEND_DIR / ".env", override=True)
    api_key = os.getenv("API_FOOTBALL_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Missing API_FOOTBALL_API_KEY in .env",
        )

    return {"x-apisports-key": api_key}


def current_season():
    configured_season = os.getenv("API_FOOTBALL_SEASON")
    if configured_season:
        return int(configured_season)

    now = datetime.now(timezone.utc)
    inferred_season = now.year if now.month >= 7 else now.year - 1

    # API-Football Free accounts currently expose historical seasons only.
    return min(inferred_season, 2024)


def normalize_match(match):
    fixture = match.get("fixture", {})
    league = match.get("league", {})
    teams = match.get("teams", {})
    home_team = teams.get("home", {})
    away_team = teams.get("away", {})
    status = fixture.get("status", {})
    goals = match.get("goals", {})
    score = match.get("score", {})

    return {
        "id": fixture.get("id"),
        "competition": league.get("name", "Unknown League"),
        "homeTeam": home_team.get("name", "Unknown Home"),
        "awayTeam": away_team.get("name", "Unknown Away"),
        "utcDate": fixture.get("date"),
        "status": status.get("short") or status.get("long"),
        "matchday": None,
        "score": {
            "winner": None,
            "duration": None,
            "fullTime": {
                "home": score.get("fulltime", {}).get("home", goals.get("home")),
                "away": score.get("fulltime", {}).get("away", goals.get("away")),
            },
            "halfTime": {
                "home": score.get("halftime", {}).get("home"),
                "away": score.get("halftime", {}).get("away"),
            },
        },
    }


def get_cached_matches(status):
    cached = _matches_cache.get(status)
    if not cached:
        return None

    expires_at, matches = cached
    if expires_at <= time.time():
        _matches_cache.pop(status, None)
        return None

    return deepcopy(matches)


def read_cache_file(path):
    try:
        with path.open("r", encoding="utf-8") as cache_file:
            return json.load(cache_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_cache_file(path, cache):
    CACHE_DIR.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8") as cache_file:
        json.dump(cache, cache_file)


def load_stale_matches(status):
    cache = read_cache_file(STALE_MATCHES_CACHE_FILE)
    matches = cache.get(status, {}).get("matches")
    if not matches:
        return None

    return deepcopy(matches)


def save_stale_matches(status, matches):
    if not matches:
        return

    cache = read_cache_file(STALE_MATCHES_CACHE_FILE)
    cache[status] = {
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "matches": matches,
    }
    write_cache_file(STALE_MATCHES_CACHE_FILE, cache)


def load_stale_match_detail(match_id):
    cache = read_cache_file(STALE_DETAILS_CACHE_FILE)
    detail = cache.get(str(match_id))
    if not detail:
        return None

    return deepcopy(detail)


def save_stale_match_detail(match_id, detail):
    if not detail:
        return

    cache = read_cache_file(STALE_DETAILS_CACHE_FILE)
    cache[str(match_id)] = {
        **detail,
        "cachedAt": datetime.now(timezone.utc).isoformat(),
    }
    write_cache_file(STALE_DETAILS_CACHE_FILE, cache)


def fallback_to_stale_matches(status, error=None):
    stale_matches = load_stale_matches(status)
    if stale_matches is not None:
        set_cached_matches(status, stale_matches)
        return stale_matches

    if error is not None:
        raise error

    return []


def get_cached(cache, key):
    cached = cache.get(key)
    if not cached:
        return None

    expires_at, value = cached
    if expires_at <= time.time():
        cache.pop(key, None)
        return None

    return deepcopy(value)


def set_cached(cache, key, value):
    cache[key] = (
        time.time() + CACHE_TTL_SECONDS,
        deepcopy(value),
    )


def set_cached_matches(status, matches):
    set_cached(_matches_cache, status, matches)
    save_stale_matches(status, matches)


def get_cached_match_detail(match_id):
    return get_cached(_match_details_cache, str(match_id))


def set_cached_match_detail(match_id, detail):
    set_cached(_match_details_cache, str(match_id), detail)
    save_stale_match_detail(match_id, detail)


def describe_response_error(response):
    try:
        body = response.json()
        detail = body.get("message") or body.get("errors") or response.text
    except ValueError:
        detail = response.text

    detail = str(detail).strip()[:300]
    return f"{response.status_code} {response.reason}: {detail}"


def api_get(path, params=None):
    try:
        response = requests.get(
            f"{BASE_URL}{path}",
            headers=get_headers(),
            params=params or {},
            timeout=10,
        )

        if response.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail="API-Football rate limit reached. Wait a minute and retry.",
            )

        if not response.ok:
            raise HTTPException(
                status_code=502,
                detail=f"API-Football error: {describe_response_error(response)}",
            )

        data = response.json()
        errors = data.get("errors")
        if errors:
            status_code = 429 if "rateLimit" in errors else 502
            raise HTTPException(
                status_code=status_code,
                detail=f"API-Football error: {errors}",
            )

        return data

    except HTTPException:
        raise
    except requests.RequestException as e:
        raise HTTPException(
            status_code=502,
            detail=f"Could not reach API-Football: {e}",
        ) from e


def fetch_fixtures(params):
    data = api_get("/fixtures", params=params)
    return [normalize_match(match) for match in data.get("response", [])]


def normalize_event(event):
    time_data = event.get("time", {})
    team = event.get("team", {})
    player = event.get("player", {})
    assist = event.get("assist", {})

    return {
        "elapsed": time_data.get("elapsed"),
        "extra": time_data.get("extra"),
        "team": team.get("name"),
        "player": player.get("name"),
        "assist": assist.get("name"),
        "type": event.get("type"),
        "detail": event.get("detail"),
        "comments": event.get("comments"),
    }


def fetch_fixture(match_id):
    matches = fetch_fixtures({"id": match_id})
    return matches[0] if matches else find_cached_match(match_id)


def fetch_fixture_events(match_id):
    data = api_get("/fixtures/events", params={"fixture": match_id})
    return [normalize_event(event) for event in data.get("response", [])]


def find_cached_match(match_id):
    matches = load_stale_matches("FINISHED") or []
    for match in matches:
        if str(match.get("id")) == str(match_id):
            return match

    return None


def fetch_season_fixtures(season):
    cache_key = f"season:{season}"
    cached_matches = get_cached(_season_fixtures_cache, cache_key)
    if cached_matches is not None:
        return cached_matches

    matches = []
    for league_id in LEAGUES.values():
        matches.extend(
            fetch_fixtures(
                {
                    "league": league_id,
                    "season": season,
                }
            )
        )

    set_cached(_season_fixtures_cache, cache_key, matches)
    return matches


def fetch_matches(status):
    cached_matches = get_cached_matches(status)
    if cached_matches is not None:
        return cached_matches

    try:
        season = current_season()
        season_matches = fetch_season_fixtures(season)
        matches = []

        for league_name in LEAGUES:
            league_matches = [
                match
                for match in season_matches
                if match.get("competition") == league_name
            ]

            league_matches = [
                match
                for match in league_matches
                if match.get("status") in FINISHED_STATUSES
            ]
            league_matches.sort(key=lambda x: x.get("utcDate") or "", reverse=True)

            matches.extend(league_matches[:10])

        matches = [
            match for match in matches if match.get("status") in FINISHED_STATUSES
        ]
        matches.sort(key=lambda x: x.get("utcDate") or "", reverse=True)

        if not matches:
            return fallback_to_stale_matches(status)

        set_cached_matches(status, matches)
        return matches

    except HTTPException as e:
        return fallback_to_stale_matches(status, e)


def group_by_date_then_league(matches):
    grouped = {}

    for match in matches:
        date_key = match.get("utcDate", "")[:10]
        league = match.get("competition", "Unknown League")

        if date_key not in grouped:
            grouped[date_key] = {}

        if league not in grouped[date_key]:
            grouped[date_key][league] = []

        grouped[date_key][league].append(match)

    return grouped


def get_past_matches():
    matches = fetch_matches("FINISHED")

    matches.sort(
        key=lambda x: x.get("utcDate", ""),
        reverse=True,
    )

    return {
        "type": "past",
        "count": len(matches),
        "groupedMatches": group_by_date_then_league(matches),
        "matches": matches,
    }


def get_match_detail(match_id):
    cached_detail = get_cached_match_detail(match_id)
    if cached_detail is not None:
        return cached_detail

    try:
        match = fetch_fixture(match_id)
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")

        events = fetch_fixture_events(match_id)
        detail = {
            "match": match,
            "events": events,
        }
        set_cached_match_detail(match_id, detail)
        return detail

    except HTTPException as e:
        stale_detail = load_stale_match_detail(match_id)
        if stale_detail is not None:
            set_cached(_match_details_cache, str(match_id), stale_detail)
            return stale_detail

        raise e
