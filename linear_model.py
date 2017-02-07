import tsa
import numpy as np 


def dX_linear_fn(x, t, topology, params):
	""" Calculates the derivative of the target species at time t under a linear model.

		Args:
		x - The values of all species at time t 

		t - The time 

		topology - A Topology object describing the model currently being examined

		params - A list of params for this model 
	"""
	parents = topology.parents

	const_term = params[0]

	deriv = const_term 

	# Add contributions from each edge
	for i in range(len(parents)):
		p = parents[i]

		k = params[i + 1]   # Parent coefficient

		parent_val = x[p]   # Value of parent

		deriv += k * parent_val

	return deriv

def param_len_linear(num_edges):
	""" Returns the length of the parameter list required for dX based on the number of edges the target has.
	"""
	num_params = 0
	num_params += 1 # For constant term 
	num_params += 1 * num_edges # For parent coefficient
	return num_params

def param_bounds_linear(num_edges):
	""" Returns the bounds of the parameters that dX requires.
	"""
	const_bound = (-10, 10)   
	coef_bound = (-10, 10)   
	param_bounds = [const_bound] + [coef_bound]*num_edges 
	return param_bounds