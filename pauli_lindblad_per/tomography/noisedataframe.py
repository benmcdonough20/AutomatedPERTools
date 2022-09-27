from framework.noisemodel import NoiseModel
from typing import List, Dict

class NoiseDataFrame:
    """Aggregates the noise models and spam errors from the learning procedure for use in PER."""

    def __init__(self, noisemodels : List[NoiseModel], spam_fidelities : Dict):
        """Creates a dictionary of learned noise models indexed by clifford layer (hashed by instructions),
        stores spam coefficients

        Args:
            noisemodels (list[LayerNoiseModel]): LayerNoiseModels from tomography
            spam_fidelities (dict[Pauli]): spam coefficients from tomography
        """

        self.noisemodels = {}
        for nm in noisemodels:
            self.noisemodels[nm.cliff_layer]  = nm

        self.spam = spam_fidelities

    def init_scaling(self, noise_strength):
        """Initializes the noise model with the scaling method at strength <noise_strength>"""

        for nm in self.noisemodels.values():
            nm.init_scaling(noise_strength)

    def init_tuning(self, noise_params):
        """Initializes the noise model with the tuning method with <noise_params>"""

        for nm in self.noisemodels.values():
            nm.init_tuning(noise_params)