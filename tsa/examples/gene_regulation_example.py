# An example formulation of a 5 species gene regulation network where
# each species can activate or inhibit the others. 
#
# The species are 1, 2, 3, 4, 5 
#
# The network is as follows:
# 1 activates 2, 3 and 4
# 2 inhibits 5
# 3 inhibits 4 
# 4 activates 5
# 5 activates 1

import tsa 
from tsa.models.gene_regulation import dX_gene_reg_fn, params_gene_reg
import numpy as np

# Parameters for our gene regulation network:
num_nodes = 5
max_parents = 2 
time_scale = [0, 10, 31]
initial_vals = np.array([1, 0.5, 1, 1.5, 0.5])

s = [0.2, 0.2, 0.2, 0.2, 0.2];      # basal synthesis for species 1-5
g = [0.9, 0.9, 0.7, 1.5, 1.5];      # basal degradation
b = [2, 2, 2, 2, 2, 2, 2];          # interaction 'strength' (beta_nk)
k = [1.5, 1.5, 1.5, 1.5, 1.5];      # hill fn parameter (theta_nk)
m = [5, 5, 5, 5, 5];                # hill fn parameter (m_nk)

# Define the accepted model
def accepted_model_fn(x, t):
	dx = [0 for i in range(len(x))]
	dx[0] = s[0] - g[0]*x[0] + b[0]*(x[4]**m[4])/(x[4]**m[4] + k[4]**m[4]);
	dx[1] = s[1] - g[1]*x[1] + b[1]*(x[0]**m[0])/(x[0]**m[0] + k[0]**m[0]);	
	dx[2] = s[2] - g[2]*x[2] + b[2]*(x[0]**m[0])/(x[0]**m[0] + k[0]**m[0]);	
	dx[3] = s[3] - g[3]*x[3] + b[3]*(x[0]**m[0])/(x[0]**m[0] + k[0]**m[0]) + b[5]/(1 + (x[2]/k[2])**m[2]);	
	dx[4] = s[4] - g[4]*x[4] + b[4]*(x[3]**m[3])/(x[3]**m[3] + k[3]**m[3]) + b[6]/(1 + (x[1]/k[1])**m[1]);
	return dx


# Perform tsa on the model space
candidate_models = tsa.generate_models(topology_fn=dX_gene_reg_fn,
                           parameter_fn=params_gene_reg,
						   num_nodes=num_nodes,
						   max_parents=max_parents,
						   accepted_model_fn=accepted_model_fn,
						   time_scale=time_scale,
						   initial_vals=initial_vals)

tsa.store_json(candidate_models, 'gene_reg.json')