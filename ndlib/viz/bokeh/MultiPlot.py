class MultiPlot(object):
    """Compatibility shim for the legacy bokeh-based multiplot helper.

    The original project exposed a bokeh layout wrapper here. The current code
    base ships only the matplotlib visualizations, so this class preserves the
    import path used by the old tutorial and documentation examples.
    """

    def __init__(self):
        self.plots = []

    def add_plot(self, plot):
        self.plots.append(plot)

    def plot(self, *args, **kwargs):
        return self.plots


__all__ = ["MultiPlot"]
