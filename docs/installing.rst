****************
Installing NDlib
****************

Before installing ``NDlib``, you need to have setuptools installed.

=============
Quick install
=============

Get ``NDlib`` from the Python Package Index at pypl_.

or install it with

.. code-block:: python

    pip install ndlib

and an attempt will be made to find and install an appropriate version that matches your operating system and Python version.

You can install the development version with

.. code-block:: python

    pip install git+http://github.com/GiulioRossetti/ndlib.git

======================
Installing from source
======================

You can install from source by downloading a source archive file (tar.gz or zip) or by checking out the source files from the GitHub source code repository.

``NDlib`` is a pure Python package; you don’t need a compiler to build or install it.

-------------------
Source archive file
-------------------
Download the source (tar.gz or zip file) from pypl_  or get the latest development version from GitHub_ 

Unpack and change directory to the source directory (it should have the files README.txt and setup.py).

Run python setup.py install to build and install

------
GitHub
------
Clone the NDlib repostitory (see GitHub_ for options)

.. code-block:: python

    git clone https://github.com/GiulioRossetti/ndlib.git

Change directory to ndlib

Run python setup.py install to build and install

If you don’t have permission to install software on your system, you can install into another directory using the --user, --prefix, or --home flags to setup.py.

For example

.. code-block:: python

    python setup.py install --prefix=/home/username/python

or

.. code-block:: python

    python setup.py install --home=~

or

.. code-block:: python

    python setup.py install --user

If you didn’t install in the standard Python site-packages directory you will need to set your PYTHONPATH variable to the alternate location. See http://docs.python.org/2/install/index.html#search-path for further details.

============
Requirements
============
------
Python
------

To use NDlib you need Python 2.7, 3.2 or later.

The easiest way to get Python and most optional packages is to install the Enthought Python distribution “Canopy” or using Anaconda.

There are several other distributions that contain the key packages you need for scientific computing. 

-----------------
Required packages
-----------------
The following are packages required by ``NDlib``.

^^^^^^^^
NetworkX
^^^^^^^^
Provides the graph representation used by the diffusion models implemented in ``NDlib``.

Download: http://networkx.github.io/download.html

-----------------
Optional packages
-----------------
The following are optional packages that ``NDlib`` can use to provide additional functions.

^^^^^
Bokeh
^^^^^
Provides support to the visualization facilities offered by ``NDlib``.

Download: http://bokeh.pydata.org/en/latest/

^^^
PIL
^^^
Enables matplotlib animations to be saved to a file, used only by ``Continuous Model`` implementations.

Download: https://pillow.readthedocs.io/en/stable/installation.html

^^^^^^
igraph
^^^^^^
Enables graphs to use layouts from the igraph library, used only by ``Continuous Model`` implementations.

Download: https://igraph.org/python/#downloads

^^^^^^^^^^^^
pyintergraph
^^^^^^^^^^^^
Enables graphs to use layouts from the igraph library, used only by ``Continuous Model`` implementations.

It helps by transforming networkx graphs to igraphs and back

Download: https://gitlab.com/luerhard/pyintergraph#installation

^^^^^
SALib
^^^^^
Enables support for sensitivity analysis, used only by ``Continuous Model Runner`` implementations.

Download: https://salib.readthedocs.io/en/latest/getting-started.html#installing-salib


--------------
Other packages
--------------
These are extra packages you may consider using with ``NDlib``

IPython, interactive Python shell, http://ipython.scipy.org/

.. _pypl: https://pypi.python.org/pypi/ndlib/
.. _GitHub: https://github.com/GiulioRossetti/ndlib/
