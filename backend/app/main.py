from fastapi import FastAPI
from app.services.football_api import get_live_matches

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Football AI backend running"}

@app.get("/matches/live")
def live_matches():
    return get_live_matches()