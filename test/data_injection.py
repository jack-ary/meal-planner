import sqlalchemy
import os
import dotenv
from faker import Faker
from faker.providers import DynamicProvider
import random
# import numpy as np

def database_connection_url():
    # DO NOT RUN IN PRODUCTION
    return os.environ.get("LOCAL_POSTGRES_URI")

# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

with engine.begin() as conn:
    conn.execute(sqlalchemy.text("""          
    DROP TABLE IF EXISTS carts CASCADE;
    DROP TABLE IF EXISTS ingredients CASCADE;
    DROP TABLE IF EXISTS cart_items CASCADE;
    DROP TABLE IF EXISTS customers CASCADE;     
    DROP TABLE IF EXISTS payments CASCADE;
    DROP TABLE IF EXISTS recipe_ingredients CASCADE;
    DROP TABLE IF EXISTS recipe_supplies CASCADE;
    DROP TABLE IF EXISTS supplies CASCADE;
    DROP TABLE IF EXISTS recipes CASCADE;
    DROP TABLE IF EXISTS reviews CASCADE;

    CREATE TABLE carts (
        cart_id bigint generated always as identity NOT NULL PRIMARY KEY,
        customer_id bigint NOT NULL
    );
    
    CREATE TABLE ingredients (
        ingredient_id bigint generated always as identity NOT NULL PRIMARY KEY,
        ingredient_name text NOT NULL,
        price double precision,
        item_type integer
    );       
                                 
    CREATE TABLE cart_items (
        id bigint generated always as identity not null PRIMARY KEY,
        cart_id bigint NOT NULL references carts(cart_id),
        item_id bigint NOT NULL references ingredients(ingredient_id),
        quantity integer
    );
                                 
    CREATE TABLE customers (
        customer_id bigint generated always as identity NOT NULL PRIMARY KEY,
        customer_name text NOT NULL
    );  
                                 
    CREATE TABLE payments (
        payment_id bigint generated always as identity NOT NULL PRIMARY KEY,
        card_num bigint NOT NULL,
        exp_date text,
        cvv integer,
        customer_id bigint references customers(customer_id)
    );

    CREATE TABLE supplies (
        supply_id bigint GENERATED BY DEFAULT AS IDENTITY NOT NULL PRIMARY KEY,
        supply_name text NOT NULL
    );           
                                                    
    CREATE TABLE recipes (
        id bigint GENERATED BY DEFAULT AS IDENTITY NOT NULL PRIMARY KEY,
        name text NOT NULL,
        instructions text,
        difficulty text,
        "time" integer
    );
                                 
    CREATE TABLE recipe_ingredients (
        id bigint GENERATED BY DEFAULT AS IDENTITY NOT NULL PRIMARY KEY,
        recipe_id bigint NOT NULL REFERENCES recipes(id),
        ingredient_id bigint NOT NULL REFERENCES ingredients(ingredient_id),
        amount_units text
    );
                                 
    CREATE TABLE reviews (
        review_id bigint generated always as identity NOT NULL PRIMARY KEY,
        recipe_id bigint NOT NULL references recipes(id),
        customer_id bigint references customers(customer_id),
        rating integer,
        review text
    );
                                 
    CREATE TABLE recipe_supplies (
        id bigint GENERATED BY DEFAULT AS IDENTITY NOT NULL PRIMARY KEY,
        recipe_id bigint NOT NULL REFERENCES recipes(id),
        supply_id bigint NOT NULL REFERENCES supplies(supply_id)
    );
    """))

num_users = 70000
num_ingredients = 10000
num_recipes = 5000
num_recipe_ingredients = 150000
num_supplies = 10000
num_recipe_supplies = 100000
num_carts = 150000
num_cart_items = 250000
num_payments = 120000
num_reviews = 135000

# If use_weighting is False, then all items have an equal chance of 
# being selected, and the selection process is much faster. The default is True.
fake = Faker(use_weighting=False)

recipe_difficulty = DynamicProvider(
     provider_name="recipe_difficulty",
     elements=["easy", "medium", "hard"],
)

fake.add_provider(recipe_difficulty)

with engine.begin() as conn:
    for _ in range(num_users):
        conn.execute(sqlalchemy.text("""
            INSERT INTO customers (customer_name) 
            VALUES (:fake_name) RETURNING customer_id
        """), {
            "fake_name": fake.name()
        })

with engine.begin() as conn:
    for _ in range(num_ingredients):
        conn.execute(sqlalchemy.text("""
            INSERT INTO ingredients (ingredient_name, price, item_type) 
            VALUES (:name, :price, :type)
        """), {
            "name": fake.word(),
            "price": random.randint(3, 15),
            "type": random.randint(1, 5)
        })

with engine.begin() as conn:
    for _ in range(num_recipes):
        conn.execute(sqlalchemy.text("""
            INSERT INTO recipes (name, instructions, difficulty, time) 
            VALUES (:name, :instructions, :difficulty, :time)
        """), {
            "name": fake.sentence(),
            "instructions": fake.paragraph(),
            "difficulty": fake.recipe_difficulty(),
            "time": random.randint(10, 120)
        })

with engine.begin() as conn:
    for _ in range(num_recipe_ingredients):
        conn.execute(sqlalchemy.text("""
            INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount_units) 
            VALUES (:recipe_id, :ingredient_id, :amount)
        """), {
            "recipe_id": random.uniform(1, num_recipes),
            "ingredient_id": random.uniform(1, num_ingredients),
            "amount": f"{random.randint(1, 5)} units"
        })

with engine.begin() as conn:
    for _ in range(num_supplies):
        conn.execute(sqlalchemy.text("""
            INSERT INTO supplies (supply_name) 
            VALUES (:name)
        """), {"name": fake.word()})

with engine.begin() as conn:
    for _ in range(num_recipe_supplies):
        conn.execute(sqlalchemy.text("""
            INSERT INTO recipe_supplies (recipe_id, supply_id) 
            VALUES (:recipe_id, :supply_id)
        """), {
            "recipe_id": random.randint(1, num_recipes),
            "supply_id": random.randint(1, num_supplies)
        })

with engine.begin() as conn:
    for _ in range(num_carts):
        conn.execute(sqlalchemy.text("""
            INSERT INTO carts (customer_id) 
            VALUES (:customer_id)
        """), {"customer_id": random.randint(1, num_users)})

with engine.begin() as conn:
    for _ in range(num_cart_items):
        conn.execute(sqlalchemy.text("""
            INSERT INTO cart_items (cart_id, item_id, quantity) 
            VALUES (:cart_id, :item_id, :quantity)
        """), {
            "cart_id": random.randint(1, num_carts),
            "item_id": random.randint(1, num_ingredients),
            "quantity": random.randint(1, 10)
        })

with engine.begin() as conn:
    for _ in range(num_payments):
        conn.execute(sqlalchemy.text("""
            INSERT INTO payments (card_num, exp_date, cvv, customer_id) 
            VALUES (:card_num, :exp_date, :cvv, :customer_id)
        """), {
            "card_num": fake.credit_card_number(),
            "exp_date": fake.credit_card_expire(),
            "cvv": random.randint(100, 999),
            "customer_id": random.randint(1, num_users)
        })

with engine.begin() as conn:
    for _ in range(num_reviews):
        conn.execute(sqlalchemy.text("""
            INSERT INTO reviews (recipe_id, customer_id, rating, review) 
            VALUES (:recipe_id, :customer_id, :rating, :review)
        """), {
            "recipe_id": random.randint(1, num_recipes),
            "customer_id": random.randint(1, num_users),
            "rating": random.randint(1, 5),
            "review": fake.text(100)
        })
    