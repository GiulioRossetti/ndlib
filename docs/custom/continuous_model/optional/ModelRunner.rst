***********************
Continuous Model Runner
***********************

Often, a model is not only executed once for n amount of iterations. Most of the time meaningful conclusions can be drawn after simulating the model multiple times and even using different inputs.
This is made possible using the ``ContinuousModelRunner``.

It takes as input a ``ContinuousModel`` object and a ``Configuration`` object (created by using ``ModelConfig``).

After instantiating the runner object, two functions can be used;
one runs the model multiple times for n amount of iterations using different parameters,
the other performs sensitivity analysis based on specified measures.

------
Runner
------

The model can be executed `N` amount with different parameters using the 
``run(N, iterations_list,  initial_statuses, constants_list=None)`` function.
If the length of a list is not equal to the amount of simulations, this is no problem, 
as the index of the list will be selected using ``iteration number % list_length``. 
This means if you want to only use one value for every simulation, simply provide a list as argument with only one value.

================  ================  =======  =========  =====================================================================
Run parameters    Value Type        Default  Mandatory  Description
================  ================  =======  =========  =====================================================================
N                 number                     True       The amount of times to run the simulation
iterations_list   list[number]               True       A list containing the amount of iterations to use per simulation
initial_statuses  list[dictionary]           True       A list containing `initial_status` dictionaries to use per simulation
constants_list    list[dictionary]  None     False      A list containing `constants` dictionaries to use per simulation
================  ================  =======  =========  =====================================================================

Example:

.. code-block:: python

    import networkx as nx
    import numpy as np
    from ndlib.models.ContinuousModel import ContinuousModel
    from ndlib.models.ContinuousModelRunner import ContinuousModelRunner
    from ndlib.models.compartments.NodeStochastic import NodeStochastic
    import ndlib.models.ModelConfig as mc

    g = nx.erdos_renyi_graph(n=1000, p=0.1)

    def initial_status_1(node, graph, status, constants):
        return np.random.uniform(0, 0.5)

    def initial_status_2(node, graph, status, constants):
        return status['status_1'] + np.random.uniform(0.5, 1)

    initial_status = {
        'status_1': initial_status_1,
        'status_2': initial_status_2,
    }

    model = ContinuousModel(g)

    model.add_status('status_1')
    model.add_status('status_2')

    # Compartments
    condition = NodeStochastic(1)

    # Update functions
    def update_1(node, graph, status, attributes, constants):
        return status[node]['status_2'] + 0.1

    def update_2(node, graph, status, attributes, constants):
        return status[node]['status_1'] + 0.5

    # Rules
    model.add_rule('status_1', update_1, condition)
    model.add_rule('status_2', update_2, condition)

    config = mc.Configuration()
    model.set_initial_status(initial_status, config)

    # Simulation
    runner = ContinuousModelRunner(model, config)
    # Simulate the model 10 times with 100 iterations
    results = runner.run(10, [100], [initial_status])

--------------------
Sensitivity Analysis
--------------------

Another important part of analysing a model is sensitivity analysis. 
Custom analysis can be done using the run function, but an integrated SALib version is included 
and can be ran using the ``analyze_sensitivity(sa_type, initial_status, bounds, n, iterations, second_order=True)`` function.

It requires the following parameters:

==============  ===================================  =======  =========  ==============================================================================
parameters      Value Type                           Default  Mandatory  Description
==============  ===================================  =======  =========  ==============================================================================
sa_type         SAType                                        True       SAType enumerated value indicating what metric to use for sensitivity analysis
initial_status  dictionary                                    True       A dictionary containing the initial status per state
bounds          dictionary{status => (lower, upper)           True       A dictionary mapping a status string to a tuple in the form of [lower, upper]
n               integer                                       True       The amount of samples to get from the SALib saltelli sampler
iterations      integer                                       True       A list containing `constants` dictionaries to use per simulation
second_order    boolean                              True     False      Boolean indicating whether to include second order indices
==============  ===================================  =======  =========  ==============================================================================

At the moment, after every simulation, the mean value for a state is taken over all the nodes, which is seen as one output for the model.
After running the analysis, a dictionary is returned, mapping a state to a dictionary with the keys "S1", "S2", "ST", "S1_conf", "S2_conf", and "ST_conf" 
which is acquired by using ``sobol.analyze()`` from SALib.

.. note::

    Currently, the following sensitivity analysis metrics can be passed for the sa_type parameter (use the SAType enum):

    - SAType.MEAN


Example:

.. code-block:: python

    import networkx as nx
    import numpy as np
    from ndlib.models.ContinuousModel import ContinuousModel
    from ndlib.models.ContinuousModelRunner import ContinuousModelRunner
    from ndlib.models.compartments.NodeStochastic import NodeStochastic
    from ndlib.models.compartments.enums.SAType import SAType
    import ndlib.models.ModelConfig as mc

    g = nx.erdos_renyi_graph(n=1000, p=0.1)

    constants = {
        'constant_1': 0.5,
        'constant_2': 0.8
    }

    def initial_status_1(node, graph, status, constants):
        return np.random.uniform(0, 0.5)

    def initial_status_2(node, graph, status, constants):
        return status['status_1'] + np.random.uniform(0.5, 1)

    initial_status = {
        'status_1': initial_status_1,
        'status_2': initial_status_2,
    }

    model = ContinuousModel(g, constants=constants)

    model.add_status('status_1')
    model.add_status('status_2')

    # Compartments
    condition = NodeStochastic(1)

    # Update functions
    def update_1(node, graph, status, attributes, constants):
        return status[node]['status_2'] * constants['constant_1']

    def update_2(node, graph, status, attributes, constants):
        return status[node]['status_1'] + constants['constant_2']

    # Rules
    model.add_rule('status_1', update_1, condition)
    model.add_rule('status_2', update_2, condition)

    config = mc.Configuration()
    model.set_initial_status(initial_status, config)

    # Simulation
    runner = ContinuousModelRunner(model, config)
    analysis = runner.analyze_sensitivity(SAType.MEAN, initial_status, {'constant_1': (0, 1), 'constant_2': (-1, 1)}, 100, 50)

