from itertools import cycle, permutations, product
import logging
 
logger = logging.getLogger("experiment")


class ProcessorSpec:
    """Responsible for interacting with the processor interface to generate the Pauli bases
    and the model terms. Also stores the mapping of virtual to physical qubits for transpilation"""

    def __init__(self, inst_map, processor):
        self._n = len(inst_map)
        self._processor = processor
        self.inst_map = inst_map
        self._connectivity = processor.sub_map(inst_map)
        self.meas_bases = self._meas_bases()
        self.model_terms = self._model_terms()

    def _meas_bases(self):

        n = self._n
        NUM_BASES = 9

        bases = [['I']*n for i in range(NUM_BASES)]

        for vertex in range(n):
            #copied from Fig. S3 in van den Berg
            orderings = {"XXXYYYZZZ":"XYZXYZXYZ",
                                "XXXYYZZZY":"XYZXYZXYZ",
                                "XXYYYZZZX":"XYZXYZXYZ",
                                "XXZYYZXYZ":"XYZXZYZYX",
                                "XYZXYZXYZ":"XYZZXYYZX"}
            
            children = self._connectivity.neighbors(vertex)
            predecessors = [c for c in children if c < vertex]

            if not predecessors:
                cycp = cycle("XYZ")
                for i,_ in enumerate(bases):
                    bases[i][vertex] = next(cycp)
            #Choose p1:"XXXYYYZZZ" and p2:"XYZXYZXYZ" if one predecessor
            elif len(predecessors) == 1:
                pred, = predecessors
                #store permutation of indices so that predecessor has X,X,X,Y,Y,Y,Z,Z,Z
                _,bases = list(zip(*sorted(zip([p[pred] for p in bases], bases))))
                cycp = cycle("XYZ")
                for i,_ in enumerate(bases):
                    bases[i][vertex] = next(cycp)
            elif len(predecessors) == 2:
                pred0,pred1 = predecessors
                _,bases = list(zip(*sorted(zip([p[pred0] for p in bases], bases))))
                #list out string with permuted values of predecessor 2
                substr = [p[pred1] for p in bases]
                #match predecessor two with a permutation of example_orderings
                reordering = ""
                for perm in permutations("XYZ"):
                    substr = "".join(["XYZ"[perm.index(p)] for p in substr])
                    if substr in orderings:
                        current = orderings[substr] 
                        for i,p in enumerate(current):
                            bases[i][vertex] = p
                        break
            else:
                    raise Exception("Three or more predecessors encountered")

        bases = ["".join(b)[::-1] for b in bases]
        logger.info("Created pauli bases")
        logger.info(bases)
        return [self._processor.pauli_type(string) for string in bases]

    def _model_terms(self):
        n = self._n
        model_terms = set()
        identity = ["I"]*n 

        #get all weight-two paulis on with suport on nieghboring qubits
        for q1,q2 in self._connectivity.edge_list():
                for p1, p2 in product("IXYZ", repeat=2):
                    pauli = identity.copy()
                    pauli[q1] = p1
                    pauli[q2] = p2
                    model_terms.add("".join(reversed(pauli)))

        model_terms.remove("".join(identity))

        logger.info("Created model with the following terms:")
        logger.info(model_terms)

        return [self._processor.pauli_type(p) for p in model_terms]


    def transpile(self, circ, **kwargs):
        return self._processor.transpile(circ, self.inst_map, **kwargs)