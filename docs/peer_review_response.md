# Responses to peer feedback 

## Schema 

### `cart_items` table
- Added primary key `id`
- Changed `item_id` column from primary key to foreign key
    - New relation: `cart_items.item_id` -> `ingredients.ingredient_id`
- Changed `cart_id` column from primary key to foreign key
    - New relation: `cart_items.cart_id` -> `carts.cart_id`

### `payments` table
- Added foreign key relation on `payments.customer_id` -> `customers.customer_id`

## Carts.py

### Create Cart - `/create/`
- Changed route from `/create/{cart_id}` to `/create/`
- Added parameters for `customer_id` and corresponding error checking
- Fixed parameter binding
- Fixed typos
- Removed references to primary key `payment_id`, which should be auto incremented and assigned by the data base 

### Set Item Quantity - `/{cart_id}/items/{item_id}`
- Added validation and corresponding `400` error for `quantity`
- Added validation and corresponding `404` error for `cart_id`
- Added validation and corresponding `404` error for `item_id`
- Corrected function parameters
- Corrected parameterization
- Fixed typo on `scalar_one()` call

### Checkout - `/{cart_id}/checkout`
- Removed unnecessary `customer_name` function parameter 
- Fixed typo on `scalar_one()` call
- Added necessary `cart_id` function parameter
- Fix checkout query
- Add validation for `exp_date` param
- Again: Removed references to primary key `payment_id`, which should be auto incremented and assigned by the data base 
- Added validation for `cart_id` and `customer_id` and corresponding HTTP error codes

## Reviews.py

### Get Reviews - `/{recipe_id}`
- Added validation for checking recipe id
- Added corresponding `404` exception for invalid recipe id
- Utilized list comprehension for creating the response

### Create Review - `/create/{recipe_id}`
- Added validation to check the review value, customer id, and recipe id
- Added corresponding `400` and `404` exceptions for invalid values

### Delete Review - `/delete/{review_id}`
- Changed REST verb from `POST` to `DELETE`
- Changed route from `/delete/{recipe_id}/{review_id}` to `/delete/{review_id}`. Subsequently deleted the `recipe_id` from the where clause of this methods query
- Removed the `deleted_by` parameter and the corresponding logging statement
- Added a `404` exception for invalid an invalid `review_id`. 
    - Due to this new exception throwing scenario, there is no need for a more verbose response upon success. `"OK"` is sufficient. 



### Recipes.py 

### 1.1 Get Recipe -  `/get/recipes/`
- Added Status Codes, and error checking and handling. 
- Added 200 Code 
- changed filtering to be in SQL not in pyton
- Program auto generates id 

### 1.2 Create Recipe - `/create/recipes/`
- Added status code 201 
- Added error handling, for validation of input 

### 1.6 Recipe Suggestions - `/get/recipes/suggestions`
- Added Status Code 
- Also added error handling
- Added matching tendencies for like things, so words do not need to be exactly the same 

### 1.3 Get Recipe By ID - `/get/recipes/{id}`
- Added Status code 

### 1.4 Update Recipe - `/put/recipes/{id}`
- Added status code 

### 1.5 Delete Recipe By id - `/delete/recipes/{id}`
- Created is ON CASCADE DELETE 
- Added foreign key relations properly
- Eliminated unnecessary SQL