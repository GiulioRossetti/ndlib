*************************
Epidemic Model Example
*************************

This example shows how the epidemic blocks can be combined into a compact
simulation scaffold. The blocks are instantiated explicitly so they can be
reused in a handwritten custom model or copied into generated code.

.. code-block:: python

   import networkx as nx

   from ndlib.models.compartments.NDQLBlocks import (
       CommunityMixingBlock,
       DoseResponseBlock,
       EdgeActivationBlock,
       ExposureRate,
       HospitalizationBlock,
       ImportationBlock,
       IncubationState,
       LatencyPeriod,
       MortalityBlock,
       PolicyIntervention,
       PreviewObservable,
       QuarantineBlock,
       RecoveryKernel,
       ReinfectionBlock,
       RewiringBlock,
       SeasonalityBlock,
       StrainBlock,
       SuperSpreaderBlock,
       TestingBlock,
       TransmissionKernel,
       TreatmentBlock,
       VaccinationBlock,
       WaningImmunity,
   )

   graph = nx.erdos_renyi_graph(20, 0.15, seed=4)
   for node in graph.nodes():
       graph.nodes[node]["com"] = 0 if node < 10 else 1

   status = {node: 0 for node in graph.nodes()}
   status[0] = 1
   status[5] = 1

   params = {"model": {"iteration": 0, "available_statuses": {"Susceptible": 0, "Infected": 1, "Removed": 2}}}

   exposure = ExposureRate(beta=0.4, infected_statuses=[1], target="exposure")
   transmission = TransmissionKernel(saturation=1.0, source="exposure", target="transmission_probability")
   dose = DoseResponseBlock(shape="logistic", scale=2.0, offset=0.1)
   latency = LatencyPeriod(duration=2)
   incubation = IncubationState(infectiousness=0.2, duration=2)
   recovery = RecoveryKernel(gamma=0.1)
   waning = WaningImmunity(rate=0.02, delay=3)
   vaccine = VaccinationBlock(coverage=0.2, efficacy=0.9)
   quarantine = QuarantineBlock(duration=3, coverage=0.5)
   testing = TestingBlock(sensitivity=0.95, specificity=0.98)
   treatment = TreatmentBlock(efficacy=0.7, delay=1)
   hospital = HospitalizationBlock(capacity=50, rate=0.1, mortality=0.02)
   mortality = MortalityBlock(fatality=0.01, target_status="Removed")
   reinfection = ReinfectionBlock(susceptibility=0.5)
   strain = StrainBlock(strain_id="A")
   super_spreader = SuperSpreaderBlock(activity=2.0, burst_rate=0.2)
   seasonality = SeasonalityBlock(period=52, amplitude=0.2)
   importation = ImportationBlock(arrival_rate=0.01, infectious_status="Infected")
   rewiring = RewiringBlock(rewire_rate=0.05)
   mixing = CommunityMixingBlock(intra_rate=1.0, inter_rate=0.2, community_field="com")
   edge_activation = EdgeActivationBlock(threshold=0.5, duration=1)
   policy = PolicyIntervention(start=5, end=20, action="scale", value=0.5, target="contact_rate")
   preview = PreviewObservable(variable="infection_probability", mode="bins", bins=10, range=[0, 1])

   # The core infection loop.
   for node in graph.nodes():
       exposure.execute(node, graph, status, status, params)
       transmission.execute(node, graph, status, status, params)
       dose.execute(node, graph, status, status, params)

       if graph.nodes[node].get("infection_probability", 0.0) > 0.5:
           status[node] = 1

   # Interventions and side effects can be layered on top of the same graph.
   for node in [0, 5]:
       vaccine.execute(node, graph, status, status, params)
       quarantine.execute(node, graph, status, status, params)
       testing.execute(node, graph, status, status, params)
       treatment.execute(node, graph, status, status, params)
       hospital.execute(node, graph, status, status, params)
       mortality.execute(node, graph, status, status, params)
       reinfection.execute(node, graph, status, status, params)
       strain.execute(node, graph, status, status, params)
       super_spreader.execute(node, graph, status, status, params)
       seasonality.execute(node, graph, status, status, params)
       importation.execute(node, graph, status, status, params)
       rewiring.execute(node, graph, status, status, params)
       mixing.execute(node, graph, status, status, params)
       edge_activation.execute(node, graph, status, status, params)
       policy.execute(node, graph, status, status, params)
       preview.execute(node, graph, status, status, params)

   _ = (latency, incubation, recovery, waning)
