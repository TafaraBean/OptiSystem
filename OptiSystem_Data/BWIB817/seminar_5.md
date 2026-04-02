# linear programming

## concerned with minimizing/maximising an objective function
- constraints are linear 
- ![img_1771845343.png](/files/BWIB817/img_1771845343.png)

## terminology


- ![img_1771845287.png](/files/BWIB817/img_1771845287.png)

## feasible points 
- set of points which satisfy all constraints

- set of all feasible points is the feasible region

## assumptions

### proportionality

### divisibility

### additivity

## forms of an LP problem 

- must be written in standard form and as a minimisation problem

- this is to apply the 2 phase simplex method

- ![img_1771845673.png](/files/BWIB817/img_1771845673.png)

- the differences are mainly around the constraints

## manipulations to transform LP problem to standard form

- inequalties and equalities
- minimisation and maximisation
- nonnegativity of decision variables

## matrix notation

- ![img_1771846617.png](/files/BWIB817/img_1771846617.png)
- ![img_1771846659.png](/files/BWIB817/img_1771846659.png)

# Solving an LP problem

## consider:


- ![img_1771847059.png](/files/BWIB817/img_1771847059.png)
- $c$ is ($n$x1)
- $x$ is ($n$x1)
- $b$ is ($m$x1)
- $A$ is ($m$x$n$)
- rank ($A$,$b$) = rank($A$) = $m$

## rearrange columns of $A$


## solutions


## improving a basic feasible solution

- can we improve the objective function?
- we first need a feasible solution
- the method discussed next can be used to find a new basic feasible
solution with a better objective value


### the basic feasible solution

### the objective value

### then we have that 

### rearranging the terms

### we then get

### for each non-basic variable

### ...

# 2 phase simplex method 

## Phase 1

## Phase 2

# Duality

## fundamental theorem of duality 
