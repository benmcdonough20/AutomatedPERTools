from per.perinstance import PERInstance
from per.perdata import PERData


class PERRun:
    def __init__(self, processor, inst_map, per_circ, samples, noise_strengths, meas_bases, expectations):
        self._per_circ = per_circ
        self._pauli_type = per_circ._qc.pauli_type
        self._noise_strengths = noise_strengths
        self._samples = samples
        self._proc = processor
        self._meas_bases = meas_bases
        self._expectations = expectations
        self._inst_map = inst_map

        self._generate()

    def _generate(self):
        self.instances = []

        for basis in self._meas_bases:
            for lmbda in self._noise_strengths:
                for sample in range(self._samples):
                    perinst = PERInstance(self._proc, self._inst_map, self._per_circ, basis, lmbda)
                    self.instances.append(perinst)
    
    def _get_spam(self, pauli):
        n = len(self._inst_map)
        idn = pauli.ID(n)
        spam = 1 
        for i,p in enumerate(pauli): 
            b = pauli.ID(n)
            b[i] = p
            if b != idn:
                spam *= self.spam[b]
        return spam
         
    def analyze(self):
        self._data = {} #keys are expectations
        self.spam = self._per_circ.spam
        sim_meas = {}
        for inst in self.instances:

            if not inst.meas_basis in sim_meas:
                expecs = []
                for pauli in self._expectations:
                    if inst.meas_basis.simultaneous(pauli):
                        expecs.append(pauli)
                sim_meas[inst.meas_basis] = expecs

            for basis in sim_meas[inst.meas_basis]:
                if not basis in self._data:
                    spam = self._get_spam(basis)
                    self._data[basis] = PERData(basis, spam)

                self._data[basis].add_data(inst)

        for perdat in self._data.values():
            perdat.fit()

    def get_result(self, label):
        pauli = self._pauli_type(label)
        return self._data[pauli]