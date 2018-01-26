import abc
import six
from ndlib.models.Block import Block

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class ConfigurationException(Exception):
    """Configuration Exception"""


@six.add_metaclass(abc.ABCMeta)
class Action(Block):
    """
    """

    def __init__(self, *args, **kwargs):
        self.composed = None
        if 'composed' in args[0]:
            if isinstance(args[0]['composed'], Block):
                self.composed = args[0]['composed']

    def execute(self, *args, **kwargs):
        pass

    def compose(self, *args, **kwargs):
        if self.composed is not None:
            return self.composed.execute(*args, **kwargs)
        else:
            return True
