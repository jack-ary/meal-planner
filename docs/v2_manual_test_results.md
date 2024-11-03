# Manual Test Results

Implementing [Example Flow 1.1](ExampleFlows.md#2-get-a-recipe)

Required prerequisite data can be found in [schema.sql](../schema.sql)

#### Alice wants to find a new beginner recipe that uses chicken and rice 

**Request:** 

```bash
curl -X 'GET' \
  'https://meal-planner-9c99.onrender.com/recipes?ingredients=chicken&ingredients=rice&skill_level=beginner' \
  -H 'accept: application/json' 

```
**Response:**
```json
[
  {
    "id": 1,
    "name": "Chicken and Rice Stir Fry",
    "ingredients": ["chicken", "rice", "soy sauce", "vegetables", "oil"],
    "instructions": "Cook rice in rice cooker or in pot on stove. Cook chicken and vegetables in a pan with soy sauce and oil. Once cooked mix with rice.",
    "time": 30,
    "difficulty": "beginner",
    "supplies_needed": ["pan", "stove", "pot or rice cooker"]
  }
]
```


#### Alice wants to create a new recipe for the database to have

**Request:** 

```bash
curl -X 'POST' \
  'https://meal-planner-9c99.onrender.com/recipes' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
        "name": "Marinara Pasta",
        "ingredients": ["pasta", "tomato sauce", "cheese", salt, pepper],
        "instructions": "Boil water with salt, and once boiling add in pasta. Once pasta cooked strain pasta, keep 1 cup of pasta water, and then add in sauce, seasonings, and cheese",
        "time": 20,
        "difficulty": "beginner",
        "supplies_needed": ["pot", "stove", "strainer", "big spoon"]
      }'
```


**Response:**
```json

{
  "completion_message": "Recipe was created successfully in db",
  "recipe_id": 2
}
```

#### Alice wants to see the new recipe she created 

**Request:** 

```bash
curl -X 'GET' \
  'https://meal-planner-9c99.onrender.com/recipes/2' \
  -H 'accept: application/json'
```

**Response:**
```json

{
  "id": 2,
  "name": "Marinara Pasta",
  "ingredients": ["pasta", "tomato sauce", "cheese", "salt", "pepper"],
  "instructions": "Boil water with salt, and once boiling add in pasta. Once pasta cooked strain pasta, keep 1 cup of pasta water, and then add in sauce, seasonings, and cheese",
  "time": 20,
  "difficulty": "beginner",
  "supplies_needed": ["pot", "stove", "strainer", "big spoon"]
}
```

#### Alice wants to update the new recipe she created

**Request:** 

```bash
curl -X 'PUT' \
  'https://meal-planner-9c99.onrender.com/recipes/2' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
        "name": "Spicy Marinara Pasta",
        "ingredients": ["pasta", "tomato sauce", "cheese", "garlic", "salt", "pepper", "red pepper flakes"],
        "instructions": "Boil water with salt, and once boiling add in pasta. Once pasta cooked strain pasta, keep 1 cup of pasta water, and then add in sauce, seasonings, and cheese",
        "time": 20,
        "difficulty": "beginner",
        "supplies_needed": ["pot","stove","strainer", "big spoon"]
      }'
```

**Response:**
```json

{
  "message": "Recipe was updated successfully in db"
}
```

#### Alice wants to delete the new recipe she created

**Request:** 

```bash 
curl -X 'DELETE' \
  'https://meal-planner-9c99.onrender.com/recipes/2' \
  -H 'accept: application/json'
```

**Response:**
```json

{
  "message": "Recipe was deleted successfully in db"
}
```

#### Alice wants suggestions based on some ingredients she has 

**Request:** 

```bash 
curl -X 'GET' \
  'https://meal-planner-9c99.onrender.com/suggestions?ingredients=vegetables&ingredients=rice' \
  -H 'accept: application/json'
  ```

**Response:**
```json

[
  {
    "id": 1,
    "name": "Chicken and Rice Stir Fry",
    "missing_ingredients": ["chicken", "soy sauce"]
  },
  {
    "id": 3,
    "name": "Vegetable Fried Rice",
    "missing_ingredients": ["soy sauce"]
  }
]