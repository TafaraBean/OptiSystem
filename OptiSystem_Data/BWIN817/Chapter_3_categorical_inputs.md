# Categorical inputs
- act as links to other datasets

## The class statement

- we don't need to create dummy variables for proc logistic as long as we have the class statement.
- can cause quasi-complete separation

## dummy variables vs smarter variables

- dummy variables increase dimensionality of the data 
- smarter variables have subject matter knowledge. These represent releveant sources of variation 


## Quasi-complete separation

- occurs when a level of the categorical inputs has a target event rate of 0% or 100%
- the most common cause of quasi-complete separtion is rare categories in categorical inputs

### How logits play a part

- the coefficients of dummy variables represent the difference in logits between a level and the reference level
- one of the logits will be infinite 
- ML estimate of the coefficient will be infinite. the likelihood won't have a maximum in at least one dimension

### if zero cell category is reference level

- all the coefficients for the dummy variable will be infinite

### implications of Quasi-complete separation

- complicates model interpretation
- convergence of the estimation algorithm is affected
- might lead to incorrect decisions for variable selection

### remedy for sparseness

- collapse the levels of the categorical input
- ideally we should use subect matter considerations when collapsing levels

### clustering levels (Greenacre's method)

- the levels (rows) are heirarchically clustered based on the reduction in the chi-square test of assocoaition between the categorical variable and target variable.
- at each step the 2 levels which result in the least reduction in the chi-square test statistic are merged 
- process is continued until the reduction of the chi square statistic drops below a certain threshold

### the result 

- this results in rare categories being combined with other categories with similar marginal response rates


### the drawbacks

- potential loss of information because only univariate associations are considered

# Code snippets 

- ![img_1772331504.png](/files/BWIN817/img_1772331504.png)


- ![img_1772331571.png](/files/BWIN817/img_1772331571.png)
