import requests

def get_live_matches():
    url = "https://www.thesportsdb.com/api/v1/json/123/eventsnext.php?id=133604"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "source": "TheSportsDB",
            "team": "Arsenal",
            "matches": data.get("events") or []
        }

    except Exception as e:
        return {
            "source": "TheSportsDB",
            "team": "Arsenal",
            "matches": [],
            "error": str(e)
        }