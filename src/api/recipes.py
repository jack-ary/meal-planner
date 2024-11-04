from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"]
)

class Ingredient(BaseModel):
    name: str
    amount_units: Optional[str]
    price: Optional[float]
    item_type: Optional[str]

class Supply(BaseModel):
    supply_name: str

class Recipe(BaseModel):
    id: Optional[int]
    name: str
    ingredients: List[Ingredient]
    instructions: str
    time: int
    difficulty: str
    supplies: List[Supply]

class RecipeResponse(Recipe):
    id: int

class SuggestedRecipe(BaseModel):
    id: int
    name: str
    missing_ingredients: List[Ingredient]



@router.get("/", response_model=List[RecipeResponse])
def get_recipes(ingredients: Optional[List[str]] = Query(None), difficulty: Optional[str] = None, supplies: Optional[List[str]] = Query(None)):

    with db.engine.begin() as connection:
        # Query for recipe data
        recipe_query = """SELECT id, name, instructions, time, difficulty FROM recipes AS r"""
        recipe_data = connection.execute(sqlalchemy.text(recipe_query)).mappings().all()

        # Query for ingredients data with amount_units from recipe_ingredients
        ingredient_query = """SELECT r.id as recipe_id, i.ingredient_name, ri.amount_units, i.price, i.item_type
                              FROM recipes AS r
                              LEFT OUTER JOIN recipe_ingredients AS ri ON ri.recipe_id = r.id
                              LEFT OUTER JOIN ingredients AS i ON i.ingredient_id = ri.ingredient_id
                           """        
        ingredient_data = connection.execute(sqlalchemy.text(ingredient_query)).mappings().all()

        # Query for supplies data
        supplies_query = """SELECT r.id as recipe_id, s.supply_name
                            FROM recipes AS r
                            LEFT OUTER JOIN recipe_supplies rs ON r.id = rs.recipe_id
                            LEFT OUTER JOIN supplies s ON rs.supply_id = s.supply_id
                         """        
        supplies_data = connection.execute(sqlalchemy.text(supplies_query)).mappings().all()

        # Organize ingredients and supplies by recipe_id with required fields
        ingredients_dict = {}
        for ingredient in ingredient_data:
            recipe_id = ingredient["recipe_id"]
            ingredient_info = {
                "name": ingredient["ingredient_name"],
                "amount_units": ingredient["amount_units"],
                "price": ingredient["price"],
                "item_type": ingredient["item_type"]
            }
            if recipe_id not in ingredients_dict:
                ingredients_dict[recipe_id] = []
            if ingredient["ingredient_name"]:  # Avoid adding None ingredients
                ingredients_dict[recipe_id].append(ingredient_info)

        supplies_dict = {}
        for supply in supplies_data:
            recipe_id = supply["recipe_id"]
            supply_info = {"supply_name": supply["supply_name"]}
            if recipe_id not in supplies_dict:
                supplies_dict[recipe_id] = []
            if supply["supply_name"]:  # Avoid adding None supplies
                supplies_dict[recipe_id].append(supply_info)

        # Create list of Recipe instances
        recipes = []
        for recipe in recipe_data:
            recipe_id = recipe["id"]
            new_recipe = Recipe(
                id=recipe["id"],
                name=recipe["name"],
                ingredients=[Ingredient(**ingredient) for ingredient in ingredients_dict.get(recipe_id, [])],
                instructions=recipe["instructions"],
                time=recipe["time"],
                difficulty=recipe["difficulty"],
                supplies=[Supply(**supply) for supply in supplies_dict.get(recipe_id, [])]
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
            if all(supply in [s.supply_name.strip().lower() for s in recipe.supplies] for supply in supplies)
        ]

    if ingredients:
        ingredients = [ingredient.strip().lower() for ingredient in ingredients]
        recipes = [
            recipe for recipe in recipes
            if all(ingredient in [i.name.strip().lower() for i in recipe.ingredients] for ingredient in ingredients)
        ]

    # Format the response as a JSON list with the updated structure
    response = [
        {
            "id": recipe.id,
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


@router.post("/", response_model=Dict[str, Any])
def create_recipe(recipe: Recipe):

    with db.engine.begin() as connection:
        # Insert the main recipe data into the recipes table
        recipe_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO recipes (name, instructions, time, difficulty)
            VALUES (:name, :instructions, :time, :difficulty)
            RETURNING id
            """
        ), {
            "name": recipe.name,
            "instructions": recipe.instructions,
            "time": recipe.time,
            "difficulty": recipe.difficulty
        }).scalar_one()
        
        # Insert each ingredient into the recipe_ingredients table
        for ingredient in recipe.ingredients:
            # Convert ingredient name to lowercase for case-insensitive uniqueness
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO ingredients (ingredient_name, price, item_type)
                VALUES (LOWER(:ingredient_name), :price, :item_type)
                ON CONFLICT (LOWER(ingredient_name)) DO NOTHING
                """
            ), {
                "ingredient_name": ingredient.name,
                "price": ingredient.price,
                "item_type": ingredient.item_type
            })

            # Retrieve the ingredient_id (either newly created or existing)
            ingredient_id = connection.execute(sqlalchemy.text(
                """
                SELECT ingredient_id FROM ingredients WHERE LOWER(ingredient_name) = LOWER(:ingredient_name)
                """
            ), {"ingredient_name": ingredient.name}).scalar_one()

            # Insert into recipe_ingredients table
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount_units)
                VALUES (:recipe_id, :ingredient_id, :amount_units)
                """
            ), {
                "recipe_id": recipe_id,
                "ingredient_id": ingredient_id,
                "amount_units": ingredient.amount_units
            })

        # Insert each supply into the recipe_supplies table
        for supply in recipe.supplies:
            # Convert supply name to lowercase for case-insensitive uniqueness
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO supplies (supply_name)
                VALUES (LOWER(:supply_name))
                ON CONFLICT (LOWER(supply_name)) DO NOTHING
                """
            ), {"supply_name": supply.supply_name})

            # Retrieve the supply_id (either newly created or existing)
            supply_id = connection.execute(sqlalchemy.text(
                """
                SELECT supply_id FROM supplies WHERE LOWER(supply_name) = LOWER(:supply_name)
                """
            ), {"supply_name": supply.supply_name}).scalar_one()

            # Insert into recipe_supplies table
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO recipe_supplies (recipe_id, supply_id)
                VALUES (:recipe_id, :supply_id)
                """
            ), {
                "recipe_id": recipe_id,
                "supply_id": supply_id
            })

    return {
        "recipe_created": "Recipe created successfully",
        "recipe_id": recipe_id
    }

# 1.6 recipe suggestions  
@router.get("/suggestions", response_model=List[SuggestedRecipe])
def get_recipe_suggestions(ingredients: Optional[List[str]] = Query([])):
    # Normalize provided ingredients to lowercase for case-insensitive matching
    normalized_ingredients = {ingredient.strip().lower() for ingredient in ingredients}
    suggestions = []

    with db.engine.begin() as connection:
        # Query to get all ingredients for recipes that include at least one of the provided ingredients
        recipes = connection.execute(sqlalchemy.text(
            """
            SELECT r.id AS recipe_id, r.name AS recipe_name, i.ingredient_name AS ingredient_name, 
                   ri.amount_units, i.price, i.item_type
            FROM recipes AS r
            INNER JOIN recipe_ingredients AS ri ON r.id = ri.recipe_id
            INNER JOIN ingredients AS i ON i.ingredient_id = ri.ingredient_id
            WHERE LOWER(i.ingredient_name) = ANY(:ingredients)
            OR r.id IN (
                SELECT DISTINCT recipe_id
                FROM recipe_ingredients ri
                INNER JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
                WHERE LOWER(i.ingredient_name) = ANY(:ingredients)
            )
            """
        ), {"ingredients": list(normalized_ingredients)}).mappings().all()

        # Organize recipes and their ingredients by recipe_id
        recipe_dict = {}
        for row in recipes:
            recipe_id = row["recipe_id"]
            if recipe_id not in recipe_dict:
                recipe_dict[recipe_id] = {
                    "id": recipe_id,
                    "name": row["recipe_name"],
                    "ingredients": []
                }
            # Append each ingredient to the recipe's ingredient list
            recipe_dict[recipe_id]["ingredients"].append(Ingredient(
                name=row["ingredient_name"],
                amount_units=row["amount_units"],
                price=row["price"],
                item_type=row["item_type"]
            ))

        # Determine missing ingredients for each recipe
        for recipe in recipe_dict.values():
            # Identify which ingredients in this recipe are missing from the provided list
            missing_ingredients = [
                ingredient for ingredient in recipe["ingredients"]
                if ingredient.name.lower() not in normalized_ingredients
            ]
            # Add to suggestions if there are missing ingredients
            if missing_ingredients:
                suggestions.append(SuggestedRecipe(
                    id=recipe["id"],
                    name=recipe["name"],
                    missing_ingredients=missing_ingredients
                ))
    
    return suggestions

# 1.3 get recipe by id
@router.get("/{id}", response_model=Recipe)
def get_recipe_by_id(id: int):

    with db.engine.begin() as connection:
        # Fetch ingredients with detailed information
        ingredients = connection.execute(sqlalchemy.text(
            """
            SELECT i.ingredient_name AS name, ri.amount_units, i.price, i.item_type
            FROM recipe_ingredients AS ri
            INNER JOIN ingredients AS i ON i.ingredient_id = ri.ingredient_id
            WHERE ri.recipe_id = :id
            """
        ), {"id": id}).all()
        
        # Structure ingredients as a list of dictionaries
        final_ingredients = [
            {
                "name": row.name,
                "amount_units": row.amount_units,
                "price": row.price,
                "item_type": row.item_type
            }
            for row in ingredients
        ]

        # Fetch supplies with supply_name
        supplies = connection.execute(sqlalchemy.text(
            """
            SELECT s.supply_name
            FROM recipe_supplies AS rs
            INNER JOIN supplies AS s ON s.supply_id = rs.supply_id
            WHERE rs.recipe_id = :id
            """
        ), {"id": id}).all()

        # Structure supplies as a list of dictionaries
        final_supplies = [{"supply_name": row.supply_name} for row in supplies]

        # Fetch the main recipe details
        recipe = connection.execute(sqlalchemy.text(
            """
            SELECT id, name, instructions, time, difficulty
            FROM recipes
            WHERE id = :id
            """
        ), {"id": id}).one_or_none()

        # If no recipe is found, raise a 404 error
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

        # Return the recipe in the expected structure
        return {
            "id": recipe.id,
            "name": recipe.name,
            "instructions": recipe.instructions,
            "time": recipe.time,
            "difficulty": recipe.difficulty,
            "ingredients": final_ingredients,
            "supplies": final_supplies
        }


# 1.4 update recipe
@router.put("/{id}", response_model=Dict[str, str])
def update_recipe(id: int, recipe: Recipe):

    with db.engine.begin() as connection:
        # Update the main recipe details in the recipes table
        result = connection.execute(sqlalchemy.text(
            """
            UPDATE recipes
            SET name = :name, instructions = :instructions,
                time = :time, difficulty = :difficulty
            WHERE id = :id
            """
        ), {
            "id": id,
            "name": recipe.name,
            "instructions": recipe.instructions,
            "time": recipe.time,
            "difficulty": recipe.difficulty
        })

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Recipe was not found in db")

        # Delete existing ingredients for the recipe in recipe_ingredients
        connection.execute(sqlalchemy.text(
            "DELETE FROM recipe_ingredients WHERE recipe_id = :id"
        ), {"id": id})

        # Insert the updated ingredients with case-insensitive handling
        for ingredient in recipe.ingredients:
            # Insert ingredient if it doesn’t exist, with case-insensitivity
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO ingredients (ingredient_name, price, item_type)
                VALUES (LOWER(:ingredient_name), :price, :item_type)
                ON CONFLICT (LOWER(ingredient_name)) DO NOTHING
                """
            ), {
                "ingredient_name": ingredient.name,
                "price": ingredient.price,
                "item_type": ingredient.item_type
            })

            # Retrieve the ingredient_id (either newly created or existing)
            ingredient_id = connection.execute(sqlalchemy.text(
                """
                SELECT ingredient_id FROM ingredients WHERE LOWER(ingredient_name) = LOWER(:ingredient_name)
                """
            ), {"ingredient_name": ingredient.name}).scalar_one()

            # Insert into recipe_ingredients table
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount_units)
                VALUES (:recipe_id, :ingredient_id, :amount_units)
                """
            ), {
                "recipe_id": id,
                "ingredient_id": ingredient_id,
                "amount_units": ingredient.amount_units
            })

        # Delete existing supplies for the recipe in recipe_supplies
        connection.execute(sqlalchemy.text(
            "DELETE FROM recipe_supplies WHERE recipe_id = :id"
        ), {"id": id})

        # Insert the updated supplies with case-insensitive handling
        for supply in recipe.supplies:
            # Insert supply if it doesn’t exist, with case-insensitivity
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO supplies (supply_name)
                VALUES (LOWER(:supply_name))
                ON CONFLICT (LOWER(supply_name)) DO NOTHING
                """
            ), {"supply_name": supply.supply_name})

            # Retrieve the supply_id (either newly created or existing)
            supply_id = connection.execute(sqlalchemy.text(
                """
                SELECT supply_id FROM supplies WHERE LOWER(supply_name) = LOWER(:supply_name)
                """
            ), {"supply_name": supply.supply_name}).scalar_one()

            # Insert into recipe_supplies table
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO recipe_supplies (recipe_id, supply_id)
                VALUES (:recipe_id, :supply_id)
                """
            ), {
                "recipe_id": id,
                "supply_id": supply_id
            })

    return {"recipe_updated": "Recipe updated successfully"}


# 1.5 delete recipe
@router.delete("/{id}", response_model=Dict[str, str])
def delete_recipe(id: int):

    with db.engine.begin() as connection:
        # First, delete entries in recipe_ingredients for the given recipe
        connection.execute(sqlalchemy.text(
            """
            DELETE FROM recipe_ingredients
            WHERE recipe_id = :id
            """
        ), {"id": id})

        # Next, delete entries in recipe_supplies for the given recipe
        connection.execute(sqlalchemy.text(
            """
            DELETE FROM recipe_supplies
            WHERE recipe_id = :id
            """
        ), {"id": id})

        # Finally, delete the main recipe record from the recipes table
        result = connection.execute(sqlalchemy.text(
            """
            DELETE FROM recipes
            WHERE id = :id
            """
        ), {"id": id})

    # Check if any rows were deleted in the recipes table
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Recipe was not found in db")

    return {"deleted_complete": "Recipe deleted"}