from scipy.optimize import nnls
import numpy as np
from matplotlib import pyplot as plt

from framework.noisemodel import NoiseModel
from tomography.termdata import TermData, COLORS
from primitives.circuit import Circuit
from primitives.pauli import Pauli
from tomography.benchmarkinstance import BenchmarkInstance, SINGLE, PAIR

import logging
from itertools import cycle

logger = logging.getLogger("experiment")

class LayerNoiseData:
    """This class is responsible for aggregating the data associated with a single layer,
    processing it, and converting it into a noise model to use for PER"""

    def __init__(self, layer : Circuit):
        self._term_data = {} #keys are terms and the values are TermDatas
        self.cliff_layer = layer #LayerNoiseData is assocaited with a clifford layer

        #used to reduce computational complexity of determining simulatanous measurements
        self.sim_measurements = {}

    def sim_meas(self, inst, pauli, procspec):
        """Given an instance and a pauli operator, determine how many terms can be measured"""
        pair = inst.cliff_layer.conjugate(pauli)
        if inst.type == SINGLE:
            return [term for term in procspec.model_terms if pauli.simultaneous(term) and pair.simultaneous(self.cliff_layer.conjugate(term))]
        elif inst.type == PAIR:
            return [term for term in procspec.model_terms if pauli.simultaneous(term)]

    def add_expectation(self, inst : BenchmarkInstance, procspec):
        """Add the result of a benchmark instance to the correct TermData object"""

        basis = inst.meas_basis
            
        if not basis in self.sim_measurements:
            self.sim_measurements[basis] = self.sim_meas(inst, basis, procspec)

        for pauli in self.sim_measurements[basis]:
            pair = self.cliff_layer.conjugate(pauli) #get the pair of the pauli term
            if not pauli in self._term_data: #add key to dictionary if it does not exist
                self._term_data[pauli] = TermData(pauli, pair)

            #add the expectation value to the data for this term
            self._term_data[pauli].add_expectation(inst.depth, inst.get_expectation(pauli), inst.type)

        
    def fit_noise_model(self):
        """Fit all of the terms, and then use obtained SPAM coefficients to make degerneracy
        lifting estimates"""

        for term in self._term_data.values(): #perform all pairwise fits
            term.fit()
        
        logger.info("Fit noise model with following fidelities:") 
        logger.info([term.fidelity for term in self._term_data.values()])

        #get noise model from fits
        self.nnls_fit()

    def _issingle(self, term):
        return term.pauli != term.pair and term.pair in self._term_data
  
    
    def nnls_fit(self):
        """Generate a noise model corresponding to the Clifford layer being benchmarked
        for use in PER"""

        def sprod(a,b): #simplecting inner product between two Pauli operators
            return int(not a.commutes(b))

        F1 = [] #First list of terms
        F2 = [] #List of term pairs
        fidelities = [] # list of fidelities from fits

        for datum in self._term_data.values():
            F1.append(datum.pauli)
            fidelities.append(datum.fidelity)
            #If the Pauli is conjugate to another term in the model, a degeneracy is present
            if self._issingle(datum):
                F2.append(datum.pauli)
            else:
                pair = datum.pair
                F2.append(pair)

        #create commutativity matrices
        M1 = [[sprod(a,b) for a in F1] for b in F1]
        M2 = [[sprod(a,b) for a in F1] for b in F2]

        #check to make sure that there is no degeneracy
        if np.linalg.matrix_rank(np.add(M1,M2)) != len(F1):
            raise Exception("Matrix is not full rank, something went wrong!")
       
        #perform least-squares estimate of model coefficients and return as noisemodel 
        coeffs,_ = nnls(np.add(M1,M2), -np.log(fidelities)) 
        self.noisemodel = NoiseModel(self.cliff_layer, F1, coeffs)

    def _model_terms(self, links): #return a list of Pauli terms with the specified support
        groups = []
        for link in links:
            paulis = []
            for pauli in self._term_data.keys():
                overlap = [pauli[q].to_label() != "I" for q in link]
                support = [p.to_label() == "I" or q in link for q,p in enumerate(pauli)]
                if all(overlap) and all(support):
                    paulis.append(pauli)
            groups.append(paulis)

        return groups

    def get_spam_coeffs(self):
        """Return a dictionary of the spam coefficients of different model terms for use in 
        readout error mitigation when PER is carried out."""

        return dict(zip(self._term_data.keys(), [termdata.spam for termdata in self._term_data.values()]))

    def plot_coeffs(self, *links):
        """Plot the model coefficients in the generator of the sparse model corresponding
        to the current circuit layer"""

        coeffs_dict = dict(self.noisemodel.coeffs)
        groups = self._model_terms(links)
        fig, ax = plt.subplots()
        colcy = cycle(COLORS)
        for group in groups:
            c = next(colcy)
            coeffs = [coeffs_dict[term] for term in group]
            ax.bar([term.to_label() for term in group], coeffs, color=c)

    def graph(self, *links):
        """Graph the fits values for a certain subset of Pauli terms"""

        groups = self._model_terms(links)
        fig, ax = plt.subplots()
        for group in groups:
            for term in group:
                termdata = self._term_data[term]
                termdata.graph(ax)

        return ax

    def plot_infidelitites(self, *links):
        """Plot the infidelities of a subset of Pauli terms"""

        groups = self._model_terms(links)
        fig, ax = plt.subplots()
        colcy = cycle(COLORS)
        for group in groups:
            c = next(colcy)
            infidelities = [1-self._term_data[term].fidelity for term in group]
            ax.bar([term.to_label() for term in group], infidelities, color=c)
        return ax