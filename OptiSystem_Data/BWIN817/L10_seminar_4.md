# Risk scorecard development and implementation
## 7 stages
- understanding, prep, mod, eval, implementation

### stage 1: preliminaries and planning
- business need, viability, plan
- business plan priorities and role of scorecard
- internal and external development
- sufficient data, generic/custom scorecards, cost constraint, volume constraint, judgement based adjudication model
- group characteristics, intuition,
- project plan, scope, seamless transition, connected processes, reliant on data, risks, show stoppers
- identify team

#### scorecard format 
- interpretation
- easy explanation in business terms
- not black box, transparent
- easy diagnosis and monitoring
- no in-depth knowledge needed to perform functions.

### stage 2: Data Review and Project Parameters (feasible)
#### exclusions
- ![img_1775613984995.png](/files/BWIN817/img_1775613984995.png)
 ![img_1775614019214.png](/files/BWIN817/img_1775614019214.png)
- day-to-day operations, sample bias

#### performance/sample windows
-  ![img_1775614169498.png](/files/BWIN817/img_1775614169498.png)
 past predict future, time frame
- ![img_1775614248152.png](/files/BWIN817/img_1775614248152.png)
new accounts opened, analysed, performance window, monitored, sample window, development
- ![img_1775614740405.png](/files/BWIN817/img_1775614740405.png)
![img_1775614791194.png](/files/BWIN817/img_1775614791194.png)
![img_1775615067807.png](/files/BWIN817/img_1775615067807.png)
development, stable, matured, minimize misclassification, varies, behavioral scorecard 
repeated analysis for delinquency definitions, ever bad, anytime,  current bad, recent

#### definition of bad 

- ![img_1775615396218.png](/files/BWIN817/img_1775615396218.png)

![img_1775615539147.png](/files/BWIN817/img_1775615539147.png)

![img_1775615593746.png](/files/BWIN817/img_1775615593746.png)

categorize, different sample count, considerations, profitability, purposes, differentiation
- ![img_1775635702273.png](/files/BWIN817/img_1775635702273.png)

![img_1775635766252.png](/files/BWIN817/img_1775635766252.png)

![img_1775637047191.png](/files/BWIN817/img_1775637047191.png)


consensus method, analytical method, roll rate analysis, current vs worst, profitability analysis

- segmentation used to identify subpopulations

#### Feature Engineering and Data Preparation
- end goal, dataset, target sample, strong features, combine
- diff timestamp, data leakage, target leakage
- application/behavioral scorecard (purpose, data input, typical output)
- snapshot/videoclip

### stage 3: database creation
- ![img_1775637434568.png](/files/BWIN817/img_1775637434568.png)

![img_1775637698702.png](/files/BWIN817/img_1775637698702.png)

needs business thought, preselect features, predictive power, reliability, ease in collection, interpretability, human intervention, leagal issues, interpretable ratios

- ![img_1775638011182.png](/files/BWIN817/img_1775638011182.png)
development, validation, proportion of goods/bads, adjust for oversampling, large sample,  proportional sampling, statistical techniques

- prior prob correction