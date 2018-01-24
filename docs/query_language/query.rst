**************************************
NDQL: Network Diffusion Query Language
**************************************

``NDlib`` aims to an heterogeneous audience composed by technicians as well as analysts.
In order to abstract from the its programming interface we designed a query language to describe diffusion simulations, ``NDQL``.

=========
Rationale
=========

``NDQL`` is built upon the custom model definition facilities offered by ``NDlib``.

It provides a simple, declarative, syntax for describing and executing diffusion simulations by

- creating a custom model composed of
	- node statuses;
	- transition rules (expressed as combinations of ``compartments``)
- creating a synthetic graph / loading an existing network
- initialize initial nodes statuses
- run the simulation

``NDQL`` is designed to allow those users that are not familiar to the Python language to:

- abstract the technicality of the programming interface, and
- directly describe the expected model behaviour

So far, ``NDQL`` supports only static network analysis.

===========
NDQL Syntax
===========

An ``NDQL`` script is composed of a minimum set of directives:

- Model definition:
	- MODEL, STATUS, COMPARTMENT (+), IF-THEN-ELSE (+), RULE,
- Model initialization:
	- INITIALIZE
- Network specification:
	- CREATE_NETWORK ($), LOAD_NETWORK ($)
- Simulation execution:
	- EXECUTE

Directives marked with (+) are optional while the ones marked with ($) are mutually exclusive w.r.t. their class.

The complete language directive specification is the following:

.. code-block:: bash

    MODEL model_name

    STATUS status_name

    COMPARTMENT compartment_name
    TYPE compartment_type
    COMPOSE compartment_name
    [PARAM param_name numeric]*
    [TRIGGER status_name]

    IF compartment_name_1 THEN compartment_name_2 ELSE compartment_name_3 AS rule_name

    RULE rule_name
    FROM status_name
    TO status_name
    USING compartment_name

    INITIALIZE
    [SET status_name ratio]+

    CREATE_NETWORK network_name
    TYPE network_type
    [PARAM param_name numeric]*

    LOAD_NETWORK network_name FROM network_file

    EXECUTE model_name ON network_name FOR iterations


The CREATE_NETWORK directive can take as *network_type* any ``networkx`` graph generator name (*param_name* are inherited from generator function parameters).

============================
Execute/Translate NDQL files
============================

``NDlib`` installs two command line commands:
- ``NDQL_translate``
- ``NDQL_execute``

The former command allows to translate a generic, well-formed, ``NDQL`` script into an equivalent Python one. It can be executed as

.. code-block:: bash

    NDQL_translate query_file python_file

where *query_file* identifies the target ``NDQL`` script and *python_file* specifies the desired name for the resulting Python script.

The latter command allows to directly execute a generic, well-formed, ``NDQL`` script.It can be executed as

.. code-block:: bash

    NDQL_execute query_file result_file

where *query_file* identifies the target ``NDQL`` script and *result_file* specifies the desired name for the execution results.
Execution results are saved as JSON files with the following syntax:

.. code-block:: json

    [{"trends":
       {
        "node_count": {"0": [270, 179, 15, 0, 0], "1": [30, 116, 273, 256, 239], "2": [0, 5, 12, 44, 61]},
        "status_delta": {"0": [0, -91, -164, -15, 0], "1": [0, 86, 157, -17, -17], "2": [0, 5, 7, 32, 17]}
        },
        "Statuses": {"1": "Infected", "2": "Removed", "0": "Susceptible"}
     }]

where
- *node_count* describe the trends built on the number of nodes per status
- *status_delta* describe the trends built on the fluctuations of number of nodes per status
- *Statuses* provides a map from numerical id to status name

========
Examples
========

Here some example of models implemented using ``NDQL``.

---
SIR
---

.. code-block:: bash

	CREATE_NETWORK g1
	TYPE erdos_renyi_graph
	PARAM n 300
	PARAM p 0.1

	MODEL SIR

	STATUS Susceptible
	STATUS Infected
	STATUS Removed

	# Compartment definitions

	COMPARTMENT c1
	TYPE NodeStochastic
	PARAM rate 0.1
	TRIGGER Infected

	COMPARTMENT c2
	TYPE NodeStochastic
	PARAM rate 0.1

	# Rule definitions

	RULE
	FROM Susceptible
	TO Infected
	USING c1

	RULE
	FROM Infected
	TO Removed
	USING c2

	# Model configuration

	INITIALIZE
	SET Infected 0.1

	EXECUTE SIR ON g1 FOR 5
