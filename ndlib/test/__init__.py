"""Test package compatibility helpers.

Older optional dependencies bundled with the test suite expect NetworkX APIs
that were removed in newer releases. Apply the compatibility shim before any
test module imports dynetx.
"""

try:
    import networkx.utils as _nx_utils
except Exception:
    _nx_utils = None

if _nx_utils is not None and not hasattr(_nx_utils, "is_string_like"):
    def is_string_like(obj):
        return isinstance(obj, str)

    _nx_utils.is_string_like = is_string_like

from .test_compartment import *
from .test_dynamic_compartment import *
from .test_dynamic_models import *
from .test_mpl_viz import *
from .test_ndlib import *
from .test_parallel import *
from .test_parser import *
