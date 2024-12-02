from fastapi import APIRouter, HTTPException, status
from src import database as db
import sqlalchemy
import time

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)

@router.get("/{recipe_id}")
def get_reviews(recipe_id: int):
    """
    Get the reviews for a given recipe
    """
    start_time = time.time()
    with db.engine.begin() as connection:
        recipe = connection.execute(sqlalchemy.text(
            """
            SELECT id
            FROM recipes
            WHERE id = :recipe_id
            """
        ), {"recipe_id": recipe_id}).one_or_none()

        if recipe is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Recipe not found')
        
        reviews = connection.execute(sqlalchemy.text(
            """
            SELECT review, rating, customer_name, name as recipe_name
            FROM reviews
            INNER JOIN customers on customers.customer_id=reviews.customer_id
            INNER JOIN recipes on recipes.id=reviews.recipe_id
            WHERE recipe_id = :desired_recipe_id
            """
        ), {"desired_recipe_id": recipe_id})

        response = [
            {
                "recipe_name": review['recipe_name'],
                "rating": review['rating'],
                "review": review['review'],
                "customer": review['customer_name']
            } for review in reviews.mappings()
        ]
        execution_time_ms = (time.time() - start_time) * 1000
        print(f"{execution_time_ms:.2f} ms")

        return response

@router.post("/create/{recipe_id}")
def create_review(recipe_id: int, customer_id: int, rating: int, review: str):
    """
    Create a review for a given recipe, on a 0-5 integer scale
    """
    start_time = time.time()
    if rating not in range(0, 6):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid review')

    with db.engine.begin() as connection:
        response = connection.execute(sqlalchemy.text(
            """
            SELECT 
            (SELECT id FROM recipes WHERE id = :recipe_id) AS recipe,
            (SELECT customer_id FROM customers WHERE customer_id = :customer_id) AS customer
            """
        ), [{"recipe_id": recipe_id, "customer_id": customer_id}]).one_or_none()

        if response.recipe is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Recipe not found')
        
        if response.customer is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid customer id')
        
        review_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO reviews (recipe_id, customer_id, rating, review)
            VALUES (:recipe_id, :customer_id, :rating, :review)
            RETURNING review_id
            """
        ), [{"recipe_id": recipe_id, "customer_id": customer_id, "rating": rating, "review": review}]).scalar_one()
    
        execution_time_ms = (time.time() - start_time) * 1000
        print(f"{execution_time_ms:.2f} ms")

        return {
            "review_id": review_id
        }

@router.delete("/delete/{review_id}")
def delete_review(review_id: int):
    """
    Delete a review for a given recipe
    """
    start_time = time.time()
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            DELETE FROM reviews
            WHERE review_id = :review_id
            """
        ), {"review_id": review_id})

        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    execution_time_ms = (time.time() - start_time) * 1000
    print(f"{execution_time_ms:.2f} ms")

    return "OK"