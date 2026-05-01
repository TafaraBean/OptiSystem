# What is a person-period data set and why is it necessary?
- A **person-period** data set converts data from having one line per person to having **multiple lines per person**, with one line for **each time period** observed.

- This format manipulation is required because **discrete event history data must be structured this way** to analyze it using standard logistic regression software.

# How is a discrete-time hazard defined?
- It is the conditional **probability** that a randomly selected individual will **experience the target event in a specific time period**.

- This calculation is based on the condition that the individual **did not already experience the target event** prior to that specific time period.

# What is the difference between left censoring and left truncation?
- **Left censoring** means the event of interest already **happened before the observation window** started, but the exact timing is unknown.

- **Left truncation** means you only observe accounts that enter the dataset **after surviving a certain period**, meaning any early defaults are missing from the data entirely.

# What is right censoring?
- Right censoring occurs when an account **reaches the end** of the observation or workout period **without** ever **experiencing** the **event** of interest.

# What is the difference between static and dynamic variables?
- **Static variables** **do not vary** over time and are typically used in **cross-sectional datasets**.

- **Dynamic variables change** over time and are tracked using **panel or longitudinal datasets**.


