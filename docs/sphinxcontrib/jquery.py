"""Compatibility shim for older sphinx_rtd_theme releases.

Some RTD theme versions import ``add_js_files`` from ``sphinxcontrib.jquery``
while older module layouts only expose different helper names or none at all.
This shim keeps the import working in the docs build environment.
"""


def add_js_files(app):
    """Legacy helper expected by sphinx_rtd_theme.

    The current docs do not require any extra JavaScript injection here, so the
    shim is intentionally a no-op.
    """

    return None


def add_javascript_files(app):
    return add_js_files(app)
