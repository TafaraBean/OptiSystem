# database marketing metrics 

## improves marketing campaigns

### we identify the customers more likely to respond to an ad

### a customer's purchase response can be predicted from previous transactions

#### RFM analysis entails that customers are classified based on their RFM score

##### Recency

- time elapsed since customer's last purchase

- typically negative relationship between response probability and recency

- product type dependent
- ![img_1771584588.png](/files/BWIB822/img_1771584588.png)

#####  Frequency

- number of times a customer has purchased in a given time period
- typically a positive relationship between frequency and response probability

- ![img_1771584689.png](/files/BWIB822/img_1771584689.png)

##### Monetary

- total amount on purchases in a given amount of time
- typically a positive relationship between response probability and monetary

- ![img_1771584996.png](/files/BWIB822/img_1771584996.png)


##### there are $k^3$ different RFM codes 

- we get an average resposne rate for each RFM code



#### these classifications are used to predict the response propensity

##### these response propensities help in identifying which customers we should target


#### RFM sas code 

##### ![img_1771586483.png](/files/BWIB822/img_1771586483.png)

- gets the number of days between the order_date and a "current" date

##### ![img_1771586606.png](/files/BWIB822/img_1771586606.png)

- creates the columns for continuous RFM values.

##### proc rank 

- ![img_1771586820.png](/files/BWIB822/img_1771586820.png)


- ![img_1771586896.png](/files/BWIB822/img_1771586896.png)


- ![img_1771586963.png](/files/BWIB822/img_1771586963.png)

##### cell sorting technique

- ![img_1771588738.png](/files/BWIB822/img_1771588738.png)


##### RFM anova 

- ![img_1771592374.png](/files/BWIB822/img_1771592374.png)


#### limitations of RFM analysis

##### independently links the RFM values to the customer data

##### unequal number of customers in each cell

##### RFM values are correlated

##### a proposal 

###### RFM cell sorting technique


- ![img_1771588474.png](/files/BWIB822/img_1771588474.png)

#### breakeven analysis

##### if we have budget constraints then we only choose the top X% of the of campaign contacts

##### if we have no budget cnstraints we must determine optimal number of campaign offers to maximize the profit 

###### we first have to determine the cut-off response probability




- ![img_1771589532.png](/files/BWIB822/img_1771589532.png)

###### order amount assumptions

- $E(Z)$ is typically assumed to be homogenous
- instead we could observe regression to the mean effects
- we could use a distributional assumption such as the gamma distribution to account for regression to the mean.
- the order amount per customer follows a gamma distribution 
- across all customers the rate parameter follows a gamma distribution 
- across the entire population the order amounts ($z$) are distributed in the following way (in purple) : 


- ![img_1771590935.png](/files/BWIB822/img_1771590935.png)


#### why are they popular? 

##### simplicity and predicts well 

##### Criticisms

- arbitrary discretization loses information 
- response probabilities don't vary much across segments
- cumbersome to add modern data like behavioural and demographic information 

##### Proposals 
- treat RFM as a anova model
- models without discretisation

##### Statistically, RFM model is a three-way ANOVA with all main effects and interactions (saturated model):

- ![img_1771592283.png](/files/BWIB822/img_1771592283.png)

##### other options 

- Weights of evidence (WoE) binning to determine number of levels
- Binary classification model with continuous R, F and M as
independent variables
- Decision trees with binned or continuous R, F and M as independent
variables
- Non-linear regression models

#### Order of importance of RFM values 

- metric with highest response rate decline. 
- dependent on the industry 


- ![img_1771592777.png](/files/BWIB822/img_1771592777.png)