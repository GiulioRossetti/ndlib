"""
The :mod:`ndlib.models.opinions` module contains common opinion dynamics network models from research literature.
"""

__author__ = 'rossetti'
__license__ = "GPL"
__email__ = "giulio.rossetti@gmail.com"

from .AlgorithmicBiasModel import AlgorithmicBiasModel
from .CognitiveOpDynModel import CognitiveOpDynModel
from .MajorityRuleModel import MajorityRuleModel
from .QVoterModel import QVoterModel
from .SznajdModel import SznajdModel
from .VoterModel import VoterModel

__all__ = [
    'AlgorithmicBiasModel',
    'CognitiveOpDynModel',
    'MajorityRuleModel',
    'QVoterModel',
    'SznajdModel',
    'VoterModel',
]
