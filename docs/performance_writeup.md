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
| Recipes      | /recipes/get                   | 12043.22             |
| Recipes      | /recipes/create                | 109.97               |
| Recipes      | /recipes/suggestions           | 1219.74              |
| Recipes      | /recipes/get-by-id             | 289.11               |
| Recipes      | /recipes/update                | 308.30               |
| Recipes      | /recipes/delete                | .                   |
| Recipes      | /recipes/get-highest-review    | 2810.81             |
| Reviews      | /reviews/get                   | 354.27               |
| Reviews      | /reviews/create                | 83.04               |
| Reviews      | /reviews/delete                | 100.04               |

### 3: Performance Tuning 

#### 3.1 Get Recipes
Original Query: 
```sql
```
Explain Result: 
```sql
```
Add Index Command:
```sql
```
Performance Improvement: 

#### 3.2
Original Query: 
```sql
```
Explain Result: 
| QUERY PLAN                                                                                                                                                                            |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hash Join  (cost=1371.31..4762.42 rows=112484 width=70) (actual time=378.677..1256.572 rows=9334 loops=1)                                                                             |
|   Hash Cond: (ri.ingredient_id = i.ingredient_id)                                                                                                                                     |
|   Join Filter: ((SubPlan 1) OR (hashed SubPlan 2))                                                                                                                                    |
|   Rows Removed by Join Filter: 140644                                                                                                                                                 |
|   ->  Hash Join  (cost=223.50..3220.31 rows=149978 width=60) (actual time=12.478..307.521 rows=149978 loops=1)                                                                        |
|         Hash Cond: (ri.recipe_id = r.id)                                                                                                                                              |
|         ->  Seq Scan on recipe_ingredients ri  (cost=0.00..2602.78 rows=149978 width=24) (actual time=0.516..166.129 rows=149978 loops=1)                                             |
|         ->  Hash  (cost=161.00..161.00 rows=5000 width=44) (actual time=11.922..11.923 rows=5001 loops=1)                                                                             |
|               Buckets: 8192  Batches: 1  Memory Usage: 440kB                                                                                                                          |
|               ->  Seq Scan on recipes r  (cost=0.00..161.00 rows=5000 width=44) (actual time=0.832..9.128 rows=5001 loops=1)                                                          |
|   ->  Hash  (cost=176.00..176.00 rows=10000 width=26) (actual time=14.292..14.304 rows=10000 loops=1)                                                                                 |
|         Buckets: 16384  Batches: 1  Memory Usage: 766kB                                                                                                                               |
|         ->  Seq Scan on ingredients i  (cost=0.00..176.00 rows=10000 width=26) (actual time=0.017..8.326 rows=10000 loops=1)                                                          |
|   SubPlan 1                                                                                                                                                                           |
|     ->  Function Scan on unnest ingredient_pattern  (cost=0.00..0.04 rows=1 width=0) (actual time=0.002..0.002 rows=0 loops=149978)                                                   |
|           Filter: (lower(i.ingredient_name) ~~ (('%'::text || ingredient_pattern) || '%'::text))                                                                                      |
|           Rows Removed by Filter: 2                                                                                                                                                   |
|   SubPlan 2                                                                                                                                                                           |
|     ->  HashAggregate  (cost=837.43..844.93 rows=750 width=8) (actual time=351.016..351.529 rows=306 loops=1)                                                                         |
|           Group Key: ri_1.recipe_id                                                                                                                                                   |
|           Batches: 1  Memory Usage: 57kB                                                                                                                                              |
|           ->  Nested Loop  (cost=0.30..835.56 rows=750 width=8) (actual time=0.469..350.230 rows=316 loops=1)                                                                         |
|                 ->  Nested Loop Semi Join  (cost=0.00..775.00 rows=50 width=8) (actual time=0.100..21.802 rows=20 loops=1)                                                            |
|                       Join Filter: (lower(i_1.ingredient_name) ~~ (('%'::text || ingredient_pattern_1.ingredient_pattern) || '%'::text))                                              |
|                       Rows Removed by Join Filter: 19972                                                                                                                              |
|                       ->  Seq Scan on ingredients i_1  (cost=0.00..176.00 rows=10000 width=14) (actual time=0.012..3.600 rows=10000 loops=1)                                          |
|                       ->  Function Scan on unnest ingredient_pattern_1  (cost=0.00..0.02 rows=2 width=32) (actual time=0.000..0.000 rows=2 loops=10000)                               |
|                 ->  Index Scan using idx_recipe_ingredients_ingredient_id on recipe_ingredients ri_1  (cost=0.29..1.06 rows=15 width=16) (actual time=2.683..16.393 rows=16 loops=20) |
|                       Index Cond: (ingredient_id = i_1.ingredient_id)                                                                                                                 |
| Planning Time: 42.208 ms                                                                                                                                                              |
| Execution Time: 1262.841 ms                                                                                                                                                           |
Add Index Command:
```sql
CREATE INDEX idx_ingredient_name 
ON ingredients (ingredient_name);
```
Performance Improvement: 
Original: 1219.74
Result: 1005.08
Improvement: 

#### 3.3 
Original Query: 
```sql
```
Explain Result: 
```sql
```
Add Index Command:
```sql
```
Performance Improvement: 
