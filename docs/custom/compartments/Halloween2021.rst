*******************************************
2021 Halloween Special: Zombie Epidemiology
*******************************************


    Zombies are a popular figure in pop culture/entertainment and they are usually portrayed as being brought about through an outbreak or epidemic.
    Consequently, we model a zombie attack, using biological assumptions based on popular zombie movies.

    We introduce a basic model for zombie infection, determine equilibria and their stability, and illustrate the outcome with numerical solutions.
    We then refine the model to introduce a latent period of zombification, whereby humans are infected, but not infectious, before becoming undead. We then modify the model to include the effects of possible quarantine or a cure.

    Finally, we examine the impact of regular, impulsive reductions in the number of zombies and derive conditions under which eradication can occur.
    We show that only quick, aggressive attacks can stave off the doomsday scenario: the collapse of society as zombies overtake us all.

**Original Paper**

Munz, Philip, et al. *"When zombies attack!: mathematical modelling of an outbreak of zombie infection."* Infectious disease modelling research progress 4 (2009): 133-150.

**Acknowledgement**

- We thank  `BrandonKMLee <https://github.com/BrandonKMLee>`_ for models implementation (inspired by the original paper).
- All descriptive texts are borrowed from the original authors.

---
SZR
---

- Susceptibles can become deceased through ‘natural’ causes, i.e., non-zombie-related death.
- The removed class consists of individuals who have died, either through attack or natural causes.
- Humans in the removed class can resurrect and become a zombie.
- Susceptibles can become zombies through transmission via an encounter with a zombie.
- Only humans can become infected through contact with zombies, and zombies only have a craving for human flesh so we do not consider any other life forms in the model.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.CompositeModel as gc
    import ndlib.models.compartments as cpm
    from ndlib.viz.mpl.DiffusionTrend import DiffusionTrend
    import matplotlib.pyplot as plt

    %matplotlib inline # comment if ran outside a jupyter notebook

    # Network generation
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Composite Model instantiation
    model = gc.CompositeModel(g)

    # Model statuses
    model.add_status("Susceptible")
    model.add_status("Infected")
    model.add_status("Removed")

    # Compartment definition
    c1 = cpm.NodeStochastic(0.02, triggering_status="Infected") # Susceptible - Zombie
    c2 = cpm.NodeStochastic(0.01) # Susceptible - Removed
    c3 = cpm.NodeStochastic(0.015) # Zombie - Removed
    c4 = cpm.NodeStochastic(0.01) # Removed - Zombie

    # Rule definition
    model.add_rule("Susceptible", "Infected", c1)
    model.add_rule("Susceptible", "Removed", c2)
    model.add_rule("Infected", "Removed", c3)
    model.add_rule("Removed", "Infected", c4)

    # Model initial status configuration
    config = mc.Configuration()
    config.add_model_parameter('fraction_infected', 0.1)

    # Simulation execution
    model.set_initial_status(config)
    iterations = model.iteration_bunch(100)
    trends = model.build_trends(iterations)

    viz = DiffusionTrend(model, trends)
    viz.plot()


---------
SIZR-Cure
---------
**Without Cure**

We now revise the model to include a latent class of infected individuals.
There is a period of time (approximately 24 hours) after the human susceptible gets bitten before they succumb to their wound and become a zombie.
We thus extend the basic model to include the (more ‘realistic’) possibility that a susceptible individual becomes infected before succumbing to zombification.
This is what is seen quite often in pop-culture representations of zombies

- Susceptibles first move to an infected class once infected and remain there for some period of time.
- Infected individuals can still die a ‘natural’ death before becoming a zombie; otherwise, they become a zombie.

**With Cure**

Suppose we are able to quickly produce a cure for ‘zombie-ism’.
Our treatment would be able to allow the zombie individual to return to their human form again.
Once human, however, the new human would again be susceptible to becoming a zombie; thus, our cure does not provide immunity.
Those zombies who resurrected from the dead and who were given the cure were also able to return to life and live again as they did before entering the R class.

Things that need to be considered now include:

- The cure will allow zombies to return to their original human form regardless of how they became zombies in the first place.
- Any cured zombies become susceptible again; the cure does not provide immunity.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.CompositeModel as gc
    import ndlib.models.compartments as cpm
    from ndlib.viz.mpl.DiffusionTrend import DiffusionTrend
    import matplotlib.pyplot as plt

    %matplotlib inline # comment if ran outside a jupyter notebook

    # Network generation
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Composite Model instantiation
    model = gc.CompositeModel(g)

    # Model statuses
    model.add_status("Susceptible")
    model.add_status("Infected")
    model.add_status("Zombie")
    model.add_status("Removed")

    # Compartment definition
    c_alpha = cpm.NodeStochastic(0.005, triggering_status="Susceptible")
    c_beta = cpm.NodeStochastic(0.0095, triggering_status="Zombie")
    c_gamma = cpm.NodeStochastic(0.0001)
    c_delta = cpm.NodeStochastic(0.0001)
    c_rho = cpm.NodeStochastic(0.005)
    c_cure = cpm.NodeStochastic(0.01) # remove if not the cure model

    # Rule definition
    model.add_rule("Susceptible", "Infected", c_beta)
    model.add_rule("Infected", "Zombie", c_rho)
    model.add_rule("Zombie", "Removed", c_alpha)
    model.add_rule("Removed", "Zombie", c_gamma)
    model.add_rule("Susceptible", "Removed", c_delta)
    model.add_rule("Infected", "Removed", c_delta)
    model.add_rule("Zombie", "Susceptible", c_cure) # remove if not the cure model

    # Model initial status configuration
    config = mc.Configuration()
    config.add_model_parameter('fraction_Zombie', 0.1)

    # Simulation execution
    model.set_initial_status(config)
    iterations = model.iteration_bunch(100)
    trends = model.build_trends(iterations)

    viz = DiffusionTrend(model, trends)
    viz.plot()



-----
SIZRQ
-----

In order to contain the outbreak, we decided to model the effects of partial quarantine of zombies.
In this model, we assume that quarantined individuals are removed from the population and cannot infect new individuals while they remain quarantined.
Thus, the changes to the previous model include:
- The quarantined area only contains members of the infected or zombie populations.
- There is a chance some members will try to escape, but any that tried to would be killed before finding their ‘freedom’.
- These killed individuals enter the removed class and may later become reanimated as ‘free’ zombies.

.. code-block:: python

    import networkx as nx
    import ndlib.models.ModelConfig as mc
    import ndlib.models.CompositeModel as gc
    import ndlib.models.compartments as cpm
    from ndlib.viz.mpl.DiffusionTrend import DiffusionTrend
    import matplotlib.pyplot as plt

    %matplotlib inline # comment if ran outside a jupyter notebook

    # Network generation
    g = nx.erdos_renyi_graph(1000, 0.1)

    # Composite Model instantiation
    model = gc.CompositeModel(g)

    # Model statuses
    model.add_status("Susceptible")
    model.add_status("Infected")
    model.add_status("Zombie")
    model.add_status("Removed")
    model.add_status("Quarantined")

    # Compartment definition
    c_alpha = cpm.NodeStochastic(0.005, triggering_status="Susceptible")
    c_beta = cpm.NodeStochastic(0.0095, triggering_status="Zombie")
    c_sigma = cpm.NodeStochastic(0.0001)
    c_delta = cpm.NodeStochastic(0.0001)
    c_rho = cpm.NodeStochastic(0.005)

    c_kappa = cpm.NodeStochastic(0.005)
    c_sigma = cpm.NodeStochastic(0.005)
    c_gamma = cpm.NodeStochastic(0.005)

    # Rule definition
    model.add_rule("Susceptible", "Infected", c_beta)
    model.add_rule("Infected", "Zombie", c_rho)
    model.add_rule("Zombie", "Removed", c_alpha)
    model.add_rule("Removed", "Zombie", c_sigma)
    model.add_rule("Susceptible", "Removed", c_delta)
    model.add_rule("Infected", "Removed", c_delta)

    model.add_rule("Infected", "Quarantined", c_kappa)
    model.add_rule("Zombie", "Quarantined", c_rho)
    model.add_rule("Quarantined", "Removed", c_gamma)

    # Model initial status configuration
    config = mc.Configuration()
    config.add_model_parameter('fraction_Zombie', 0.1)

    # Simulation execution
    model.set_initial_status(config)
    iterations = model.iteration_bunch(100)
    trends = model.build_trends(iterations)

    viz = DiffusionTrend(model, trends)
    viz.plot()
