# Example Flows for Meal Planner Backend

## 1. Get a Recipe
## 2. Create a Review
Bob wants to make a cake for himself to celebrate his promotion. Given Bob's ingredients, he finds a cake recipe using the Meal Planner. He wants to check the reviews before making the cake. He uses: ```GET /reviews/34``` to find that the reviews for this cake recipe are spectacular. He makes the cake.

Unbeknownst to Bob, he used salt instead of baking poweder in the cake recipe. Becuase of this, Bob ended up with a horrible cake and wants to leave an angry review on the recipe. Bob will do the following:
```json
POST /reviews/create/34
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
After Bob recieves lashback for his horrible review and realizes the mistake that he made, he reluctantly decides to delete his angry review:
```json
POST /review/delete/34
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