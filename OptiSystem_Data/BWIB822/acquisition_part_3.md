# Retention 
- hint: keep, maximize, analyze
- keep customers for as long as possible 
1) these customers should be good ones who maximize profit
- retention is all about analyzing the duration or predicting
the tenure of customer relationship
## linear regression
- hint: ubiquitous, discards, identical
- linear regression is referred to as a ubiquitous model for
numeric responses
- linear regression only models on churned customers.
 This discards valuable information and thus
linear regression is not the best model.
- classification models treats all cases identically
# time-to-event data
- hint: tools
- survival analysis is the collection of tools to analyze this type of data
## Understanding time-to-event data
### definition
- hint: event, response
- Time-to-event data is data on how long it takes until some event occurs
- duration/time is the response
- probability of an event occurring at or before time t
### censoring
- hint: observation, experience, right, left, interval
- data is collected in observation window. 
Some may not experience this event by the end of window (censoring)
- censoring means we have some information about the survival time.
 these are records which haven't experienced event
- there are different types: Right, left and interval censoring
1) right censoring: end of window reached before event occurs
2) left censoring: event occurred before window began
3) interval censoring: event's timing only partially known
- Ignoring censoring is not advisable: biased results, less efficient estimation
### Distributional shape of survival data
- hint: skewed, divided, aggregated
- survival data is positively skewed
- Continuous-time survival analysis entails that time can be divided
so that no 2 subjects can experience an event at the same time
- Discrete-time survival analysis entails that units of time are 
aggregate intervals
### Survival Analysis Terminology
- hint: T,C, delta
- Let $T$ denote survival time (failure time or event time): $T \geq 0$
- Time at which the event occurs (lapse, next purchase, default)
- $T=0$ : origin (policy inception, acquisition, account opened)
- Let $C$ denote censoring time (time at which censoring occurs)
- Only $T$ or $C$ will be observed
> The following random variable is observed as the response
for survival analysis: $Y = min(T,C)$
> we want to note whether $Y$ is an event time or censoring time
- Let's denote it by $\delta$ and define it formally as:
$$
\delta=\left\{\begin{array}{cc}
1, & \text { event } \\
0, & \text { censored }
\end{array}\right.
$$

## Describing time-to-event data 
- hint: beyond
- survival function/probability is the probability of surviving beyond a time t
- $S(t)=P(T>t)=1-F(t)$
### Kaplan-Meier Survival Curve
- hint: complicates, handles
- Censoring complicates estimation of survival function $S(t)$
- Well-known estimator of the survival function: Kaplan-Meier estimator
- Handles censoring by adjusting the risk set at every step
$$
\hat{S}\left(d_k\right)=\prod_{j=1}^k \frac{r_j-q_j}{r_j}
$$
- $r_j$ : nr of observations alive just before time $d_j$ (at risk observations)
- $q_j$ : nr of observations that experienced event at time $d_j$
- $r_j-q_j$ : nr of observations survived beyond time $d_j$
- $\frac{r_j-q_j}{r_j}$ : proportion of observations alive before time $d_j$ that have survived beyond time $d_j$
- Plotting $\hat{S}\left(d_k\right)$ against time: Kaplan-Meier (KM) survival curve

## Log-rank test
- hint: compare
- compare survival curves
- ![img_1775301951358.png](/files/BWIB817/img_1775301951358.png)



# Survival modelling
- hint: instantaneous, simplified, function
- hazard rate is the probability of experiencing the event at time t. It is the instantaneous event rate of individuals that survived up until time t


- ![img_1775382949478.png](/files/BWIB822/img_1775382949478.png)

- which simplifies to 


- ![img_1775383125475.png](/files/BWIB822/img_1775383125475.png) this is the simplified version
of the hazard rate. it has a relationship with the survival function

- modelling survival data as a function of covariates relies on the hazard function ( cox proportional hazards model)
- to predict the tenure of an individual we have to model the hazard

## Continuous-time survival analysis approaches
### parametric models
- hint: known, specified, MLE
- distribution of survival time is known (assumption)
- completely specified hazard function (except for unknown parameters)
- MLE used to estimate unknown parameters.
### semi-parametric models
- hint: unknown, unspecified, flexible
- distribution of survival time is unknown (assumption)
- unspecified hazard function (can take any form. flexible)
- example of this is a cox proportional hazards model
## cox proportional hazards model
hint: 2 components
- comprises of: baseline hazard and relative risk
- the baseline hazard is the hazard function with all covariates set to 0. it is a function of $t$.
- the relative risk is the risk of customer with covariates $X_i$
### proportional hazards assumption
- hazard rates for different customers should be proportional.
proportionality should be constant over time.
![img_1775384814197.png](/files/BWIB822/img_1775384814197.png)


- hazard ratio used to interpret effect of change in
significant covariate on hazard rate

# Advantages/Disadvantages of the Cox PH Model

- Advantages:
- Does not require a particular probability distribution to represent survival times
- Relatively easy to incorporate time-dependent covariates
- Fairly robust to outliers
- Well studied and popular

- Disadvantages:
- Needs an estimate of the baseline hazard function for predictive modelling where you are not only interested in the relative effect of a covariate on the hazard rate
- Proportional hazards assumption not always valid
- Computationally expensive for big data (volume \& number of covariates) where observations are made at discrete timepoints with many ties

# model validation 
- not always straight-forward; outcome is time-
dependent and data is often censored
- use concentration curves:
> exclude customers who experienced event prior to a certain date
> apply right censoring after choosing validation interval
> assign risk score to each customer with model and sort
> hit occurs if event happens
> concentration curve visualises the percentage of hits captured within each decile of scored data.


