# Responses to peer feedback 

## Carts.py

### Create Cart - `/create/`
- Changed route from `/create/{cart_id}` to `/create/`
- Added parameters for `customer_id` and `payment_id` and corresponding error checking
- Fixed parameter binding
- Fixed typos

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
