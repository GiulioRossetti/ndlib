****************
Visual Framework
****************

``NDlib`` aims to an heterogeneous audience composed by technicians as well as analysts.
In order to abstract from the its programming interface we built a simple visual framework that allows to simulate ``NDlib`` built-in models on synthetic graphs.

.. figure:: viz.png
   :scale: 50%
   :align: center
   :alt: Framework visual interface

   Visual Framework.

**Project Website**: https://github.com/GiulioRossetti/NDLib_viz


=========
Rationale
=========

``NDlib-Viz`` aims to make non-technicians able to design, configure and run epidemic simulations, thus removing the barriers introduced by the usual requirements of programming language knowledge.
Indeed, apart from the usual research-oriented audience, we developed ``NDlib-Viz`` to support students and facilitate teachers to introduce epidemic models.
The platform itself is a web application: it can be executed on a local as well as on a remote ``NDlib-REST`` installation.

============
Installation
============

``NDlib-Viz`` requires a local active instance of ``NDlib-REST`` to be executed.

.. code-block:: bash

    # install dependencies
    npm install

    # serve with hot reload at localhost:8080
    npm run dev

    # build for production with minification
    npm run build

    # build for production and view the bundle analyzer report
    npm run build --report


For detailed explanation on how things work, checkout the `guide <http://vuejs-templates.github.io/webpack/>`_ and `docs for vue-loader <http://vuejs.github.io/vue-loader>`_.

============
Architecture
============

The Visualization Framework is a single-page web application implemented using Javascript and HTML 5.
The decoupling of the simulation engine and the visual interface allows us to exploit modern browsers to provide an efficient environment for visualization of models and interactions.

- The structure and layout of the page are managed with Bootstrap.
- The business logic and visualization of graphical widgets are implemented in D3.js.
- Nodes and edges of the networks are drawn using the Force Layout library provided by the D3 library.
- The network visualization is implemented using Canvas object provided by standard HTML5. This allows a very efficient update of the network view.
- The charts showing the Diffusion Trend and Prevalence are created using NVD3 library.

The Visualization Framework is implemented using a Model-Control-View (MCV) design pattern.
The model is managed by a central component that implements a REST API client that handle the status of the experiment.
When the user interacts with one of the views (charts, network layout, toolbar), the controller notifies the model to update the experiment.
Each interaction with the visual interface is managed by the model component that centralizes all the communications with the REST server.
The calls to the server are executed asynchronously, and the component updates the visual interface as soon as a response arrives from the server.

