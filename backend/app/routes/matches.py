from fastapi import APIRouter
from app.services.football_api import (
    get_match_detail,
    get_past_matches,
)

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get("/past")
def past_matches():
    return get_past_matches()


@router.get("/{match_id}")
def match_detail(match_id: int):
    return get_match_detail(match_id)
