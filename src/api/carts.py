from fastapi import APIrouter
from src import database as db
import sqlalchemy

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
)

@router.post("/create/{cart_id}")
def create_cart(cart_id: int, customer_id: int,payment_id: int):
    """ create cart """
    with db.engine.begin() as connection:
      cart_id = connection.execute(sqlalchemy.text(
         """
        INSERT INTO carts(cart_id, customer_id, payment_id)
        VALUES (:cart_id, :customer_id, :payment_id)
        RETURNING cart_id
        """),[{"cart_id": cart_id,
              "customer_id": customer_id,
              "payment_id": payment_id}]).scalarone()

    return {"cart_id":cart_id}

@router.post("/{cart_id}/items/{item_id}")
def set_item_quantity(cart_id:int, item_id: int,quantity:int):
   """ add items to cart """
   with db.engine.begin() as connection:
      connection.execute(sqlalchemy.text(
        """
        INSERT INTO cart_items (cart_id, item_id, quantity)
        VALUES (:cart_id, :item_id, :quantity)
        RETURNING cart_id, item_id, quantity
        """),[{"cart_id":cart_id,
              "item_id":item_id,
              "quantity":quantity }]).scalarone()

   return {"Success": True}


@router.post("/{cart_id}/checkout")
def checkout(cart_id:int,payment_id:int,card_num:int,exp_date:str,customer_id:int):
   """purchase items"""
   with db.engine.begin() as connection:
      payment = connection.execute(sqlalchemy.text(
         """
        INSERT INTO payments (payment_id, card_num, exp_date, cvv, customer_id)
        VALUES (:payment_id, :card_num, :exp_date, :cvv, :customer_id)
        RETURNING payment_id, card_num, exp_date, cvv, customer_id

        """))
      if not payment:
        raise Exception("Payment failed")
      cart_checkout = connection.execute(sqlalchemy.text(
           """
        SELECT cart_items.cart_id,
        cart_items.item_id,
        SUM(cart_items.quantity) AS total_ingredients_purchased,
        SUM(cart_items.quantity*ingredients.price) AS total_amount_paid
        FROM cart_items
        JOIN ingredients ON ingredients.ingredient_id = cart_items.item_id
            """),{"cart_id":cart_id}).scalarone()
      
      total_ingredients_purchased = cart_checkout["total_ingredients_purchased"]
      total_amount_paid = cart_checkout["total_amount_paid"]

   return {
            "total_ingredients_purchased": total_ingredients_purchased,
            "total_amount_paid": total_amount_paid
   }