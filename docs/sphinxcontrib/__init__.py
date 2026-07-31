"""Local compatibility namespace for Sphinx contrib modules.

This package exists so the documentation build can provide small shims for
legacy contrib APIs without shadowing the real Sphinx contrib namespace.
"""

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
