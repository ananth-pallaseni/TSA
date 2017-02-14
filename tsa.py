import itertools
import numpy as np 
from scipy.integrate import odeint
from scipy.optimize import minimize
import time
import platform 
import multiprocessing as mp 
from model import *


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


def find_best_models(models, target, species_vals, species_derivs, time_scale,  edge_ptypes, node_ptypes, num_best_models=10, num_restarts=5, weak_sig_thresh=1e-5):
	""" Outputs the model topologies for a certain target that produce data close to its "true" values. 

		Performs gradient matching on each model to find parameters that produce gradient values that are closest to to those in species_derivs.

		Args: 
		models - An iterator containing all the possible model topologies in the form (dX, param_len, bounds, top). See the generate_models function for more details 

		target - The target species the models are for (eg. species 0)

		species_derivs - The "true" values of all species derivatives for all time steps. Should be a numpy array such that species_derivs[t, s] is the derivative of species s at time t. 

		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

		edge_ptypes - A list of ParameterType objects representing types of parameters attached to edges

		node_ptypes - A list of ParameterType objects representing types of parameters attached to nodes

		num_best_models - The number of best_performing models to retain. 

		num_restarts - The number of times we restart the optimization function to avoid local optima

		weak_sig_thresh - The threshold below which any parameter is considered to be spurious

		Returns:
		A list of the of length num_best_models containing the models that closest matched the "true" values in the form (topology, dX, optimal_parameters, distance_from_true_vals).
	"""
	best = []
	target_derivs = species_derivs[:, target]

	# Iterate through all models in the list
	for (dX, param_len, bounds, top) in models:
		# Calculate objective function 
		obj = objective_fn(dX, species_vals, target_derivs, top, time_scale)

		min_AIC = 1e12
		best_params = []
		best_dist = 1e12

		# Random restarts 
		for rr in range(num_restarts):

			# Randomly initiate starting values 
			param_list = top.to_param_lst(self, edge_ptypes, node_ptypes)
			param_list = list(map(lambda x:x.value, param_list)) 

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

			if AIC < min_AIC:
				min_AIC = AIC
				best_params = opt_params
				best_dist = dist 

		# Create TargetModel using best parameters and AIC 
		model_details = model_details = TargetModel(topology=top,
													params=best_params,
													dist=best_dist,
													AIC=min_AIC)

		# Check if any parameter is below the weak signal threshold
		weakest_param = min(best_params, key=lambda x:abs(x))
		if abs(weakest_param) < weak_sig_thresh:
			continue
		
		if len(best) < num_best_models:
			best.append(model_details)
		else:
			# Find the index and AIC of the worst model we have stored
			biggest_ind, biggest_item = max(enumerate(best), key=lambda x:x[1].AIC)
			biggest_AIC = biggest_item.AIC

			# If the AIC of this model is less than the AIC of the worst model, replace the worst with this
			if AIC < biggest_AIC:
				best[biggest_ind] = model_details

	# Sort the list of best models
	best = sorted(best, key=lambda x: x.AIC)

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

def whole_model_to_ode(topology_fn, topologies, params):
	""" Converts from a list of topologies to a function that computes the derivative of the whole model.

		Args:
		topology_fn -  A function that converts from a topology and specie values to a function, dX, that outputs the value of a species' derivatives

		topologies - A list of Topology objects representing the parental structure of each species 

		params - A list such that params[i] is the ist of parameters for topology i 

		Returns:
		A function that calculates the derivatives of every species in the model given their values and the time t.
	"""
	num_species = len(topologies)
	def fn(x, t):
		derivs = [0 for i in range(num_species)]
		for i in range(num_species):
			top = topologies[i]
			pars = params[i]
			derivs[i] = topology_fn(x, t, top, pars)
		return derivs 
	return fn 

def fit_whole_model(models, topology_fn, initial_values, true_vals, time_scale):
	""" Fits the parameters of every model in the models to match true_vals.

		Args:
		models - A list of models 

		topology_fn -  A function that converts from a topology and specie values to a function, dX, that outputs the value of a species' derivatives

		initial_values - The starting values of the system 

		true_vals - The values to fit to 

		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

		Returns:
		A list containing every model in models, but refit to match the values in true_vals. Sorted in order of increasing distance from the true_vals.
	"""
	results = []
	cnt = 0
	ts = np.linspace(time_scale[0], time_scale[1], time_scale[2])
	t_start = time.time()
	for m in models:
		print("cnt={}".format(cnt))
		if cnt % 10 == 0:
			t_end = time.time()
			print("batch={}, took {} seconds".format(cnt//10, t_end-t_start))
			t_start = time.time()
		cnt += 1
		topologies = [tup[0] for tup in m]
		initial_guess = sum([list(tup[3]) for tup in m], [])
		param_lens = [tup[2] for tup in m]
		bounds = sum([list(tup[6]) for tup in m], [])
		
		def whole_model_obj(params):
			ode = whole_model_to_ode(topology_fn, topologies, params, param_lens)
			sim_vals = odeint(ode, initial_values, ts)
			dist = np.linalg.norm(sim_vals-true_vals)
			return dist 


		res = minimize(whole_model_obj, initial_guess, method="SLSQP", bounds=bounds)
		opt_params = res.x 
		opt_dist = whole_model_obj(opt_params)
		results.append((m, opt_params, opt_dist))

	return sorted(results, key=lambda x: x[2])[:100]

def model_dist(model, topology_fn, initial_values, true_vals, time_scale):
	""" Checks the distance of all the input models from the true_vals.

		Args: 
		model - An array of TargetModel objects

		topology_fn -  A function that converts from a topology and specie values to a function, dX, that outputs the value of a species' derivatives

		initial_values - The starting values of the system

		true_vals - The values to compare against 

		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

		Returns:
		A sorted list of the models in ascending order of distace from the true_vals 
	"""
	ts = np.linspace(time_scale[0], time_scale[1], time_scale[2])
	topologies = [tup.topology for tup in model]
	params = [tup.params for tup in model]
	ode = whole_model_to_ode(topology_fn, topologies, params)
	sim_vals = odeint(ode, initial_values, ts)
	dist = np.linalg.norm(sim_vals-true_vals)
	return dist 

def model_dist_par(tup):
	""" Does the same as the model_dist fuction but exists to facilitate parallelization.
		Returns the model and the dist in a tuple
	"""
	model, topology_fn, initial_values, true_vals, time_scale = tup 
	return model, model_dist(model, topology_fn, initial_values, true_vals, time_scale)

def whole_model_check(models, topology_fn, initial_values, true_vals, time_scale):
	""" Checks the distance of all the input models from the true_vals.

		Args: 
		models - An array of TargetModel objects

		topology_fn -  A function that converts from a topology and specie values to a function, dX, that outputs the value of a species' derivatives

		initial_values - The starting values of the system

		true_vals - The values to compare against 

		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

		Returns:
		A sorted list of the models in ascending order of distace from the true_vals 
	"""
	results = []
	num = len(models)
	i=0
	for m in models:
		dist = model_dist(m, topology_fn, initial_values, true_vals, time_scale)
		results.append((m, dist))
		i += 1
		print('Done {:.1%}\r'.format(i / num), end='')
	return sorted(results, key=lambda x: x[1])

def whole_model_check_par(models, topology_fn, initial_values, true_vals, time_scale, processes=4):
	""" Checks the distance of all the input models from the true_vals. Parallelized

		Args: 
		models - A list of models 

		topology_fn -  A function that converts from a topology and specie values to a function, dX, that outputs the value of a species' derivatives

		initial_values - The starting values of the system

		true_vals - The values to compare against 

		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

		processes - The number of processes to parallelize across 

		Returns:
		A sorted list of the models in ascending order of distace from the true_vals 
	"""	
	pool = mp.Pool(processes=processes)
	args = map(lambda m: (m, topology_fn, initial_values, true_vals, time_scale), models)
	num = len(models)
	results = []
	for i, _ in enumerate(pool.imap(model_dist_par, args) , 1):
		print('Done {:.1%}\r'.format(i/num), end='')
	return sorted(results, key=lambda x: x[1])



def TSA(topology_fn, param_len_fn, bounds_fn, parameter_fn, accepted_model_fn, time_scale, initial_vals, num_nodes=-1, max_parents=-1, num_interactions=-1, max_order=-1, enf_edges=[], enf_gaps=[], processes=None):
	""" Perform Topological Sensitivity Analysis on a given representation of a model space.

		Args:
		topology_fn -  A function that converts from a topology and specie values to a function, dX, that outputs the value of a species' derivatives

		param_len_fn - A function that returns the number of parameters the topology function requires in its parameter list

		bounds_fn - A function that returns the bounds of the parameters in the parameter list for the topology function.

		parameter_fn - A function that returns all the types of parameters the model contains

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


	# Seperate parameter types into nodes/edges
	all_params = parameter_fn()
	node_ptypes = [pt for pt in all_params if not pt.is_edge_param]
	edge_ptypes = [pt for pt in all_params if pt.is_edge_param]

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

	print("Starting gradient matching ... ", end='')
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
								edge_ptypes= ,
								node_ptypes= ,
								num_best_models=5,
								num_restarts=1)

		best_target_models.append(best)
	print('Done')

	print("Creating Whole Models ... ", end='')
	# Generate list of best ensemble models, taking all permutations of the best topologies for each target that we found. 
	system_models = permute_whole_models(best_target_models)
	system_models = list(system_models)
	print('Done')


	# Resimulate each ensemble model and reorder based on distace from our accepted model
	best_whole_models = []
	if platform.system() != 'Windows':
		if processes is None:
			num_procs = 8
		else:
			num_procs = processes
		print("Running simple integrity check on generated whole models.\nMultiprocessing enabled, using {} processes".format(num_procs))
		mp_start = time.time()
		mp_best_models = whole_model_check_par(system_models, topology_fn, initial_vals, species_vals, time_scale, processes=num_procs)
		print('Time taken = {} seconds'.format(time.time() - mp_start))
		best_whole_models = mp_best_models
	else:
		if processes is not None:
			print("Process count is set, but cannot run multiprocessing on Windows machines. Proceeding without parallelization")
		print("Running simple integrity check on generated whole models")
		est_start = time.time()
		est_best_models = whole_model_check(system_models, topology_fn, initial_vals, species_vals, time_scale)
		print('Time taken = {} seconds'.format(time.time() - est_start))
		best_whole_models = est_best_models
	

	# Convert to WholeModel format for future analysis

	return best_whole_models
	


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

def visulize(whole_model):
	tops = [t[0] for t in whole_model[0]]
	n, e, et = parse_topology(tops)
	graph = to_graph(n, e, et)
	vis(graph)

def mosaic(whole_model_list):
	g_list = []
	for i in range(9):
		whole_model = whole_model_list[i][0]
		tops = [t[0] for t in whole_model]
		n, e, et = parse_topology(tops)
		graph = to_graph(n, e, et) 
		g_list.append(graph)

	colors = dict(enumerate(color_choices))
	for j in range(len(g_list)):
		g = g_list[j]
		plt.subplot(3,3,j+1)
		clist = [colors[g[n1][n2]['type']] for (n1, n2) in g.edges()]
		nx.draw_circular(g, with_labels=True, edge_color=clist)
	plt.tight_layout()
	plt.show()
	plt.clf()







