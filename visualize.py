
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

def mosaic(whole_model_list):
	g_list = []
	for i in range(9):
		whole_model = whole_model_list[i]
		tops = [t.topology for t in whole_model.targets]
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
