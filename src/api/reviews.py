from fastapi import APIRouter
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)

@router.get("/reviews/{recipe_id}")
def get_reviews(recipe_id: int):
    """
    Get the reviews for a given recipe
    """

    response = []

    with db.engine.begin() as connection:
        reviews = connection.execute(sqlalchemy.text(
            """
            SELECT review, rating, customer_name, name as recipe_name
            FROM reviews
            INNER JOIN customers on customers.customer_id=reviews.customer_id
            INNER JOIN recipes on recipes.id=reviews.recipe_id
            WHERE recipe_id = :desired_recipe_id
            """
        ), [{"desired_recipe_id": recipe_id}])

        for review in reviews.mappings():
            response.append(
                {
                    "recipe_name": review['recipe_name'],
                    "rating": review['rating'],
                    "review": review['review'],
                    "customer": review['customer_name']
                }
            )

    return response

@router.post("/reviews/create/{recipe_id}")
def create_review(recipe_id: int, customer_id: str, rating: int, review: str):
    """
    Create a review for a given recipe
    """

    with db.engine.begin() as connection:
        review_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO reviews (recipe_id, customer_id, rating, review)
            VALUES (:recipe_id, :customer_id, :rating, :review)
            RETURNING review_id
            """
        ), [{"recipe_id": recipe_id, "customer_id": customer_id, "rating": rating, "review": review}]).scalar_one()
    
    return {
        "review_id": review_id
    }

@router.post("/reviews/delete/{recipe_id}/{review_id}")
def delete_review(recipe_id: int, review_id: int, deleted_by: str):
    """
    Delete a review for a given recipe
    """

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """
            DELETE FROM reviews
            WHERE recipe_id = :recipe_id AND review_id = :review_id
            """
        ), {"recipe_id": recipe_id, "review_id": review_id})

    print(f"review id:{review_id} for recipe:{recipe_id} deleted by:{deleted_by}")

    return "OK"