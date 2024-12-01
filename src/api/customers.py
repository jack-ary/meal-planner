from fastapi import APIRouter, HTTPException, status
from src import database as db
import sqlalchemy 

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
)

@router.post("/register")
def register_customer(customer_name: str):
    """
    Register a customer - allows customers to create an id for themselves
    """

    if not customer_name.strip():  # Validate customer_name input
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer name cannot be empty."
        )
    try:

        with db.engine.begin() as connection:
            customer_id = connection.execute(sqlalchemy.text(
                """
                INSERT INTO customers (customer_name)
                VALUES (:customer_name)
                RETURNING customer_id
                """
            ), [{"customer_name": customer_name}]).scalar_one()

        return {
            "customer_id": customer_id
        }
    except sqlalchemy.exc.IntegrityError as e:  # Handle database constraint violations
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer name already exists or violates database constraints."
        ) from e
