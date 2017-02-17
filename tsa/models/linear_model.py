import numpy as np 
from tsa import ParameterType

# Define parameters
const = ParameterType(param_type='CONST', bounds=(-10, 10), is_edge_param=False)
coeff = ParameterType(param_type='COEFF', bounds=(-10, 10), is_edge_param=True)


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

def params_linear():
	return [const, coeff]
