
# LP basics

## Introduction

- a linear programming problem relates to minimising/maximising a linear objective function in the presence of linear constraints
- consider the following linear programming problem with $n$ decision variables and $m$ constraints

- ![img_1772620760.png](/files/BWIB817/img_1772620760.png)
- the objective function is given by $c_1x_1$ +$c_2x_2$ + $...$ + $c_nx_n$
- the cost coeffiecients are $c_1$, $c_2$,$...$, $c_n$
- the decision variables are $x_1$,$x_2$,$...$,$x_n$
- the constraints are given by  ![img_1772621411.png](/files/BWIB817/img_1772621411.png)
- the technological coefficients are ![img_1772621467.png](/files/BWIB817/img_1772621467.png)

- the right hand side vector ![img_1772621541.png](/files/BWIB817/img_1772621541.png)
- the non-negativity variables  ![img_1772621573.png](/files/BWIB817/img_1772621573.png)

## feasibility 

- the set of all points $x_1,x_2,...,x_n$ that satisfies all constraints is known as a feasible point
- the set of all feasible points is known as the feasible region

## The assumptions to represent an optimisation problem

### Proportionality
- Given a decision variable $x_j$, its contribution to cost is $c_jx_j$ and its contribution to the $i_{th}$ constraint is $a_{ij}x_j$

### 
Additivity 

- the total cost is the sum of the individual costs 
- the total contribution to the $i_{th}$ constraint is the sum of the individual contributions to the $i_{th}$ constraint.
### Divisibility
- the values of the decison variables can be fractional

## requirements for 2-phase simplex method

- **the LP problem must be written in standard form and as a minimisation problem.**

## the standard and canonical forms of LP problems 


- ![img_1772622625.png](/files/BWIB817/img_1772622625.png)
- standard forms have equality constraints 
- canonical forms have inequality constraints 
- the signs of the inequalities differ for minimisation and maximisation problems 


## Transforming the LP problem to a standard form 

### Inequalities and equalities

- for a constraint:
- ![img_1772622908.png](/files/BWIB817/img_1772622908.png)
- subtract a nonnegative slack varible $s_i$ > 0 to change the constraint to an equality
- ![img_1772623078.png](/files/BWIB817/img_1772623078.png)
- for a constraint: 


- ![img_1772623126.png](/files/BWIB817/img_1772623126.png)
- we add a non-negative slack variable $s_i$ > 0 to change the constraint to an equality  
- ![img_1772623239.png](/files/BWIB817/img_1772623239.png)

### Minimisation and maximisation

- any maximisation problem can be converted to a minimisation problem (and vice versa)
- we do this by multiplying the cost coefficients by -1
- that is: 

- ![img_1772623602.png](/files/BWIB817/img_1772623602.png) ![img_1772623618.png](/files/BWIB817/img_1772623618.png)

## Non-negativity of decision variables 

- the decision variables are usually physical quantities and are inherently positive

# Solving an LP 

## the basic feasible solution

