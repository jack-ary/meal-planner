from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"]
)

class Recipe(BaseModel):
    name: str
    ingredients: List[str]
    instructions: str
    time: int
    difficulty: str
    supplies: List[str]

class RecipeResponse(Recipe):
    id: int

class SuggestedRecipe(BaseModel):
    id: int
    name: str
    missing_ingredients: List[str]

# 1.1 get recipe
@router.get("/", response_model=List[RecipeResponse])
def get_recipes(ingredients: Optional[List[str]] = Query(None), difficulty: Optional[str] = None, supplies: Optional[List[str]] = Query(None)):

    with db.engine.begin() as connection:
        query = "SELECT id, name, ingredients, instructions, time, difficulty, supplies FROM recipes"
        recipes = connection.execute(sqlalchemy.text(query)).mappings().all()

        # Filter recipes in Python since PostgreSQL does not support list containment directly in simple queries
        if difficulty:
            recipes = [recipe for recipe in recipes if recipe['difficulty'] == difficulty]

        if supplies:
            recipes = [
                recipe for recipe in recipes
                if all(supply in recipe['supplies'] for supply in supplies)
            ]
        if ingredients:
            recipes = [
                recipe for recipe in recipes
                if all(ingredient in recipe['ingredients'] for ingredient in ingredients)
            ]

        response = [dict(recipe) for recipe in recipes]

    return response

# 1.2 create recipe
@router.post("/", response_model=Dict[str, Any])
def create_recipe(recipe: Recipe):

    with db.engine.begin() as connection:
        recipe_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO recipes (name, ingredients, instructions, time, difficulty, supplies)
            VALUES(:name, :ingredients, :instructions, :time, :difficulty, :supplies)
            RETURNING id
            """
        ), {
            "name": recipe.name,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "time": recipe.time,
            "difficulty": recipe.difficulty,
            "supplies": recipe.supplies
        }).scalar_one()
    
    return {
        "recipe_created": "Recipe created successfully",
        "recipe_id": recipe_id
    }

# 1.3 get recipe by id
@router.get("/{id}", response_model=RecipeResponse)
def get_recipe_by_id(id: int):

    with db.engine.begin() as connection:
        recipe = connection.execute(sqlalchemy.text(
            """
            SELECT id, name, ingredients, instructions, time, difficulty, supplies
            FROM recipes
            WHERE id = :id
            """
        ), {"id": id}).mappings().first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe was not found in db")
    
    return recipe

# 1.4 update recipe
@router.put("/{id}", response_model=Dict[str, str])
def update_recipe(id: int, recipe: Recipe):

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            UPDATE recipes
            SET name = :name, ingredients = :ingredients, instructions = :instructions,
                time = :time, difficulty = :difficulty, supplies = :supplies
            WHERE id = :id
            """
        ), {
            "id": id,
            "name": recipe.name,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "time": recipe.time,
            "difficulty": recipe.difficulty,
            "supplies": recipe.supplies
        })

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Recipe was not found in db")
    
    return {"recipe_updated": "Recipe updated successfully"}

# 1.5 delete recipe
@router.delete("/{id}", response_model=Dict[str, str])
def delete_recipe(id: int):

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            DELETE FROM recipes
            WHERE id = :id
            """
        ), {"id": id})

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Recipe was not found in db")

    return {"deleted_complete": "Recipe deleted"}

# 1.6 recipe suggestions
@router.get("/suggestions", response_model=List[SuggestedRecipe])
def get_recipe_suggestions(ingredients: List[str] = Query(...)):

    suggestions = []

    with db.engine.begin() as connection:
        recipes = connection.execute(sqlalchemy.text(
            "SELECT id, name, ingredients FROM recipes"
        )).mappings().all()

        for recipe in recipes:
            missing_ingredients = []
            for ingredient in recipe['ingredients']:
                if ingredient not in ingredients:
                    missing_ingredients.append(ingredient)  # Add missing ingredient
            if missing_ingredients:
                suggestions.append({
                    "id": recipe["id"],
                    "name": recipe["name"],
                    "missing_ingredients": missing_ingredients
                })
    
    return suggestions
