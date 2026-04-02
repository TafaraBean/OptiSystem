# Subset selection

## Variable selection in regression 

- concerned with finding subsets of inputs which are jointly important in predicting the output.
- most thorough search is the all possible subsets
- can be expensive 

## Stepwise selection
- often criticized
- model is incremetally built until no improvement is made
- variables can be removed from the model at each step if they have become unimportant
- computationally efficient alternative to all subsets
- may ot find the best subsets and can perform badly in many situations.

## Backward elimination

- starts with all candidate variables 
- at each step the least important variable is removed
- less likely to exclude important variables or include spurious inputs
- more computationally expensive than stepwise methods because more steps are usually required

# Code snippets 



									

- ![img_1772395332.png](/files/BWIN817/img_1772395332.png)


- ![img_1772395358.png](/files/BWIN817/img_1772395358.png)