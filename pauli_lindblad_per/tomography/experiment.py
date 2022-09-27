from tomography.processorspec import ProcessorSpec
from tomography.layerlearning import LayerLearning
from tomography.analysis import Analysis
from framework.percircuit import PERCircuit
from per.perexperiment import PERExperiment

from typing import List, Any
import logging
 
logging.basicConfig(filename="experiment.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

logger = logging.getLogger("experiment")
logger.setLevel(logging.INFO)

from primitives.circuit import QiskitCircuit
from primitives.processor import QiskitProcessor
import pickle

class SparsePauliTomographyExperiment:
    """This class carries out the full experiment by creating and running a LayerLearning
    instance for each distinct layer, running the analysis, and then returning a PERCircuit
    with NoiseModels attached to each distinct layer"""

    def __init__(self, circuits, inst_map, backend):

        circuit_interface = None

        if circuits[0].__class__.__name__ == "QuantumCircuit":
            circuit_interface = QiskitCircuit
            processor = QiskitProcessor(backend)
        else:
            raise Exception("Unsupported circuit type")
    
        self._profiles = set()
        for circuit in circuits: 
            circ_wrap = circuit_interface(circuit)
            parsed_circ = PERCircuit(circ_wrap)
            for layer in parsed_circ._layers:
                if layer.cliff_layer:
                    self._profiles.add(layer.cliff_layer)

        logger.info("Generated layer profile with %s layers:"%len(self._profiles))
        for layer in self._profiles:
            logger.info(layer)

        self._procspec = ProcessorSpec(inst_map, processor)
        self.instances = []
        self.analysis = Analysis(self._procspec)
        self._inst_map = inst_map

    def generate(self, samples, single_samples, depths):
        """This method is used to generate the experimental benchmarking procedure. The samples
        are the number of times to sample from the Pauli twirl. The single_samples controls
        how many twirl samples to take from the degeneracy-lifting measurements. It may desirable
        to make this higher since the error on these measurements will generally be higher.
        The depths control the different circuit depths to use for the exponential fits."""

        if len(depths) < 2:
            raise Exception("Exponental fit required 3 or more depth data points.")

        self.instances = []
        for l in self._profiles:
            learning = LayerLearning(l, samples, single_samples, depths)
            self.instances += learning.procedure(self._procspec)

    def run(self, executor):
        """This method produces a list of circuits in the native representation, passes them 
        as a list to the executor method, and associates the result with the benchmark instances
        that produced it"""

        for l in self._profiles:
            circuits = [inst.get_circuit() for inst in self.instances]

        results = executor(circuits)

        for res,inst in zip(results, self.instances): #TODO: find out if order can be preserved
            inst.add_result(res)

    def analyze(self):
        """Runs analysis on each layer representative and stores for later plotting/viewing"""
        self.analysis.analyze(self.instances)
        return self.analysis.noisedataframe

    def create_per_experiment(self, circuits : Any) -> PERExperiment:
        experiment = PERExperiment(circuits, self._inst_map, self.analysis.noisedataframe, backend = None, processor = self._procspec._processor)
        return experiment

    def save(self):
        raise NotImplementedError()

    def load(self):
        raise NotImplementedError()
