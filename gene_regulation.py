from tsa import ModelSpace
import numpy as np 

def gene_regulation_fn(topology, specie_vals):
	""" Converts the topology of a network into an ODE representing the gene regulation for the target species X. 

		Args:
		topology - A TargetTopology object. Contains the exact network description
		specie_vals - A numpy array of the value of each species in the model at all time steps. Rows are time steps, columns are species such that specie_vals[t, s] = value of species s at time t. 

		Returns: 
		A tuple containing the function that calculates the value of dX and also the length of the param list it takes.
	"""
	target_species = topology.target
	parents = topology.parents
	interactions = topology.interactions
	
	def dX(params):
		""" Calculates the value of dX at all time steps, where X is the target species we are considering. 

			Args:
			params - A list of parameters that this model requires t calculate dX. In this case, it takes the form [basal synth for target, basal degr for target] + [b, k, m] for each parent.
		"""

		base_synth = params[0]
		base_degr = params[1]

		# Add basal synthesis and basal degradation terms
		dX = base_synth - specie_vals[:, target_species] * base_degr


		# Add contributions from each edge
		for i in range(len(parents)):
			p = parents[i]
			inter = interactions[i]

			j = 2 + i*3
			b = params[ j ] 	  # Interaction 'Strength'
			k = params[ j + 1 ]   # Hill fn parameter (theta)
			m = params[ j + 2 ]   # Hill fn parameter (m)

			# Value of parent for all t
			parent_vals = specie_vals[:, p]

			if inter == 0:
				dX += (b * parent_vals**m) / (parent_vals**m + k**m)
			elif inter == 1:
				dX += b / (1 + (parent_vals/k)**m)
		
		return dX

	# Enumerate the length of the parameter list that dX requires
	param_len = 2 + 3*len(parents)   # [base_synth, base_degr] + [b, k, m] for each parent

	# Specify the bounds for each parameter:
	s_bound = (0.1, 1)
	g_bound = (0.1, 2)
	b_bound = (0.5, 4)
	k_bound = (0.2, 3)
	m_bound = (0.7, 5)
	param_bounds = [s_bound, g_bound] + [b_bound, k_bound, m_bound] * len(parents)

	return dX, param_len, param_bounds




class GeneRegulationModel(ModelSpace):
	"""Specifies the form and limits of a model based on Gene Regualation networks
	"""

	def __init__(self, max_parents, num_nodes):
		# Invoke the parent constructor with specific values
		super(GeneRegulationModel, self).__init__(
			max_parents=max_parents,
			num_nodes=num_nodes,
			num_interactions = 2,   # Edges can either Activate or Repress
			max_order=0,   			# Order not used in this model
			topology_fn=gene_regulation_fn   # Using function specific to gene regulation networks (based on hill-kinetics)
			)
