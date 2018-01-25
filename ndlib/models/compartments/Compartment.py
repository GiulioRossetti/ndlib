import abc
import six

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class ConfigurationException(Exception):
    """Configuration Exception"""


@six.add_metaclass(abc.ABCMeta)
class Compartiment(object):
    """
    """

    def __init__(self, *args, **kwargs):
        self.composed = None
        if 'composed' in args[0]:
            if isinstance(args[0]['composed'], Compartiment):
                self.composed = args[0]['composed']

    def execute(self, *args, **kwargs):
        pass

    def compose(self, *args, **kwargs):
        if self.composed is not None:
            return self.composed.execute(*args, **kwargs)
        else:
            return True
