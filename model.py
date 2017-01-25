import itertools
import numpy as np 
import math
from scipy.integrate import odeint

class TargetTopology():
	""" Contains all information required to define a certain topology for a target species
	"""

	def __init__(self, target, interactions, parents, order):
		self.target = target 					 # The target species
		self.interactions = interactions # The interactions that each parent has with the target. 
		self.parents = parents
		self.order = order 

	def __getitem__(self, key):
		if type(key) != int or type(key) != str:
			raise TypeError
		if key == 0 or key == "target":
			return self.target
		elif key == 1 or key == "parents":
			return self.parents
		elif key == 2 or key == "interactions":
			return self.interactions
		elif key == 3 or key == "order":
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

	def __init__(self, max_parents, num_interactions=1, num_nodes=-1, max_order=0, time_scale=[], fn=[], accepted_model_fn=[]):
		self.max_parents = max_parents				
		self.num_interactions = num_interactions	# Number of possible interactions (eg: Activation, Repression etc). Not necessarily required for all models.
		self.max_order = max_order					# Max order of ODE that can result from a network in this model. Not necessarily required for all models.
		self.num_nodes = num_nodes
		self.time_scale = time_scale				# The time scale to simulate across. Should have the form [start, stop, num_steps]
		self.target_topology_to_function = fn 		# A function to convert from a given topology for target X to a function for dX and the length of the parameter list that dX requires.
		self.accepted_model_fn = accepted_model_fn 	# The accepted model for your system. Should be a function that takes in the values of your species and the time and outputs an array of derivatives. 

	def sim_data(self, model_fn, time_scale, x0=[]):
		""" Create time series data for a model by simulating it across the given time scale. 

			Args:
			model_fn - The function that takes in the value of its variables and the time and outputs the derivatives of those variables.

			time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

			Returns:
			A numpy array of the value of each species derivatives in the model at all time steps. Rows are time steps, columns are species such that specie_vals[t, s] = value of derivative of species s at time t. 
		"""

		# Create time scale array
		ts = np.linspace(time_scale[0], time_scale[1], time_scale[2])

		# Simulate the value of species across the time scale
		specie_vals = np.ndarray.astype(odeint(model_fn, x0, ts), float)

		# Calculate derivatives of the species
		specie_derivs = np.zeros(specie_vals.shape, dtype=float)
		for step in range(len(ts)):
			specie_derivs[step, :] = model_fn(specie_vals[step, :], ts[step])

		return specie_vals, specie_derivs


	def __enumerate_inter_perms(self, num_parents, interactions):
		""" Generates an iterator of all possible ways of having `num_parents species interact with the target, with the possible interactions in `interactions.
		"""
		def perms(length, options, lst):
			if length == 0:
				yield lst 
			else:
				for i in options:
					lst[length-1] = i
					for p in perms(length-1, options, lst):
						yield p
		perm_list = perms(length=num_parents, options=interactions, lst=[-1 for i in range(num_parents)])
		for i in perm_list:
			yield tuple(i)



	def generate_models(self, target, true_data):
		""" Generate all possible network topologies concerning one certain target species
		"""
		nodes = [i for i in range(self.num_nodes)]
		interactions = [i for i in range(self.num_interactions)]

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
						
						target_topology = TargetTopology(target=target, interactions=interaction_perm, parents=parent_comb, order=order)

						dX, params, bounds = self.target_topology_to_function(topology=target_topology, specie_vals=true_data)

						yield (dX, params, bounds, target_topology)


	def objective_fn(self, top_fn, target, true_data):

		def obj(params):
			sim = top_fn(params)
			true = true_data[:, target]
			diff = sim - true 
			return math.sqrt(sum(diff**2))
			
		return obj



	def __str__(self):
		return self.__class__.__name__


		
		







				