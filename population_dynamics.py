import tsa
import numpy as np 

def population_dynamics_fn(topology, specie_vals):
	""" Converts the topology of a network into an ODE representing a population dunamics network for the target species X. 

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

		growth_rate = params[0]

		growth_term = growth_rate * specie_vals[:, target_species]
		strength_term = 1 - specie_vals[:, target_species]

		# Add contributions from each edge
		for i in range(len(parents)):
			p = parents[i]

			s = params[i + 1]   # Interaction Strength

			# Value of parent for all t
			parent_vals = specie_vals[:, p]

			strength_term -= s * parent_vals

		dX = growth_term * strength_term
		
		return dX

	# Enumerate the length of the parameter list that dX requires
	param_len = 1 + len(parents)   # [growth_rate] + [interaction strength] for each parent

	growth_bound = (0.1, 1)
	strength_bound = (0.1, 2)

	param_bounds = [growth_bound]   # Basal synth, basal degr
	for i in parents:
		param_bounds += [strength_bound]

	return dX, param_len, param_bounds

