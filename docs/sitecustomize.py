"""Early startup shims for the documentation build.

Python imports ``sitecustomize`` automatically at startup if it is present on
``sys.path``. Because the docs build runs from ``docs/``, this file can patch
legacy dependencies before Sphinx loads the theme.
"""

try:
    import sphinxcontrib.jquery as sphinxcontrib_jquery

    if not hasattr(sphinxcontrib_jquery, "add_js_files"):
        # Older sphinx_rtd_theme releases expect this name.
        def add_js_files(app):
            return None

        sphinxcontrib_jquery.add_js_files = add_js_files
except Exception:
    # Keep the docs build resilient even if the optional module is absent.
    pass
