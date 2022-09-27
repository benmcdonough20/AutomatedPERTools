from framework.noisemodel import NoiseModel
from tomography.benchmarkinstance import BenchmarkInstance, SINGLE

from itertools import product
import logging

logger = logging.getLogger("experiment")


class LayerLearning:
    """This class is responsible for generating circuits corresponding """
    def __init__(self, cliff_layer, samples, single_samples, depths):
        self._cliff_layer = cliff_layer
        self.samples = samples
        self.depths = depths
        self.single_samples = single_samples

    #checks if a pauli term is conjugate to a different term also included in the model
    def _issingle(self, term, procspec): 
        pair = self._cliff_layer.conjugate(term)
        return pair != term and pair in procspec.model_terms

    def _single_bases(self, procspec):
        #The degeneracy-lifting measurements can be made simultaneously two terms have
        #have disjoint supports and the results of conjugating both by the Clifford layer
        #are also disjoint

        pairs = [(p,self._cliff_layer.conjugate(p)) for p in procspec.model_terms if self._issingle(p, procspec)]
        pairs_set = set([frozenset(tup) for tup in pairs])
        single_bases = []
        for p1,p2 in pairs_set:
            for i,pauli in enumerate(single_bases):
                pair = self._cliff_layer.conjugate(pauli)
                if pauli.separate(p1) and pair.separate(p2):
                    single_bases[i] = pauli * p1
                    break
            else:
                single_bases.append(p2)

        return single_bases

    def procedure(self, procspec):
        """Generate the single and pair measurements required to reconstruct the noise model"""

        single_bases = self._single_bases(procspec)
        logger.info("Chose single bases:")
        logger.info([str(p) for p in single_bases])

        instances = []

        for basis,d,s in product(procspec.meas_bases, self.depths, range(self.samples)):
            inst = BenchmarkInstance(basis, basis, d, procspec, self._cliff_layer)
            instances.append(inst)

        for basis,s in product(single_bases, range(self.single_samples)):
            inst = BenchmarkInstance(self._cliff_layer.conjugate(basis), basis, SINGLE, procspec, self._cliff_layer, SINGLE)
            instances.append(inst)

        logger.info("Created experiment consisting of %u instances"%len(instances))
        self.instances = instances 
        return instances