# What does a linear programming problem relate to?

- Hint: Mini/Max
- A linear programming (LP) problem relates to minimising/maximising a linear objective function in the presence of linear constraints (equalities/inequalities).
## Define the terminology for the following LP problem.
* **What is the terminology for the following LP problem**? 
$$ 
\begin{array}{ll}
\min & c_{1} x_{1}+c_{2} x_{2}+\cdots+c_{n} x_{n} \\
\text { s.t. } & a_{11} x_{1}+a_{12} x_{2}+\cdots+a_{1 n} x_{n} \geq b_{1} \\
& a_{21} x_{1}+a_{22} x_{2}+\cdots+a_{2 n} x_{n} \geq b_{2} \\
& \vdots \\
& \vdots \\
& a_{m 1} x_{1}+a_{m 2} x_{2}+\cdots+a_{m n} x_{n} \geq b_{m} \\
& x_{1}, x_{2}, \ldots, x_{n} \geq 0
\end{array}
$$

- **Objective function**: $c_{1} x_{1}+c_{2} x_{2}+\cdots+c_{n} x_{n}$.
- **Cost coefficients**: $c_{1}, c_{2}, \ldots, c_{n}$.
- **Decision variables**: $x_{1}, x_{2}, \ldots, x_{n}$.
- **Constraints**: $\sum_{j=1}^{n} a_{i j} x_{j} \geq b_{i}, i=1, \ldots, m$.
- **Technological coefficients**: $a_{i j}, i=1, \ldots, m, j=1, \ldots, n$.
- **Right-hand-side vector**: $b_{1}, \ldots, b_{m}$.
- **Nonnegativity constraints**: $x_{1}, \ldots, x_{n} \geq 0$.

# What is the difference between feasible points and feasible regions?

- A set of values $x_{1}, \ldots, x_{n}$ that satisfies all constraints is called a feasible point and the set of all feasible points is called the feasible region.

# Among which points does the simplex method search for an optimal solution?

- he simplex method searches among extremal points for the optimal solution to the LP problem.


# What are the necessary assumptions to represent an optimization problem as an LP?

- **Proportionality:** Given a decision variable $x_{j}$, its contribution to cost is $c_{j} x_{j}$ and its contribution to the $i$ th constraint is $a_{i j} x_{j}$ (for example, if $x_{j}$ is doubled, its contribution to cost and each constraint is also doubled).

- **Additivity:** The total cost is the sum of the individual costs and the total contribution to the $i$ th constraint is the sum of the individual contributions to the $i$ th constraint.

- **Divisibility:** The values of decision variables can be fractional (i.e., noninteger values for decision variables are allowed).





# in what way should a LP be written to apply the 2 phase simplex method?

- An LP problem must be written in standard form and as a minimisation problem

# What is the difference between the canonical form and standard form of an LP problem?

- ![img_1775002999.png](/files/BWIB817/img_1775002999.png)



# What transformations can we perform to transform an LP problem into standard form?

- **inequalities and equalities:** For a constraint $\sum_{j=1}^{n} a_{i j} x_{j} \geq b_{i}$, substract a nonnegative slack variable $s_{i} \geq 0$ to change the constraint to an equality. That is, $\sum_{j=1}^{n} a_{i j} x_{j} \geq b_{i}$ is equivalent to $\sum_{j=1}^{n} a_{i j} x_{j}-s_{i}=b_{i}$, where $s_{i} \geq 0$. For a constraint $\sum_{j=1}^{n} a_{i j} x_{j} \leq b_{i}$, add a nonnegative slack variable $s_{i} \geq 0$ to change the constraint to an equality. That is, $\sum_{j=1}^{n} a_{i j} x_{j} \leq b_{i}$ is equivalent to $\sum_{j=1}^{n} a_{i j} x_{j}+s_{i}=b_{i}$, where $s_{i} \geq 0$.

- **Minimisation and maximisation:** Any maximisation problem can be converted to a minimisation problem (and vice versa) by multiplying the cost coefficients by -1 . After the optimisation, the objective value of the original problem is then -1 times the objective value of the converted problem. That is, $\max \sum_{j=1}^{n} c_{j} x_{j} \equiv -\left(\min \sum_{j=1}^{n}-c_{j} x_{j}\right)$.

- **Nonnegativity of decision variables:** For most practical problems the decision variables represent physical quantities, which are inherently nonnegative. The simplex method requires that the decision variables are nonnegative. If $x_{j}$ is unrestricted in sign, it can be replaced by $x_{j}^{\prime}-x_{j}^{\prime \prime}$, where $x_{j}^{\prime} \geq 0$ and $x_{j}^{\prime \prime} \geq 0$. If $x_{j} \geq l_{j}$, it can be replaced by $x_{j}^{\prime}=x_{j}-l_{j}$, such that $x_{j}^{\prime} \geq 0$. If $x_{j} \leq \mu_{j}$ where $\mu_{j} \leq 0$, it can be replaced by $x_{j}^{\prime}=\mu_{j}-x_{j}$, such that $x_{j}^{\prime} \geq 0$.

# how do we express an LP problem in matrix notation?
- how can the following be **converted**? 
$$
\begin{array}{cl}
\min & \sum_{j=1}^{n} c_{j} x_{j} \\
\text {r} m s . t . & \sum_{j=1}^{n} a_{i j} x_{j}=b_{i}, i=1, \ldots, m \\
& x_{j} \geq 0, j=1, \ldots, n
\end{array}
$$

- **matrix notation**: 
$$
\begin{array}{cl}
\min & \boldsymbol{c}^{\top} \boldsymbol{x} \\
\text { s.t. } & \boldsymbol{A} \boldsymbol{x}=\boldsymbol{b} \\
& \boldsymbol{x} \geq \mathbf{0}
\end{array}
$$

- with **terminology**
$$
\boldsymbol{c}=\left[\begin{array}{c}
c_{1} \\
c_{2} \\
\vdots \\
c_{n}
\end{array}\right], \boldsymbol{x}=\left[\begin{array}{c}
x_{1} \\
x_{2} \\
\vdots \\
x_{n}
\end{array}\right], \boldsymbol{b}=\left[\begin{array}{c}
b_{1} \\
b_{2} \\
\vdots \\
b_{m}
\end{array}\right], \mathbf{0}=\left[\begin{array}{c}
0 \\
0 \\
\vdots \\
0
\end{array}\right], \boldsymbol{A}=\left[\begin{array}{cccc}
a_{11} & a_{12} & \cdots & a_{1 n} \\
a_{21} & a_{22} & \cdots & a_{2 n} \\
\vdots & \vdots & & \vdots \\
a_{m 1} & a_{m 2} & \cdots & a_{m n}
\end{array}\right]=\left[\begin{array}{llll}
\boldsymbol{a}_{1} & \boldsymbol{a}_{2} & \cdots & \boldsymbol{a}_{n}
\end{array}\right],
$$

# How do we acquire a basic feasible solution?

- Suppose that $\operatorname{rank}(\boldsymbol{A}, \boldsymbol{b})=\operatorname{rank}(\boldsymbol{A})=m .^{1}$
- rearranging the columns of $\boldsymbol{A}$, let $\boldsymbol{A}=\left[\begin{array}{ll}\boldsymbol{B} & \boldsymbol{N}\end{array}\right]$
- the basic solution:$$
\boldsymbol{x}=\left[\begin{array}{l}
\boldsymbol{x}_{B} \\
\boldsymbol{x}_{N}
\end{array}\right],
$$
where $\boldsymbol{x}_{B}=\boldsymbol{B}^{-1} \boldsymbol{b}$ and $\boldsymbol{x}_{N}=\mathbf{0}$ is called a basic solution for the system $\boldsymbol{A} \boldsymbol{x}=\boldsymbol{b}$ and $\boldsymbol{x} \geq \mathbf{0}$

- If $\boldsymbol{x}_{B} \geq \mathbf{0}$, then $\boldsymbol{x}$ is called a basic feasible solution for the system

# how do we improve the basic feasible solution ?


- Suppose that we have a basic feasible solution
$$
\boldsymbol{x}=\left[\begin{array}{c}
\boldsymbol{x}_{B} \\
\boldsymbol{x}_{N}
\end{array}\right]=\left[\begin{array}{c}
\boldsymbol{B}^{-1} \boldsymbol{b} \\
\mathbf{0}
\end{array}\right],
$$

- whose objective value, denoted by $z_{0}$, is given by
$$
z_{0}=\boldsymbol{c}^{\top} \boldsymbol{x}=\left[\begin{array}{ll}
\boldsymbol{c}_{B}^{\top} & \boldsymbol{c}_{N}^{\top}
\end{array}\right]\left[\begin{array}{c}
\boldsymbol{B}^{-1} \boldsymbol{b} \\
\mathbf{0}
\end{array}\right]=\boldsymbol{c}_{B}^{\top} \boldsymbol{B}^{-1} \boldsymbol{b}
$$

- Now, let $\boldsymbol{x}$ be an arbitrary feasible solution. $\boldsymbol{b}=\boldsymbol{A} \boldsymbol{x}= \boldsymbol{B} \boldsymbol{x}_{B}+\boldsymbol{N} \boldsymbol{x}_{N}$. Rearranging the terms and multiplying by $\boldsymbol{B}^{-1}$ gives
$$
\begin{align*}
\boldsymbol{x}_{B} & =\boldsymbol{B}^{-1}\left(\boldsymbol{b}-\boldsymbol{N} \boldsymbol{x}_{N}\right) \\
& =\boldsymbol{B}^{-1} \boldsymbol{b}-\boldsymbol{B}^{-1} \boldsymbol{N} \boldsymbol{x}_{N}  \tag{1}\\
& =\boldsymbol{B}^{-1} \boldsymbol{b}-\sum_{j \in R} \boldsymbol{B}^{-1} \boldsymbol{a}_{j} x_{j}
\end{align*}
$$
where $R$ is the current set of indices for the nonbasic variables

- By letting $z$ denote the objective value at $\boldsymbol{x}$, we get
$$
\begin{align*}
z & =\boldsymbol{c}^{\top} \boldsymbol{x} \\
& =\boldsymbol{c}_{B}^{\top} \boldsymbol{x}_{B}+\boldsymbol{c}_{N}^{\top} \boldsymbol{x}_{N} \\
& =\boldsymbol{c}_{B}^{\top}\left(\boldsymbol{B}^{-1} \boldsymbol{b}-\sum_{j \in R} \boldsymbol{B}^{-1} \boldsymbol{a}_{j} x_{j}\right)+\sum_{j \in R} c_{j} x_{j}  \tag{2}\\
& =\boldsymbol{c}_{B}^{\top} \boldsymbol{B}^{-1} \boldsymbol{b}-\sum_{j \in R}\left(\boldsymbol{c}_{B}^{\top} \boldsymbol{B}^{-1} \boldsymbol{a}_{j} x_{j}-c_{j} x_{j}\right) \\
& =z_{0}-\sum_{j \in R}\left(z_{j}-c_{j}\right) x_{j},
\end{align*}
$$
where $z_{j}=\boldsymbol{c}_{B}^{\top} \boldsymbol{B}^{-1} \boldsymbol{a}_{j}$ for each nonbasic variable.

- Fix all $x_{j}=0$ except for $x_{k}$ with a positive $z_{k}-c_{k}$, where $z_{k}-c_{k}$ is the
largest positive value among the $z_{j}-c_{j}$ values. From Equation (2), the new objective value is then
$$
\begin{equation*}
z=z_{0}-\left(z_{k}-c_{k}\right) x_{k} \tag{3}
\end{equation*}
$$

- We thus have $\boldsymbol{x}_{B}=\boldsymbol{B}^{-1} \boldsymbol{b}-\boldsymbol{B}^{-1} \boldsymbol{a}_{k} x_{k}$.
- Then we have
$$
\begin{align*}
\boldsymbol{x}_{B} & =\boldsymbol{B}^{-1} \boldsymbol{b}-\boldsymbol{B}^{-1} \boldsymbol{a}_{k} x_{k} \\
{\left[\begin{array}{c}
x_{B_{1}} \\
x_{B_{2}} \\
\vdots \\
x_{B_{m}}
\end{array}\right] } & =\left[\begin{array}{c}
\left(\boldsymbol{B}^{-1} \boldsymbol{b}\right)_{1} \\
\left(\boldsymbol{B}^{-1} \boldsymbol{b}\right)_{2} \\
\vdots \\
\left(\boldsymbol{B}^{-1} \boldsymbol{b}\right)_{m}
\end{array}\right]-\left[\begin{array}{c}
\left(\boldsymbol{B}^{-1} \boldsymbol{a}_{k}\right)_{1} \\
\left(\boldsymbol{B}^{-1} \boldsymbol{a}_{k}\right)_{2} \\
\vdots \\
\left(\boldsymbol{B}^{-1} \boldsymbol{a}_{k}\right)_{m}
\end{array}\right] x_{k} \tag{4}
\end{align*}
$$

- $x_{k}$ can be increased until
$$
x_{k}=\frac{\left(\boldsymbol{B}^{-1} \boldsymbol{b}\right)_{r}}{\left(\boldsymbol{B}^{-1} \boldsymbol{a}_{k}\right)_{r}}=\min _{1 \leq i \leq m}\left\{\frac{\left(\boldsymbol{B}^{-1} \boldsymbol{b}\right)_{i}}{\left(\boldsymbol{B}^{-1} \boldsymbol{a}_{k}\right)_{i}}:\left(\boldsymbol{B}^{-1} \boldsymbol{a}_{k}\right)_{i}>0\right\}
$$

- Thus, the variable $x_{k}$ enters the basic matrix and the variable $x_{B_{r}}$ leaves the basic matrix.


# How do we apply the 2 phase simplex method?

- Ensure that the LP problem is written in standard form with $\boldsymbol{b} \geq \mathbf{0}$

- Introduce an artificial variable for each constraint, denoted
by $\boldsymbol{x}_{a}$, such that
$$
\begin{aligned}
& \boldsymbol{A} \boldsymbol{x}+\boldsymbol{I} \boldsymbol{x}_{a} \quad=\boldsymbol{b}, \quad \boldsymbol{x}_{a} \geq \mathbf{0}, \\
& {\left[\begin{array}{ll}
\boldsymbol{A} & \boldsymbol{I}
\end{array}\right]\left[\begin{array}{c}
\boldsymbol{x} \\
\boldsymbol{x}_{a}
\end{array}\right]=\boldsymbol{b}, \quad \boldsymbol{x}_{a} \geq \mathbf{0} .}
\end{aligned}
$$

- we have a starting basic feasible solution to the LP problem min $\boldsymbol{I} \boldsymbol{x}_{a}$ as $\boldsymbol{x}=\mathbf{0}$ and $\boldsymbol{x}_{a}=\boldsymbol{b}$.
- If at optimality $\boldsymbol{x}_{a} \neq \mathbf{0}$, then the original LP problem has no feasible solutions. If $\boldsymbol{x}_{a}=\mathbf{0}$, a basic feasible solution for the original LP problem has been identified. Continue to Phase II with this new starting basic feasible solution.
- Start with the previous basic feasible solution and solve the original LP problem. Continue until all $z=\boldsymbol{c}_{B}^{\top} \boldsymbol{B}^{-1} \boldsymbol{N}-\boldsymbol{c}_{N}^{\top}$ values are negative, which means that an optimal solution has been reached. The optimal objective value is then
$$
z^{*}=\boldsymbol{c}_{B}^{\top} \boldsymbol{B}^{-1} \boldsymbol{b}
$$
where $\boldsymbol{B}^{-1} \boldsymbol{b}$ contains the optimal solution values for $\boldsymbol{x}$.

# What are some considerations for when we convert a primal LP problem to a dual LP problem?

- When converting a primal LP problem to a dual LP problem, note that, (1) there is exactly one dual variable for each primal constraint, (2) there is exacly one dual constraint for each primal variable, (3) the dual of the dual is the primal, and (4) if the primal is a minimisation problem, the dual is a
maximisation problem (vice versa).

# What is the fundamental theorem of duality?

- With regard to the primal and dual LP problems, exactly one of the following is true.
(1) Both possess optimal solutions $\boldsymbol{x}^{*}$ and $\boldsymbol{w}^{*}$, such that $\boldsymbol{c}^{\top} \boldsymbol{x}^{*}=\boldsymbol{b}^{\top} \boldsymbol{w}^{*}$.
(2) One problem has an unbounded objective value, in which case the other problem is infeasible.
(3) Both problems are infeasible.







