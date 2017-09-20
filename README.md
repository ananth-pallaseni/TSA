# TSA

A package for performing topological sensitivty analysis (TSA), see: http://www.pnas.org/content/111/52/18507.abstract 

**Quick Summary**: A biological model can be represented by a network of nodes and edges where nodes are species (of organism, or chemicals) and edges represent interactions. 
Given experimental data, a candidate network and a mathematical model for how interactions work, one can perform TSA to see what other network topologies result in similar outputs to the candidate. 
TSA provides alternative hypotheses that also explain the data and can be a valuable tool for checking the validity of models inferred from experiments.

# Basic Usage
See the `examples` folder for more fleshed out examples.

To perform TSA on a model space, one must first define:
- **A Model Framework**: must contain a derivative function and a parameter function describing how to translate an interaction network into a set of ODEs
- **"True" Model Function**: a function that takes in a vector of species values and the time and outputs a vector containing the derivatives of all species. This should represent the system that the user wants to start with / perturb.
- **A dictionary** which maps from species ID to the name of the species.This allows nodes to have access to the name of the species they represent.
- **An array of initial values** which are the starting values of each species
- **A time scale** which should have the form [start time, stop time, num steps]

Given the above, use the `topsa.generate_models function` as follows:

```python
# Maximal number of parents any node can have.
max_parents = ...

# Number of interactions possible (eg. up-regulation / down-regulation)
num_interactions = ...

# Maximum order of compound parent generated. eg: order of 1 generates 
# only linear terms of species, order of 2 generates parents of order 1 but also 
# squared terms and products
max_order = ...

# Edges which must exist in all generated models. Can be an empty list
enforced_edges = [...]

# Edges which CANNOT exist in any model. Can be an empty list.
enforced_gaps = [...]

# Number of best gradient-matched topologies to keep for each species. 
# eg: A value of four means that the top four topologies for each species 
# will be retained and used in combination to create the combined models. 
# Note that increasing this value exponentially increases runtime.
retained = ...

# How many times to run the gradient-matching optimization per topology. 
# Higher values mean a greater chance to escape local optima
restarts = ...

# ModelBag object representing the results of TSA
alt_models = topsa.generate_models(topology_fn = deriv_function,
    parameter_fn = param_function,
    nodes = nodes,
    max_parents = max_parents,
    num_interactions = num_interactions,
    max_order = max_order,
    initial_vals = initial_values,
    time_scale = time_scale,
    enf_edges = enforced_edges,
    enf_gaps = enforced_gaps,
    retained_top = retained,
    restarts = restarts) 
    
```

Finally, the results of the analysis can be stored in json format with the `topsa.store_json` function:

```python
tsa.store_json(alt_models, 'filename.json')
```

# GUI
To view the results of the analysis in a more friendly form, the gui can be invoked in one of three ways:

- Using a `ModelBag` object: `topsa.start_gui(alt_models)`
- Using a json file: `topsa.start_gui_from_file(filename)`
- From the gui folder using command line & a json file: `python gui.py filepath_to_json_file`
