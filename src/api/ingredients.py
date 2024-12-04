from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/ingredients",
    tags=["ingredients"]
)

@router.get("/")
def get_ingredient_by_name(name: str):
    with db.engine.begin() as connection:
        # gets all matching ingreidents by name
        ingredients = connection.execute(sqlalchemy.text(
            """
            SELECT ingredient_id as id, ingredient_name as name, price
            FROM ingredients
            WHERE ingredient_name like :name
            """
        ), {"name": name}).all()
        
        if not ingredients:
            raise HTTPException(status_code=204, detail="Ingredient not found")

        response = [
            {
                "name": row.name,
                "id": row.id,
                "price": row.price
            }
            for row in ingredients
        ]

        return response

