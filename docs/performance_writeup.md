## V5: Performance Tuning
### 1: Fake Data Modeling

[data_injection.py](../test/data_injection.py)

#### Data Distribution
| Table                  | Count     |
|--------------------------|-----------|
| Number of Users          | 70,000    |
| Number of Ingredients    | 10,000    |
| Number of Recipes        | 5,000     |
| Number of Recipe Ingredients | 150,000  |
| Number of Supplies       | 10,000    |
| Number of Recipe Supplies| 100,000   |
| Number of Carts          | 150,000   |
| Number of Cart Items     | 250,000   |
| Number of Payments       | 120,000   |
| Number of Reviews        | 135,000    |
| **Total**                | **1,000,000** |

The above table shows how the data has been distributed for our performance tuning/testing. In order to get to a million rows, these numbers were chosen as estimates for how our service would scale. The larger quantities reflect what we would anticipate to be more common and perhaps the easier operations. For example, we anticipate that reviews, payments, and carts would be the the areas resulting in the most data. Smaller tables include supplies, recipes, and ingredients, which are much more limited by physical items usable in a real world kitchen scenario.  

### 2: Performance Results of Hitting Endpoints

| Controller   | Endpoint                       | Time to Execute (ms) |
|--------------|---------------------------------|-----------------------|
| Carts        | /carts/create                  | 42.52                |
| Carts        | /carts/set-item-quantity       | 126.18               |
| Carts        | /carts/checkout                | 611.26               |
| Customers    | /customers/register            | 119.08               |
| Recipes      | /recipes/get                   | 1964.34             |
| Recipes      | /recipes/create                | 109.97               |
| Recipes      | /recipes/suggestions           | 1979.04             |
| Recipes      | /recipes/get-by-id             | 289.11               |
| Recipes      | /recipes/update                | 308.30               |
| Recipes      | /recipes/delete                | 94.04                |
| Recipes      | /recipes/get-highest-review    | 2810.81             |
| Reviews      | /reviews/get                   | 354.27               |
| Reviews      | /reviews/create                | 83.04               |
| Reviews      | /reviews/delete                | 100.04               |

### 3: Performance Tuning 

#### 3.1 Get Recipe Suggestions
Original Query: 
```sql
SELECT r.id AS recipe_id, r.name AS recipe_name, i.ingredient_name AS ingredient_name, 
    ri.amount_units, i.price, i.item_type
FROM recipes AS r
INNER JOIN recipe_ingredients AS ri ON r.id = ri.recipe_id
INNER JOIN ingredients AS i ON i.ingredient_id = ri.ingredient_id
WHERE EXISTS (
    SELECT 1
    FROM unnest(:ingredients) AS ingredient_pattern
    WHERE LOWER(i.ingredient_name) LIKE '%' || ingredient_pattern || '%'
)
OR r.id IN (
    SELECT DISTINCT recipe_id
    FROM recipe_ingredients ri
    INNER JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
    WHERE EXISTS (
        SELECT 1
        FROM unnest(:ingredients) AS ingredient_pattern
        WHERE LOWER(i.ingredient_name) LIKE '%' || ingredient_pattern || '%'
    )
)
```
Explain Result: 
| QUERY PLAN                                                                                                                                           |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hash Join  (cost=4215.27..7606.16 rows=112484 width=70)                                                                                              |
|   Hash Cond: (ri.ingredient_id = i.ingredient_id)                                                                                                    |
|   Join Filter: ((SubPlan 1) OR (hashed SubPlan 2))                                                                                                   |
|   ->  Hash Join  (cost=223.50..3220.31 rows=149978 width=60)                                                                                         |
|         Hash Cond: (ri.recipe_id = r.id)                                                                                                             |
|         ->  Seq Scan on recipe_ingredients ri  (cost=0.00..2602.78 rows=149978 width=24)                                                             |
|         ->  Hash  (cost=161.00..161.00 rows=5000 width=44)                                                                                           |
|               ->  Seq Scan on recipes r  (cost=0.00..161.00 rows=5000 width=44)                                                                      |
|   ->  Hash  (cost=176.00..176.00 rows=10000 width=26)                                                                                                |
|         ->  Seq Scan on ingredients i  (cost=0.00..176.00 rows=10000 width=26)                                                                       |
|   SubPlan 1                                                                                                                                          |
|     ->  Function Scan on unnest ingredient_pattern  (cost=0.00..0.02 rows=1 width=0)                                                                 |
|           Filter: (lower(i.ingredient_name) ~~ (('%'::text || ingredient_pattern) || '%'::text))                                                     |
|   SubPlan 2                                                                                                                                          |
|     ->  Unique  (cost=3685.14..3688.89 rows=750 width=8)                                                                                             |
|           ->  Sort  (cost=3685.14..3687.02 rows=750 width=8)                                                                                         |
|                 Sort Key: ri_1.recipe_id                                                                                                             |
|                 ->  Hash Join  (cost=476.63..3649.32 rows=750 width=8)                                                                               |
|                       Hash Cond: (ri_1.ingredient_id = i_1.ingredient_id)                                                                            |
|                       ->  Seq Scan on recipe_ingredients ri_1  (cost=0.00..2602.78 rows=149978 width=16)                                             |
|                       ->  Hash  (cost=476.00..476.00 rows=50 width=8)                                                                                |
|                             ->  Nested Loop Semi Join  (cost=0.00..476.00 rows=50 width=8)                                                           |
|                                   Join Filter: (lower(i_1.ingredient_name) ~~ (('%'::text || ingredient_pattern_1.ingredient_pattern) || '%'::text)) |
|                                   ->  Seq Scan on ingredients i_1  (cost=0.00..176.00 rows=10000 width=14)                                           |
|                                   ->  Function Scan on unnest ingredient_pattern_1  (cost=0.00..0.01 rows=1 width=32)                                |
Add Index Command:
```sql
CREATE INDEX idx_ingredient_name 
ON ingredients (ingredient_name);
```
Performance Improvement: 
- Original: 1979.04
- Final: 992.18
- Improvement: 986.86

#### 3.2 Get Highest Reviewed
Original Query: 
```sql
WITH rankedReviews AS (
SELECT reviews.review, 
    reviews.rating, 
    reviews.recipe_id,
    recipes.name AS recipe,
    AVG(reviews.rating) OVER (PARTITION BY reviews.recipe_id) AS avgRating,
    ROW_NUMBER() OVER (PARTITION BY reviews.recipe_id ORDER BY reviews.rating DESC, reviews.review_id ASC) AS row_num
FROM reviews
INNER JOIN recipes ON recipes.id = reviews.recipe_id
)
SELECT recipe, 
    review, 
    rating, 
    avgRating
FROM rankedReviews
WHERE row_num <= 3
ORDER BY recipe, row_num
LIMIT 100;
```
Explain Result: 
| QUERY PLAN                                                                                                                                                |
| --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Limit  (cost=36437.53..36437.78 rows=100 width=153) (actual time=2166.580..2166.627 rows=100 loops=1)                                                     |
|   ->  Sort  (cost=36437.53..36775.03 rows=135000 width=153) (actual time=2166.559..2166.594 rows=100 loops=1)                                             |
|         Sort Key: rankedreviews.recipe, rankedreviews.row_num                                                                                             |
|         Sort Method: top-N heapsort  Memory: 67kB                                                                                                         |
|         ->  Subquery Scan on rankedreviews  (cost=24865.43..31277.93 rows=135000 width=153) (actual time=1724.121..2151.926 rows=15000 loops=1)           |
|               ->  WindowAgg  (cost=24865.43..29927.93 rows=135000 width=169) (actual time=1724.119..2146.898 rows=15000 loops=1)                          |
|                     Filter: ((row_number() OVER (?)) <= 3)                                                                                                |
|                     Rows Removed by Filter: 120000                                                                                                        |
|                     ->  WindowAgg  (cost=24865.43..27902.93 rows=135000 width=137) (actual time=1723.886..1991.155 rows=135000 loops=1)                   |
|                           Run Condition: (row_number() OVER (?) <= 3)                                                                                     |
|                           ->  Sort  (cost=24865.43..25202.93 rows=135000 width=129) (actual time=1723.785..1851.247 rows=135000 loops=1)                  |
|                                 Sort Key: reviews.recipe_id, reviews.rating DESC, reviews.review_id                                                       |
|                                 Sort Method: external merge  Disk: 19040kB                                                                                |
|                                 ->  Hash Join  (cost=223.50..4132.18 rows=135000 width=129) (actual time=22.541..331.859 rows=135000 loops=1)             |
|                                       Hash Cond: (reviews.recipe_id = recipes.id)                                                                         |
|                                       ->  Seq Scan on reviews  (cost=0.00..3554.00 rows=135000 width=93) (actual time=0.009..35.795 rows=135000 loops=1)  |
|                                       ->  Hash  (cost=161.00..161.00 rows=5000 width=44) (actual time=22.425..22.427 rows=5001 loops=1)                   |
|                                             Buckets: 8192  Batches: 1  Memory Usage: 457kB                                                                |
|                                             ->  Seq Scan on recipes  (cost=0.00..161.00 rows=5000 width=44) (actual time=0.381..16.985 rows=5001 loops=1) |
| Planning Time: 17.668 ms                                                                                                                                  |
| Execution Time: 2173.148 ms                                                                                                                               |
**Add Index Command:**
```sql
CREATE INDEX idx_review_recipe_id 
ON reviews (recipe_id);
```
**Performance Improvement:**
- Original: 2810.81 
- Final: 707.86
- Improvement: 2102.95


#### 3.3 Checkout 
Original Query: 
```sql
SELECT cart_items.cart_id,
        SUM(cart_items.quantity) AS total_ingredients_purchased,
        SUM(cart_items.quantity*ingredients.price) AS total_amount_paid
        FROM cart_items
        JOIN ingredients ON ingredients.ingredient_id = cart_items.item_id
        WHERE cart_items.cart_id = 45
        GROUP BY cart_items.cart_id
```
**Explain Result:**
| QUERY PLAN                                                                                                                                |
| ----------------------------------------------------------------------------------------------------------------------------------------- |
| GroupAggregate  (cost=4.73..41.09 rows=3 width=24) (actual time=2.283..2.294 rows=1 loops=1)                                              |
|   Group Key: cart_items.cart_id                                                                                                           |
|   ->  Nested Loop  (cost=4.73..41.03 rows=3 width=20) (actual time=0.928..2.256 rows=4 loops=1)                                           |
|         ->  Bitmap Heap Scan on cart_items  (cost=4.44..16.12 rows=3 width=20) (actual time=0.807..1.528 rows=4 loops=1)                  |
|               Recheck Cond: (cart_id = 45)                                                                                                |
|               Heap Blocks: exact=4                                                                                                        |
|               ->  Bitmap Index Scan on idx_items_cart_id  (cost=0.00..4.44 rows=3 width=0) (actual time=0.726..0.726 rows=4 loops=1)      |
|                     Index Cond: (cart_id = 45)                                                                                            |
|         ->  Index Scan using ingredients_pkey on ingredients  (cost=0.29..8.30 rows=1 width=16) (actual time=0.174..0.174 rows=1 loops=4) |
|               Index Cond: (ingredient_id = cart_items.item_id)                                                                            |
| Planning Time: 28.803 ms                                                                                                                  |
| Execution Time: 2.895 ms                                                                                                                  |
**Add Index Command:**
```sql
CREATE INDEX idx_items_cart_id 
ON cart_items (cart_id);
```
**Performance Improvement:**
- Original: 611.26  
- Result: 43.86
- Improvement: 567.4
