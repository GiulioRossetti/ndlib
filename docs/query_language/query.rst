**************************************
NDQL: Network Diffusion Query Language
**************************************

=========
Rationale
=========

===========
NDQL Syntax
===========

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


Examples
--------


Query Browser
=============
