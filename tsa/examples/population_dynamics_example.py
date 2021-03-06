import tsa 
from tsa.models.population_dynamics import dX_pop_dynamics_fn, params_pop_dynamics
import numpy as np

r = [0.3, 0.7, 0.5, 0.4, 0.4]
a = [0.4, 0.7, 1.5, 1.4, 0.7, 1.2]

def accepted_model_fn(y,t):
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

nodes =  {0: 'Species 0', 
          1: 'Species 1', 
          2: 'Species 2', 
          3: 'Species 3', 
          4: 'Species 4'}

y0 = [0.2, 0.5, 0.2, 0.2, 0.3]
time_scale = [0,10,40]

# Perform tsa on the model space
candidate_models = tsa.generate_models(topology_fn=dX_pop_dynamics_fn,
                           parameter_fn=params_pop_dynamics,
						   nodes=nodes,
						   max_parents=max_parents,
						   accepted_model_fn=accepted_model_fn,
						   time_scale=time_scale,
						   initial_vals=y0,
						   retained_top=5,
                           restarts=1)

tsa.store_json(candidate_models, 'pop_dynamics.json')