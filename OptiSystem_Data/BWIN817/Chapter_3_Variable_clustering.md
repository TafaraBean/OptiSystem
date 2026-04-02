# Variable clustering

- finds groups of variables which are as correlated as possible among themselves and uncorrelated as possible with variables in other clusters
- a common strategy is to choose a single variable from each cluster based on subject matter knowledge

## Redundant inputs

- redundancy is an unsupervised concept 
- it does not include the target variable

### degrades the analysis

- **destabilizing** the parameter **estimates** 
- increase the risk of **overfitting **
- confounding interpretation
- increasing **computation** time 
- increasing scoring **effort** 
- increasing the **cost** of data collection and augmentation


### relevancy

-  takes into account the association between the input variable and target

### drawback of high dimensional data 

- detecting irrelevant inputs is more difficult than identifying redundant inputs

### a good strategy 

- first reduce redundancy and then tackle irrelevancy in a lower dimensional space

## Principal components

- weighted linear combinations of predictor variables where the weights are chosen to account for the largest amount of variation in the data

- variable clustering is based on principal components
- ordered according to how much variation in the data is accounted for
- accounts for a unique portion of the variation in the data (they are not correlated)

### total variation 

- the sum of sample variances of the prdictor variables

### Constraints

- constraints are imposed on the on the sum of squared weights for each principal component
- the sum of squared weights must be equal to 1

### the correlation matrix

- the covariance matrix of the standardized variables
- each standardized variable has a variance equal to one
- hence total variability is just the number of variables
- Principal compnents are produced from the eigen-decomposition of the correlation matrix


### eigenvalues 
- the variances of Principal components
- the sum of the eigenvalues is the number of variables


### use-case for principal component analysis

- reducing redundant dimensions
- a set of k predictors can be transformed into a set of k principal components
- we'd then keep the first few PCs if they explain a sufficient proportion of the total variation
- the reduced set could then be used in place of the original variables 

## Advantage of Variable clustering over PC

- the chief advantage of variable clustering over PCs is the coefficients
- the coefficients for PC are usually non-zero for the original variables
- even if a few PCs were used, all of the original variables would still need to be retained in the analysis.

## Divisive Clustering
- this is the algorithm for variable clustering
- variable clustering finds groups of variables that are as correlated as possible among themselves and uncorrelated as possible to variables in other clusters
- the basic algorithm is binary and divisive

### the algorithm

- 1. all variables start in one cluster and then principal component analysis is done to all variables in the cluster.
- 2. if the second eigenvalue is above a certain threshold then we split the cluster
- 3. PC scores are rotated obliquely so that the cluster can be split
- 4. this process is repeated for the 2 child clusters until the second eigenvalue falls below the threshold

### larger thresholds
- larger thresholds for the second eigenvalue give fewer clusters and less variation is explained
- smaller thresholds give more clusters and more variation is explained

### common choice of thresholds

- 1. average size of the eigenvalue
- 0.7 accounts for sampling variability

## Cluster representative

- dimension reduction could be achieved by replacing the original variables with cluster scores. (sounds complex)
- a simple alternative is to use representative variable from each cluster
- ideal representative variables have high correlations with their own clusters and low correlations with other clusters
- Thesse are the variables with the lowest 1-$R^2$ ratios in each cluster.

- ![img_1772139181.png](/files/BWIN817/img_1772139181.png)

# Code snippets


- ![img_1772332963.png](/files/BWIN817/img_1772332963.png)


- ![img_1772333007.png](/files/BWIN817/img_1772333007.png)

