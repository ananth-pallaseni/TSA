import itertools
import numpy

class TargetTopology():
	""" Contains all information required to define a certain topology for a target species
	"""

	def __init__(self, target=0, interaction_perm=[], parents=[], order=0):
		self.target = target 					 # The target species
		self.interactions = interactions # The interactions that each parent has with the target. 
		self.parents = parents
		self.order = order 

	def __getitem__(self, key):
		if type(key) != int or type(key) != str:
			raise TypeError
		if key == 0 || key == "target":
			return self.target
		elif key == 1 || key == "parents":
			return self.parents
		elif key == 2 || key == "interactions":
			return self.interactions
		elif key == 3 || key == "order":
			return self.order
		else:
			raise IndexError

	def __str__(self):
		return "Parents=" + str(self.parents) + "\n" \
			   "Interactions=" + str(self.interactions) + "\n" \
			   "Order=" + str(self.order)

	def __repr__(self):
		return self.__str__()


class Model():
	""" Container for the functional description and limitations of the model set.
	"""

	def __init__(self, max_parents, num_interactions=1, num_nodes, max_order=0, time_scale, fn, accepted_topology):
		self.max_parents = max_parents				
		self.num_interactions = num_interactions	# Number of possible interactions (eg: Activation, Repression etc). Not necessarily required for all models.
		self.max_order = max_order					# Max order of ODE that can result from a network in this model. Not necessarily required for all models.
		self.num_nodes = num_nodes
		self.time_scale = time_scale				# The time scale to simulate across. Should have the form [start, stop, step]
		self.target_topology_to_function = fn 		# A function to convert from a given topology for target X to a function for dX and the length of the parameter list that dX requires.
		self.accepted_topology = accepted_topology 	# The accepted topology for your model. Should be a list of TargetTopology objects, one for each species.

	def create_time_series(self, topology=self.accepted_topology, time_scale=self.time_scale):
		""" Create time series data for a model by simulating it across the given time scale. 

			Args:
			topology - The topology of the entire model. Should be a list of TargetTopology objects, one for each species.

			time_scale - The time scale to simulate across. Should have the form [start, stop, step]

			Returns:
			A numpy array of the value of each species in the model at all time steps. Rows are time steps, columns are species such that specie_vals[t, s] = value of species s at time t. 
		"""
		pass



	def __enumerate_inter_perms(self, num_parents=3, interactions=[1,2]):
		""" Generates an iterator of all possible ways of having `num_parents interact with the target, with the possible interactions in `interactions.
		"""
		def perms(length, options, lst):
			if length == 0:
				yield lst 
			else:
				for i in options:
					lst[length-1] = i
					for p in perms(length-1, options, lst):
						yield p
		return perms(length=num_parents, options=interactions, lst=[-1 for i in range(num_parents)])



	def generate_models(self, target, true_data):
		""" Generate all possible network topologies concerning one certain target species
		"""
		nodes = [i for i in range(num_nodes)]
		interactions = [i for i in range(num_interactions)]

		# How many parents?
		for num_parents in range(1, self.max_parents+1):
			all_parent_combs = itertools.combinations(nodes, num_parents)

			# What combination of parents (includes self interactions)?
			for parent_comb in all_parent_combs:
				all_interaction_perms = self.__enumerate_inter_perms(num_parents, interactions)

				# What permutation of interactions?
				for interaction_perm in all_interaction_perms:

					# What order?
					for order in range(self.max_order+1):
					
						target_topology = Topology(target=target, interaction_perm=interaction_perm, parent_comb=parent_comb, order=order)

						dX, params = self.target_topology_to_function(topology=target_topology, specie_vals=true_data)

						yield (dX, params)

	def __str__(self):
		return self.__class__.__name__

		
		







				