# What is the difference between cross-selling and up-selling?

- **Cross-selling:** when the firm **sells different products** to its customers.
- **Up-selling:** when the firm **sells more of the same product** to the customer.

# Define the simplifoed retention model for CLV?
 
![img_1778442480381.png](/files/BWIB822/img_1778442480381.png)

# What are the 3 potential benefits for cross-/up-selling:
- can generate higher sales in the current period.
- can increase future revenue.
- might increase retention rate.

# What is the key question for cross-selling models?
- **Key question:** what **products** should the firm sell at what **time** to which **customers**?

# Discuss the 2 types of predictive cross-selling models. What do they predict?

- **Next-Product-To-Buy (NPTB) models:** Predict what product the customer needs.
- **Next-product-to-buy with timing and response:** Predicts whether the customer will respond to a cross-selling offer.


# discuss in detail how NPTB models work. What is the strategy, ideal data source and the realistic data source?

- The strategy is to cross-sell the product that the customer is most likely going to buy next. 

- the ideal data asource would be to have a survey asking the customer the products they need but in reality we analyse the products of customers with similar profiles.
- we look at the products these similar customers bought next. Our assumption is that this is a product the customer needs.
- the most basic approaches of NPTB is market basket analysis and collaborative filtering.

# What is market basket analysis (MBA)?
- MBA analyses products customers tend to buy together
- typically the input is the customer transaction data, followed by an anlysis of all the combinations of products bought together. the output is product association rules.
- These association rules are used to decide which products to cross-sell or promote
- The value we get from MBA is: 
- 1. Association rules inform how shelves should be stocked.
- 2. design of promotional strategies.
- 3. selection of cross-selling items.

# What do association rules consist of?
- Association rules consist of an **antecedent** and a **consequent**

![img_1778443946142.png](/files/BWIB822/img_1778443946142.png)

- we are looking for interesting, relevant and good rules.
* we evaluate the **quality** of the association rules by the **support, confidence and lift**


# What is the Support evaluation metric?
*
**Support** is the % of transactions
that contain a specific
combination of items


![img_1778444208880.png](/files/BWIB822/img_1778444208880.png)

Example:


![img_1778444251878.png](/files/BWIB822/img_1778444251878.png)


# What is the confidence evaluation metric?
*
Confidence is the strength of association.
it measures how much the consequent depends on the antecedent.
formally, it is the conditional probability of basket containing product B if it already contains product A.


![img_1778444533364.png](/files/BWIB822/img_1778444533364.png)



# What is the disadvantage of support as an evaluation metric?

# What is the disadvantage of confidence as an evaluation metric?








