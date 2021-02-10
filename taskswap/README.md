Simulation/implementation of paper from Northwestern University by Hanlin Wang and Michael Rubenstein. The link can be found here: http://users.eecs.northwestern.edu/~mrubenst/tro20a.pdf

Because I didn't have the capability to simulate asynchronously, I instead made the simplification that each robot executes 
fairly close in time to one another. As such, I loop through the agents at each time step. Other than that, the same assumptions
are made in the paper as in the algorithm; namely 4 directions of movement and only local communications with neighbors. 

I have several changes in mind I would like to play with as well. Stay tuned for more updates!