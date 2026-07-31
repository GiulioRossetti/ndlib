***********************
Opinion Model Example
***********************

This example uses the continuous model together with the opinion blocks. It is
close to the patterns exercised by the current continuous-model tests: a block
is used to seed the initial values and the update rule combines assimilation,
noise, polarization, and bounded drift.

.. code-block:: python

   import networkx as nx
   import numpy as np
   import ndlib.models.ModelConfig as mc
   import ndlib.models.ContinuousModel as gc
   import ndlib.models.compartments as cpm

   from ndlib.models.compartments.NDQLBlocks import (
       ClampNormalize,
       Observe,
       OpinionAssimilation,
       OpinionBoundedDrift,
       OpinionDistribution,
       OpinionNoise,
       OpinionPolarization,
   )

   graph = nx.erdos_renyi_graph(100, 0.08, seed=12)
   model = gc.ContinuousModel(graph, clean_status=True)
   model.add_status("opinion")

   init_dist = OpinionDistribution(
       family="bimodal",
       params={"low": 0.2, "high": 0.8, "sigma": 0.05, "mix": 0.5},
       bounds=[0, 1],
   )
   noise = OpinionNoise(sigma=0.03)
   assimilation = OpinionAssimilation(rate=0.4)
   polarization = OpinionPolarization(strength=0.15, attractor_points=[0.0, 1.0])
   drift = OpinionBoundedDrift(step=0.02, bounds=[0, 1])
   clip = ClampNormalize(min=0.0, max=1.0, target="opinion")
   observe = Observe(variable="opinion", mode="bins", bins=20, range=[0, 1])

   condition = cpm.NodeStochastic(1)

   def initial_opinion(node, graph, status, constants):
       return float(init_dist.sample(1)[0])

   def update_opinion(node, graph, status, attributes, constants):
       current = status[node]["opinion"]
       neighbor_values = [status[n]["opinion"] for n in graph.neighbors(node) if n in status]
       neighbor_mean = sum(neighbor_values) / len(neighbor_values) if neighbor_values else current

       value = current + assimilation.rate * (neighbor_mean - current)
       value += np.random.normal(0.0, noise.sigma)

       if current >= 0.5:
           value += polarization.strength * (1.0 - value)
       else:
           value -= polarization.strength * value

       if neighbor_mean >= current:
           value += drift.step
       else:
           value -= drift.step

       return float(min(max(value, clip.minimum), clip.maximum))

   model.add_rule("opinion", update_opinion, condition)

   initial_status = {"opinion": initial_opinion}
   cfg = mc.Configuration()
   model.set_initial_status(initial_status, cfg)

   iterations = model.iteration_bunch(25, node_status=True, progress_bar=False)
   _ = observe, iterations
