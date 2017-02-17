
# Visualization


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

	srt = sorted(model_lst, key=lambda x: x.dist)
	top_n = srt[:numtop]

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
		nx.draw_networkx_edges(graph, pos=pos, edgelist=[(u,v)], width=d['weight'],alpha=0.5, arrows=False)
	nx.draw_networkx_nodes(graph, pos, with_labels=True)

	plt.show()
	plt.clf()

