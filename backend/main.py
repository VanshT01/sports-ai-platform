from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Football AI backend running"}

@app.get("/matches")
def get_matches():
    return [
        {
            "id": 1,
            "home_team": "Manchester United",
            "away_team": "Arsenal",
            "home_score": 1,
            "away_score": 2,
            "status": "LIVE"
        }
    ]