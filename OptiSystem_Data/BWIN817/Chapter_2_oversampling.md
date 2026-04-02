# Objectives 

## ![img_1771281249.png](/files/BWIN817/img_1771281249.png)

### What is oversampling?

#### Our aim is to oversample the rare event

#### This is done for data efficiency purposes

#### 
- ![img_1771281423.png](/files/BWIN817/img_1771281423.png)

### Joint sampling vs. separate sampling

#### ![img_1771281658.png](/files/BWIN817/img_1771281658.png)

##### Bernoulli ML assumes a independent bernoulli distribution of $y_i$   

##### This assumption is appropriate for joint sampling but not for separate sampling

##### separate sampling offsets the intercept term $B_0$ 

###### to correct this we have to fit the pseudo model: 


- ![img_1771339713.png](/files/BWIN817/img_1771339713.png)
- where $p^*$ is the posterior probability corresponding to the biased sample
- When rare events have been oversampled $\pi_0$ > $p_0$ and $\pi_1$ < $p_1$, the offset is positive
- this means that our new dataset has more observations of the rare target events and less of the non-target events
- alternatively we could apply the offset after the standard model is fitted 
- ![img_1771340490.png](/files/BWIN817/img_1771340490.png)
- $\widehat{p^*_i}$ is the unadjusted posterior probability. we subtract the offset from it.


###### correcting the offset using proc logistic 

- ![img_1771341281.png](/files/BWIN817/img_1771341281.png)

# Code snippets 


- ![img_1772331067.png](/files/BWIN817/img_1772331067.png)