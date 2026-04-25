
# How does dynamic scoring differ from traditional application and behavioral scoring?
- In dynamic scoring, datasets consist of multiple lines per customer or account, and risk assessments are provided for multiple time horizons into the future (e.g., 3, 4, 5, 6, or 12 months), rather than a single fixed time horizon.

# What is the difference between the survivor function and the hazard function?
- The survivor function evaluates the probability of an account surviving (not defaulting) beyond a specific time, focusing on not failing. The hazard function is the instantaneous rate at which a default event occurs given survival up to that time, focusing on the event of failing.

# What is the difference between a Conditional PD and a Marginal PD?
- A Conditional PD (also called a discrete hazard rate) is the probability that an account will default in the very next time period, given that it has not defaulted up to the current point in time. A Marginal PD represents the unconditional probability of defaulting in a specific future time period, taking into account the entire survival distribution.

# How is the Expected Credit Loss (ECL) mathematically calculated under IFRS 9?
- The expected cash shortfall is calculated by aggregating the Probability of Default (PD), Loss Given Default (LGD), and Exposure at Default (EAD) over a specified time period, discounted by an effective interest rate. 

# What is the fundamental difference between the Basel framework and IFRS 9?
- The Basel framework focuses on regulatory capital meant to absorb unexpected losses, utilizing a "through the cycle" Probability of Default (PD). IFRS 9 is an accounting standard focusing on provisions for expected losses, utilizing a forward-looking, "point in time" PD.

# What dictates whether a 12-month ECL or a Lifetime ECL is calculated under IFRS 9?
- A loan initially sits in Stage 1, which requires a 12-month ECL. However, if the account experiences a Significant Increase in Credit Risk (SICR), it moves to Stage 2 or 3, triggering a requirement to measure the loss allowance at an amount equal to the Lifetime Expected Credit Losses.

# Why might a logistic regression model for discrete hazard rates omit a global intercept?
- When building the model (e.g., `modLR <- glm(Event ~ -1 + factor(SpellPeriod) + Inputs`), the `-1` indicates no global intercept is required because time is used as a dummy variable, allowing each individual time period to have its own specific "intercept".
