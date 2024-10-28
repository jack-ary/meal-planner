# API Specification for Meal Planner Backend

## 1. Recipe Endpoints

### 1.1 Get Recipes - `/recipes` (GET)
Fetches a list of recipes based on the user's available ingredients, skill level, and supplies.

**Request Parameters:**
- `ingredients`: List of strings representing available ingredients and passed in by user
- `skill_level`: String representing the user's skill level (e.g., "beginner", "intermediate", "advanced") (also passed in by user).
- `supplies`: List of strings representing available kitchen tools or appliances. supplies the user has available to them so we know what type of recipes to include.

**Response:**
```json
{
  "recipes": [
    {
      "id": "string",
      "name": "string",
      "ingredients": ["string"],
      "instructions": "string",
      "time": "integer", /* Cooking time in minutes */
      "difficulty": "string", /* beginner, intermediate, advanced */
      "supplies": ["string"]
    }
  ]
}
```

### 1.2 Create Recipe - `/recipes` (POST)
Submits a new recipe to the  database so that it can then be searched by another user later.

**Request Body:**
```json
{
  "name": "string",
  "ingredients": ["string"],
  "instructions": "string",
  "time": "integer", /* Cooking time in minutes */
  "difficulty": "string", /* beginner, intermediate, advanced */
  "supplies_needed": ["string"] /* Required kitchen tools */
}
```

**Response:**
```json
{
  "completion_messsage": "Recipe created successfully",
  "recipe_id": "string"
}
```

### 1.3 Get Recipe by ID - `/recipes/{id}` (GET)
Gets the details of a specific recipe by its ID.

**Request Parameters:**
- `id`: String representing the unique identifier of the recipe.

**Response:**
```json
{
  "name": "string",
  "ingredients": ["string"],
  "instructions": "string",
  "time": "integer", /* Cooking time in minutes */
  "difficulty": "string", /* beginner, intermediate, advanced */
  "supplies_needed": ["string"] /* Required kitchen tools */
}
```

### 1.4 Update Recipe - `/recipes/{id}` (PUT)
Updates an existing recipe by its ID.

**Request Parameters:**
- `id`: String representing the unique identifier of the recipe.

**Request Body:**
```json
{
  "name": "string",
  "ingredients": ["string"],
  "instructions": "string",
  "time": "integer", /* Cooking time in minutes */
  "difficulty": "string", /* beginner, intermediate, advanced */
  "supplies_needed": ["string"] /* Required kitchen tools */
}
```

**Response:**
```json
{
  "message": "Recipe updated successfully"
}
```

### 1.5 Delete Recipe - `/recipes/{id}` (DELETE)
Deletes a recipe by its ID.

**Request Parameters:**
- `id`: String representing the unique identifier of the recipe.

**Response:**
```json
{
  "message": "Recipe deleted successfully"
}
```

### 1.6 Get Recipe Suggestions - `/suggestions` (GET)
Gets suggested recipes that require some additional ingredients based on the user's current avalability.

**Request Parameters:**
- `ingredients`: List of strings representing the ingredients the user currently has.

**Response:**
```json
{
  "suggested_recipes": [
    {
      "id": "string",
      "name": "string", /* Recipe Name */
      "missing_ingredients": ["string"] /* Ingredients user needs to buy*/
    }
  ]
}
```


## 2. Review Endpoints
### 2.1 Fetch Reviews - `/reviews/{recipe_id}` (GET)
Gives the reviews for a given recipe.


**Response**
```json
[
    {
        "rating": "integer", /* 0-5 rating */
        "name": "string", /* Recipe name */
        "reviewer_name": "string",
        "review": "string", /* Recipe review */
    },
    {
        ...
    }
]
```
### 2.2 Create Review - `/reviews/create/{recipe_id}` (POST)
**Request**
```json
{
  "name": "string", /* Reviewer name */
  "rating": "integer", /* 0-5 rating */
  "review": "string" /* Recipe review */
}
```
**Response**
```json
{
  "review_id": "integer", /* This id will be used to delete a review if necessary */
}
```
### 2.3 Delete a Review - `/reviews/delete/{recipe_id}/{review_id}` (POST)
**Request**
```json
{
    "deleted_by": "string"
}
```
**Response**
```json
"OK"
```
## 3. Cart Endpoints

## 3.1 Get Stock - `/stock/` (GET)
Fetches what is currently in stock. Each item will have a single price. 
**Response:**
```json
[
    {
        "sku": "string", /* each value unique to the item */
        "name": "string",
        "quantity": "integer", /* Between 1 and 10000 */
        "price": "integer", /* Between 1 and 5000 */
        "item_type": "string" /* Meat, Produce, Dried/Canned/ Frozen, Sweets
    }
]
```

### 3.2 New Cart - `/carts/` (POST)
Creates a new cart for when the customer wants to purchase ingredients. 
**Request:**
```json
{
    "customer_name": "string",
}
```
**Response:**
```json
{
    "cart_id": "string" /* ID used to add to cart and checkout 
}
```
### 3.3 Add Item To Cart - `/carts/{cart_id}/items/{item_sku}` (PUT)
Updates when an item is added/deleted to a cart.
**Request:**
```json
{
    "quantity": "integer",
}
```
**Response**
```json
{
    "success": "boolean"
}
```
### 3.4 Checkout Cart - `/carts/{cart_id}/checkout` (POST)
Trades United States Currency for some of the finest items in stock in a checkout fashion
**Request:**
```json
{
    "payment" : "string",
    "card_num": "integer",
    "exp_date": "string",
    "cvv": "integer"

}
```
**Response**
```json
{
    "total_ingredients_purchased": "integer",
    "total_amount_paid": "float"
}
```
 
