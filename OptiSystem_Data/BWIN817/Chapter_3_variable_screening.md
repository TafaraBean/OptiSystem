# Variable screening

- post variable clustering, further variable reduction may be needed prior to using variable selection techniques
- this is done to **eliminate clearly irrelevant input variables**

## univariate associations

- tempting to use for detecting irrelevant input variables
- each input is screened individually against the target
- only the most important inputs are retained 
- liberal univariate screening may be helpful when the number of clusters are large 

## shortcoming
- does not account for partial associations among the input variables 
- inputs could be erroneously omitted or erroneously included
- presence of interactions can give misleading univariate associations

## partial association 

- occurs when the effect of one variable changes in the presence of another variable

## preferable methods 

- multivariate methods 
- these consider subsets of variables jointly
- the best k inputs which are found via univariate screening would not necessarily be the best k-elemnt subset 

## the benefits of further variable reduction

- eliminating irrelevant variables when using the full model will stabilize the full model and **improve the variable selection technique** 
- doing so will not amount to much risk for eliminating important input variables

# Univariate smoothing 

## Scatter plots 

- standard practice to examine scatter plots of the target variable vs the input variable 
- when the target is binary, the plot isn't very enlightening 

## empirical logits
- a useful plot for detecting nonlinear relationships 

- ![img_1772225089.png](/files/BWIN817/img_1772225089.png)


## Smoothing method 
- these better reveal the relationship between a continous input variable and a target
- a simple method is to plot the empirical logits for quantiles of the input variables 
## determining factor of the smoothing 

- the number of bins 

# code snippets



- ![img_1772395015.png](/files/BWIN817/img_1772395015.png)


- ![img_1772395051.png](/files/BWIN817/img_1772395051.png)


- ![img_1772395105.png](/files/BWIN817/img_1772395105.png)


- ![img_1772395202.png](/files/BWIN817/img_1772395202.png)


- ![img_1772395251.png](/files/BWIN817/img_1772395251.png)


- ![img_1772395276.png](/files/BWIN817/img_1772395276.png)