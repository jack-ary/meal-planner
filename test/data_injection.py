import sqlalchemy
import os
import dotenv
# from faker import Faker
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
                                 
    CREATE TABLE recipe_ingredients (
        recipe_id bigint generated always as identity NOT NULL PRIMARY KEY,
        ingredient_id bigint NOT NULL references ingredients(ingredient_id),
        amount_units text
    );

    CREATE TABLE supplies (
        supply_id bigint generated always as identity NOT NULL PRIMARY KEY,
        supply_name text NOT NULL
    );           
                                                    
    CREATE TABLE recipes (
        id bigint generated always as identity NOT NULL PRIMARY KEY,
        name text NOT NULL,
        instructions text,
        difficulty text,
        "time" integer,
        ingredients text[] NOT NULL DEFAULT '{}',
        supplies_needed text[] NOT NULL DEFAULT '{}'
    );
                                 
    CREATE TABLE reviews (
        review_id bigint generated always as identity NOT NULL PRIMARY KEY,
        recipe_id bigint NOT NULL references recipes(id),
        customer_id bigint references customers(customer_id),
        rating integer,
        review text
    );
                                 
    CREATE TABLE recipe_supplies (
        recipe_id bigint NOT NULL REFERENCES recipes(id),
        supply_id bigint NOT NULL REFERENCES supplies(supply_id),
        PRIMARY KEY (recipe_id, supply_id)
    );
    """))