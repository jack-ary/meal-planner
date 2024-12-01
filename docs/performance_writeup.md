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

### 2: Performance Results of Hitting Endpoints

| Controller   | Endpoint                       | Time to Execute (ms) |
|--------------|---------------------------------|-----------------------|
| Carts        | /carts/create                  | .                   |
| Carts        | /carts/set-item-quantity       | .                    |
| Carts        | /carts/checkout                | .                   |
| Customers    | /customers/register            | .                   |
| Recipes      | /recipes/get                   | .                   |
| Recipes      | /recipes/create                | .                   |
| Recipes      | /recipes/suggestions           | .                   |
| Recipes      | /recipes/get-by-id             | .                    |
| Recipes      | /recipes/update                | .                   |
| Recipes      | /recipes/delete                | .                   |
| Recipes      | /recipes/get-highest-review    | .                   |
| Reviews      | /reviews/get                   | .                    |
| Reviews      | /reviews/create                | .                   |
| Reviews      | /reviews/delete                | .                   |

### 3: Performance Tuning 

#### 3.1 
#### 3.2
#### 3.3 