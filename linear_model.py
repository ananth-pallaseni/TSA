import tsa
import numpy as np 

def linear_model_fn(topology, specie_vals):
	""" Converts the topology of a network into an ODE representing a linear model for the target species X. 

		Args:
		topology - A TargetTopology object. Contains the exact network description
		specie_vals - A numpy array of the value of each species in the model at all time steps. Rows are time steps, columns are species such that specie_vals[t, s] = value of species s at time t. 

		Returns: 
		A tuple containing the function that calculates the value of dX and also the length of the param list it takes.
	"""
	target_species = topology.target
	parents = topology.parents
	
	def dX(params):
		""" Calculates the value of dX at all time steps, where X is the target species we are considering. 

			Args:
			params - A list of parameters that this model requires t calculate dX. In this case, it takes the form [basal synth for target, basal degr for target] + [b, k, m] for each parent.
		"""
		target_vals = specie_vals[:, target_species]   # Value of target for all t

		const_term = params[0]

		dX = const_term 

		# Add contributions from each edge
		for i in range(len(parents)):
			p = parents[i]

			k = params[i + 1]   # Parent coefficient

			parent_vals = specie_vals[:, p]   # Value of parent for all t

			dX += k * parent_vals
		
		return dX

	# Enumerate the length of the parameter list that dX requires
	param_len = 1 + len(parents)   # [constant] + [parent coeff] for each parent

	# Specify the bounds for each parameter:
	const_bound = (-1e12, 1e12)   # unbounded
	coef_bound = (-1e12, 1e12)   # unbounded
	param_bounds = [const_bound] + [coef_bound]*len(parents) 

	return dX, param_len, param_bounds

