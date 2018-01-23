.. NDlib documentation master file, created by
   sphinx-quickstart on Wed May 24 10:59:33 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

NDlib - Network Diffusion Library
=================================
.. image:: https://badge.fury.io/py/ndlib.svg
    :target: https://badge.fury.io/py/ndlib.svg

.. image:: https://img.shields.io/pypi/pyversions/ndlib.svg
   :target: https://badge.fury.io/py/ndlib

.. image:: https://secure.travis-ci.org/GiulioRossetti/ndlib.png
    :target: http://travis-ci.org/GiulioRossetti/ndlib

.. image:: https://coveralls.io/repos/GiulioRossetti/ndlib/badge.png?branch=master
    :target: https://coveralls.io/r/GiulioRossetti/ndlib?branch=master

NDlib is a Python software package that allows to describe, simulate, and study diffusion processes on complex networks.

================ =================== ==================  ==========  ===============
   **Date**      **Python Versions**   **Main Author**   **GitHub**      **pypl**
January 22, 2018      2.7.x/3.x      `Giulio Rossetti`_  `Source`_   `Distribution`_
================ =================== ==================  ==========  ===============

If you use our library in a research paper please cite the following works:

    G. Rossetti, L. Milli, S. Rinzivillo, A. Sirbu, D. Pedreschi, F. Giannotti.
    *"NDlib: a Python Library to Model and Analyze Diffusion Processes Over Complex Networks"*
    Journal of Data Science and Analytics. 2017. DOI:0.1007/s41060-017-0086-6
    (pre-print available at: https://arxiv.org/abs/1801.05854)

    G. Rossetti, L. Milli, S. Rinzivillo, A. Sirbu, D. Pedreschi, F. Giannotti.
    *"NDlib: Studying Network Diffusion Dynamics"*
    IEEE International Conference on Data Science and Advanced Analytics, DSAA. 2017.

-----
Promo
-----

.. raw:: html

        <object width="480" height="385" align="center"><param name="movie"
        value="https://www.youtube.com/watch?v=tYHNOuKJwbE&t=172s"></param><param
        name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="https://www.youtube.com/watch?v=tYHNOuKJwbE&t=172s"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="480"
        height="385"></embed></object>

--------
Contents
--------

.. toctree::
   :maxdepth: 2

   overview.rst
   download.rst
   installing.rst
   tutorial.rst
   reference/reference.rst
   custom/custom.rst
   query_language/query.rst
   rest/ndlib-rest.rst
   viz/ndlib-viz.rst
   developer/developer.rst
   bibliography.rst

----------
Developers
----------
**Models:** Letizia Milli, Alina Sirbu

**Visual Platform:** Salvatore Rinzivillo

------------
Contributors
------------
Vincenzo Caproni, Beatrice Caputo, Ettore Puccetti (SEIS model)

Elisa Salatti (SEIS, SEIR models)

.. _`Giulio Rossetti`: http://www.about.giuliorossetti.net
.. _`Source`: https://github.com/GiulioRossetti/ndlib
.. _`Distribution`: https://pypi.python.org/pypi/ndlib
