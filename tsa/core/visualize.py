
# Visualization


import matplotlib.pyplot as plt
import networkx as nx
from scipy.stats import gaussian_kde, fisher_exact
import numpy as np 
import tsa

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

# def param_density(model_lst, numtop, param_type, node=None, edge=None):
# 	params = model_lst.get_param(param_type, numtop, node=node, edge=edge)
# 	params = [p.value for p in params]
# 	density = gaussian_kde(params)
# 	bins = np.linspace(min(params)-0.5, max(params)+0.5, 200)
# 	plt.plot(bins, density(bins), label='Parameter Density Estimate')
# 	plt.xlabel('Parameter Value')
# 	plt.ylabel('Density')
# 	if edge != None:
# 		plt.title('Density from top {} models of {} for edge {}'.format(numtop, param_type, edge))
# 	elif node != None:
# 		plt.title('Density from top {} models of {} for node {}'.format(numtop, param_type, node))
# 	else:
# 		raise ValueError('Need to specify either node or edge')
# 	plt.show()
# 	plt.clf()

def param_density(model_lst,numtop,p_type,index,cushion = 1):
	a = []
	best = model_lst.top(numtop)
	for i in range(0,numtop):
		mod1 = best[i]
		try:
			if type(index) == int:
				if mod1.param_exists(p_type, node=index):
					a.append(mod1.get_param(p_type,node=index).value)
			elif type(index) == tuple or type(index) == list:
				if mod1.param_exists(p_type, edge=index):
					pval = mod1.get_param(p_type,edge=index).value
					a.append(pval)
		except ValueError:
			pass
	density1 = gaussian_kde(a)
	bins = np.linspace(min(a)-cushion,max(a)+cushion,200)
	return bins,density1(bins)

def contingency(x1, x2):
    d = {}
    z = zip(x1, x2)
    for tup in z:
        if tup not in d:
            d[tup] = 1
        else:
            d[tup] += 1
   
    maxind = max([max(k[0], k[1]) for k in d.keys()])
    ret = np.zeros((int(maxind+2), int(maxind+2)))
    for key in d:
        ret[int(key[0]+1), int(key[1]+1)] = d[key]
    
    rowind = np.sum(ret, 1) != 0
    colind = np.sum(ret, 0) != 0
    
    ret = ret[rowind].T[colind].T
    rowind = [i-1 for i in range(len(rowind)) if rowind[i]]
    colind = [i-1 for i in range(len(colind)) if colind[i]]
    return rowind, colind, ret


def chi_edge(model_lst,num_top = 100, ignore_same= True, threshold = 0.01):
    l1 = model_lst
    # num_top = 100 # number of top models to consider
    # ignore_same = True # choose whether to ignore
    # threshold = 0.01
    
    num_spec = l1.top(1)[0].num_species
    a = -1*np.ones((num_top,num_spec,num_spec))
    for i in range(0,num_top):
        for (nfrom, nto, ninter) in l1.top(100)[i].get_edges():
            a[i][(nfrom, nto)] = 1
            
    b = np.ones((num_spec**2,num_spec**2))
    c = np.ones((num_spec**2,num_spec**2))
    c = {}
    
    for i in range(0,num_spec**2-1):
        out1 = i %num_spec
        inc1 = i //num_spec
        for j in range(i+1,num_spec**2):
            out2 = j %num_spec
            inc2 = j //num_spec
            rind, cind, cont = contingency(a[:,out1,inc1],a[:,out2,inc2])
            sh = np.array(cont.shape)
            if (np.array(cont.shape) >=2).sum() == np.array(cont.shape).size:
                if(ignore_same == True):
                    if(inc2!=inc1):
                        b[i,j] = fisher_exact(cont)[1]
                        c[(i,j)] = cont, rind, cind
                else:
                    b[i,j] = fisher_exact(cont)[1]
                    c[(i,j)] = cont, rind, cind
    
    sigs = np.transpose(np.nonzero(b<threshold))
    edges = []
    
    for k in range(0,sigs.shape[0]):
        e1 = (float(sigs[k,0]%num_spec), float(sigs[k,0]//num_spec))
        e2 = (float(sigs[k,1]%num_spec), float(sigs[k,1]//num_spec))
        pval = float(b[sigs[k,0],sigs[k,1]])
        ctable = c[sigs[k,0],sigs[k,1]]
       	edges.append((e1, e2, pval, ctable))
    
    # Returns [ ( edge1, edge2, p-value, (contingency table, row indices, column indices)) ]
    return edges




def start_gui(model_bag):
	tsa.run_using_model_bag(model_bag)

def start_gui_from_file(fname):
	tsa.run_using_fname(fname)

