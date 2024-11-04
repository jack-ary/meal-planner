
# Manual Test Results

### Implementing [Example Flow 1.1](ExampleFlows.md#2-get-a-recipe)

Required prerequisite data can be found in [schema.sql](../schema.sql)

#### Test Case: Get Recipe with Case-Insensitive Ingredient and Supply Matching

**Scenario**: A user searches for recipes with ingredients and supplies that should match regardless of case (e.g., "Flour" and "flour" are treated as the same).

**Request**:
```bash
curl -X 'GET' \
  'https://meal-planner-9c99.onrender.com/recipes?ingredients=flour&ingredients=egg' \
  -H 'accept: application/json' 
```
**Expected Response**:
```json
[
  {
    "id": 1,
    "name": "Pancakes",
    "ingredients": [
      { "name": "flour", "amount_units": "2 cups", "price": 1.5, "item_type": "dry" },
      { "name": "egg", "amount_units": "2", "price": 0.5, "item_type": "wet" }
    ],
    "instructions": "Mix and cook.",
    "time": 15,
    "difficulty": "beginner",
    "supplies": [
      { "supply_name": "pan" },
      { "supply_name": "spatula" }
    ]
  }
]
```

#### Test Case: Create Recipe with Conflict Handling for Ingredients and Supplies

**Scenario**: Adding a recipe with existing ingredients and supplies (case-insensitive) should not duplicate entries.

**Request**:
```bash
curl -X 'POST' \
  'https://meal-planner-9c99.onrender.com/recipes' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Omelette",
    "instructions": "Beat eggs and cook.",
    "time": 5,
    "difficulty": "beginner",
    "ingredients": [
      { "name": "Egg", "amount_units": "3", "price": 0.5, "item_type": "wet" },
      { "name": "Milk", "amount_units": "1/4 cup", "price": 0.3, "item_type": "wet" }
    ],
    "supplies": [
      { "supply_name": "pan" }
    ]
  }'
```

**Expected Behavior**: Recipe is created successfully without duplicating `Egg` or `pan` in the ingredients or supplies table.

#### Test Case: Update Recipe with Conflict Handling

**Scenario**: Updating a recipe with ingredients and supplies, ensuring `ON CONFLICT` handles existing entries.

**Request**:
```bash
curl -X 'PUT' \
  'https://meal-planner-9c99.onrender.com/recipes/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Updated Pancakes",
    "instructions": "Mix ingredients and cook.",
    "time": 20,
    "difficulty": "beginner",
    "ingredients": [
      { "name": "Flour", "amount_units": "2 cups", "price": 1.5, "item_type": "dry" },
      { "name": "Egg", "amount_units": "2", "price": 0.5, "item_type": "wet" }
    ],
    "supplies": [
      { "supply_name": "Spatula" }
    ]
  }'
```

**Expected Behavior**: Recipe is updated, existing entries for `Flour`, `Egg`, and `Spatula` are not duplicated.

#### Test Case: Get Recipe Suggestions with Missing Ingredients

**Scenario**: A user provides a subset of ingredients, and the system suggests recipes with the list of missing ingredients.

**Request**:
```bash
curl -X 'GET' \
  'https://meal-planner-9c99.onrender.com/recipes/suggestions?ingredients=flour&ingredients=sugar' \
  -H 'accept: application/json' 
```

**Expected Response**:
```json
[
  {
    "id": 2,
    "name": "Cake",
    "missing_ingredients": [
      { "name": "egg", "amount_units": "3", "price": 0.5, "item_type": "wet" },
      { "name": "butter", "amount_units": "1/2 cup", "price": 1.2, "item_type": "fat" }
    ]
  }
]
```

#### Test Case: Delete Recipe

**Scenario**: A user requests to delete an existing recipe by its ID. The recipe and its associated ingredients and supplies should be removed from the database.

**Request**:
```bash
curl -X 'DELETE' \
  'https://meal-planner-9c99.onrender.com/recipes/1' \
  -H 'accept: application/json'
```

**Expected Behavior**:
- If the recipe with ID `1` exists, it is deleted, and all associated entries in `recipe_ingredients` and `recipe_supplies` are removed.
- If the recipe with ID `1` does not exist, a 404 error is returned with the message "Recipe was not found in db".

**Expected Response on Success**:
```json
{
  "deleted_complete": "Recipe deleted"
}
```

**Expected Response on Failure**:
```json
{
  "detail": "Recipe was not found in db"
}
```


### Test Case: Cart Creation: 

**Request**
```bash
curl -X 'POST' \
  'https://meal-planner-9c99.onrender.com/carts/create/1?customer_id=1&payment_id=1' \
  -H 'accept: application/json' \
  -d ''
```

**Response**
```json
{
  "cart_id" : 1
}
```
### Test Case: Add items to Cart: 

**Request**
```bash
curl -X 'POST' \
  'https://meal-planner-9c99.onrender.com/carts/1/items/1?quantity=1' \
  -H 'accept: application/json' \
  -d ''
```


**Response**
```json
{
  "Success"
}
```

### Test Case: Checkout: 

**Request**
```bash
curl -X 'POST' \
  'https://meal-planner-9c99.onrender.com/carts/2/checkout?payment_id=3&card_num=6768123456789012&exp_date=12%2F24&customer_id=2' \
  -H 'accept: application/json' \
  -d ''
```


**Response**
```json
{
  "total_ingredients_purchased": "7",
  "total_amount_paid":" 70" 
}

```