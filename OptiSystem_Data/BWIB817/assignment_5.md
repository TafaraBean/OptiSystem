# Worker scheduling/planning
- You have recently been employed at a company and your first task in your new role is to assist with
determining the assignment of workers to tasks.
The main activity of the company is the manufacturing of a specific product across various
machines/tasks, but your project only includes the scheduling of workers against the tasks needed to
manufacture this product i.e. the production itself is out of scope for this project.
Each task requires a specific skill set and therefore, workers can only complete tasks for which they
have undergone training (these are indicated in the tasks table as binary indicators). Additionally, each
task requires a specific number of hours to be completed and there is a “demand” for the number of
times each task must be completed in a given week.
Due to the nature of the work, some workers are not available on all days in the week (indicated in the
availability table as binary indicators for each day). Working hours are furthermore limited to a total of
8 hours per day per worker and a total of 320 hours per week for all workers.
Furthermore, workers are remunerated at varying rates, and this therefore must be taken into
consideration. Your objective is therefore to minimise the cost associated with assigning a worker to a
task(s).
In addition to the data sets given, your manager provides you with the below information:
• Workers are not permitted to complete more than one task per day.
• As the problem is a scheduling/planning problem, your manager requires a table as part of your
solution, indicating which worker was assigned to a task(s) so that the company can efficiently
plan the coming week (the output here should be for all tasks in the coming week and therefore
does not need to include which day the task should be completed).


# Index Sets
-	Tasks, availibility, workers
# Declare the data that will be used in the formulation.
-	the maximum hours per day
-	the maximum hours per week
-	the rates, per worker
-	the tasks
-	the hours per task
-	the availibility per worker
-	eligibility per task per worker matrix
# Declare the variables that need to be determined in the problem.
-	daily rates

# Declare any variables that need to be determined using decision variables.
-	task assigned per worker
# Declare any constraints needed for the problem.
-	no more than one task per worker
-	no more than 8 hours for each worker, per day
-	no more than 320 hours for each worker per week
# Objective Function
- minimise the daily rates for each worker assigned a task.




