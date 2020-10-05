************
HIOM example
************

-----------
Description
-----------

This example will be slightly more complex, 
as it involves different schemes and update functions to model the spread of opinion polarization within and across individuals.

The paper: `The polarization within and across individuals: the hierarchical Ising opinion model (Han L J van der Maas, Jonas Dalege, Lourens Waldorp) <https://academic.oup.com/comnet/article-abstract/8/2/cnaa010/5823576>`_

----
Code
----

.. code-block:: python

    import networkx as nx
    import random
    import numpy as np
    import matplotlib.pyplot as plt

    from ndlib.models.ContinuousModel import ContinuousModel
    from ndlib.models.compartments.NodeStochastic import NodeStochastic

    import ndlib.models.ModelConfig as mc

    ################### MODEL SPECIFICATIONS ###################

    constants = {
        'dt': 0.01,
        'A_min': -0.5,
        'A_star': 1,
        's_O': 0.01,
        's_I': 0,
        'd_A': 0,
        'p': 1,
        'r_min': 0,
        't_O': np.inf,
    }

    def initial_I(node, graph, status, constants):
        return np.random.normal(0, 0.3)

    def initial_O(node, graph, status, constants):
        return np.random.normal(0, 0.2)

    initial_status = {
        'I': initial_I,
        'O': initial_O,
        'A': 1
    }

    def update_I(node, graph, status, attributes, constants):
        nb = np.random.choice(graph.neighbors(node))
        if abs(status[node]['O'] - status[nb]['O']) > constants['t_O']:
            return status[node]['I'] # Do nothing
        else:
            # Update information
            r = constants['r_min'] + (1 - constants['r_min']) / (1 + np.exp(-1 * constants['p'] * (status[node]['A'] - status[nb]['A'])))
            inf = r * status[node]['I'] + (1-r) * status[nb]['I'] + np.random.normal(0, constants['s_I'])

            # Update attention
            status[node]['A'] = status[node]['A'] + constants['d_A'] * (2 * constants['A_star'] - status[node]['A'])
            status[nb]['A'] = status[nb]['A'] + constants['d_A'] * (2 * constants['A_star'] - status[nb]['A'])

            return inf

        return

    def update_A(node, graph, status, attributes, constants):
        return status[node]['A'] - 2 * constants['d_A'] * status[node]['A']/len(graph.nodes)

    def update_O(node, graph, status, attributes, constants):
        noise = np.random.normal(0, constants['s_O'])
        x = status[node]['O'] - constants['dt'] * (status[node]['O']**3 - (status[node]['A'] + constants['A_min']) * status[node]['O'] - status[node]['I']) + noise
        return x

    def shrink_I(node, graph, status, attributes, constants):
        return status[node]['I'] * 0.999

    def shrink_A(node, graph, status, attributes, constants):
        return status[node]['A'] * 0.999

    def sample_attention_weighted(graph, status):
        probs = []
        A = [stat['A'] for stat in list(status.values())]
        factor = 1.0/sum(A)
        for a in A:
            probs.append(a * factor)
        return np.random.choice(graph.nodes, size=1, replace=False, p=probs)

    schemes = [
        {
            'name': 'random agent',
            'function': sample_attention_weighted,
        },
        {
            'name': 'all',
            'function': lambda graph, status: graph.nodes,
        },
        {
            'name': 'shrink I',
            'function': lambda graph, status: graph.nodes,
            'lower': 5000
        },
        {
            'name': 'shrink A',
            'function': lambda graph, status: graph.nodes,
            'lower': 10000
        },
    ]

    ################### MODEL CONFIGURATION ###################

    # Network definition
    g = nx.watts_strogatz_graph(400, 2, 0.02)

    # Visualization config
    visualization_config = {
        'layout': 'fr',
        'plot_interval': 100,
        'plot_variable': 'O',
        'variable_limits': {
            'A': [0, 1]
        },
        'cmin': -1,
        'cmax': 1,
        'color_scale': 'RdBu',
        'plot_output': './HIOM.gif',
        'plot_title': 'HIERARCHICAL ISING OPINION MODEL',
    }

    # Model definition
    HIOM = ContinuousModel(g, constants=constants, iteration_schemes=schemes)
    HIOM.add_status('I')
    HIOM.add_status('A')
    HIOM.add_status('O')

    # Compartments
    condition = NodeStochastic(1)

    # Rules
    HIOM.add_rule('I', update_I, condition, ['random agent'])
    HIOM.add_rule('A', update_A, condition, ['all'])
    HIOM.add_rule('O', update_O, condition, ['all'])
    HIOM.add_rule('I', shrink_I, condition, ['shrink I'])
    HIOM.add_rule('A', shrink_A, condition, ['shrink A'])

    # Configuration
    config = mc.Configuration()
    HIOM.set_initial_status(initial_status, config)
    HIOM.configure_visualization(visualization_config)

    ################### SIMULATION ###################

    iterations = HIOM.iteration_bunch(15000, node_status=True)
    trends = HIOM.build_trends(iterations)

    ################### VISUALIZATION ###################

    HIOM.plot(trends, len(iterations), delta=True)
    HIOM.visualize(iterations)

------
Output
------

.. figure:: https://i.imgur.com/xIpmL6X.png
   :align: center
   :alt: Verification

.. figure:: https://i.imgur.com/emEFOlx.gif
   :align: center
   :alt: Verification

