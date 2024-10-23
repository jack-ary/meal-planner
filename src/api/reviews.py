from fastapi import APIRouter
from src import database as db
import sqlalchemy

router = APIRouter()

@router.get("/reviews/", tags=["reviews"])
def get_reviews():
    """
    Fetch ...
    """

    return "OK"
