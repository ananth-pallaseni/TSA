import random 

class Parameter():
	num_params = 0
	def __init__(self, param_type, value, bounds, is_edge_param, edge=None, node=None):
		self.idx = Parameter.num_params
		Parameter.num_params += 1
		self.param_type = param_type 
		self.value = value 
		self.bounds = bounds 
		self.is_edge_param = is_edge_param
		if is_edge_param:
			if edge is None:
				raise ValueError('Edge cannot be none if this is an edge parameter')
			self.edge = edge 
			self.node = None
		else:
			if node is None:
				raise ValueError('Node cannot be none if this is a node parameter')
			self.edge = None
			self.node = node

	def update_val(self, new_val):
		self.value = new_val

	def random(self):
		rnd = random.random()
		rng = self.bounds[1] - self.bounds[0]
		lb = self.bounds[0]
		return rnd * rng + lb 

	def from_value_list(param_lst, is_edge_param, param_type, bound):
		return [Parameter(param_type, is_edge_param, value, bound) for value in param_lst]

	def get_params_by_type(param_lst, param_type):
		by_type = [p.value for p in param_lst if p.param_type == param_type]
		if len(by_type) == 0:
			raise ValueError('No Parameters with type {}'.format(param_type))
		return by_type
		
	def get_param_by_parent(param_lst, param_type, parent):
		by_type = [p for p in param_lst if p.param_type == param_type]
		if len(by_type) == 0:
			raise ValueError('No Parameters with type {}'.format(param_type))
		by_parent = [p.value for p in by_type if p.edge is not None and p.edge[0] == parent]
		if len(by_parent) == 0:
			raise ValueError('No Parameters with type {} and parent {}'.format(param_type, parent))
		elif len(by_parent) > 1:
			raise ValueError('More than one Parameter with type {} and parent {}'.format(param_type, parent))
		return by_parent

	def get_param_by_node(param_lst, param_type, node):
		by_type = [p for p in param_lst if p.param_type == param_type]
		if len(by_type) == 0:
			raise ValueError('No Parameters with type {}'.format(param_type))
		by_node = [p.value for p in by_type if p.node is not None and p.node == node]
		if len(by_node) == 0:
			raise ValueError('No Parameters with type {} and node {}'.format(param_type, node))
		elif len(by_node) > 1:
			raise ValueError('More than one Parameter with type {} and node {}'.format(param_type, node))
		return by_node

	def __str__(self):
		return 'Parameter of type {} with value {}'.format(self.param_type, self.value)

class ParameterType():
	def __init__(self, param_type, bounds, is_edge_param):
		self.param_type = param_type 
		self.bounds = bounds 
		self.is_edge_param = is_edge_param

	def create(self, value, edge=None, node=None):
		return Parameter(param_type=self.param_type, 
						 value=value, 
						 bounds=self.bounds, 
						 is_edge_param=self.is_edge_param, 
						 edge=edge, 
						 node=node)

	def create_random(self, edge=None, node=None):
		p = Parameter(param_type=self.param_type, 
						 value=self.bounds[0], 
						 bounds=self.bounds, 
						 is_edge_param=self.is_edge_param, 
						 edge=edge, 
						 node=node)
		p.value = p.random()
		return p 


class Species():
	num_species = 0
	default_name = 'species'
	def __init__(self, name=None):
		self.idx = Species.num_species
		Species.num_species += 1
		if name == None:
			self.name = Species.default_name + str(self.idx)
		else:
			self.name = name 

	def from_list(specie_lst):
		return [Species(name) for name in specie_lst]

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

	# def __repr__(self):
	# 	return self.__str__()

	def to_param_lst(self, edge_ptypes, node_ptypes):
		param_lst = [n.create_random(node=self.target) for n in node_ptypes]
		for p in self.parents:
			edge = (p, self.target)
			param_lst += [e.create_random(edge=edge) for e in edge_ptypes]
		return param_lst

	def to_bounds_lst(self, edge_ptypes, node_ptypes):
		bounds_lst = [n.bounds for n in node_ptypes]
		for p in self.parents:
			bounds_lst += [e.bounds for e in edge_ptypes]
		return bounds_lst

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


class TargetModel():
	def __init__(self, topology, params, dist, AIC):
		self.topology = topology 
		self.params = params 
		self.dist = dist 
		self.AIC = AIC 


class WholeModel():
	def __init__(self, num_species, edge_params, node_params, edge_interactions, topologies, dist=-1):
		self.num_species = num_species
		self.node_params = node_params
		self.edge_params = edge_params
		self.edge_interactions = edge_interactions
		self.topologies = topologies 
		self.dist = dist

	def edge_exists(self, n1, n2):
		if (n1, n2) in self.edge_params:
			return True
		else:
			return False

	def edge_val(self, n1, n2):
		if self.edge_exists(n1, n2):
			return self.edge_params( (n1, n2) )
		else:
			raise IndexError("No such edge exists")

	def edges(self):
		return self.edge_params.keys()

	def parents(self, node):
		if self.node_exists(node):
			res = [p for (p, t) in self.edges() if t == node]
			return list(set(res))
		else:
			raise IndexError("No such node exists")

	def topology_for(self, node):
		return self.topologies[node]

	def parameters_for(self, node):
		node_pars = [self.node_params[n] for n in self.node_params if self.node_params[n].node == node]
		edge_pars = [self.edge_params[e] for e in self.edge_params if e[1] == node]
		edge_pars = sorted(edge_pars, key=lambda x:x.edge[0])
		return node_pars + edge_pars

	def node_exists(self, node):
		if node in self.node_params:
			return True
		else:
			return False

	def node_vals(self, node):
		if self.node_exists(node):
			return self.node_params[node]
		else:
			raise IndexError("No such node exists")

	def dist(self):
		return self.dist

	def add_edge(self, n1, n2, param_lst, param_bounds_lst, edge_type):
		if self.edge_exists(n1, n2):
			self.edge_params[(n1, n2)] += param_lst
			self.edge_param_bounds[(n1, n2)] += param_bounds_lst
			self.edge_types[(n1, n2)] = edge_type 
		else:
			self.edge_params[(n1, n2)] = param_lst
			self.edge_param_bounds = param_bounds_lst
			self.edge_types[(n1, n2)] = edge_type


	def add_node_param(self, node, param_lst, param_bounds_lst):
		if node in self.node_params:
			self.node_params[node] += param_lst
			self.node_param_bounds += param_bounds_lst
		else:
			self.node_params[node] = param_lst
			self.node_param_bounds = param_bounds_lst

	def to_ode(self, topology_fn):
		def fn(x, t):
			derivs = [0 for i in range(self.num_species)]
			for i in range(self.num_species):
				top = self.topology_for(i)
				params = [p.value for p in self.parameters_for(i)]
				derivs[i] = topology_fn(x, t, top, params)
			return derivs
		return fn

	def from_list(lst):
		num_species = len(lst)

		all_params = sum([tm.params for tm in lst], [])
		edge_params = [p for p in all_params if p.is_edge_param]
		node_params = [p for p in all_params if not p.is_edge_param]

		edge_params = dict(map(lambda x: (x.edge, x), edge_params))
		node_params = dict(map(lambda x: (x.node, x), node_params))

		edge_interactions = []
		order = []
		for tm in lst:
			top = tm.topology 
			for i in range(len(top.parents)):
				edge = (top.parents[i], top.target)
				interaction = top.interactions[i]
				edge_interactions += [(edge, interaction)]
				order += [(edge, top.order)]
		edge_interactions = dict(edge_interactions)

		topologies = [tm.topology for tm in lst]

		wm = WholeModel(num_species=num_species, 
				   	    edge_params=edge_params,
				   	    node_params=node_params,
				   	    edge_interactions=edge_interactions,
				   	    topologies=topologies)

		return wm 



