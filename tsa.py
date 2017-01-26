import itertools
import numpy as np 
from scipy.integrate import odeint
from scipy.optimize import minimize

class ModelSpace():
	""" Container for the functional description and limitations of the model space
	"""
	def __init__(self, max_parents, num_interactions, num_nodes, max_order, topology_fn):
		self.max_parents = max_parents				
		self.num_interactions = num_interactions	# Number of possible interactions (eg: Activation, Repression etc). Not necessarily required for all models.
		self.max_order = max_order					# Max order of ODE that can result from a network in this model. Not necessarily required for all models.
		self.num_nodes = num_nodes
		self.topology_fn = topology_fn 				# A function to convert from a given topology for target X to a function for dX and the length of the parameter list that dX requires.

class Topology():
	""" Container for all the parameters required to fully describe a certain topology.
	"""
	def __init__(self, target, interactions, parents, order):
		self.target = target 			 # The target species
		self.interactions = interactions # The interactions that each parent has with the target. 
		self.parents = parents 			 # The parents of the species
		self.order = order 				 # Order of equation that represents the topology

	def __str__(self):
		return 'target = {},\nparents = {},\ninteractions = {},\norder = {}'.format(self.target, self.parents, self.interactions, self.order)

	def __repr__(self):
		return self.__str__()

def sim_data(model_fn, time_scale, x0):
	""" Create time series data for a model by simulating it across the given time scale. 

		Args:
		model_fn - The function that takes in the value of its variables and the time and outputs the derivatives of those variables.

		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

		Returns:
		A numpy array of each species values and another numpy aray of each species derivatives. In both cases rows are time steps, columns are species such that specie_derviates[t, s] = value of derivative of species s at time t. 
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


def generate_models(model_space, target, species_vals):
	""" Generate all possible network topologies concerning one target species

		Args:
		model_space - A ModelSpace object containing the dexcription of the model space 

		target - The value of the target species 

		species_vals - A numpy array containing the value of each species across all time stpes, such that species_vals[t, s] = value of species s at time t.

		Returns:
		An iterator containing all possible network topologies in the form (dX, param_len, bounds, topology). dX is a function that takes in a list of length param_len and returns the derivatives of the target variable for the given topology. bounds specifies the lower and upper bounds for each parameter to dX, such that bounds[i] = (lower bound, upper bound) for parameter i. 
	"""
	
	def enumerate_inter_perms(num_parents, interactions):
		""" Generates all possible ways of having `num_parents species interact with the target, with the possible interactions in `interactions.

			Examples:
			>>> e = enumerate_inter_perms(3, [0,1])
			>>> for perm in e:
			...    print(perm)
			(0, 0, 0)
			(1, 0, 0)
			(0, 1, 0)
			(1, 1, 0)
			(0, 0, 1)
			(1, 0, 1)
			(0, 1, 1)
			(1, 1, 1)
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

	# List out the nodes and interactions
	nodes = [i for i in range(model_space.num_nodes)]
	interactions = [i for i in range(model_space.num_interactions)]

	# How many parents?
	for num_parents in range(1, model_space.max_parents+1):
		all_parent_combs = itertools.combinations(nodes, num_parents)

		# What combination of parents (includes self interactions)?
		for parent_comb in all_parent_combs:
			all_interaction_perms = enumerate_inter_perms(num_parents, interactions)

			# What permutation of interactions?
			for interaction_perm in all_interaction_perms:

				# What order?
				for order in range(model_space.max_order+1):
				
					topology = Topology(target=target, interactions=interaction_perm, parents=parent_comb, order=order)

					dX, param_len, bounds = model_space.topology_fn(topology=topology, specie_vals=species_vals)

					yield (dX, param_len, bounds, topology)


def objective_fn(fn, true_vals):
	""" Creates an objective function that calculates the euclidean distance between the true_vals and the output of fn for given parameters. 

		Args:
		fn - A function that takes in a parameter list and outputs a numpy array 

		true_vals - A numpy array containing the values against which to compare the output of fn.

		Returns:
		A function that takes in a list of parameters and outputs the euclidean distance (L2 Norm) between fn(params) and true_vals.

		Examples:
		>>> fn = lambda x: np.arange(10) * x[0] + x[1]
		>>> true_vals = np.arange(10)
		>>> obj = objective_fn(fn, true_vals)
		>>> params = [1, 0]
		>>> obj(params)
		0
		>>> params = [2, 1]
		>>> obj(params)
		19.621416870348583
	"""
	def obj(params):
		sim = fn(params)
		return np.linalg.norm(sim-true_vals)
	return obj

def find_best_models(models, target, species_derivs, num_best_models=10):
	""" Outputs the model topologies for a certain target that produce data close to its "true" values. 

		Performs gradient matching on each model to find parameters that produce gradient values that are closest to to those in species_derivs.

		Args: 
		models - An iterator containing all the possible model topologies in the form (dX, param_len, bounds, top). See the generate_models function for more details 

		target - The target species the models are for (eg. species 0)

		species_derivs - The "true" values of all species derivatives for all time steps. Should be a numpy array such that species_derivs[t, s] is the derivative of species s at time t. 

		num_best_models - The number of best_performing models to retain. 

		Returns:
		A list of the of length num_best_models containing the models that closest matched the "true" values in the form (topology, dX, optimal_parameters, distance_from_true_vals).
	"""
	best = []
	target_derivs = species_derivs[:, target]

	# Iterate through all models in the list
	for (dX, param_len, bounds, top) in models:
		# Calculate objective function 
		obj = objective_fn(dX, target_derivs)

		# Randomly initiate starting values 
		rnd = np.random.random()
		param_list = [rnd for i in range(param_len)]

		# Perform gradient matching to find optimal parameters
		res = minimize(obj, param_list, method='SLSQP', tol=1e-6, bounds=bounds)
		opt_params = res.x

		# Calculate the distance of best guess
		dist = obj(opt_params)

		model_details = (top, dX, param_len, opt_params, dist)

		
		if len(best) < num_best_models:
			best.append(model_details)
		else:
			# Find the index and distance of the worst model we have stored
			biggest_ind, biggest_item = max(enumerate(best), key=lambda x:x[1][4])
			biggest_dist = biggest_item[4]

			# If the distance of this model is less than the distance of the worst model, replace the worst with this
			if dist < biggest_dist:
				best[biggest_ind] = model_details

	# Sort the list of best models
	best = sorted(best, key=lambda x: x[4])

	return best


def TSA(model_space, accepted_model_fn, time_scale, initial_vals):
	""" Perform Topological Sensitivity Analysis on a given representation of a model space.

		Args:
		model_space -  A ModelSpace object containing the dexcription of the model space 

		accepted_model_fn - A function that takes in a time t and the value of all species at that time and outputs the derivatives of all species at time t. 

		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

		initial_vals - The initial values for all species. Should be a numpy array such that initial_vals[s] is the starting value of species s.

		Returns:
		The top models that fit closest the "true" values for each species. 
	"""
	# Simulate the 'true' values of the species and their derivatives from the accepted model. 
	# We use these values as the 'truth' against which to compare our candidate models
	species_vals, species_derivs = sim_data(accepted_model_fn, time_scale, initial_vals)

	# Specify the list of possible target species
	targets = [i for i in range(model_space.num_nodes)]

	best_models = []

	for t in targets:
		# Generate all possible permutations of topologies involving the target
		models = generate_models(model_space=model_space, 
								 target=t,
								 species_vals=species_vals)

		# Perform gradient matching on each candidate model and obtain the closest matches to our 'true' data
		best = find_best_models(models=models,
								target=t,
								species_derivs=species_derivs,
								num_best_models=10)

		best_models.append(best)

	return best_models








