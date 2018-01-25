.. NDlib documentation master file, created by
   sphinx-quickstart on Wed May 24 10:59:33 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. |date| date::

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

``NDlib`` is a Python software package that allows to describe, simulate, and study diffusion processes on complex networks.

================ =================== ==================  ==========  ===============
   **Date**      **Python Versions**   **Main Author**   **GitHub**      **pypl**
|date|                2.7.x/3.x      `Giulio Rossetti`_  `Source`_   `Distribution`_
================ =================== ==================  ==========  ===============

.. raw:: html

		<div style="text-align: center">
        <object width="480" height="385" align="center"><param name="movie"
        value="https://www.youtube.com/watch?v=tYHNOuKJwbE&t=172s"></param><param
        name="allowFullScreen" value="true"></param><param
        name="allowscriptaccess" value="always"></param><embed
        src="https://www.youtube.com/watch?v=tYHNOuKJwbE&t=172s"
        type="application/x-shockwave-flash" allowscriptaccess="always"
        allowfullscreen="true" width="480"
        height="385"></embed></object>
        </div>
        <br/><br/>



If you use ``NDlib`` as support to your research consider citing:

.. epigraph::

    G. Rossetti, L. Milli, S. Rinzivillo, A. Sirbu, D. Pedreschi, F. Giannotti.
    **"NDlib: a Python Library to Model and Analyze Diffusion Processes Over Complex Networks"**
    Journal of Data Science and Analytics. 2017. `DOI:0.1007/s41060-017-0086-6 <https://dx.doi.org/10.1007/s41060-017-0086-6>`_
    (pre-print available on `arXiv <https://arxiv.org/abs/1801.05854>`_)

    G. Rossetti, L. Milli, S. Rinzivillo, A. Sirbu, D. Pedreschi, F. Giannotti.
    **"NDlib: Studying Network Diffusion Dynamics"**
    IEEE International Conference on Data Science and Advanced Analytics, DSAA. 2017.


^^^^^^^^^^^^^^
NDlib Dev Team
^^^^^^^^^^^^^^

======================= ============================
**Name**                **Contribution**
`Giulio Rossetti`_      Library Design/Documentation
`Letizia Milli`_        Epidemic Models
`Alina Sirbu`_          Opinion Dynamics Model
`Salvatore Rinzivillo`_ Visual Platform
======================= ============================


.. toctree::
   :maxdepth: 1
   :hidden:

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


.. _`Giulio Rossetti`: http://www.about.giuliorossetti.net
.. _`Letizia Milli`: https://github.com/letiziam
.. _`Alina Sirbu`: https://github.com/alinasirbu
.. _`Salvatore Rinzivillo`: https://github.com/rinziv
.. _`Source`: https://github.com/GiulioRossetti/ndlib
.. _`Distribution`: https://pypi.python.org/pypi/ndlib
