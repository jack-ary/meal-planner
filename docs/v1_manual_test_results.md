# Manual Test Results

Implementing [Example Flow 2](ExampleFlows.md#2-create-a-review)

Required prerequisite data can be found in [schema.sql](../schema.sql)

#### Bob wants to check the reviews for the cake recipe

**Request:** 
```bash
curl -X 'GET' \
  'https://meal-planner-9c99.onrender.com/reviews/1' \
  -H 'accept: application/json'
```
**Response:**
```json
[
  {
    "recipe_name": "Scrambled Eggs",
    "rating": 5,
    "review": "Test-This recipe rocks",
    "customer": "Robert California"
  }
]
```

#### Bob wants to leave a horrible review

**Request:**
```bash
curl -X 'POST' \
  'https://meal-planner-9c99.onrender.com/reviews/create/1?customer_id=1&rating=0&review=This%20cake%20sucks%21' \
  -H 'accept: application/json' \
  -d ''
```
**Response:**
```json
{
  "review_id": 6
}
```

#### Bob later needs to delete his review
**Request**
```bash
curl -X 'POST' \
  'https://meal-planner-9c99.onrender.com/reviews/delete/1/6?deleted_by=Bob' \
  -H 'accept: application/json' \
  -d ''
```
**Response**
```json
"OK"
```
