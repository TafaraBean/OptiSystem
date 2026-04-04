# Response probability

- One of the **key questions** we want to answer with regard to customer acquisition is
whether we can determine which future prospects have the **highest likelihood of
adoption**

## mathematical preliminaries
- hint: binary, logistic, latent, probability, logit
- Typical binary response in acquisition modelling:
$$
y_i=\left\{\begin{array}{lc}
1, & \text { acquired } \\
0, & \text { not acquired }
\end{array}\right.
$$
- A logistic regression model models the probability that the response belongs to either of these categories
- Let $x^T=\left(1, x_1, \ldots, x_p\right)$ denote the vector of independent variables appended with a 1 to account for the intercept
- Let $\beta^T=\left(\beta_0, \beta_1, \ldots, \beta_p\right)$ denote the corresponding regression coefficients
- One way to motivate the logistic regression model is through
the latent variable model
- The idea is that there is a latent unobserved variable, $y^*$, and that once a threshold on $y^*$ is passed, the observed binary $y$ switches from 0 (not acquired) to 1 (acquired).
- $$
y_i= \begin{cases}1, & y_i^*>0 \\ 0, & y_i^* \leq 0\end{cases}
$$
- the probability:
$$
P(y=1)=P\left(y^*>0\right)=1-P\left(y^* \leq 0\right)=1-P\left(\varepsilon \leq-x^T \beta\right)
$$
- If $\varepsilon$ has a logistic distribution with mean zero and variance $\pi^2 / 3$, then
$$
F_{\varepsilon}(z)=\frac{1}{1+e^{-z}}
$$
- Letting $z=-x^T \beta$, it follows that
$$
P(y=1)=1-\frac{1}{1+e^{x^T \beta}}=\frac{1}{1+e^{-x^T \beta}}
$$
- The type of model depends on the assumption of the distribution of
the error term. the previous is a binary logit model.
## the probit model
- hint: normal, 2-stage
- if the error term has a standard normal distribution we use a probit model. it is 
particularly useful in **2-stage modeling framework**
- the second stage is a least squares regression
with a normally distributed error term
- e.g. linking customer acquisition and relationship duration
together using a probit two-stage least squares model
- in the first stage we determine the response probability
and the second stage determines the duration of the 
relationship using the first stage probability as input
## attitudinal propensity
- hint:  unobserved, intention
- As the prospects’ response likelihood is not always behaviorally observed,
 attitudinal propensity scale is also used to **measure prospects’ response intention**
 -  attitude is usually positively related with behavior

## the predictive model for response probabilities

- ![img_1775255113.png](/files/BWIB822/img_1775255113.png)

### implementation
- we should be able to:
Predict the number of prospects we are likely to acquire.
Determine the **accuracy** of our prediction.
- use the estimates we obtained from the response
probability model in stage 1 (logistic regression)
- do this for each customer and choose which customer to select given
acquisition spending and prospect characteristics
- create a **cutoff value** to split prospects
into 2 new groups ( predicted to acquire and predicted not to acquire )
- choose the one that provides the
best predictive accuracy for the dataset
- To determine the predictive accuracy we **compare the predicted to the actual acquisition values** in a 2 by 2 table

## calculating odds ratios 
- $\operatorname{Odds}($ Acquisition $\mid$ Revenue $=\mathrm{x})=\exp (-26.206+0.032 \mathrm{x})$, and, for Revenue $=\mathrm{x}+1$,
$$
\text { Odds(Acquisition } \mid \text { Revenue }=\mathrm{x}+1)=\exp (-26.206+0.032(\mathrm{x}+1)) .
$$
- By dividing the second equation by the first we get
$$
\frac{\text { Odds }(\text { Acquisition } \mid \text { Revenue }=\mathrm{x}+1)=\exp (-26.206+0.032(\mathrm{x}+1))}{\text { Odds }(\text { Acquisition } \mid \text { Revenue }=\mathrm{x})=\exp (-26.206+0.032 \mathrm{x})} .
$$

We then simplify the equation to get the following:
$$
\frac{\operatorname{Odds}(\text { Acquisition } \mid \text { Revenue }=\mathrm{x}+1)}{\operatorname{Odds}(\text { Acquisition } \mid \text { Revenue }=\mathrm{x})}=\exp (0.032)=1.033
$$

### Acq_expense odds ratio

- Recall both linear and squared acquisition expense included
- Let $x$ denote Acq_Expense and $\hat{p}^{\prime}$ denote the logit (log of the odds).
- Then
$$
\hat{p}^{\prime}\left(x_j\right)=\ln \left(o d d s_1\right)=-26.1899+0.0672 x_j-0.00004\left(x_j\right)^2
$$
and
$$
\hat{p}^{\prime}\left(x_j+1\right)=\ln \left(o d d s_2\right)=-26.1899+0.0672\left(x_j+1\right)-0.00004\left(x_j+1\right)^2
$$
- - The difference is given by
$$
\ln \left(o d d s_2\right)-\ln \left(o d d s_1\right)=\ln \left(\frac{o d d s_2}{o d d s_1}\right)=0.0672-0.00008 x_j
$$


## Initial order quantity
hint: maximize profit, initial, good predictor,bias
- Can't just focus on acquiring as many prospects as possible, also need to consider the value the customer might add to maximize profit
- Initial order value is the value of the first purchase after being acquired
- It has been identified as a potentially good predictor in a customer's future value to the firm
- It can also justify the money spent on customer acquisition
- Ignoring acquisition probability when modelling initial order value will give bias estimates (sample selection bias)
- Two-stage modelling addresses the selection bias problem




