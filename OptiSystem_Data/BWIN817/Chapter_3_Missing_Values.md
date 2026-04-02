# ![img_1771355914.png](/files/BWIN817/img_1771355914.png)

# Missing values

## Probability of missing depends on multiple cases

### MCAR

- Missing completely at random
- easy to manage but also unrealistic 

### other dependencies

- might depend on the unobserved values
- might depend on the observed values of other input variables
- might depend on a combination of values of correlated inputs 

### problematic missing-value mechanism

- might depend on onobserved (lurking) predictors

## fundamental concern for predictive modelling

- missing values might depend on the observed value of the target

## Complete case analysis

- only cases without any missing values are considered for analysis.

### practical shortcomings 

- huge loss of data in high dimensional data

## Practical considerations

### scorability 

- how would a model trained on complete cases score a new case with missing values?

## Imputation

-filling in missing values with some reasonable value 

- subject matter knowledge is often important

### principal consideration 

- getting valid statistical inference on the imputed data and not generalization. (meaning it must be valid and not skew the data)


## reasonable strategy to address missing values

- 1. create missing indicators and treat them as new input variables for analysis
- ![img_1771972450.png](/files/BWIN817/img_1771972450.png)
- 2. use median imputation for numeric variables. 
- fill the missing value with the median of the complete cases for that variable
- 3. create a new level representing missing for categorical inputs
- this strategy is unsophisticated but satisfies 2 of the most important considerations for predictive modeling
- 1. efficient scorability 
- 2. captures the relationship between missing variables and the target

### new cases are easily scored 

- replace the missing values with the medians from the development data
- apply the prediction model

# Code snippets 


- ![img_1772331223.png](/files/BWIN817/img_1772331223.png)


