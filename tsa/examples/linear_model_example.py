import tsa 
from tsa.models.linear_model import dX_linear_fn, params_linear
import numpy as np


s = [0.5, 0.3, 0.7, 0.4, 1,1.5];        # basal synthesis for species 1-5
g = [1, 0.3, 0.7, 1.5, 1.5, 3];         # basal degradation
b = [-1,-0.5,1.5,-0.8,-0.6,0.7,-1.5,1]  # edge coefficients

y0 = [0,0,0,0,0,0]

def accepted_model_fn(x, t):
    dx = [0 for i in range(len(x))]
    dx[0] = s[0] - g[0]*x[0] + b[0]*x[2] + b[1]*x[4]
    dx[1] = s[1] - g[1]*x[1] + b[2]*x[5]
    dx[2] = s[2] - g[2]*x[2] + b[3]*x[4]
    dx[3] = s[3] - g[3]*x[3] + b[4]*x[0]
    dx[4] = s[4] - g[4]*x[4] + b[5]*x[1]
    dx[5] = s[5] - g[5]*x[5] + b[6]*x[0] + b[7]*x[3]
    return dx

num_nodes = 6
max_parents = 3

nodes =  {0: 'Node 0', 
          1: 'Node 1', 
          2: 'Node 2', 
          3: 'Node 3', 
          4: 'Node 4',
          5: 'Node 5'}

time_scale = [0,20,51]

# Perform tsa on the model space
candidate_models = tsa.generate_models(topology_fn=dX_linear_fn,
                           parameter_fn=params_linear,
            						   nodes=nodes,
            						   max_parents=max_parents,
            						   accepted_model_fn=accepted_model_fn,
            						   time_scale=time_scale,
            						   initial_vals=y0,
                           retained_top=5,
                           restarts=1)

tsa.store_json(candidate_models, 'linear.json')
