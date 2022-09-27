from abc import ABC, abstractmethod
from typing import List

class Instruction(ABC):

    @abstractmethod
    def name(self) -> str:
        """Returns a name to identify the type of instruction"""

    @abstractmethod
    def support(self) -> List:
        """Return an ordered list of the qubits the instruction affects nontrivially"""

    @abstractmethod
    def ismeas(self):
        """Identifies whether the instruction is a measurement"""
        pass

    def weight(self):
        """Return the number of qubits nontrivially affected by the instruction"""
        return len(self.support())

    def __hash__(self):
        #Hash the instruction based on its name and its (ordered) support
        return (self.name(),self.support()).__hash__()

    def __eq__(self, other):
        #Instructions are equal if they have the same name and the same support
        return self.name() == other.name() and self.support() == other.support()

    def __str__(self):
        return str((self.name(), self.support()))


class QiskitInstruction(Instruction):

    def __init__(self, instruction):
        self.instruction = instruction
    
    def support(self):
        return self.instruction.qubits

    def name(self):
        return self.instruction.operation.name

    def ismeas(self):
        return self.name() == "measure"