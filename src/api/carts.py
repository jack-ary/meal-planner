from fastapi import APIRouter, HTTPException, status
from src import database as db
import sqlalchemy
import re

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
)

@router.post("/create/")
def create_cart(customer_id: int):
    """ create cart """
    
    with db.engine.begin() as connection:
      response = connection.execute(sqlalchemy.text(
         """
         SELECT customer_id
         FROM customers
         WHERE customer_id = :customer_id
         """), {"customer_id": customer_id}).one_or_none()
      
      if response is None:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid customer id')
        
      cart_id = connection.execute(sqlalchemy.text(
         """
        INSERT INTO carts(customer_id)
        VALUES (:customer_id)
        RETURNING cart_id
        """), [{"customer_id": customer_id}]).scalar_one()

    return {"cart_id":cart_id}

@router.post("/{cart_id}/items/{item_id}")
def set_item_quantity(cart_id: int, item_id: int, quantity: int):
   """ add items to cart """

   if quantity <= 0:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid quantity')

   with db.engine.begin() as connection:
      response = connection.execute(sqlalchemy.text(
            """
            SELECT 
            (SELECT ingredient_id FROM ingredients WHERE ingredient_id = :ingredient_id) AS item,
            (SELECT cart_id FROM carts WHERE cart_id = :cart_id) AS cart
            """
        ), [{"ingredient_id": item_id, "cart_id": cart_id}]).one_or_none()
      
      if response.item is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Ingredient not found')

      if response.cart is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Cart not found')

      connection.execute(sqlalchemy.text(
        """
        INSERT INTO cart_items (cart_id, item_id, quantity)
        VALUES (:cart_id, :item_id, :quantity)
        """),[{"cart_id": cart_id, "item_id": item_id, "quantity": quantity}])

   return {"Success": True}


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, card_num: int, exp_date: str, customer_id: int, cvv: int):
   """purchase items. exp_date must be of the form MM/YY """

   # MM/YY regex to compare against exp_date
   regex = r"^(0[1-9]|1[0-2])\/([0-9]{2})$"
    
   # Check if expiration date matches the regex
   if not re.match(regex, exp_date):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid expiration date')
   
   with db.engine.begin() as connection:
      response = connection.execute(sqlalchemy.text(
            """
            SELECT 
            (SELECT customer_id FROM customers WHERE customer_id = :customer_id) AS customer,
            (SELECT cart_id FROM carts WHERE cart_id = :cart_id) AS cart
            """
        ), [{"customer_id": customer_id, "cart_id": cart_id}]).one_or_none()
      
      if response.customer is None:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid customer id')
      
      if response.cart is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Cart not found')

      connection.execute(sqlalchemy.text(
         """
         INSERT INTO payments (card_num, exp_date, cvv, customer_id)
         VALUES (:card_num, :exp_date, :cvv, :customer_id)
         """), [{"card_num": card_num,
                  "exp_date": exp_date,
                  "cvv": cvv,
                  "customer_id": customer_id}])
      
      cart_checkout = connection.execute(sqlalchemy.text(
           """
        SELECT cart_items.cart_id,
        SUM(cart_items.quantity) AS total_ingredients_purchased,
        SUM(cart_items.quantity*ingredients.price) AS total_amount_paid
        FROM cart_items
        JOIN ingredients ON ingredients.ingredient_id = cart_items.item_id
        WHERE cart_items.cart_id = :cart_id
        GROUP BY cart_items.cart_id
            """), [{"cart_id": cart_id}]).one()
      
      total_ingredients_purchased = cart_checkout.total_ingredients_purchased
      total_amount_paid = cart_checkout.total_amount_paid

   return {
            "total_ingredients_purchased": total_ingredients_purchased,
            "total_amount_paid": total_amount_paid
   }