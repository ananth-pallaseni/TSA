import itertools
import numpy as np 
from scipy.integrate import odeint
from scipy.optimize import minimize
import time
import platform 
import multiprocessing as mp 
from .model import *

import pickle
import json
import math
import sys

def sim_data(model_fn, time_scale, x0):
	""" Create time series data for a model by simulating it across the given time scale. 

		Args:
		model_fn - The function that takes in the value of its variables and the time and outputs the derivatives of those variables.

		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

		x0 - The initial values of the system 

		Returns:
		A tuple of numpy array. The first is each species values and the second is each species derivatives. In both cases rows are time steps, columns are species such that specie_vals[t, s] = value of species s at time t and specie_derivatives[t, s] = value of derivative of species s at time t. 
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

def generate_target_topologies(model_space, target, enf_edges=[], enf_gaps=[]):
	""" Generate all possible network topologies concerning one target species

		Args:
		model_space - A ModelSpace object containing the description of the model space 

		target - The id of the target species (must be an integer > 0)

		enf_edges - An array of nodes that specify which nodes must be parents of this target 

		enf_gaps - An array of nodes that specify which nodes cannot be parents of this target 

		Returns:
		An iterator containing all possible network topologies in the form (dX, topology). 
		dX is a function that takes in a list of parameters and returns the derivatives of the target variable for the given topology. topology is a Topology object specifying the structure of this part of the graph.
	"""
	# Check if there are more enforced edges than allowable parents
	num_enf_edges = len(enf_edges)
	if num_enf_edges > model_space.max_parents:
		# If so, then cut down the list of enforced edges until it is equal to the number of alwed parents
		print ("Warning. More enforced edges than allowed parents. Have {} enforced edges and at most {} parents".format(num_enf_edges, model_space.max_parents))
		enf_edges = enf_edges[:model_space.max_parents]
		num_enf_edges = model_space.max_parents

	# Put all enforced nodes in tuple form for next steps
	enf_edges = tuple([tuple([e]) for e in enf_edges])
	enf_gaps = tuple([tuple([e]) for e in enf_gaps])
	
	# List out the nodes that are not enforced gaps 
	nodes = [(i) for i in range(model_space.num_nodes) if i not in enf_gaps]
	
	# Generate a list of interactomes based on order
	max_order = model_space.max_order
	interactomes = [itertools.combinations(nodes, i) for i in range(1, max_order+1)]
	interactomes = [map(lambda x: x[0] if len(x)==1 else x, i) for i in interactomes] # Makes it so that non-complex interactomes are represented as ints, while complex ones are tuples (eg: (1) becomes 1, but (1,2) stays the same)
	interactomes = itertools.chain(*tuple(interactomes))

	# Remove enforced nodes so that they can be added in later:
	interactomes = filter(lambda x: x not in enf_edges, interactomes)

	interactomes = list(interactomes)

	# List out interactions
	interactions = [i for i in range(model_space.num_interactions)]

	# How many parents?
	for num_parents in range(model_space.max_parents+1 - num_enf_edges):
		# Enumerate all non-enforced edges
		all_parent_combs = itertools.combinations(interactomes, num_parents)
		
		# Add in all enforced edges
		all_parent_combs = map(lambda x: x + enf_edges, all_parent_combs)
		
		# What combination of parents (includes self interactions)?
		for parent_comb in all_parent_combs:
			all_interaction_perms = enumerate_perms(num_parents, interactions)

			# What permutation of interactions?
			for interaction_perm in all_interaction_perms:
				topology = Topology(target=target, interactions=interaction_perm, parents=parent_comb)

				dX = model_space.topology_fn

				yield (dX, topology)


def objective_fn(fn, specie_vals, target_derivs, topology, time_scale):
	""" Creates an objective function that calculates the euclidean distance between the target_derivs and the output of fn for given parameters. 
		
		Args:
		fn - A function that takes in the value of species at time t, the time t, the topology and parameter list and outputs the derivative of x.
		
		specie_vals - A numpy array containing the value of each species across all time steps, such that species_vals[t, s] = value of species s at time t.
		
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


def gradient_match_topologies(models, target, species_vals, species_derivs, time_scale,  edge_ptypes, node_ptypes, num_best_models=10, num_restarts=5, weak_sig_thresh=1e-5):
	""" Outputs the model topologies for a target species that produce data closest to its "true" values. 

		Performs gradient matching on each model to find parameters that produce gradient values that are closest to to those in species_derivs.

		Args: 
		models - An iterator containing model topologies in the form (dX, topology). See the generate_target_topologies function for more details 

		target - The target species the models are for (eg. species 0)

		species_derivs - The "true" values of all species derivatives for all time steps. Should be a numpy array such that species_derivs[t, s] is the derivative of species s at time t. 

		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

		edge_ptypes - A list of ParameterType objects representing types of parameters attached to edges

		node_ptypes - A list of ParameterType objects representing types of parameters attached to nodes

		num_best_models - The number of best_performing models to retain. 

		num_restarts - The number of times we restart the optimization function to avoid local optima

		weak_sig_thresh - The threshold below which any parameter is considered to be spurious

		Returns:
		A list of length length num_best_models containing TargetModel objects that closest match the "true" values.
	"""
	best = []
	target_derivs = species_derivs[:, target]

	# Iterate through all models in the list
	for (dX, top) in models:
		# Calculate objective function 
		obj = objective_fn(dX, species_vals, target_derivs, top, time_scale)

		min_AIC = 1e12
		best_params = []
		best_dist = 1e12

		bounds_list = top.to_bounds_lst(edge_ptypes, node_ptypes)
		num_params = len(bounds_list)

		# Random restarts 
		for rr in range(num_restarts):

			# Randomly initiate starting values 
			param_list = top.to_param_lst(edge_ptypes, node_ptypes)
			param_list = list(map(lambda x:x.value, param_list)) 

			# Perform gradient matching to find optimal parameters
			res = minimize(obj, param_list, method='SLSQP', tol=1e-6, bounds=bounds_list)
			opt_params = res.x

			# Calculate the distance of best guess
			dist = obj(opt_params)

			# Calculate num time steps
			ts = species_derivs.shape[0]

			# Calculate Biased AIC for this model
			AIC_bias = 2 * (num_params + 1) * (ts / (ts - num_params))
			AIC  = ts * np.log(dist / ts) + AIC_bias

			if AIC < min_AIC:
				min_AIC = AIC
				best_params = opt_params
				best_dist = dist 

		# Create TargetModel using best parameters and AIC 
		model_details = TargetModel(topology=top,
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

		params - A list such that params[i] is the list of parameters for topology i 

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

def fit_whole_model(model_lst, topology_fn, initial_values, true_vals, time_scale, node_ptypes, edge_ptypes):
	""" Fits the parameters of every model in the input list to produce outputs similar to true_vals. This method compares the actual values of all species against the true values of all species, making it different from gradient matching where the only derivatives are compared. Warning: this method can take a long time on even small lists (expect on the order of ~10 seconds per item). 

		Args:
		model_lst - A list of WholeModel objects

		topology_fn -  A function that converts from a topology and specie values to a function, dX, that outputs the value of a species' derivatives

		initial_values - The starting values of the system 

		true_vals - The values to fit to 

		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

		node_ptypes - A list of ParameterType objects representing types of parameters attached to nodes

		edge_ptypes - A list of ParameterType objects representing types of parameters attached to edges

		Returns:
		A list of WholeModels containing every model in model_lst, but refit to match the values in true_vals. Sorted in order of increasing distance from the true_vals.
	"""
	results = []
	cnt = 0
	ts = np.linspace(time_scale[0], time_scale[1], time_scale[2])
	t_start = time.time()
	print('Reporting times every batch of 10:')
	t_ind_start = time.time()
	for wm in model_lst:
		if cnt > 0 and cnt % 10 == 0:
			t_end = time.time()
			print("batch={}, took {} seconds".format(cnt//10, t_end-t_start))
			sys.stdout.flush()
			t_start = time.time()
		cnt += 1
		topologies = [tup.topology for tup in wm.targets]
		initial_guess = [tup.params for tup in wm.targets]
		param_lens = [len(ig) for ig in initial_guess]
		bounds = [tup.topology.to_bounds_lst(node_ptypes, edge_ptypes) for tup in wm.targets]
		bounds = sum(bounds, [])
		bounds = [tuple(b) for b in bounds]

		def whole_model_obj(params):
			len_sums = [sum(param_lens[:i]) for i in range(1, len(param_lens))]
			formatted = []
			at = 0
			for pl in param_lens:
				formatted += [params[at:at+pl]]
				at += pl 
			ode = whole_model_to_ode(topology_fn, topologies, formatted)
			sim_vals = odeint(ode, initial_values, ts)
			dist = np.linalg.norm(sim_vals-true_vals)
			return dist 

		initial_guess = sum(initial_guess, [])
		res = minimize(whole_model_obj, initial_guess, method="SLSQP", bounds=bounds)
		opt_params = res.x 
		opt_dist = whole_model_obj(opt_params)
		opt_formatted = []
		opt_at = 0
		for pl in param_lens:
			opt_formatted += [opt_params[opt_at:opt_at+pl]]
			opt_at += pl 
		new_targets = [TargetModel(topology=wm.targets[i].topology, 
								   params=opt_formatted[i],
								   dist=None,
								   AIC=None) for i in range(len(wm.targets))]
		new_wm = WholeModel(new_targets, opt_dist, node_ptypes, edge_ptypes)
		results.append(new_wm);

		print('	Finished {} in {} seconds'.format(cnt, time.time()-t_ind_start))
		sys.stdout.flush()
		t_ind_start = time.time()


	return results

def model_dist(model, topology_fn, initial_values, true_vals, time_scale):
	""" Checks the distance of the input model from the true_vals.

		Args: 
		model - An array of TargetModel objects

		topology_fn -  A function that converts from a topology and specie values to a function, dX, that outputs the value of a species' derivatives

		initial_values - The starting values of the system

		true_vals - The values to compare against 

		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

		Returns:
		The euclidean distance between the input model and the true vals.
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
		models - A list of models, represented by arrays of TargetModels for each species.

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
	for i, m in enumerate(pool.imap(model_dist_par, args) , 1):
		results.append(m)
		print('Done {:.1%}\r'.format(i/num), end='')
	return sorted(results, key=lambda x: x[1])



def generate_models(topology_fn, parameter_fn, accepted_model_fn, time_scale, initial_vals, nodes=[], max_parents=-1, num_interactions=-1, max_order=-1, enf_edges=[], enf_gaps=[], processes=None, retained_top=5, restarts=1):
	""" Generate a set of models that show similar behaviour to the accepted model. 

		Each model is a permuation of the original system with attached parameter values that are based on gradient matching. 

		Args:
		topology_fn -  A function that converts from a topology and specie values to a function, dX, that outputs the value of a species' derivatives

		parameter_fn - A function that returns all the types of parameters the model contains

		accepted_model_fn - A function that takes in a time t and the value of all species at that time and outputs the derivatives of all species at time t. 

		time_scale - The time scale to simulate across. Should have the form [start, stop, num_steps]

		initial_vals - The initial values for all species. Should be a numpy array such that initial_vals[s] is the starting value of species s.

		nodes - A dictionary of (id, name) pairs for each specie in the system

		max_parents - The maximum number of parents that any node in the system can have

		num_interactions - The number of different interactions that nodes can have (eg activation or repression for gene regulation)

		max_order - The maximum order of term that any expression can have in the system

		enf_edges - A list of edge tuples for edges that must be present in all models 

		enf_gaps - A list of edge tuples for edges that must not be present in any models 

		processes - How many processes to use when multiprocessing (only valid for non-windows systems)

		retained_top - How many of the top gradient-matched topologies are
			 retained for each species. The retained topologies are combined 
			 (one per species) to create whole models. Thus lower values of 
			 this parameter result in a smaller search space of models 
			 (and thus shorter runtime).

		restarts - How many times to run the gradient-matching optimization 
			per topology (to escape local minima). Note that increasing this 
			parameter greatly increases runtime. 

		Returns:
		A ModelBag object containing the top models that closest match the accepted model.
	"""
	# Check for built in functions:
	fn_module = topology_fn.__module__
	if fn_module == 'tsa.models.gene_regulation' :
		num_interactions = 2
		max_order = 1 
	elif fn_module == 'tsa.models.population_dynamics':
		num_interactions = 1
		max_order = 1
	elif fn_module == 'tsa.models.linear_model':
		num_interactions = 1
		max_order = 1
	elif fn_module == 'tsa.models.mass_action':
		num_interactions = 1

	num_nodes = len(nodes)

	# Create Model Space
	print("Creating Model Space ... ", end='')
	model_space = ModelSpace(num_nodes=num_nodes, 
							 node_names=nodes,
							 max_parents=max_parents,
							 num_interactions=num_interactions,
							 max_order=max_order,
							 topology_fn=topology_fn)
	print("Done")


	# Seperate parameter types into nodes/edges
	print('Parsing paramter types ... ', end='')
	all_params = parameter_fn()
	node_ptypes = [pt for pt in all_params if not pt.is_edge_param]
	edge_ptypes = [pt for pt in all_params if pt.is_edge_param]
	print('Done')

	# Simulate the 'true' values of the species and their derivatives from the accepted model. 
	# We use these values as the 'truth' against which to compare our candidate models
	print('Simulating given model ... ', end='')
	species_vals, species_derivs = sim_data(accepted_model_fn, time_scale, initial_vals)
	print('Done')

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
		topologies = generate_target_topologies(model_space=model_space, 
								 target=t,
								 enf_edges=enf_edges_target[t],
								 enf_gaps=enf_gaps_target[t])

		# Perform gradient matching on each candidate model and obtain the closest matches to our 'true' data
		best = gradient_match_topologies(models=topologies,
								target=t,
								species_vals=species_vals,
								species_derivs=species_derivs,
								time_scale=time_scale,
								edge_ptypes= edge_ptypes,
								node_ptypes= node_ptypes,
								num_best_models=retained_top,
								num_restarts=restarts)

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
	best_whole_models = ModelBag(best_whole_models, 
								 node_ptypes, 
								 edge_ptypes,
								 max_parents,
								 num_interactions,
								 max_order,
								 enf_edges,
								 enf_gaps,
								 nodes)

	return best_whole_models
	


def store(model_bag, fname=None):
	if fname == None:
		return pickle.dumps(model_bag)
	else:
		with open(fname, 'wb') as f:
			pickle.dump(model_bag, f, protocol=2)


def whole_model_to_dict(wm, rank):
	json_d = {}
	json_d['dist'] = wm.dist 
	json_d['rank'] = rank
	edges = wm.get_edges()
	edges = list(map(lambda e: {'from': e[0], 'to':e[1], 'interaction':e[2], 'parameters': list(map(lambda ep: {'paramType': ep.param_type, 'val': ep.value, 'bounds': ep.bounds}, wm.get_edge_params((e[0], e[1]))))}, edges))
	json_d['edges'] = edges
	nodes = [{'id': n, 'parameters': list(map(lambda p: {'paramType': p.param_type, 'val': p.value, 'bounds': p.bounds}, wm.get_node_params(n)))} for n in range(wm.num_species)]
	json_d['nodes'] = nodes
	step = math.pi * 2 / wm.num_species
	theta = [step * i for i in range(wm.num_species)]
	layout = [[math.cos(t), math.sin(t)] for t in theta]
	json_d['layout'] = layout
	return json_d

def whole_model_to_json(wm, rank):
	json_d = whole_model_to_dict(wm, rank)
	return json.dumps(json_d)


def model_bag_to_json(model_bag):
	model_bag_json = {}
	to_dict = [whole_model_to_dict(model_bag[i], i) for i in range(len(model_bag))]
	model_bag_json['models'] = to_dict
	model_bag_json['systemInfo'] = {'numSpecies': model_bag[0].num_species,
									'maxParents': model_bag.max_parents,
									'numInteractions': model_bag.num_interactions,
									'maxOrder': model_bag.max_order,
									'enfEdges': model_bag.enf_edges,
									'enfGaps': model_bag.enf_gaps,
									'numModels': len(model_bag.models),
									'node_ptypes': [pt.to_dict() for pt in model_bag.node_ptypes],
									'edge_ptypes': [pt.to_dict() for pt in model_bag.edge_ptypes],
									'node_names': model_bag.node_names}
	return json.dumps(model_bag_json)

def json_to_model_bag(json_data):
	si = json_data['systemInfo']
	models = json_data['models']
	target_lst = []
	for m in models:
		tops = {}
		for e in m['edges']:
			if e['to'] not in tops:
				tops[e['to']] = []
			tops[e['to']] += [(e['from'], e['interaction'], e['parameters'])]

		tmodels = []
		for target in tops:
			parents = [e[0] for e in tops[target]]
			interactions = [e[1] for e in tops[target]]
			new_top = Topology(target, interactions, parents)
			tnode = [n for n in m['nodes'] if n['id'] == target][0]
			eparams = sum([e[2] for e in tops[target]], [])
			params = [d['val'] for d in tnode['parameters'] + eparams]
			new_target_model = TargetModel(new_top, params, None, None)
			tmodels.append(new_target_model)

		target_lst.append((tmodels, m['dist']))

	return ModelBag(target_lst, 
					[ParameterType.from_dict(d) for d in si['node_ptypes']], 
					[ParameterType.from_dict(d) for d in si['edge_ptypes']],
					si['maxParents'],
					si['numInteractions'],
					si['maxOrder'],
					si['enfEdges'],
					si['enfGaps'],
					si['node_names'])




def store_json(model_bag, fname):
	with open(fname, 'w') as f:
		f.write(model_bag_to_json(model_bag))

def load_json(fname):
	with open(fname, 'r') as f:
		json_data = json.load(f)
		return json_to_model_bag(json_data)

def load(fname):
	with open(fname, 'rb') as f:
		return pickle.load(f)

