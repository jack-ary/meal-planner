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

