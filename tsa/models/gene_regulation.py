import numpy as np 
from tsa import ParameterType

# Define parameters
param_basal_synth = ParameterType(param_type='Basal Synth', bounds=(0.1, 1), is_edge_param=False)
param_basal_degr = ParameterType(param_type='Basal Degr', bounds=(0.1, 2), is_edge_param=False)
param_strength = ParameterType(param_type='Strength', bounds=(0.5, 4), is_edge_param=True)
param_theta = ParameterType(param_type='Theta', bounds=(0.2, 3), is_edge_param=True)
param_hill_coeff = ParameterType(param_type='Hill Coeff', bounds=(0.7, 5), is_edge_param=True)



def dX_gene_reg_fn(x, t, topology, params):
	""" Calculates the derivative of the target species at time t under a gene regulation model.

		Args:
		x - The values of all species at time t 

		t - The time 

		topology - A Topology object describing the model currently being examined

		params - A list of params for this model 
	"""
	parents = topology.parents
	target = topology.target
	interactions = topology.interactions

	base_synth = params[0]
	base_degr = params[1]

	# Add basal synthesis and basal degradation terms
	dX = base_synth - x[target] * base_degr

	# Add contributions from each edge
	for i in range(len(parents)):
		p = parents[i]
		inter = interactions[i]

		j = 2 + i*3
		b = params[ j ] 	  # Interaction 'Strength'
		k = params[ j + 1 ]   # Hill fn parameter (theta)
		m = params[ j + 2 ]   # Hill fn parameter (m)

		# Value of parent for all t
		parent_val = x[p]

		if inter == 0:
			dX += (b * parent_val**m) / (parent_val**m + k**m)
		elif inter == 1:
			dX += b / (1 + (parent_val/k)**m)
	
	return dX

def params_gene_reg():
	return [param_basal_synth, param_basal_degr, param_strength, param_theta, param_hill_coeff]