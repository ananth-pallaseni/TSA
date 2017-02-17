import numpy as np 



def dX_pop_dynamics_fn(x, t, topology, params):
	""" Calculates the derivative of the target species at time t under a population dynamics model.

		Args:
		x - The values of all species at time t 

		t - The time 

		topology - A Topology object describing the model currently being examined

		params - A list of params for this model 
	"""
	parents = topology.parents
	target = topology.target

	growth_rate = params[0]
	growth_term = growth_rate * x[target]
	strength_term = 1 - x[target]

	# Add contributions from each edge
	for i in range(len(parents)):
		p = parents[i]
		s = params[i + 1]   # Interaction Strength
		parent_vals = x[p]
		strength_term -= s * parent_vals

	dX = growth_term * strength_term

	return dX

	
def param_len_pop_dynamics(num_edges):
	""" Returns the length of the parameter list required for dX based on the number of edges the target has.
	"""
	num_params = 0
	num_params += 1 # For growth rate  
	num_params += 1 * num_edges # For parent interaction strengths
	return num_params

def param_bounds_pop_dynamics(num_edges):
	""" Returns the bounds of the parameters that dX requires.
	"""
	growth_bound = (0.1, 1)
	strength_bound = (0.1, 2)
	param_bounds = [growth_bound] + [strength_bound] * num_edges 
	return param_bounds

