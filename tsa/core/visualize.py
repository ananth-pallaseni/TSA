
# Visualization


import matplotlib.pyplot as plt
import networkx as nx
from scipy.stats import gaussian_kde
import numpy as np 

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
	nx.draw_circular(g, with_labels=True, edge_color=clist, font_size=22)
	plt.show()
	plt.clf()

def visulize(whole_model):
	tops = [t.topology for t in whole_model.targets]
	n, e, et = parse_topology(tops)
	graph = to_graph(n, e, et)
	vis(graph)

def mosaic(whole_model_list, w=3, h=3):
	g_list = []
	num_models = w * h
	for i in range(num_models):
		whole_model = whole_model_list[i]
		tops = [t.topology for t in whole_model.targets]
		n, e, et = parse_topology(tops)
		graph = to_graph(n, e, et) 
		g_list.append(graph)

	colors = dict(enumerate(color_choices))
	for j in range(len(g_list)):
		g = g_list[j]
		plt.subplot(w,h,j+1)
		clist = [colors[g[n1][n2]['type']] for (n1, n2) in g.edges()]
		nx.draw_circular(g, with_labels=True, edge_color=clist)
	plt.tight_layout()
	plt.show()
	plt.clf()

def prevalence_graph(model_lst, numtop):
	""" Generates a graph whose edges are weighted based on how often that edge appeared in the top N models.
	"""
	max_width=20.0
	min_width=1.0

	top_n = model_lst.top(numtop)

	edge_list = sum([wm.get_edges() for wm in top_n], [])
	edges = {}
	for e in edge_list:
		if e in edges:
			edges[e] += 1
		else:
			edges[e] = 1

	most = max(edges.values())

	scale = lambda x: (x/most) * (max_width-min_width) + min_width
	
	graph = nx.DiGraph()
	for e in edge_list:
		graph.add_edge(e[0], e[1], weight=scale(edges[e]))

	pos = nx.circular_layout(graph)

	for (u, v, d) in graph.edges(data=True):
		nx.draw_networkx_edges(graph, pos=pos, edgelist=[(u,v)], width=d['weight'],alpha=0.7, arrows=False)
	nx.draw_networkx_nodes(graph, pos, with_labels=True)

	plt.show()
	plt.clf()


def plot_errs(model_bag, numtop):
	""" Plot a bar chart of the best models by distance from the original model.

		Args:
		model_bag - A ModelBag object 

		numtop - The number of best mdoels to select

		Returns:
		Nothing. Displays a chart.
	"""
	ys = [m.dist for m in model_bag.top(numtop)]
	xs = range(numtop)
	for i in xs:
	    plt.plot([xs[i]+1,xs[i]+1],[0,ys[i]],'k-')
	plt.xlabel('Model')
	plt.ylabel('Distance')
	plt.show()
	plt.clf()

def inter_map(model_lst, numtop):
	""" Plot a heat map where square i, j is colored according to how often edge i,j exists in the top models.

		Args:
		model_lst - A ModelBag object 

		numtop - The number of best models to select

		Returns:
		Nothing. Displays a heat map.
	"""
	topx = model_lst.top(numtop)
	means = sum([model.to_adjacency_mat() for model in topx]) / numtop
	plt.imshow(means, cmap='Blues', interpolation='nearest')
	plt.title("Interaction Prevalence %")
	plt.ylabel("Outgoing Node")
	plt.xlabel("Incoming Node")
	plt.colorbar()
	plt.show()

def param_density(model_lst, numtop, param_type, node=None, edge=None):
	params = model_lst.get_param(param_type, numtop, node=node, edge=edge)
	params = [p.value for p in params]
	density = gaussian_kde(params)
	bins = np.linspace(min(params)-0.5, max(params)+0.5, 200)
	plt.plot(bins, density(bins), label='Parameter Density Estimate')
	plt.xlabel('Parameter Value')
	plt.ylabel('Density')
	if edge != None:
		plt.title('Density from top {} models of {} for edge {}'.format(numtop, param_type, edge))
	elif node != None:
		plt.title('Density from top {} models of {} for node {}'.format(numtop, param_type, node))
	else:
		raise ValueError('Need to specify either node or edge')
	plt.show()
	plt.clf()



