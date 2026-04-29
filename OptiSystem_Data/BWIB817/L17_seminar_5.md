# What are some issues ?
- **something must be wrong** with the methods described in this chapter. specifically, an issue of **dependent observations** because they are created from a single observation. 
this would **violate the basic assumption** used to create the **likelihood function**.
The **proportional hazards** model results are very **similar** to the **standard logistic regression** provided that the likelihood function is **factored for the data**.
the records in **person-period** data needs to only assume **conditional independence**. each time period is treated as a separate, independent observation.
Other issues are Handling large numbers of observations, Unequal intervals, Empty intervals, Left truncations, Competing risks

# How can we handle large numbers of observations?
- ![img_1777327785919.png](/files/BWIN817/img_1777327785919.png)

# How can we handle unequal intervals?

- rarely a case in the financial area because intervals are usually monthly, quarterly or yearly

# How can we handle empty intervals?
- fit a model with restrictions on the time effect (quadratic functions)
# How can we handle left truncations?
- delete time periods where individuals aren't usually at risk. 
this can severely limit the smaple size.
# How can we handle competing risks?
- These are events which **happen for before the event of interest**.
in credit risk, an early settlement would affect the PD-term structure. 
we can address this by modelling a **multinomial logit model**.

# How do we do model validation for time-dependent outcomes?
- validation is not straightforward because of **time dependency** and **censoring** of available data.
We cannot use the Proc Logistic ROC becuase it incorporates all **time periods**

# how do we measure ranking and accuracy for time dependent outcomes?

- Ranking (discrimination) is measured through a time-dependent ROC
Accuracy (calibration) is measured through a time-dependent brier score

# How do we handle multiple defaults?
- add an indicator for each spell.

![img_1777339333761.png](/files/BWIB817/img_1777339333761.png)

# what is the difference between the LR used in scorecards and this LR used in discrete hazard?
- discrete hazard models enable the **estimation of the probability of default
for future time periods** given the individual has not defaulted.

# How do we forecast application, behavioral and macroeconomic variables?
- application variables: don't pose a significant challenge. they are stable over short horizons
macroeconomic variables: forecasts can be sourced from internal economic forecasts or external macroeconomic forecasts
behavioural variables: forecasted using a naive method or using simple time-based models
![img_1777339587478.png](/files/BWIB817/img_1777339587478.png)


# what are the benefits of using discrete hazard rates for IFRS 9 PD modelling?
- Enables the use of logistic regression, a well-established and widely understood technique within
banks. 
- Facilitates direct inclusion of standard predictor categories, such as application variables, behavioural variables, and macroeconomic variables.
- Eliminates the need for separate macroeconomic scenario modelling (e.g. scalars), as discrete-time
hazard models can accommodate both time-static and time-varying covariates, including
macroeconomic indicators.
- Offers practical advantages over continuous-time models, particularly in handling right-censoring
and tied event times, which are common in real-world credit datasets.




