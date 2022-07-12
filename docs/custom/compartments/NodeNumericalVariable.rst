************************
Node Numerical Variable
************************

Node Numerical Variable compartments are used to evaluate events attached to numeric edge attributes or statuses.

Consider the transition rule **Addicted->Not addicted** that requires that the susceptible node satisfies a specific condition
of an internal numeric attribute, *attr*, to be satisfied (e.g. "Self control" *attr* < "Craving" *status*).
Such a rule can be described by a simple compartment that models Node Numerical Attribute and Status selection. Let's call it *NNV*.

The rule will take as input the *initial* node status (Susceptible), the *final* one (Infected) and the *NNV* compartment.
*NNV* will thus require a probability (*beta*) of activation.

During each rule evaluation, given a node *n* and one of its neighbors *m*

- if the actual status of *n* equals the rule *initial*
    - if *var(n)* **op** *var(n)* (where var(n) = attr(n) or status(n))
    - a random value *b* in [0,1] will be generated
    - if *b <= beta*, then *NNV* is considered *satisfied* and the status of *n* changes from *initial* to *final*.

**op** represent a logic operator and can assume one of the following values:
- equality: "=="
- less than: "<"
- greater than: ">"
- equal or less than: "<="
- equal or greater than: ">="
- not equal to: "!="
- within: "IN"

Moreover, *NNV* allows to specify a *triggering* status in order to restrain the compartment evaluation to those nodes that:

1. match the rule *initial* state, and
2. have at least one neighbors in the *triggering* status.

The type of the values that are compared have to be specified in advance, which is done using an enumerated type. 
This is done to specify whether the first value to be compared is either a status or an attribute, 
the same thing is done for the second value to be compared. 
If the value type is not specified, the value to compare the variable to should be a number.

----------
Parameters
----------

=================  =================  =======  =========  ===================================
Name               Value Type         Default  Mandatory  Description
=================  =================  =======  =========  ===================================
variable           string             None     True       The name of the variable to compare
variable_type      NumericalType      None     True       Numerical type enumerated value
value              numeric(*)|string  None     True       Name of the testing value or number
value_type         NumericalType      None     False      Numerical type enumerated value
op                 string             None     True       Logic operator
probability        float in [0, 1]    1        False      Event probability
triggering_status  string             None     False      Trigger
=================  =================  =======  =========  ===================================

(*) When *op* equals "IN" the attribute *value* is expected to be a tuple of two elements identifying a closed interval.

-------
Example
-------

In the code below the formulation of a model is shown using NodeNumericalVariable compartments.

The first compartment, *condition*, is used to implement the transition rule *Susceptible->Infected*.
It restrains the rule evaluation to all those nodes having more "Friends" than 18.

The second compartment, *condition2*, is used to implement the transition rule *Infected->Recovered*.
It restrains the rule evaluation to all those nodes where "Age" is less than the amount of "Friends" attributes.

Note that instead of attributes, the states could have been used as well by using *NumericalType.STATUS* instead. 
This would only be applicable for numerical states, which can be modelled when using the ``ContinuousModel`` instead of the ``CompositeModel``.


.. code-block:: python

    import networkx as nx
    import random
    import numpy as np

    from ndlib.models.CompositeModel import CompositeModel
    from ndlib.models.compartments.NodeStochastic import NodeStochastic
    from ndlib.models.compartments.enums.NumericalType import NumericalType
    from ndlib.models.compartments.NodeNumericalVariable import NodeNumericalVariable
    import ndlib.models.ModelConfig as mc

    # Network generation
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Setting edge attribute
    attr = {n: {"Age": random.choice(range(0, 100)), "Friends": random.choice(range(0, 100))} for n in g.nodes()}
    nx.set_node_attributes(g, attr)

    # Composite Model instantiation
    model = CompositeModel(g)

    # Model statuses
    model.add_status("Susceptible")
    model.add_status("Infected")
    model.add_status("Removed")

    # Compartment definition
    condition = NodeNumericalVariable('Friends', var_type=NumericalType.ATTRIBUTE, value=18, op='>')
    condition2 = NodeNumericalVariable('Age', var_type=NumericalType.ATTRIBUTE, value='Friends', value_type=NumericalType.ATTRIBUTE, op='<')
 
    # Rule definition
    model.add_rule("Susceptible", "Infected", condition)
    model.add_rule("Infected", "Removed", condition2)

    # Model initial status configuration
    config = mc.Configuration()
    config.add_model_parameter('fraction_infected', 0.5)

    # Simulation execution
    model.set_initial_status(config)
    iterations = model.iteration_bunch(100)