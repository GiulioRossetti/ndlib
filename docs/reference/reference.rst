***********************************
Network Diffusion Library Reference
***********************************

In this section are introduced the components that constitute ``NDlib``, namely

- The implemented diffusion models (organized in **Epidemics** and **Opinion Dynamics**)
- The methodology adopted to configure a general simulation
- The visualization facilities embedded in the library to explore the results

Advanced topics (Custom model definition, Network Diffusion Query language (NDQL), Experiment Server and Visual Framework) are reported in separate sections.

================
Diffusion Models
================
The analysis of diffusive phenomena that unfold on top of complex networks is a task able to attract growing interests from multiple fields of research. 

In order to provide a succinct framing of such complex and extensively studied problem it is possible to split the related literature into two broad, related, sub-classes: **Epidemics** and **Opinion Dynamics**.

Moreover, ``NDlib`` also supports the simulation of diffusive processes on top of evolving network topologies: the **Dynamic Network Models** section the ones ``NDlib`` implements.

---------
Epidemics
---------

When we talk about epidemics, we think about contagious diseases caused by biological pathogens, like influenza, measles, chickenpox and sexually transmitted viruses that spread from person to person. 
However, other phenomena can be linked to the concept of epidemic: think about the spread of computer virus [#]_ where the agent is a malware that can transmit a copy of itself from computer to computer, or the spread of mobile phone virus [#]_ [#]_, or the diffusion of knowledge, innovations, products in an online social network [#]_ - the so-called “social contagion”, where people are making decision to adopt a new idea or innovation.

Several elements determine the patterns by which epidemics spread through groups of people: the properties carried by the pathogen (its contagiousness, the length of its infectious period and its severity), the structure of the network as well as the mobility patterns of the people involved. Although often treated as similar processes, diffusion of information and epidemic spreading can be easily distinguished by a single feature: the degree of activeness of the subjects they affect.

Indeed, the spreading process of a virus does not require an active participation of the people that catch it (i.e., even though some behaviors acts as contagion facilitators – scarce hygiene, moist and crowded environment – we can assume that no one chooses to get the flu on purpose); conversely, we can argue that the diffusion of an idea, an innovation, or a trend strictly depend not only by the social pressure but also by individual choices.

In ``NDlib`` are implemented the following **Epidemic** models:

.. toctree::
   :maxdepth: 1

   models/epidemics/SIm.rst
   models/epidemics/SIS.rst
   models/epidemics/SIR.rst
   models/epidemics/SEIR.rst
   models/epidemics/SEIR_ct.rst
   models/epidemics/SEIS.rst
   models/epidemics/SEIS_ct.rst
   models/epidemics/SWIR.rst
   models/epidemics/Threshold.rst
   models/epidemics/GeneralisedThreshold.rst
   models/epidemics/KThreshold.rst
   models/epidemics/IndependentCascades.rst
   models/epidemics/Profile.rst
   models/epidemics/ProfileThreshold.rst
   models/epidemics/UTLDR.rst
   models/epidemics/ICEP.rst
   models/epidemics/ICP.rst
   models/epidemics/ICE.rst


----------------
Opinion Dynamics
----------------

A different field related with modelling social behaviour is that of opinion dynamics.

Recent years have witnessed the introduction of a wide range of models that attempt to explain how opinions form in a population [#]_, taking into account various social theories (e.g. bounded confidence [#]_ or social impact [#]_). 

These models have a lot in common with those seen in epidemics and spreading. 
In general, individuals are modelled as agents with a state and connected by a social network. 

The social links can be represented by a complete graph (mean field models) or by more realistic complex networks, similar to epidemics and spreading. 

The state is typically represented by variables, that can be discrete (similar to the case of spreading), but also continuous, representing for instance a probability to choose one option or another [#]_ . The state of individuals changes in time, based on a set of update rules, mainly through interaction with the neighbours. 

While in many spreading and epidemics models this change is irreversible (susceptible to infected), in opinion dynamics the state can oscillate freely between the possible values, simulating thus how opinions change in reality. 

A different important aspect in opinion dynamics is external information, which can be interpreted as the effect of mass media. 
In general external information is represented as a static individual with whom all others can interact, again present also in spreading models. 
Hence, it is clear that the two model categories have enough in common to be implemented under a common framework, which is why we introduced both in our framework.

In ``NDlib`` are implemented the following **Opinion Dynamics** models:

.. toctree::
   :maxdepth: 1

   models/opinion/Voter.rst
   models/opinion/QVoter.rst
   models/opinion/MajorityRule.rst
   models/opinion/Snajzd.rst
   models/opinion/COD.rst
   models/opinion/AlgorithmicBias.rst
   models/opinion/AlgorithmicBiasMedia.rst
   models/opinion/ARWHK.rst
   models/opinion/WHK.rst
   models/opinion/HK.rst



----------------------
Dynamic Network Models
----------------------

Network topology may evolve as time goes by.

In order to automatically leverage network dynamics ``NDlib`` enables the definition of diffusion models that work on *Snapshot Graphs* as well as on *Interaction Networks*.

In particular ``NDlib`` implements dynamic network versions of the following models:

.. toctree::
   :maxdepth: 1

   models/dynamics/dSI.rst
   models/dynamics/dSIS.rst
   models/dynamics/dSIR.rst
   models/dynamics/dKThreshold.rst
   models/dynamics/dProfile.rst
   models/dynamics/dProfileThreshold.rst


===================
Model Configuration
===================

``NDlib`` adopts a peculiar approach to specify the configuration of expetiments.
It employs a centralyzed system that take care of:

1. Describe a **common syntax** for model configuration;
2. Provide an interface to set the **initial conditions** of an experiment (nodes/edges properties, initial nodes statuses)

.. toctree::
   :maxdepth: 1
   
   mconf/Mconf.rst

===========
NDlib Utils
===========

The ``ndlib.utils`` module contains facilities that extend the simulation framework (i.e., automated multiple executions).

.. toctree::
   :maxdepth: 1

   utils/multiple_run.rst

=============
Visualization
=============

In order to provide an easy proxy to study diffusion phenomena and compare different configurations as well as models ``NDlib`` offers built-in visualization facilities.

In particular, the following plots are made available:

----------
Pyplot Viz
----------

**Classic Visualizations**

.. toctree::
   :maxdepth: 1

   viz/mpl/DiffusionTrend.rst
   viz/mpl/DiffusionPrevalence.rst
   viz/mpl/OpinionEvolution.rst


**Model Comparison Visualizations**

.. toctree::
   :maxdepth: 1

   viz/mpl/TrendComparison.rst
   viz/mpl/PrevalenceComparison.rst

   

.. [#] P. Szor, “Fighting computer virus attacks.” USENIX, 2004.
.. [#] S. Havlin, “Phone infections,” Science, 2009.
.. [#] P.Wang,M.C.Gonzalez,R.Menezes,andA.L.Baraba ́si,“Understanding the spread of malicious mobile-phone programs and their damage potential,” International Journal of Information Security, 2013.
.. [#] R. S. Burt, “Social Contagion and Innovation: Cohesion Versus Structural Equivalence,” American Journal of Sociology, 1987.
.. [#] A. Sırbu, V. Loreto, V. D. Servedio, and F. Tria, “Opinion dynamics: Models, extensions and external effects,” in Participatory Sensing, Opinions and Collective Awareness. Springer International Publishing, 2017, pp. 363–401.
.. [#] G. Deffuant, D. Neau, F. Amblard, and G. Weisbuch, “Mixing beliefs among interacting agents,” Advances in Complex Systems, vol. 3, no. 4, pp. 87–98, 2000.
.. [#] K. Sznajd-Weron and J. Sznajd, “Opinion evolution in closed community,” International Journal of Modern Physics C, vol. 11, pp. 1157–1165, 2001.
.. [#] A. Sırbu, V. Loreto, V. D. Servedio, and F. Tria, “Opinion dynamics with disagreement and modulated information,” Journal of Statistical Physics, pp. 1–20, 2013.
