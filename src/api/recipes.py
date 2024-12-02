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

class CreateRecipe(BaseModel):
    name: str
    ingredients: List[Ingredient]
    instructions: str
    time: int
    difficulty: str
    supplies: List[Supply]

class Recipe(BaseModel):
    id: int
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



# 1.1 get recipes
@router.get("/", response_model=List[RecipeResponse], status_code=200)
def get_recipes(ingredients: Optional[List[str]] = Query(None), difficulty: Optional[str] = None, supplies: Optional[List[str]] = Query(None)):

    with db.engine.begin() as connection:
        # get all the recipe data that we need
        recipe_query = """SELECT id, name, instructions, time, difficulty FROM recipes AS r"""
        recipe_data = connection.execute(sqlalchemy.text(recipe_query)).mappings().all()

        # get all the ingredient data
        ingredient_query = """SELECT r.id as recipe_id, i.ingredient_name, ri.amount_units, i.price, i.item_type
                              FROM recipes AS r
                              LEFT OUTER JOIN recipe_ingredients AS ri ON ri.recipe_id = r.id
                              LEFT OUTER JOIN ingredients AS i ON i.ingredient_id = ri.ingredient_id
                           """        
        ingredient_data = connection.execute(sqlalchemy.text(ingredient_query)).mappings().all()

        # get all the supply data
        supplies_query = """SELECT r.id as recipe_id, s.supply_name
                            FROM recipes AS r
                            LEFT OUTER JOIN recipe_supplies rs ON r.id = rs.recipe_id
                            LEFT OUTER JOIN supplies s ON rs.supply_id = s.supply_id
                         """        
        supplies_data = connection.execute(sqlalchemy.text(supplies_query)).mappings().all()

        # filter the ingredients and supplies by recipe_id 
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
            if ingredient["ingredient_name"]:  # don't want to get an ingredient if its name is None
                ingredients_dict[recipe_id].append(ingredient_info)

        supplies_dict = {}
        for supply in supplies_data:
            recipe_id = supply["recipe_id"]
            supply_info = {"supply_name": supply["supply_name"]}
            if recipe_id not in supplies_dict:
                supplies_dict[recipe_id] = []
            if supply["supply_name"]:  # catching an edge case, don't want to get a None supply name
                supplies_dict[recipe_id].append(supply_info)

        # with all the information we have above create a list of recipes 
        recipes = []
        for recipe in recipe_data:
            recipe_id = recipe["id"]
            new_recipe = Recipe(
                id=recipe["id"],
                name=recipe["name"],
                ingredients=[
                    Ingredient(
                        name=ingredient["name"],
                        amount_units=ingredient["amount_units"],
                        price=ingredient["price"],
                        item_type=ingredient["item_type"]
                    ) for ingredient in ingredients_dict.get(recipe_id, [])
                ],
                instructions=recipe["instructions"],
                time=recipe["time"],
                difficulty=recipe["difficulty"],
                supplies=[
                    Supply(supply_name=supply["supply_name"]) for supply in supplies_dict.get(recipe_id, [])
                ]
            )
            recipes.append(new_recipe)

    # this is going to filter all the recipes so we can match their input preferences and also takes care of case and whitespace
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

    response = []
    for recipe in recipes:
        response.append({
            "id": recipe.id,
            "name": recipe.name,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "time": recipe.time,
            "difficulty": recipe.difficulty,
            "supplies": recipe.supplies
        })

    return response


# 1.2 create recipe
@router.post("/", response_model=Dict[str, Any], status_code=201)
def create_recipe(recipe: CreateRecipe):

    if recipe.time <= 0:
        raise HTTPException(status_code=400, detail="Time must be a positive integer.")
    if not recipe.name.strip():
        raise HTTPException(status_code=400, detail="Recipe name cannot be empty.")

    ingredient_names = set()
    for ingredient in recipe.ingredients:
        if not ingredient.name.strip():
            raise HTTPException(status_code=400, detail="Ingredient name cannot be empty.")
        if ingredient.amount_units is not None and not ingredient.amount_units.strip():
            raise HTTPException(status_code=400, detail=f"Ingredient {ingredient.name}: amount units cannot be empty.")
        if ingredient.name.lower() in ingredient_names:
            raise HTTPException(status_code=400, detail=f"Duplicate ingredient: {ingredient.name}")
        ingredient_names.add(ingredient.name.lower().strip())

    supply_names = set()
    for supply in recipe.supplies:
        if not supply.supply_name.strip():
            raise HTTPException(status_code=400, detail="Supply name cannot be empty.")
        if supply.supply_name.lower() in supply_names:
            raise HTTPException(status_code=400, detail=f"Duplicate supply: {supply.supply_name}")
        supply_names.add(supply.supply_name.lower().strip())

    with db.engine.begin() as connection:
        # insert the recipe the person wants to create into the recipes table
        recipe_result = connection.execute(sqlalchemy.text(
            """
            INSERT INTO recipes (name, instructions, time, difficulty)
            VALUES (:name, :instructions, :time, :difficulty)
            RETURNING id
            """
        ), {
            "name": recipe.name.strip(),
            "instructions": recipe.instructions,
            "time": recipe.time,
            "difficulty": recipe.difficulty.strip()
        })
        recipe_id = recipe_result.scalar_one()

        # insert each ingredient for the recipe
        for ingredient in recipe.ingredients:
            # check if the ingredient already exists (case insensitive)
            existing_ingredient_result = connection.execute(sqlalchemy.text(
                """
                SELECT ingredient_id FROM ingredients WHERE LOWER(ingredient_name) = LOWER(:ingredient_name)
                """
            ), {"ingredient_name": ingredient.name})
            existing_ingredient_id = existing_ingredient_result.scalar()

            # if the ingredient does not exist, insert it
            if existing_ingredient_id is None:
                ingredient_insert_result = connection.execute(sqlalchemy.text(
                    """
                    INSERT INTO ingredients (ingredient_name, price, item_type)
                    VALUES (LOWER(:ingredient_name), :price, :item_type)
                    RETURNING ingredient_id
                    """
                ), {
                    "ingredient_name": ingredient.name,
                    "price": ingredient.price,
                    "item_type": ingredient.item_type
                })
                ingredient_id = ingredient_insert_result.scalar_one()
            else:
                ingredient_id = existing_ingredient_id

            # insert into recipe_ingredients with the retrieved or new ingredient_id
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

        # insert each supply for the recipe
        for supply in recipe.supplies:
            # check if the supply already exists (case insensitive)
            existing_supply_result = connection.execute(sqlalchemy.text(
                """
                SELECT supply_id FROM supplies WHERE LOWER(supply_name) = LOWER(:supply_name)
                """
            ), {"supply_name": supply.supply_name})
            existing_supply_id = existing_supply_result.scalar()

            # if the supply does not exist, insert it
            if existing_supply_id is None:
                supply_insert_result = connection.execute(sqlalchemy.text(
                    """
                    INSERT INTO supplies (supply_name)
                    VALUES (LOWER(:supply_name))
                    RETURNING supply_id
                    """
                ), {"supply_name": supply.supply_name})
                supply_id = supply_insert_result.scalar_one()
            else:
                supply_id = existing_supply_id

            # insert into recipe_supplies with the retrieved or new supply_id
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
@router.get("/suggestions", response_model=List[SuggestedRecipe], status_code=200)
def get_recipe_suggestions(ingredients: Optional[List[str]] = Query([])):
    # create normalized_ingredients so we dont worry about case or spacing
    normalized_ingredients = {ingredient.strip().lower() for ingredient in ingredients}
    suggestions = []

    with db.engine.begin() as connection:
        # fetch all recipes that contain at least one of the ingredients provided by the user
        recipes_result = connection.execute(sqlalchemy.text(
            """
            SELECT r.id AS recipe_id, r.name AS recipe_name, i.ingredient_name AS ingredient_name, 
                ri.amount_units, i.price, i.item_type
            FROM recipes AS r
            INNER JOIN recipe_ingredients AS ri ON r.id = ri.recipe_id
            INNER JOIN ingredients AS i ON i.ingredient_id = ri.ingredient_id
            WHERE EXISTS (
                SELECT 1
                FROM unnest(:ingredients) AS ingredient_pattern
                WHERE LOWER(i.ingredient_name) LIKE '%' || ingredient_pattern || '%'
            )
            OR r.id IN (
                SELECT DISTINCT recipe_id
                FROM recipe_ingredients ri
                INNER JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
                WHERE EXISTS (
                    SELECT 1
                    FROM unnest(:ingredients) AS ingredient_pattern
                    WHERE LOWER(i.ingredient_name) LIKE '%' || ingredient_pattern || '%'
                )
            )
            """
        ), {"ingredients": list(normalized_ingredients)})
        
        # get all rows returned by the query
        recipes_data = recipes_result.mappings().all()

        # organize recipes and their ingredients by recipe_id
        recipe_dict = {}
        for row in recipes_data:
            recipe_id = row["recipe_id"]

            # if the recipe does not exist in the dictionary, add it
            if recipe_id not in recipe_dict:
                recipe_dict[recipe_id] = {
                    "id": recipe_id,
                    "name": row["recipe_name"],
                    "ingredients": []
                }

            # create the ingredient dictionary and append it to the recipe's ingredient list
            ingredient_info = Ingredient(
                name=row["ingredient_name"],
                amount_units=row["amount_units"],
                price=row["price"],
                item_type=row["item_type"]
            )
            recipe_dict[recipe_id]["ingredients"].append(ingredient_info)

        # create suggestions by finding missing ingredients for each recipe
        for recipe in recipe_dict.values():
            missing_ingredients = []
            for ingredient in recipe["ingredients"]:
                # check if the ingredient is not in the user's provided list
                if ingredient.name.lower() not in normalized_ingredients:
                    missing_ingredients.append(ingredient)

            # if there are missing ingredients, add the recipe to the suggestions list
            if missing_ingredients:
                suggested_recipe = SuggestedRecipe(
                    id=recipe["id"],
                    name=recipe["name"],
                    missing_ingredients=missing_ingredients
                )
                suggestions.append(suggested_recipe)

    return suggestions


# 1.3 get recipe by id
@router.get("/{id}", response_model=Recipe, status_code=200)
def get_recipe_by_id(id: int):

    with db.engine.begin() as connection:
        ingredients = connection.execute(sqlalchemy.text(
            """
            SELECT i.ingredient_name AS name, ri.amount_units, i.price, i.item_type
            FROM recipe_ingredients AS ri
            INNER JOIN ingredients AS i ON i.ingredient_id = ri.ingredient_id
            WHERE ri.recipe_id = :id
            """
        ), {"id": id}).all()
        
        final_ingredients = [
            {
                "name": row.name,
                "amount_units": row.amount_units,
                "price": row.price,
                "item_type": row.item_type
            }
            for row in ingredients
        ]

        supplies = connection.execute(sqlalchemy.text(
            """
            SELECT s.supply_name
            FROM recipe_supplies AS rs
            INNER JOIN supplies AS s ON s.supply_id = rs.supply_id
            WHERE rs.recipe_id = :id
            """
        ), {"id": id}).all()

        final_supplies = [{"supply_name": row.supply_name} for row in supplies]

        recipe = connection.execute(sqlalchemy.text(
            """
            SELECT id, name, instructions, time, difficulty
            FROM recipes
            WHERE id = :id
            """
        ), {"id": id}).one_or_none()

        # f no recipe exists raise error 
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

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
@router.put("/{id}", response_model=Dict[str, str], status_code=200)
def update_recipe(id: int, recipe: Recipe):

    with db.engine.begin() as connection:
        # update main recipe details in the recipes table
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

        # check if any rows were updated, if not raise 404 error
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Recipe was not found in db")

        # delete existing ingredients for the recipe to avoid duplicates
        connection.execute(sqlalchemy.text(
            "DELETE FROM recipe_ingredients WHERE recipe_id = :id"
        ), {"id": id})

        # insert or update each ingredient in the recipe
        for ingredient in recipe.ingredients:
            # check if the ingredient already exists in the ingredients table (case-insensitive)
            existing_ingredient_id = connection.execute(sqlalchemy.text(
                """
                SELECT ingredient_id FROM ingredients WHERE LOWER(ingredient_name) = LOWER(:ingredient_name)
                """
            ), {"ingredient_name": ingredient.name}).scalar()

            # if the ingredient does not exist, insert it
            if not existing_ingredient_id:
                ingredient_id = connection.execute(sqlalchemy.text(
                    """
                    INSERT INTO ingredients (ingredient_name, price, item_type)
                    VALUES (:ingredient_name, :price, :item_type)
                    RETURNING ingredient_id
                    """
                ), {
                    "ingredient_name": ingredient.name.lower().strip(),  # ensure case insensitivity
                    "price": ingredient.price,
                    "item_type": ingredient.item_type
                }).scalar_one()
            else:
                # if the ingredient already exists, use its id
                ingredient_id = existing_ingredient_id

            # insert ingredient into recipe_ingredients table with amount_units
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

        # delete existing supplies for the recipe to avoid duplicates
        connection.execute(sqlalchemy.text(
            "DELETE FROM recipe_supplies WHERE recipe_id = :id"
        ), {"id": id})

        # insert or update each supply in the recipe
        for supply in recipe.supplies:
            # check if the supply already exists in the supplies table (case-insensitive)
            existing_supply_id = connection.execute(sqlalchemy.text(
                """
                SELECT supply_id FROM supplies WHERE LOWER(supply_name) = LOWER(:supply_name)
                """
            ), {"supply_name": supply.supply_name}).scalar()

            # if the supply does not exist, insert it
            if not existing_supply_id:
                supply_id = connection.execute(sqlalchemy.text(
                    """
                    INSERT INTO supplies (supply_name)
                    VALUES (:supply_name)
                    RETURNING supply_id
                    """
                ), {"supply_name": supply.supply_name.lower().strip()}).scalar_one()
            else:
                # if the supply already exists, use its id
                supply_id = existing_supply_id

            # insert supply into recipe_supplies table with recipe_id and supply_id
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
@router.delete("/{id}", response_model=Dict[str, str], status_code=200)
def delete_recipe(id: int):

    with db.engine.begin() as connection:

        # delete in recipe
        result = connection.execute(sqlalchemy.text(
            """
            DELETE FROM recipes
            WHERE id = :id
            """
        ), {"id": id})

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Recipe was not found in db")

    return {"deleted_complete": "Recipe deleted"}

@router.get("/highest-reviewed/")
def get_highest_review():
    """
    Get the best 3 reviews per recipe and average rating
    """

    response = []
    with db.engine.begin() as connection:
        best_reviews =connection.execute(sqlalchemy.text(
            """
            WITH rankedReviews AS (
            SELECT reviews.review, 
                reviews.rating, 
                reviews.recipe_id,
                recipes.name AS recipe,
                AVG(reviews.rating) OVER (PARTITION BY reviews.recipe_id) AS avgRating,
                ROW_NUMBER() OVER (PARTITION BY reviews.recipe_id ORDER BY reviews.rating DESC, reviews.review_id ASC) AS row_num
            FROM reviews
            INNER JOIN recipes ON recipes.id = reviews.recipe_id
            )
            SELECT recipe, 
                review, 
                rating, 
                avgRating
            FROM rankedReviews
            WHERE row_num <= 3
            ORDER BY recipe, row_num;
            """))

        for review in best_reviews.mappings():
            response.append(
                {
                "recipe": review['recipe'],
                "review": review['review'],
                "rating": review['rating'],
                "average rating": review['avgrating']
            }
        )
    return response

   