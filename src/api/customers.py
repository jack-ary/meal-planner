from fastapi import APIRouter
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
)

@router.post("/create")
def register_customer(customer_name: str):
    """
    Register a customer - allows customers to create an id for themselves
    """

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