import abc
import six

__author__ = 'Giulio Rossetti'
__license__ = "BSD-2-Clause"
__email__ = "giulio.rossetti@gmail.com"


class ConfigurationException(Exception):
    """Configuration Exception"""


@six.add_metaclass(abc.ABCMeta)
class Block(object):
    """
    """

    def execute(self, *args, **kwargs):
        pass

    def compose(self, *args, **kwargs):
        pass
