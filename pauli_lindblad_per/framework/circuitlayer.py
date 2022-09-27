from primitives.circuit import Circuit
from primitives.pauli import Pauli

from typing_extensions import Self
from typing import Tuple

class CircuitLayer:
    """When benchmarking a circuit, it first needs to be separated into layers of the form
    single qubit gates + disjoint self-adjoint two-qubit clifford gates. This class stores
    layers of this form. The layer input must be passed in with this form"""

    def __init__(self, layer : Circuit):
        """input - Circuit
        summary: parses circuit and stores single and clifford gates in separate circuits
        """
        self.layer = layer
        self.single_layer = self.separate_gates(1)
        self.cliff_layer =  self.separate_gates(2) 
        self.noisemodel = None
        self.pauli_type = self.cliff_layer.pauli_type

    def separate_gates(self, weight : int) -> Circuit:
        """This method parses the list of gates in the input layer and returns a Circuit
        consisting only of gates with the desired weight"""

        qc = self.layer.copy_empty() 
        for inst in self.layer:
            if inst.weight() == weight:
                qc.add_instruction(inst)
        return qc
    
    def sample(self, noise_strength, circ):
        """Sample from the noise-scaled representation of this circuit layer, including pauli
        twirling"""

        p_type = self.pauli_type

        self.noisemodel.init_scaling(noise_strength) #set up coefficients for sampling
        circ.compose(self.single_layer) #compose single-qubit layer

        twirl = p_type.random(circ.num_qubits()) #generate a random pauli
        circ.add_pauli(twirl)

        op, sgn = self.noisemodel.sample() #sample from noise and record sign
        circ.add_pauli(op) 

        circ.compose(self.cliff_layer)
        circ.barrier()

        #invert pauil twirl and compose into next layer for consistent noise
        circ.add_pauli(self.cliff_layer.conjugate(twirl))

        return sgn

    def __eq__(self, other : Self):
        """Two layers have the same noise profile if their clifford layers are equal. Thus,
        two layers with the same clifford gates are considered to be equal"""

        return frozenset([q for q in self.cliff_layer]) == frozenset([q for q in other.cliff_layer])

    def __hash__(self):
        """The hash function is chosed to reflect the new notion of layer equality. This may
        be unneccessary as long as __eq__ is defined for set creation, but this remains to be
        be investigated."""

        return hash(self.cliff_layer)

    def sample_PER(self, noise_model) -> Tuple[Circuit, int, Pauli]:
        """sample a PER representation of the layer"""
        pass

    def __str__(self):
        return self.layer.__str__()