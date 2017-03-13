import numpy as np 
from tsa import ParameterType

# Define parameters
param_growth_rate = ParameterType(param_type='Growth Rate', bounds=(0.1, 1), is_edge_param=False)
param_inter_strength = ParameterType(param_type='Interaction Strength', bounds=(0.1, 2), is_edge_param=True)


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


def params_pop_dynamics():
	return [param_growth_rate, param_inter_strength]
