from scipy.optimize import curve_fit, OptimizeWarning
import warnings
import numpy as np
from random import choice
from collections import Counter
import logging

from tomography.benchmarkinstance import SINGLE, PAIR

logger = logging.getLogger("experiment")

warnings.simplefilter('error', OptimizeWarning) #Catch if the curve fit fails to converge

COLORS = [
    "tab:blue", 
    "tab:orange", 
    "tab:green", 
    "tab:red", 
    "tab:purple", 
    "tab:cyan", 
    "tab:brown", 
    "tab:pink", 
    "tab:gray", 
    "tab:olive"
    ]

class TermData:
    """This class stores the expectation values collected at different depths for a single
    Pauli in the sparse model. It handles fitting a fidelitiy and SPAM coefficients to this
    expectation value as well as storing and interpreting the results of degeneracy-lifting measurements"""

    def __init__(self, pauli, pair):
        self.pauli = pauli #pauli term
        self.pair = pair #conjugate by clifford layer

        self._expectations = {} #expectations at different depths
        self._count = Counter() #counts at different depths

        self._single_vals = [] #degeneracy-lifting single-depth measurements
        self._single_count = 0 #number of single-depth measurements
        self.single_fidelity = None

        self._spam = None #spam coefficients
        self._fidelity = None #fidelity
        self.pair_fidelity = None

        #Record whether the expecatation value resulted from a single or double measurement
        self.type = PAIR
    
    def add_expectation(self, depth, expectation, type):
        """Add the value of a measurement to the term data"""
        self._expectations[depth] = self._expectations.get(depth, 0) + expectation
        self._count[depth] = self._count.get(depth, 0) + 1
            
    def add_single_expectation(self, expectation):
        self._single_vals.append(expectation) #record expectation value
        self._single_count += 1

    def depths(self):
        """Return the measurement depths as a list in increasing order"""

        return list(sorted(self._expectations.keys()))

    def expectations(self):
        """Return the expectation values measured corresponding to the different depths
        in increasing order"""

        return [self._expectations[d]/self._count[d] for d in self.depths()]

    def _fit(self):
        expfit = lambda x,a,b: a*np.exp(-b*x) #Decay of twirled channel is exponential
        try: #OptimizeWarning will be caught by filter
            (a,b),_ = curve_fit(expfit, self.depths(), self.expectations(), p0 = [.8, .01], bounds = ((0,0),(1,1)))
        except:
            (a,b) = 1,0
            logger.warning("Fit did not converge!")
        return a,b

    def fit_single(self):
        """Use the measurement error obtained from the spam parameter of the conjugate term
        to make a degeneracy-lifting measurement of the fidelity"""

        #get expectation by dividing by single count and then divide by SPAM coefficient
        expectation = sum(self._single_vals)/self._single_count
        fidelity = abs(expectation)/self.spam

        #the pair measurements are more accurate, so the single-depth measurement is assumed
        #to be bounded by the fidelity that makes its pair 1
        if self.fidelity**2 > fidelity:
            logger.warning("Single-depth measurement produced fidelity greater than one: %s,%s"%(str(self.pauli), str(self.pair)))
            logger.warning("Product fidelity: %s"%str(self.fidelity))
            logger.warning("Single fidelity: %s"%str(fidelity))
            fidelity = self.fidelity**2

        self.single_fidelity = fidelity
        self.fidelity = fidelity

    def fit(self):
        """Fit the fidelity curve to an exponential decay and store the fidelity and spam
        parameters"""

        #perform fit of pair
        a,b = self._fit()
        self.spam = a
        self.pair_fidelity = np.exp(-b)
        self.fidelity = np.exp(-b)

    def graph(self, ax):
        """Graph the fidelity of the Pauli at different depths vs the exponential fit"""

        c = choice(COLORS)
        axis = np.linspace(0,max(self.depths()), 100)
        a,b = self._fit()
        ax.plot(self.depths(), self.expectations(), color = c, linestyle = 'None', marker = 'x')
        ax.plot(axis, [a*np.exp(-b*x) for x in axis], color = c)