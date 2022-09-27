import numpy as np
from random import random

SCALING = "scaling"
LOCAL_DEPOL = "ldepol"
CROSSTALK_SCALING = "ctscale"


class NoiseModel:
    """ Stores noise parameters, computes probabilities and overhead to perform noise scaling and
    tuning, provides a sampling method to automatically sample from the partial noise inverse
    """

    def __init__(self, cliff_layer, model_terms, coefficients):
        """Initalizes a noise model with the associate clifford layer, model terms, and the
        coefficients learned from tomography.

        Args:
            cliff_layer (Circuit): The clifford layer corresponding to this noise profile
            model_terms (list): The terms considered in the sparse model
            coefficients (list): The coefficients of these terms in the generator
        """

        self.cliff_layer = cliff_layer
        self.coeffs = list(zip(model_terms, coefficients))
        self.pauli_type = cliff_layer.pauli_type

    def init_scaling(self, strength):
        """Set up noise coefficients for scaling
        """
        new_coeffs = [(term, strength*coeff) for term,coeff in self.coeffs]
        self._init_tuning(new_coeffs)

    def _init_tuning(self, noise_params):
        """Noise scaling is cast as a specific case of a more general noise tuning, which is
        is implemented here"""

        new_coeffs =  dict(noise_params)
        new_probs = []

        #sample p_k with probability w_k^{phi-lambda}, change sign if phi_k < lambdak
        for pauli, lambdak in self.coeffs:
            phik = new_coeffs.get(pauli, 0)
            new_prob = .5*(1-np.exp(-2*abs(phik-lambdak)))
            sgn = 0

            if phik < lambdak:
                sgn = 1
            new_probs.append((pauli, new_prob, sgn))
       
        #compute overhead as the product of overheads of terms which are downscaled 
        overhead = 1
        for pauli, lambdak in self.coeffs:
            phik = new_coeffs[pauli]
            if phik < lambdak:
                overhead *= np.exp(2*(lambdak-phik))

        self.probs = new_probs
        self.overhead = overhead

    def sample(self):
        """Sample from the QPD representation of the partial inverse and return the sign."""

        operator = self.pauli_type("I"*self.cliff_layer.num_qubits())
        sgn_tot = 0

        for term, prob, sgn in self.probs:
            if random() < prob: #sample with probability prob
                operator *= term #compose into product
                sgn_tot ^= sgn #record sign

        return operator, sgn_tot

    def terms(self):
        return list(zip(*self.coeffs))[0]

    def coeffs(self):
        return list(zip(*self.coeffs))[1]