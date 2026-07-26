********************
Interactive Dashboard
********************

NDlib ships with a browser-based dashboard service that lets you build a graph, configure a model, and run a simulation from a single interface.

The dashboard is intended for quick experimentation, classroom use, and exploratory analysis when you want to compare multiple models without writing code.

Main features
=============

- Generate synthetic graphs or upload a custom network.
- Inspect epidemic and opinion models through a three-step workflow.
- Configure model parameters directly from the UI.
- Select initial epidemic seeds by clicking nodes in the graph preview.
- Use community-aware graph layouts to highlight structural groups.
- Visualize trends, opinion evolution, prevalence, and network state.

Quick start
===========

From the repository root, launch the service with:

.. code-block:: bash

   python ndlib/dashboard/server.py

If the package is installed, the same service is also exposed as:

.. code-block:: bash

   ndlib-dashboard

Then open the local URL printed by the server in your browser.

The standard workflow is:

1. Build or load a network.
2. Configure the model parameters.
3. Run the simulation and inspect the plots and graph view.

Example usage
=============

Generate a small graph and simulate an epidemic model:

.. code-block:: bash

   python ndlib/dashboard/server.py

or, if installed as a command:

.. code-block:: bash

   ndlib-dashboard

In the dashboard:

1. Choose an epidemic model such as ``SIR``.
2. Set the graph topology and the model parameters.
3. Click ``Build / Load Network``.
4. Click ``Run Simulation``.
5. Use the network tab to inspect the graph at each step.

For epidemic models, you can seed the outbreak by clicking nodes in the preview graph. If no nodes are selected, the dashboard uses the ``Initial infected share (%)`` field instead.

Visual Model Builder
====================

The dashboard includes an interactive visual programming canvas to build custom compartmental models. This allows modeling complex diffusion scenarios by composing and branching rules using flowcharts.

Available Blocks
----------------

* **Status Node**: Declares a state value.
  * *Parameters*: ``Identifier/Name`` (alphanumeric name), ``Status Code`` (integer index).
  * *Example*: Create ``S`` (code 0), ``I`` (code 1), and ``R`` (code 2) statuses for a standard SIR simulation.

* **Node Stochastic**: Propagates infection stochastically from matching neighbor statuses.
  * *Parameters*: ``Transmission Rate (rate)`` (probability in [0, 1]), ``Triggering Status`` (the neighbor status that triggers the check).
  * *Example*: A rate of ``0.05`` and trigger status ``Infected`` transitions Susceptible to Infected.

* **Node Threshold**: Activates state change if the fraction of infected neighbors exceeds a threshold.
  * *Parameters*: ``Threshold`` (float in [0, 1]), ``Triggering Status``.
  * *Example*: A threshold of ``0.20`` and trigger status ``Infected`` means the node transitions if >=20% of its neighbors are infected.

* **Edge Stochastic**: Stochastically propagates state change across individual active links.
  * *Parameters*: ``Threshold`` (float in [0, 1]), ``Triggering Status``.
  * *Example*: Implements link-level stochastics based on active interaction links.

* **Count Down**: Implements fixed iteration-based delays.
  * *Parameters*: ``Count Down Iterations`` (integer >= 1).
  * *Example*: Recovering after exactly 10 simulation steps.

* **Node Categorical Attribute**: Checks categorical node properties from the NetworkX network configuration.
  * *Parameters*: ``Attribute Name`` (string), ``Value`` (expected string), ``Success Probability`` (probability of passing if attributes match).
  * *Example*: ``gender`` equals ``female`` with probability ``0.80``.

* **Node Numerical Attribute**: Compares numerical node parameters.
  * *Parameters*: ``Attribute Name`` (string), ``Operator`` (``==``, ``!=``, ``<``, ``>``, ``<=``, ``>=``, ``IN``), ``Value`` (value to compare, or list range for ``IN``), ``Success Probability``.
  * *Example*: ``age`` operator ``IN`` value ``18,65`` with probability ``1.0``.

* **Conditional Composition**: Composes logic gates by routing sub-compartments.
  * *Parameters*: None directly on the node. Connected via wires to ports:
    * ``cond``: the conditional compartment to evaluate.
    * ``true``: executed if the condition passes.
    * ``false``: executed if the condition fails.
  * *Example*: If ``NodeStochastic`` condition passes, execute ``NodeCategoricalAttribute`` branch, else execute ``NodeNumericalAttribute`` branch.

Step-by-Step Instructions
-------------------------

1. Open the Visual Model Builder canvas from the top navbar.
2. Clear the canvas or start modifying the default layout.
3. Click components in the left sidebar to add them to the canvas.
4. Drag node cards to position them.
5. Draw connections by dragging from the blue ``out`` handle on the right of any node/compartment to:
   * The purple ``in`` handle on the left of target nodes.
   * Named sub-port handles (``cond``, ``true``, ``false``) on a ``ConditionalComposition`` block.
6. Select any card to configure its parameters in the right sidebar.
7. Enter a unique model name, then click ``Save & Register Model``.
8. The compiled model will immediately be listed under the **Custom Models** tab in the dashboard side panel, ready to simulate.

Screenshots
===========

Configuration view:

.. figure:: _static/dashboard/dashboard-config.png
   :align: center
   :alt: NDlib dashboard configuration view
   :width: 95%

   Dashboard configuration view with graph, model, and simulation controls.

Network view:

.. figure:: _static/dashboard/dashboard-network.png
   :align: center
   :alt: NDlib dashboard network view
   :width: 95%

   Dashboard network tab with the preview and layout controls.

Visual Model Builder view:

.. figure:: _static/dashboard/dashboard-builder.png
   :align: center
   :alt: NDlib dashboard visual builder view
   :width: 95%

   The flowchart canvas for building custom compartmental models.

Notes
=====

The dashboard is a lightweight local service and is meant to complement, not replace, the Python API and the documented visualization modules.
