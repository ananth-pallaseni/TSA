import tsa 
from population_dynamics import dX_pop_dynamics_fn, param_len_pop_dynamics, param_bounds_pop_dynamics
import numpy as np


def accepted_model_fn(y,t):
	r = [0.3, 0.7, 0.5, 0.4, 0.4]
	a = [0.4, 0.7, 1.5, 1.4, 0.7, 1.2]

    # competitive Lotka-Volterra model.  5 species, model B.  
	dy = np.zeros(5)
	dy[0] = (r[0]*y[0])*(1 - y[0] - a[0]*y[2] - a[1]*y[4])
	dy[1] = (r[1]*y[1])*(1 - y[1] - a[2]*y[3])
	dy[2] = (r[2]*y[2])*(1 - y[2])
	dy[3] = (r[3]*y[3])*(1 - y[3] - a[3]*y[1] - a[4]*y[2])
	dy[4] = (r[4]*y[4])*(1 - y[4] - a[5]*y[1])
	return dy

num_nodes = 5
max_parents = 3 

y0 = [0.2, 0.5, 0.2, 0.2, 0.3]
time_scale = [0,10,40]

# Perform tsa on the model space
candidate_models = tsa.TSA(topology_fn=dX_pop_dynamics_fn,
                           param_len_fn=param_len_pop_dynamics,
                           bounds_fn=param_bounds_pop_dynamics,
						   num_nodes=num_nodes,
						   max_parents=max_parents,
						   accepted_model_fn=accepted_model_fn,
						   time_scale=time_scale,
						   initial_vals=y0)