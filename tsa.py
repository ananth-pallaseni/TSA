import itertools
import numpy as np 
from scipy.integrate import odeint
from scipy.optimize import minimize
import time

class ModelSpace():
	""" Container for the functional description and limitations of the model space
	"""
	def __init__(self, max_parents, num_interactions, num_nodes, max_order, topology_fn, param_len_fn, bounds_fn):
		self.max_parents = max_parents				
		self.num_interactions = num_interactions	# Number of possible interactions (eg: Activation, Repression etc). Not necessarily required for all models.
		self.max_order = max_order					# Max order of ODE that can result from a network in this model. Not necessarily required for all models.
		self.num_nodes = num_nodes
		self.topology_fn = topology_fn 				# A function to convert from a given topology for target X to a function for dX and the length of the parameter list that dX requires.
		self.param_len_fn = param_len_fn			# A function that takes in the number of inbound edges and returns the number of parameters required for the topology fn
		self.bounds_fn = bounds_fn					# A function that takes in the number of inbound edges and returns the bounds on each paramter in the parameter list for topology fn. 

class Topology():
	""" Container for all the parameters required to fully describe a certain topology.
	"""
	def __init__(self, target, interactions, parents, order):
		self.target = target 			 # The target species
		self.interactions = interactions # The interactions that each parent has with the target. 
		self.parents = parents 			 # The parents of the species
		self.order = order 				 # Order of equation that represents the topology

	def __str__(self):
		return 'target = {},\nparents = {},\ninteractions = {},\norder = {}\n'.format(self.target, self.parents, self.interactions, self.order)

	def __repr__(self):
		return self.__str__()

def sim_data(model_fn, time_scale, x0):
	""" Create time series data for a model by simulating it across the given time scale. 

		Args:
		model_fn - The function that takes in the value of its variables and the time and outputs the derivatives of those variables.

		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

		x0 - The initial values of the system 

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

def enumerate_perms(num_parents, interactions):
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

def generate_models(model_space, target, species_vals, enf_edges=[], enf_gaps=[]):
	""" Generate all possible network topologies concerning one target species

		Args:
		model_space - A ModelSpace object containing the dexcription of the model space 

		target - The value of the target species 

		species_vals - A numpy array containing the value of each species across all time stpes, such that species_vals[t, s] = value of species s at time t.

		enf_edges - An array of nodes that specify which nodes must be parents of this target 

		enf_gaps - An array of nodes that specify which nodes cannot be parents of this target 

		Returns:
		An iterator containing all possible network topologies in the form (dX, param_len, bounds, topology). dX is a function that takes in a list of length param_len and returns the derivatives of the target variable for the given topology. bounds specifies the lower and upper bounds for each parameter to dX, such that bounds[i] = (lower bound, upper bound) for parameter i. 
	"""
	# Check if there are more enforced edges than allowable parents
	num_enf_edges = len(enf_edges)
	if num_enf_edges > model_space.max_parents:
		# If so, then cut down the list of enforced edges until it is equal to the number of alwed parents
		print ("Warning. More enforced edges than allowed parents. Have {} enforced edges and at most {} parents".format(num_enf_edges, model_space.max_parents))
		enf_edges = enf_edges[:model_space.max_parents]
		num_enf_edges = model_space.max_parents

	enf_edges = tuple(enf_edges)

	# List out the non-enforced nodes and interactions
	nodes = [i for i in range(model_space.num_nodes) if i not in enf_gaps and i not in enf_edges]
	interactions = [i for i in range(model_space.num_interactions)]

	# How many parents?
	for num_parents in range(model_space.max_parents+1 - num_enf_edges):
		# Enumerate all non-enforced edges
		all_parent_combs = itertools.combinations(nodes, num_parents)
		
		# Add in all enforced edges
		all_parent_combs = map(lambda x: x + enf_edges, all_parent_combs)
		
		# What combination of parents (includes self interactions)?
		for parent_comb in all_parent_combs:
			all_interaction_perms = enumerate_perms(num_parents, interactions)

			# What permutation of interactions?
			for interaction_perm in all_interaction_perms:

				# What order?
				for order in range(model_space.max_order+1):
				
					topology = Topology(target=target, interactions=interaction_perm, parents=parent_comb, order=order)

					dX = model_space.topology_fn
					param_len = model_space.param_len_fn(len(topology.parents))
					bounds = model_space.bounds_fn(len(topology.parents))

					yield (dX, param_len, bounds, topology)


def objective_fn(fn, specie_vals, target_derivs, topology, time_scale):
	""" Creates an objective function that calculates the euclidean distance between the target_derivs and the output of fn for given parameters. 
		Args:
		fn - A function that takes in the value of species at time t, the time t, the topology and parameter list and outputs the derivative of x.
		A numpy array containing the value of each species across all time stpes, such that species_vals[t, s] = value of species s at time t.
		target_derivs - A numpy array containing the values against which to compare the output of fn.
		topology - A Topology object describing the model currently being examined
		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]
		
		Returns:
		A function that takes in a list of parameters and outputs the euclidean distance (L2 Norm) between fn(params) and target_derivs.
	"""
	ts = np.linspace(time_scale[0], time_scale[1], time_scale[2])
	def obj(params):
		sim = [fn(specie_vals[i], ts[i], topology, params) for i in range(len(ts))]
		return np.linalg.norm(sim-target_derivs)
	return obj


def find_best_models(models, target, species_vals, species_derivs, time_scale, num_best_models=10):
	""" Outputs the model topologies for a certain target that produce data close to its "true" values. 

		Performs gradient matching on each model to find parameters that produce gradient values that are closest to to those in species_derivs.

		Args: 
		models - An iterator containing all the possible model topologies in the form (dX, param_len, bounds, top). See the generate_models function for more details 

		target - The target species the models are for (eg. species 0)

		species_derivs - The "true" values of all species derivatives for all time steps. Should be a numpy array such that species_derivs[t, s] is the derivative of species s at time t. 

		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

		num_best_models - The number of best_performing models to retain. 

		Returns:
		A list of the of length num_best_models containing the models that closest matched the "true" values in the form (topology, dX, optimal_parameters, distance_from_true_vals).
	"""
	best = []
	target_derivs = species_derivs[:, target]

	# Iterate through all models in the list
	for (dX, param_len, bounds, top) in models:
		# Calculate objective function 
		obj = objective_fn(dX, species_vals, target_derivs, top, time_scale)

		# Randomly initiate starting values 
		param_list = [np.random.random() for i in range(param_len)]

		# Perform gradient matching to find optimal parameters
		res = minimize(obj, param_list, method='SLSQP', tol=1e-6, bounds=bounds)
		opt_params = res.x

		# Calculate the distance of best guess
		dist = obj(opt_params)

		# Calculate num time steps
		ts = species_derivs.shape[0]

		# Calculate Biased AIC for this model
		AIC_bias = 2 * (param_len + 1) * (ts / (ts - param_len))
		AIC  = ts * np.log(dist / ts) + AIC_bias


		model_details = (top, dX, param_len, opt_params, dist, AIC)

		
		if len(best) < num_best_models:
			best.append(model_details)
		else:
			# Find the index and AIC of the worst model we have stored
			biggest_ind, biggest_item = max(enumerate(best), key=lambda x:x[1][5])
			biggest_AIC = biggest_item[5]

			# If the AIC of this model is less than the AIC of the worst model, replace the worst with this
			if AIC < biggest_AIC:
				best[biggest_ind] = model_details

	# Sort the list of best models
	best = sorted(best, key=lambda x: x[5])

	return best

def permute_whole_models(best_models):
	""" Consider a list of length n where each position in the list can take one of a set of values for that position. This function finds all permutations of that list given the set of values that each position can take. 

		Args:
		best_models - A list of lists such that best_models[i] is the list of values that position i can take.

		Returns:
		A generator of all the permutations of the list. 

		Examples:
		>>> a = [ [c + str(i) for i in range(2)] for c in ['AB'] ]
		>>> all = permute_whole_models(a)
		>>> for i in all:
		...    print(i)
		('A0', 'B0')
		('A0', 'B1')
		('A1', 'B0')
		('A1', 'B1')
	"""
	num_species = len(best_models)

	def permute_helper(n, opts, lst, pos):
		if pos == n:
			yield lst 
		else:
			for i in opts[pos]:
				lst[pos] = i 
				for p in permute_helper(n, opts, lst, pos+1):
					yield p 


	lst = [-1 for i in range(num_species)]
	permutations = permute_helper(num_species, best_models, lst, 0)

	for perm in permutations:
		yield tuple(perm)
		


def TSA(topology_fn, param_len_fn, bounds_fn, accepted_model_fn, time_scale, initial_vals, num_nodes=-1, max_parents=-1, num_interactions=-1, max_order=-1, enf_edges=[], enf_gaps=[]):
	""" Perform Topological Sensitivity Analysis on a given representation of a model space.

		Args:
		topology_fn -  A function that converts from a topology and specie values to a function, dX, that outputs the value of a species' derivatives

		param_len_fn - A function that returns the number of parameters the topology function requires in its parameter list

		bounds_fn - A function that returns the bounds of the parameters in the parameter list for the topology function.

		accepted_model_fn - A function that takes in a time t and the value of all species at that time and outputs the derivatives of all species at time t. 

		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

		initial_vals - The initial values for all species. Should be a numpy array such that initial_vals[s] is the starting value of species s.

		num_nodes - The number of nodes/species that exist in the system

		max_parents - The maximum number of parents that any node in the system can have

		num_interactions - The number of different interactions that nodes can have (eg activation or repression for gene regulation)

		max_order - The maximum order of term that any expression can have in the system

		enf_edges - A list of edge tuples for edges that must be present in all models 

		enf_gaps - A list of edge tuples for edges that must not be present in any models 

		Returns:
		The top models that fit closest the "true" values for each species. 
	"""
	# Check for built in functions:
	fn_module = topology_fn.__module__
	if fn_module == 'gene_regulation' :
		num_interactions = 2
		max_order = 0 
	elif fn_module == 'population_dynamics':
		num_interactions = 1
		max_order = 0
	elif fn_module == 'linear_model':
		num_interactions = 1
		max_order = 0



	# Create Model Space
	model_space = ModelSpace(num_nodes=num_nodes, 
							 max_parents=max_parents,
							 num_interactions=num_interactions,
							 max_order=max_order,
							 topology_fn=topology_fn,
							 param_len_fn=param_len_fn,
							 bounds_fn=bounds_fn)



	# Simulate the 'true' values of the species and their derivatives from the accepted model. 
	# We use these values as the 'truth' against which to compare our candidate models
	species_vals, species_derivs = sim_data(accepted_model_fn, time_scale, initial_vals)

	# Specify the list of possible target species
	targets = [i for i in range(model_space.num_nodes)]

	# Parse the list of enforced edges:
	enf_edges_target = [ [] for i in range(num_nodes) ]
	enf_gaps_target = [ [] for i in range(num_nodes) ]
	for (p, t) in enf_edges:
		enf_edges_target[t].append(p)
	for (p, t) in enf_gaps:
		enf_gaps_target[t].append(p)

	best_target_models = []

	print("Starting gradient matching")
	for t in targets:
		# Generate all possible permutations of topologies involving the target
		models = generate_models(model_space=model_space, 
								 target=t,
								 species_vals=species_vals,
								 enf_edges=enf_edges_target[t],
								 enf_gaps=enf_gaps_target[t])

		# Perform gradient matching on each candidate model and obtain the closest matches to our 'true' data
		best = find_best_models(models=models,
								target=t,
								species_vals=species_vals,
								species_derivs=species_derivs,
								time_scale=time_scale,
								num_best_models=5)

		best_target_models.append(best)


	print("Creating Whole Models")
	# Generate list of best ensemble models, taking all permutations of the best topologies for each target that we found. 
	system_models = permute_whole_models(best_target_models)



	return system_models
		





import matplotlib.pyplot as plt
import networkx as nx

def parse_topology(topology_lst):
	nodes = [i for i in range(len(topology_lst))]
	edges = []
	edge_type = []
	for top in topology_lst:
		target = top.target
		parents = top.parents
		interactions = top.interactions 

		for i in range(len(parents)):
			p = parents[i]
			inter = interactions[i]
			edges.append( (p, target) )
			edge_type.append( inter )

	return nodes, edges, edge_type

def to_graph(nodes, edges, edge_types):
	g = nx.DiGraph()
	g.add_nodes_from(nodes)
	for i in range(len(edges)):
		start, end = edges[i]
		g.add_edge(start, end)
		g[start][end]['type'] = edge_types[i]

	return g 


color_choices = ['r', 'g', 'b', 'y', 'black', 'grey']
def vis(g):
	colors = dict(enumerate(color_choices))
	clist = [colors[g[n1][n2]['type']] for (n1, n2) in g.edges()]
	nx.draw(g, with_labels=True, edge_color=clist)
	plt.show()
	plt.clf()








