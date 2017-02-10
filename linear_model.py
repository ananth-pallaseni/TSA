from model import *
import numpy as np 


# Define parameters
const = ParameterType(param_type='CONST', bounds=(-10, 10), is_edge_param=False)
coeff = ParameterType(param_type='COEFF', bounds=(-10, 10), is_edge_param=True)

def dX_linear_fn(x, t, topology, params):
	""" Calculates the derivative of the target species at time t under a linear model.

		Args:
		x - The values of all species at time t 

		t - The time 

		topology - A Topology object describing the model currently being examined

		params - A list of parameters for this model 
	"""
	parents = topology.parents
	target = topology.target

	const_term = params[0]

	deriv = const_term 

	# Add contributions from each edge
	for i in range(len(parents)):
		p = parents[i]

		k = params[i + 1]   # Parent coefficient

		parent_val = x[p]   # Value of parent

		deriv += k * parent_val

	return deriv

def params_linear():
	return [const, coeff]


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