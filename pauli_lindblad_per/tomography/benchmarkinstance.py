from random import choices

from primitives.pauli import QiskitPauli
from tomography.processorspec import ProcessorSpec
from primitives.circuit import Circuit
from framework.instance import Instance

import logging
logger = logging.getLogger("experiment")

SINGLE = 1
PAIR = 2

class BenchmarkInstance(Instance):
    """Generates a benchmark instance implementing basis change gates, noise layer repetitions,
    Pauli twirling, and readout twirling. Stores circuit and corresponding metadata, including
    the layer to which it pertains. Fundamentally the experiment consists only of a list of
    benchmarkinstances."""

    def __init__(
        self, 
        prep_basis : QiskitPauli, 
        meas_basis : QiskitPauli, 
        noise_repetitions : int, 
        procspec : ProcessorSpec, 
        cliff_layer : Circuit, 
        type = PAIR
        ):

        self.prep_basis = prep_basis #preparation bases
        self.meas_basis = meas_basis #measurement basis
        self.cliff_layer = cliff_layer #Clifford layer profile associated with noise
        self.depth = noise_repetitions #number of repetitions of noisy layer
        self.type = type #Whether circuit is instance of pair or single measurement
        self._procspec = procspec

        super().__init__(cliff_layer, meas_basis)

    def _instance(self): #called by super().__init__

            #Generates a circuit for benchmarking. Takes as input the processor specification
            #in case piecewise transpilation is necessary.
            self._circ = self.cliff_layer.copy_empty() #storing the final circuit

            circ = self._circ

            n = self.cliff_layer.num_qubits()
            pauli_type = circ.pauli_type
            pauli_frame = pauli_type.ID(n) 

            #apply the prep operators to the circuit
            circ.compose(self.prep_basis.basis_change(circ))

            #apply repetitions of noise, including basis-change gates when needed
            for i in range(self.depth):

                twirl = pauli_type.random(n)
                pauli_frame *= twirl 
                pauli_frame = self.cliff_layer.conjugate(pauli_frame)

                circ.add_pauli(twirl)

                circ.compose(self.cliff_layer)
                circ.barrier()

            #choose string of bit flips for readout twirling
            circ.add_pauli(pauli_frame)

            #Add basis change and readout twirling
            self._basis_change()
            self._readout_twirl()

            #add measurements to the circuit and transpile
            circ.measure_all()
            self._circ = self._procspec.transpile(self._circ)