# Concept statement

- investigate the feasibility of designing a centralised system which will assist border authorities to screen motorists using real time scan triggered queries across multipl data sources with the chief aim of reducing the number of stolen vehicles crossing the norder

# Agenda

# Motivation

## Origin
- there is a high volume of vehicles at the border whch causes a lot of friction
- Client was requested to look into possible solutions on behalf of Momentum
- insight from Momentum combined with his personal experience at the border to formulate a new system or the border 
- which is a framework for screening vehicles and their owners in an automated fashion

## statistics

- in 2005, interpol reported that 96% to 98% of stolen vehicles circulating the SADC region are sourced from South Africa 
- More recent statistics from 2025 appear to support this statistic
- every 22 minutes a car is stolen in south africa 
- 30% of all stolen vehicles are destined for neighbouring countries
- domestic recovery rates are 70% to 95% but drop to 30% when a car crosses the border
- in fiscal terms, approximately R4.9B was lost due to cross-border smuggling in 2025

## impact on financial institutions 

- South Africa contributes 70% of the total insurance premium payments in Africa
- yet only 30% of motorists have insured vehicles 
- this disparity points to the fact that premiums have gotten so expensive that motorists would rather risk their car being stolen than paying a premium. 
- insurance companies are losing out on potential customers because of the cross-border vehicle smuggling. 

## Current system 

- we have identified that the primary factors contributing to this issue is fragmented departments and the lack of a unified database

- migrants arrive at the border with prepared documents 
- they present them at different offices which they have to visit sequentially 
- at each stage an officer manually crosschecks 
- this process can be tedious and inefficient 
- the BMA was established as a way to address this issue, marginally improving the coordination between the offices but it does not qualify as a unified database 
- a unified database was also proposed, NaVISS, a system which would combine data from different sources to improve the screening process. no updates have been released on it 
- The client has proposed a system which is very similar to this. 

## Proposed Client system

- a system which will query a database through a scan trigger 
- this database is composed of multiple data sources
- instead of visiting multiple different offices, a migrant can be screened at a single point 
- the results would be sent to the border officer for validation

## Considerations

- the amount of data to be collected can be difficult to pool into a single database 
- the question becomes whether such a system is even possible since NaVISS is yet to make any progress
- we have to consider that the nature of the stakeholder data is sensitive and may be difficult to obtain
- the infrastructure to build a server for such data may be lagging at the border
- the way the data may be collected at different firms/companies/departments may not be consistent
- the process of validation may differ at different borders or different vehicle types
- the aim is now to determine whether the system is technically feasible
- and whether a functional framework is obtainable 

# The scope 

- we address the fragmented nature of the border posts 
- the lack of a unified database
- the limited cross- jurisdictional cooperation
- the uncertainty of whether a system like this would be feasible

# The objectives 

## Design phase 

- construct a conceptul architecture framework 
- this will be in the form of an ERD

## Demonstration phase 

- a prototype will be built so that the client can present it to investors

## evaluation phase

- a report on challenges, mitigations and instructions relating to how to construct the database will be compiled. 

# The approach


## The design phase 

- we identify the tables (data sources) and the relationships which exist between them
- we do this by finding similar variables in the tables 
- once these relationships are found, we create an ERD of the tables by mapping the corresponding tables together.
- we clearly define what the validation logic will be. these are the structured approaches we use to identify possibly stolen vehicles
- additional features will include a GUI to display results and other insightful stats such as

## Demonstration phase

- once a sound conceptual ERD is established along the validation logic
- we implement it practically by creating the tables and their relationships 
- the prototype would allow for a user to scan a QR code which would then be sent to a live database for automatic querying, following the initially defined validation logic.
- the results would then be displayed to the officer who would then accept or deny passage 

## Evaluation phase 

- we detail the data handling challenges we face such as data harmonisation
- we assess the latency of each query and how we would expect it to behave on an institutional level. what kind of hardware would be needed. 
- how the validation logic can be defined 
- if it is possiblt to pull data of a migrant across multiple data sources simultaneously 
- instructions on how to integrate APIs of their own to fetch sensitive data from custom databases

# Delivarables 
- the ERD
- the prototype
- detailed instruction manual

# Fees 

this project will be free but would have costed this much based on the billable hours 

# Assumptions and conditions 

- We assume that the client would provide the necessary data 
- all the necessary software will be installed on user's computer

- the conditions are that the proposal should be accepted before the end of march 
- no further assistance will be provided beyond the project-closeout meeting


# Risks 

- data availibility and quality 
- key person depency risk 
- scaling and volume assumption risk 
- resource and infrastructure risk 

# Measures of success 

- lean towards on the tangible system as it will be of most value to the client 
- we don't disregard the documentation as we need to ensure that the steps within are replicatable. 

# Summary 

# Questions
