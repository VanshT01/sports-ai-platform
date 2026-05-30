from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.matches import router as matches_router

app = FastAPI(title="Football AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matches_router)

@app.get("/")
def home():
    return {"message": "Football AI backend running"}