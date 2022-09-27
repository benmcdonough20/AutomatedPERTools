import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit

class PERData:
    """Aggregate the data for runs of PER on a single circuit for multiple noise strengths and 
    a single expectation value"""

    def __init__(self, pauli, spam):
        """Initializes a data instance for a single expectation value

        Args:
            pauli (Pauli): 
            spam (dict[Pauli]): spam coefficients from learning procedure
        """

        self.pauli = pauli
        self.spam = spam
        self._data = {}
        self._counts = {} #keep track of the number of data points for each depth

    def add_data(self, inst):
        """Add data from a PERInstance to the class. Compute the expectation value and store
        as a function of noise strength

        Args:
            inst (PERInstance): a run of PER
        """

        strength = inst.noise_strength
        expectation = inst.get_adjusted_expectation(self.pauli) #get mitigated, untwirled expectation value

        #TODO: non-local spam approximation
        expectation /= self.spam 

        #update estimator of expectation value
        self._data[strength] = self._data.get(strength, 0) + expectation
        self._counts[strength] = self._counts.get(strength, 0)+1

    def get_expectations(self):
        """returns a list of expectation values in order of increasing noise
        """
        return [self._data[s]/self._counts[s] for s in self.get_strengths()]

    def get_strengths(self):
        """returns the noise strengths in increasing order"""
        return list(sorted(self._data.keys()))

    def fit(self):
        """Perform an exponential fit of the expectation value as a function of the noise strength.
        
        - In the large noise limit,
        the noise is completely depolarizing, and all expectation values tend toward zero.

        - A more thorough investigation of how non-clifford gates affect this behavior should be
        carried out.

        - One possibility is that taking advantage of noise tuning to predictably scale the noise
        would allow for a more reliable fit
        """ 
        
        expfit = lambda x,a,b: a*np.exp(b*x)
        popt, pcov = curve_fit(
            expfit, self.get_strengths(), 
            self.get_expectations(), 
            bounds = [(-1.5, -1),(1.5,0)] #b > 0 is enforced. Technically |a| <= 1 could also be enforced
            #to improve the accuracy, but this feels a bit like cheating 
            )
        a,b = popt
        self.expectation = a
        return a,b

    def plot(self):
        """Plots the expectation values against an exponential fit.
        """

        fig, ax = plt.subplots()
        ax.plot(self.get_strengths(), self.get_expectations())
        a,b = self.fit()
        xlin = np.linspace(0, max(self.get_strengths()), 100)
        ax.plot(xlin, [a*np.exp(b*x) for x in xlin])
        return ax

    