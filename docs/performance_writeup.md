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
```sql
```
Add Index Command:
```sql
```
Performance Improvement: 

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
