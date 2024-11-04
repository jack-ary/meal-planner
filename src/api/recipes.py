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
    id: int
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


# {
#   "recipes": [
#     {
#       "id": "string",
#       "name": "string",
#       "ingredients": ["string"],
#       "instructions": "string",
#       "time": "integer", /* Cooking time in minutes */
#       "difficulty": "string", /* beginner, intermediate, advanced */
#       "supplies": ["string"]
#     }
#   ]
# }
# 1.1 get recipe
@router.get("/", response_model=List[RecipeResponse])
def get_recipes(ingredients: Optional[List[str]] = Query(None), difficulty: Optional[str] = None, supplies: Optional[List[str]] = Query(None)):

    with db.engine.begin() as connection:
        recipe_query = """SELECT id, name, instructions, time, difficulty FROM recipes AS r"""
        recipe_data = connection.execute(sqlalchemy.text(recipe_query)).mappings().all()

        ingredient_query = """SELECT r.id as recipe_id, i.ingredient_name
                            FROM recipes AS r
                            LEFT OUTER JOIN recipe_ingredients AS ri ON ri.recipe_id = r.id
                            LEFT OUTER JOIN ingredients AS i ON i.ingredient_id = ri.ingredient_id
                            """        
        ingredient_data = connection.execute(sqlalchemy.text(ingredient_query)).mappings().all()

        supplies_query = """SELECT r.id as recipe_id, s.supply_name
                            FROM recipes AS r
                            LEFT OUTER JOIN recipe_supplies rs on r.id = rs.recipe_id
                            LEFT OUTER JOIN supplies s on rs.supply_id = s.supply_id
                            """        
        supplies_data = connection.execute(sqlalchemy.text(supplies_query)).mappings().all()


        # Organize ingredients and supplies by recipe_id
        ingredients_dict = {}
        for ingredient in ingredient_data:
            recipe_id = ingredient["recipe_id"]
            ingredient_name = ingredient["ingredient_name"]
            if recipe_id not in ingredients_dict:
                ingredients_dict[recipe_id] = []
            if ingredient_name:  # Avoid adding None ingredients
                ingredients_dict[recipe_id].append(ingredient_name)

        supplies_dict = {}
        for supply in supplies_data:
            recipe_id = supply["recipe_id"]
            supply_name = supply["supply_name"]
            if recipe_id not in supplies_dict:
                supplies_dict[recipe_id] = []
            if supply_name:  # Avoid adding None supplies
                supplies_dict[recipe_id].append(supply_name)

        # Create list of Recipe instances
        recipes = []
        for recipe in recipe_data:
            recipe_id = recipe["id"]
            new_recipe = Recipe(
                id=recipe["id"],
                name=recipe["name"],
                ingredients=ingredients_dict.get(recipe_id, []),
                instructions=recipe["instructions"],
                time=recipe["time"],
                difficulty=recipe["difficulty"],
                supplies=supplies_dict.get(recipe_id, [])
            )
            recipes.append(new_recipe)

    # Filter recipes in Python with case-insensitive and whitespace-trimmed matching
    if difficulty:
        difficulty = difficulty.strip().lower()
        recipes = [recipe for recipe in recipes if recipe.difficulty.strip().lower() == difficulty]

    if supplies:
        supplies = [supply.strip().lower() for supply in supplies]
        recipes = [
            recipe for recipe in recipes
            if all(supply in [s.strip().lower() for s in recipe.supplies] for supply in supplies)
        ]

    if ingredients:
        ingredients = [ingredient.strip().lower() for ingredient in ingredients]
        recipes = [
            recipe for recipe in recipes
            if all(ingredient in [i.strip().lower() for i in recipe.ingredients] for ingredient in ingredients)
        ]

    # Format the response as a JSON list with the "recipes" root key
    response = [
        {
            "id": recipe.dict().get("id"),
            "name": recipe.name,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "time": recipe.time,
            "difficulty": recipe.difficulty,
            "supplies": recipe.supplies
        }
        for recipe in recipes
    ]

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
