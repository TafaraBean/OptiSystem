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

![img_1778444712634.png](/files/BWIB822/img_1778444712634.png)


# What is the lift evaluation metric?
*
lift is a measure that overcomes the problems of support and confidence.
it is the factor by which the confidence exceeds the expected confidence.

![img_1778444927559.png](/files/BWIB822/img_1778444927559.png)

a larger lift means more interesting association rules.


# What is the disadvantage of support as an evaluation metric?

# What is the disadvantage of confidence as an evaluation metric?

# What is the disadvantage of lift as an evaluation metric?

# What are the issues with using MBA for cross-selling?


- **Disadvantages** of support, confidence and lift.
- Selection of **time period** to construct confidence metric.
- Which products to **consider** out of a very large product line.
- We looked at **one antecedent and one consequent** – want to
make more recommendations?
- **Collaborative filtering** a possible solution.


# What are collaborative filtering models?

*
A **step up** from MBA as it takes into account **multiple
antecedents**.

Very popular in current era of
recommendation engines.

Two major forms:
Memory-based / User-based
Model-based / Item-based

They can be used in ratings matrixes. this allows us to predict missing ratings.
we predict empty cells in a ratings matrix using the CF algorithm and make recommendations using the top-N list.

# discuss memory-based collaborative filtering models?

*
Also known as user-based or nearest neighbour.

predictions for a target user's ratings for some target item are based on users with similar profiles to the target user.

For this approach, extract only users that have purchased and
rated the target item.


![img_1778445793510.png](/files/BWIB822/img_1778445793510.png)


this equation consists of the target user's own average rating.
ratings of target item by other users.
similarity between the active user and the other users.

If target/active user doesn’t have many ratings, this could
severely affect ratings quality

This won’t take account of differences between
products/items

however, will the active/target user also prefer the item or not? This
depends on whether the active/target user and the other user have similar tastes. the similarity is computed over items rated by both users.

If the other user is dissimilar to the active/target user, their relative preference
will be weighted down.
If the other user is similar to the active/target user, their relative preference
will be weighted up

This weighted sum is then used to adjust the active/target
user’s overall average rating to a more accurate estimate.

to compute the similarity we could use the pearson correlation or the spearman rank correlation as a non-paramteric alternative.

This method is easy to implement but data sparsity leads to poor predictive accuracy and computations grow exponentially.

# Discuss model-based collaborative filtering models?
*
Also known as item-based methods

Considers set of items bought and rated by target user


Two-step process:
1. Calculate similarity between items in the set and the target item
2. **Combines similarities into a predicted preference rating**

Two most popular similarity measures:
1. Pearson correlation coefficient
2. Cosine vector



![img_1778447492976.png](/files/BWIB822/img_1778447492976.png)

and 


![img_1778447537829.png](/files/BWIB822/img_1778447537829.png)


The approach:
1. extract only items purchased and rated by the target user
2. predict the rating of item j by the target user $u$, $r_{u,j}$

![img_1778447826782.png](/files/BWIB822/img_1778447826782.png)

This leads to **better quality predictions** and **fast online recommendations** but **model building is expensive** and there is a trade-off between **predictive performance and scalability**.

Hybrid collaborative filtering tries to
overcome these limitations


