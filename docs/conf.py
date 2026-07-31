# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import sys, os

from pygments.lexers import TextLexer
from sphinx.highlighting import lexers

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
try:
    from ndlib import __version__
except ImportError:
    __version__ = u'6.0.0'

version = __version__
# The full version, including alpha/beta/rc tags.
release = version

lexers["ndql"] = TextLexer()
html_theme = "alabaster"

# -- Project information -----------------------------------------------------

project = "NDlib"
copyright = "2024, Giulio Rossetti"
author = "Giulio Rossetti"

autodoc_mock_imports = [
    'ipython', 'pygtk', 'gtk', 'gobject', 'sklearn.metrics', 'argparse', 'matplotlib', 'matplotlib.pyplot', 'numpy', 'pandas', 'dynetx', 'networkx',
                'scipy', 'salib', 'pillow', 'pyintergraph', 'igraph', 'past', 'bokeh', 'future'
]

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.mathjax",
    "sphinx.ext.githubpages",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
]


# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'

html_logo = 'ndlib_2024.png'

# The name of an image file (relative to this directory) to use as a favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
