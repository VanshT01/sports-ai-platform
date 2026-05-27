import requests

def get_live_matches():
    url = "https://www.thesportsdb.com/api/v1/json/123/eventsnext.php?id=133604"

    response = requests.get(url, timeout=10)
    data = response.json()

    events = data.get("events") or []

    return {
        "source": "TheSportsDB",
        "team": "Arsenal",
        "matches": events
    }