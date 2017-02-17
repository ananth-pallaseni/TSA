import numpy as np 


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

def param_len_gene_reg(num_edges):
	""" Returns the length of the parameter list required for dX based on the number of edges the target has.
	"""
	num_params = 0
	num_params += 2 # For base synth and base degradation
	num_params += 3 * num_edges # For parent interaction strength, theta and m 
	return num_params

def param_bounds_gene_reg(num_edges):
	""" Returns the bounds of the parameters that dX requires.
	"""
	s_bound = (0.1, 1)
	g_bound = (0.1, 2)
	b_bound = (0.5, 4)
	k_bound = (0.2, 3)
	m_bound = (0.7, 5)
	param_bounds = [s_bound, g_bound] + [b_bound, k_bound, m_bound] * num_edges
	return param_bounds