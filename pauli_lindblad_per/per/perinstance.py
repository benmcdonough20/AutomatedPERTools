"""Take in a per circuit with expectation value and return a single sampled instance"""
from framework.instance import Instance

class PERInstance(Instance):
    """Represents a single circuit to be run with PER. Stores the original circuit to sample
    from the layers. Implements Pauli twirling, readout twirling, and measurement in an instance
    arbtrary basis. Stores result and computes expectation values on result."""

    def __init__(
        self, 
        processor,
        inst_map,
        percirc, 
        meas_basis, 
        noise_strength):
        
        self._percirc = percirc #the base circuit to sample from
        self._processor = processor #for transpilation
        self.noise_strength = noise_strength #noise-scaled strength
        self.meas_basis = meas_basis #measurement basis
        self.pauli_type = percirc._qc.pauli_type
        self._inst_map = inst_map

        super().__init__(percirc._qc, meas_basis) #call self._instance

    def _instance(self): #called automatically by super().__init__
        
        self._circ = self._circ.copy_empty()
        circ = self._circ
        self.sgn_tot = 0
        self.overhead = 1
       
       #Sample from each layer and compose together 
        for layer in self._percirc:
            sgn = layer.sample(self.noise_strength,circ)
            self.sgn_tot ^= sgn
            self.overhead *= layer.noisemodel.overhead 

        #implement basis change and readout twirling
        self._basis_change()
        self._readout_twirl()
        
        circ.measure_all()
        #transpile to reduce unnecessary single-qubit gates
        self._circ = self._processor.transpile(self._circ, self._inst_map)

    def get_adjusted_expectation(self, pauli):
        """Returns the expectation value reported by the parent class, but with the sign
        and overhead from the error mitigation"""

        expec = self.get_expectation(pauli)
        return expec * self.overhead * (-1)**self.sgn_tot