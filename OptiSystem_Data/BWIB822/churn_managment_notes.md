
# What is the definition and focus of churn management?

* At the customer level, churn is defined as the probability that a customer leaves in a given period.


* At the firm level, it is the proportion of the customer base that leaves in a given period.


* The churn rate ($c$) is defined mathematically as $1$ minus the retention rate ($1-r$).



# Why is managing churn financially important?

* A lower churn rate leads to a longer expected customer lifetime. the expected customer lifetime represents how long a customer stays with the company.


* Decreasing the churn rate results in a higher Customer Lifetime Value (LTV) and a higher Return on Investment (ROI).


* When accounting for a continuous margin ($m$), discount rate ($\delta$), and churn rate ($c$), the lifetime value equation simplifies to $LTV=\frac{m(1+\delta)}{(\delta+c)}$.



# What are the two main types of customer churn?

* 
**Involuntary churn:** Occurs when the company decides to terminate the relationship with the customer.


* 
**Voluntary churn:** Occurs when the customer decides to terminate the relationship with the company.


* Voluntary churn can be further categorized as deliberate (e.g., the customer is dissatisfied or received a better offer) or incidental (e.g., the customer moved or no longer needs the product).



# What factors cause or alleviate customer churn?

* 
**Customer Satisfaction:** Service quality, fitting the customer's needs, meeting expectations, and appropriate pricing impact satisfaction.


* 
**Switching Costs:** Low physical switching costs (real inconveniences) and low psychological switching costs (inertia, brand pull, familiarity) increase the probability of churn.

low switching costs results in higher churn probabilities.


* 
**Customer Characteristics:** Risk takers, variety seekers, shopping mavens, deal-prone individuals, and lower-income customers generally have a **higher likelihood of churning**. Married, rural, and higher-income customers have a **lower likelihood of churning**.


* 
**Marketing Efforts:** Special services, customized products, loyalty programs, promotions, and matching customers to the right price plans decrease churn.

*
**Competition:** within category and between category.



# What predictive models are used in proactive churn management?

*
the key theme in Proactive churn management is identifying customers likely to churn. but sometimes there is no data on the causes of churn, no pyschographic data while there is competitive activity we have to stay mindful of.

We are usually limited to behavioural measures, retention efforts, customer complaints, offers extended to the customer and price information.

* 
**Single future period models:** These models aim to **predict the probability of a customer churning** in a specific upcoming period (like the next month or 3 months) using predictors collected **before the target "churn period"**.


* 
**Time series models (Survival models):** These observe predictors and churn simultaneously as they occur from period to period to **track duration**, predict hazard/risk, and **understand why and when a customer is likely to churn**. The aim is to underestand the difference between customers that have churned and customers that haven't left yet.



# How does the AFT model function?

* The AFT model is a parametric alternative to the Cox Proportional Hazard model that **examines the effects of predictors on event times** in censored data regression.
specifically it aims to find how changes in the drivers of customer duration affect the customer duration.


* It models the natural log of a customer's duration (log-normal distribution) using the formula $ln(Duration_{i})=X_{i}^{\prime}\beta+\sigma\epsilon_{i}$.


* It is used to determine drivers of customer churn, predict the expected duration of customers yet to leave, and determine predictive accuracy.



# How do predictive thresholds and intervention costs interact in single future period models?

* If a bank has a high-value customer (high balance and generates significant monthly interest) **predicted to stay** (a **false negative**), but the customer **actually churns**, the bank misses the chance to save them and takes a **huge financial hit**. To prevent this, banks might lower the predictive threshold and **accept more false positives** (offering lower rates/incentives to customers who might have stayed anyway).


* The threshold for taking action is directly proportional to the cost of the intervention. Every time a customer swipes a credit card, the bank collects a fee which makes it possible to reduce the threshold.


* If an **intervention generates offset revenue**—such as a "spend and get" promotion that incurs **interchange fees** from merchants—the **cost is very low**, meaning the bank can comfortably lower its threshold to target more customers, **accepting more false positives**.

* in the case of a "lost wallet share" we can perform such a threshold adjustment.



# What are the managerial approaches to reducing churn?

* 
**Untargeted approaches:** Broad strategies intended to increase overall customer satisfaction and switching costs through better products, advertising, or loyalty programs.


* 
**Targeted approaches:** Specific attempts to rescue customers identified as likely to churn.


* The **two types of targeted approaches**:
**Reactive targeted management:** Waiting for customers to identify themselves as a flight risk, such as when they call to cancel their service. While targeting is perfect, **large incentives can be very costly** and may train customers to threaten cancellation for better deals. However it can afford significant incentives.


* 
**Proactive targeted management:** Using advanced models to identify likely churners, diagnose their reasons, and take **preventative action** before they decide to leave.



# What are the main trade-offs associated with proactive churn management?

* Organizations must **balance the predictive accuracy** of their models **with the actual effectiveness** of the offers they make.


* There is a **risk of wasting money** on offers made to non-churners (false positives).


* Proactive outreach might **accidentally stimulate satisfied customers** into realizing they have options and considering churning.



# How does the profitability framework quantify proactive churn management?

* The profitability framework calculates whether a proposed **offer** will result in **increased revenue**, or **how much should be offered** to meet a specific ROI goal.


* it allows us to calculate the optimal incentive value.
