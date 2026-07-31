"""Local compatibility shims loaded automatically by Python.

This keeps older optional dependencies working with newer NetworkX releases
without forcing the rest of the codebase to depend on deprecated APIs.
"""

try:
    import networkx.utils as _nx_utils
except Exception:
    _nx_utils = None

if _nx_utils is not None and not hasattr(_nx_utils, "is_string_like"):
    def is_string_like(obj):
        return isinstance(obj, str)

    _nx_utils.is_string_like = is_string_like
