from framework.noisemodel import NoiseModel
from tomography.benchmarkinstance import BenchmarkInstance, SINGLE

from itertools import product
import logging

logger = logging.getLogger("experiment")


class LayerLearning:
    """This class is responsible for generating circuits corresponding """
    def __init__(self, cliff_layer, procspec):
        self._procspec = procspec
        self._cliff_layer = cliff_layer
        self.single_bases = None
        self.single_pairs = None
        self.pairs = {}

        for pauli in self._procspec.model_terms:
            self.pairs[pauli] = cliff_layer.conjugate(pauli)

    #checks if a pauli term is conjugate to a different term also included in the model
    def _issingle(self, term): 
        pair = self.pairs[term]
        return pair != term and pair in self._procspec.model_terms

    def _single_bases(self):
        #The degeneracy-lifting measurements can be made simultaneously two terms have
        #have disjoint supports and the results of conjugating both by the Clifford layer
        #are also disjoint

        pairs = [
            (p,self.pairs[p]) for p in self._procspec.model_terms 
            if self._issingle(p)
            ]
        pairs_set = set([frozenset(tup) for tup in pairs])
        self.single_pairs = [tuple(pair) for pair in pairs_set]

        single_bases = []
        for p1,p2 in self.single_pairs:
            for i,pauli in enumerate(single_bases):
                pair = self._cliff_layer.conjugate(pauli)
                if pauli.separate(p1) and pair.separate(p2):
                    single_bases[i] = pauli * p2
                    break
            else:
                single_bases.append(p2)

        self.single_bases = single_bases
        logger.info("Chose single bases:")
        logger.info([str(p) for p in self.single_bases])

    def procedure(self, samples, single_samples, depths):
        """Generate the single and pair measurements required to reconstruct the noise model"""

        self.samples = samples
        self.depths = depths
        self.single_samples = single_samples

        self._single_bases()
        
        instances = []

        for basis,d,s in product(self._procspec.meas_bases, self.depths, range(self.samples)):
            inst = BenchmarkInstance(basis, basis, d, self._procspec, self._cliff_layer)
            instances.append(inst)

        for basis,s in product(self.single_bases, range(self.single_samples)):
            inst = BenchmarkInstance(self._cliff_layer.conjugate(basis), basis, SINGLE, self._procspec, self._cliff_layer, SINGLE)
            instances.append(inst)

        logger.info("Created experiment consisting of %u instances"%len(instances))
        self.instances = instances 
        return instances

    def __hash__(self):
        return self._cliff_layer.__hash__()

    def __eq__(self, other):
        return self._cliff_layer == other._cliff_layer