from framework.circuitlayer import CircuitLayer

class PERCircuit:
    """Aggregation of circuit layers. Responsable for parsing a circuit to create a list of
    of circuit layers used in the benchmarking and in the PER experiments. 
    
    args: primitive.Circuit
    """

    def __init__(self, qc):
        """Initialize a PER circuit from a Circuit object
        """
        self.n = qc.num_qubits()
        self._qc = qc
        self._layers = self._circuit_to_benchmark_layers()

    def add_noise_models(self, noise_data_frame):
        """Add the Noisemodels contained in a NoiseDataFrame"""

        self.spam = noise_data_frame.spam #store spam coefficients
        #add noise models to corresponding layers (hashed by clifford instructions)
        for layer in self._layers:
                nm = noise_data_frame.noisemodels[layer.cliff_layer]
                layer.noisemodel = nm

    def overhead(self, noise_strength):
        overhead = 1
        for layer in self._layers:
            layer.noisemodel.init_scaling(noise_strength)
            overhead *= layer.noisemodel.overhead
        return overhead

    def _circuit_to_benchmark_layers(self):
        """
        input - self._qc
        output - layers (CircuitLayer)

        Breaks a circuit into layers following the pattern - 
            -> Single qubit gates + disjoint layer of self-adjoint Clifford gates
        """

        layers = []
        qc = self._qc
        inst_list = [inst for inst in qc if not inst.ismeas()] 

        #pop off instructions until inst_list is empty
        while inst_list:

            circ = qc.copy_empty() #blank circuit to add instructions
            layer_qubits = set() #qubits in the support of two-qubit clifford gates

            for inst in inst_list.copy(): #iterate through remaining instructions

                #check if current instruction overlaps with support of two-qubit gates
                #already on layer
                if not layer_qubits.intersection(inst.support()):
                    circ.add_instruction(inst) #add instruction to circuit and pop from list
                    inst_list.remove(inst)

                if inst.weight() == 2:
                    layer_qubits = layer_qubits.union(inst.support()) #add support to layer

            newlayer = CircuitLayer(circ)
            if newlayer.cliff_layer: #append only if not empty
                layers.append(CircuitLayer(circ))

        return layers
    
    def __getitem__(self, item):
        """Iterate through the PER circuit via layers"""
        return self._layers.__getitem__(item)