
# Concurrency Phenomena and Solutions

## Case 1: Dirty Read
**Scenario:**  
An example of a Dirty Read would be if Transaction A updates a recipe's name in the database but has not committed yet. Transaction B reads the recipe's name before Transaction A commits or rolls back.

**Sequence Diagram:**  
![Dirty Read](dirtyReadpt1.png)
![Dirty Read Diagram](dirtyReadPt2.png)

**Potential Impact:**  
If Transaction A rolls back, Transaction B would then be operating on invalid data.

**Solution:**  
Use the **Read Committed** isolation level to ensure that Transaction B only sees committed data. This prevents dirty reads by delaying Transaction B until Transaction A commits or rolls back.

---

## Implementation Notes
In our system, we will apply isolation levels at the database level using the following strategies:

1. **Read Committed** for queries like reading recipe details to avoid dirty reads.

## Ensuring Isolation of Transactions

To ensure isolation and lower the potential of example issues like laid out in the above section we would implement the  following strategies:

### Case 1: Dirty Read
- **Strategy:** Use the **Read Committed** isolation level for transactions that involve reading data.
- **Why this is appropriate:** The Read Committed isolation level ensures that a transaction cannot read data that has been modified but not yet committed by another transaction. This prevents the use of uncommitted ("dirty") data.

