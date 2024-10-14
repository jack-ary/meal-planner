# Example Flows for Meal Planner Backend

## 1. Get a Recipe

As a college student living on campus, I have limited groceries and I am tired of the same bland salt, pepper, chicken, and rice dish. I want to spice up my dinner and come up with a new recipe.

**Request: GET /recipes?ingredients=chicken,rice,veggies&skill_level=beginner&supplies=stovetop,pan**

**Response:**
```json
{
    "recipes": [
        {
            "id": "1",
            "recipe_name": "Chicken Fried Rice",
            "ingredients": ["oil", "chicken", "day old rice", "soy sauce", "salt", "pepper", "frozen veggies", "eggs"],
            "instructions": "Heat up some oil in a pan and put the chicken on it and season with salt and pepper. Once the chicken is cooked, move it to the side and begin cooking the veggies and rice. Heat up more oil in a pan and put the veggies in. Once the veggies begin to soften, throw the rice in and douse with soy sauce and some more pepper. Finally, after the rice and veggies are almost cooked, move the rice over and crack the eggs in the pan and scramble them. Allow the full mixture to cook, and then the grub is ready!",
            "time": "25",
            "difficulty": "beginner",
            "supplies": ["Pan", "Wooden Spoon or Spatula"]
        }
    ]
}
```

## 2. Create a Review
Bob wants to make a cake for himself to celebrate his promotion. Given Bob's ingredients, he finds a cake recipe using the Meal Planner. He wants to check the reviews before making the cake. He uses: ```GET /reviews/34``` to find that the reviews for this cake recipe are spectacular. He makes the cake.

Unbeknownst to Bob, he used salt instead of baking powder in the cake recipe. Because of this, Bob ends up with a horrible cake and wants to leave an angry review on the recipe. Bob will do the following:

**Request: POST /reviews/create/34**
```json
    {
        "name": "Bob",
        "rating": 0,
        "review": "This cake sucks! I wanted to treat myself after a promotion and this cake ruined has completely ruined my excitement. I cannot believe ..."
    }
```
**Response**
```json
{
    "review_id": 54
}
```
After Bob receives lashback for his horrible review and realizes the mistake that he made, he reluctantly decides to delete his angry review:

**Request: POST /reviews/delete/34**
```json
{
    "deleted_by": "bob"
}
```
**Response**
```json
{
    "success": "true"
}
```

## 3. Purchase Ingredients
Sally, an experienced home baker, is looking for dinner ideas to surprise her sister, Susan, on her birthday. Looking through the options on Meal Planner, she finds a delicious-looking recipe for homemade pizza, but realizes that she doesn’t have any flour to make the dough! She uses: ```GET/stock/``` to check if she can order flour directly from the Meal Planner site. Luckily, flour is in supply so Sally does the following:

**Request: POST/carts/**
```json
{
    "customer_name": “Sally”,
    "cooking_type": "string",
    "skill_level": “4” 
}
```
**Response**
```json
{
    "cart_id": “72”
}
```
**Request: /carts/72/items/flour**
```json
{
    "quantity": 2,
}
```
**Response**
```json
{
    "success": true
}
```
After successfully adding 2 bags of flour to her cart, Sally moves to checkout:

**Request: /carts/72/checkout**
```json
{
    "payment": "string",
}
```
**Response**
```json
{
    "total_ingredients_purchased": 1,
    "total_amount_paid": 7.98
}
```
