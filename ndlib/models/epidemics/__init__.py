"""
The :mod:`ndlib.models.epidemic` module contains common network models from epidemic research literature.
"""

from .GeneralisedThresholdModel import GeneralisedThresholdModel
from .IndependentCascadesModel import IndependentCascadesModel
from .KerteszThresholdModel import KerteszThresholdModel
from .ProfileModel import ProfileModel
from .ProfileThresholdModel import ProfileThresholdModel
from .SEIRModel import SEIRModel
from .SEISModel import SEISModel
from .SIModel import SIModel
from .SIRModel import SIRModel
from .SISModel import SISModel
from .SWIRModel import SWIRModel
from .ThresholdModel import ThresholdModel

__all__ = [
    'GeneralisedThresholdModel',
    'IndependentCascadesModel',
    'KerteszThresholdModel',
    'ProfileModel',
    'ProfileThresholdModel',
    'SEIRModel',
    'SEISModel',
    'SIModel',
    'SIRModel',
    'SISModel',
    'SWIRModel',
    'ThresholdModel',
]
