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

ll = tsa.load_json('linear.json')

top1000 = ll.top(1000)

node_ptypes = [p for p in params_linear() if not p.is_edge_param]
edge_ptypes = [p for p in params_linear() if p.is_edge_param]


species_vals, species_derivs = tsa.sim_data(accepted_model_fn, time_scale, y0)

rr = tsa.fit_whole_model(top1000, dX_linear_fn, y0, species_vals, time_scale, node_ptypes, edge_ptypes)

rrmb = ll.from_wm_list(rr)

tsa.store_json(rrmb, 'lin_refit.json')