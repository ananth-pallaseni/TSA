import tsa 
from tsa.models.mass_action import dX_massact_fn, params_massact
import numpy as np



def accepted_model_fn(x, t):
  dx = [0 for i in range(len(x))]
  dx[0] = 1.6 - 2*x[0] + 1.5*x[2]*x[3]
  dx[1] = 4 - 3*x[1] - 2*x[3]*x[0]
  dx[2] = 3 - 1*x[2] - .5*x[4]*x[1] + x[1]
  dx[3] = 4 - 3*x[3] + 1.5*x[0]*x[1] - x[0]
  dx[4] = 3 - 1*x[4] - 2*x[1]*x[3]
  return dx

x0=[0, 1.5, 1, 3, 2]

num_nodes = 5
max_parents = 3 

nodes =  {0: 'Molecule 0', 
          1: 'Molecule 1', 
          2: 'Molecule 2', 
          3: 'Molecule 3', 
          4: 'Molecule 4'}

time_scale = [0,2,51]

# Perform tsa on the model space
candidate_models = tsa.generate_models(topology_fn=dX_massact_fn,
                           parameter_fn=params_massact,
						   nodes=nodes,
						   max_parents=max_parents,
               max_order=2,
               num_interactions=1,
						   accepted_model_fn=accepted_model_fn,
						   time_scale=time_scale,
						   initial_vals=x0)

tsa.store_json(candidate_models, 'mass_action.json')
