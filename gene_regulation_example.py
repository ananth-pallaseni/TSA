# An example formulation of a 5 species gene regulation network where
# each species can activate or inhibit the others. 
#
# The species are 1, 2, 3, 4, 5 
#
# The network is as follows:
# 1 activates 2, 3 and 4
# 2 inhibits 5
# 3 inhibits 4 
# 4 activates 5
# 5 activates 1

from gene_regulation import GeneRegulationModel
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt 
from scipy.optimize import minimize


max_parents = 2
num_nodes = 5
time_scale = [0,10,31]

# accepted_topology = [TargetTopology(target=1, parents=[5], interactions=[1], order=0),
# 				  TargetTopology(target=2, parents=[1], interactions=[1], order=0),
# 				  TargetTopology(target=3, parents=[1], interactions=[1], order=0),
# 				  TargetTopology(target=4, parents=[1,3], interactions=[1,2], order=0),
# 				  TargetTopology(target=5, parents=[2,4], interactions=[2,1], order=0)]

gene_reg_model = GeneRegulationModel(max_parents=max_parents, 
							num_nodes=num_nodes,
							time_scale=time_scale
							)

#########################################

# Simulate "true" data
species_data, species_derivs = gene_reg_model.sim_data(model_fn=gene_reg_model.accepted_model_fn,
									time_scale = gene_reg_model.time_scale,
									x0=[1, 0.5, 1, 1.5, 0.5])



## Plot
# plt.plot(ts, true_data[:, 0], "+", label="x1")
# plt.plot(ts, true_data[:, 1], "x", label="x2")
# plt.plot(ts, true_data[:, 2], "o", label="x3")
# plt.xlabel("Time")
# plt.ylabel("X")
# plt.legend();

# enumerate all models
models = gene_reg_model.generate_models(0, species_data)

# fo each model, optimize it
best_models = []
cnt = 0
for t in [0]:
	for m in models:
		cnt += 1
		if cnt > 100:
			input("done 100")
		# if cnt > 1:
		# 	print ("best 0 = ", best_models[0][0])
		# 	print()
		dX, paramlen, bounds, top = m
		# print (top)
		# print()
		obj = gene_reg_model.objective_fn(dX, t, species_derivs)

		init_params = [1 for i in range(paramlen)]
		res = minimize(obj, init_params, method='TNC', tol=1e-7, bounds=bounds)
		opt_params = res.x 
		dist = obj(opt_params)

		# Do Ordering
		# print(top)
		# print()
		best_models.append( (top, dX, opt_params, dist) )




s = sorted(best_models, key=lambda x:x[3])
for i in s:
	print(i[0])
	print(i[3])
	print()






