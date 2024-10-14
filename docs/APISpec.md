# API Specification for Meal Planner Backend

## 1. Recipe Endpoints

## 2. Review Endpoints
### 2.1 Fetch Reviews - `/reviews/{recipe_id}` (GET)
Fetches the reviews for a given recipe


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
### 2.3 Delete a Review - `/reviews/delete/{recipe_id}` (POST)
**Request**
```json
{
    "deleted_by": "string"
}
```
**Response**
```json
{
    "success": "boolean"
}
```
## 3. Cart Endpoints

## 3.1 Get Stock - `/stock/` (GET)
Fetches what is currently in stock. Each item will have a single price. 
**Response:**
```json
[
    {
        "sku": "string", /* each value unique to the item
        "name": "string",
        "quantity": "integer", /* Between 1 and 10000
        "price": "integer", /* Between 1 and 5000
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
    "cooking_type": "string",
    "skill_level": "number" 
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
    "payment": "string",
}
```
**Response**
```json
{
    "total_ingredients_purchased": "integer",
    "total_amount_paid": "integer"
}
```
 
