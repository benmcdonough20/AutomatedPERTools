# Autonomous error mitigation based on probabilistic error reduction

Current quantum computers suffer from a level of noise that prohibits extracting useful results directly from longer computations. The figure of merit in many near-term quantum algorithms is an expectation value measured at the end of the computation, which experiences a bias in the presence of hardware noise. A systematic way to remove such bias is probabilistic error cancellation (PEC). PEC requires the noise to be fully characterized and introduces a sampling overhead which increases exponentially with circuit depth, prohibiting high-depth circuits at realistic noise levels. 
Probabilistic error reduction (PER) is a related quantum error mitigation method which largely reducing the sampling overhead by predictably reducing the noise rather than fully cancelling it. In combination with extrapolation techniques to approximate the expectation value in the zero-noise limit, the accuracy of PER can be comparable to that of PEC. PER is broadly applicable to near-term algorithms, and the autonomous implementation of PER is desirable for facilitating its widespread use. This package is intended to be a set of software tools for autonomously applying error mitigation by parsing a user-specified circuit, obtaining the necessary tomography data either through gate set tomography (GST) or a recently-developed method of sparse Pauli tomography [1], using this data to generate noise-scaled representations of circuits, and analyzing the results to obtain an error-reduced expectation value.

## Dependencies
As of writing this, Mitiq [4] dependencies are in conflict with PyGSTi [7] and PyQuil dependencies, so different environments are requierd to run the notebooks:
### Mitiq Environment
* Mitiq: 0.16.0
* Numpy: 1.20.3
* Scipy: 1.7.3
### Main Environment
* Qiskit: 0.37.0
* PyQuil: 3.1.0
* Numpy: 1.22.4

## Features
* Use of PyGSTi + Mitiq for QPD channel repersentations on Rigetti hardware
* Application of canonical noise scaling [2] to sparse Pauli noise model
* Proposal of parameter scaling technique for applying PER to sparse Pauli model
* Implementation of sparse Pauli model learning procedure for arbitrary circuit layers consisting of single-qubit gates and self-adjoint two-qubit Clifford gates
* Package for easily importing this procedure as part of a Qiskit or PyQuil workflow
* Routine for parsing an arbitrary circuit to generate benchmark procedure

## Features that are not currently implemented
* Complete testing suite
* Scalable GST under no-crosstalk assumptions
* Generation of error-reduced circuits
* Incorporation of Qiskit and PyQuil experiment frameworks
* Parametric compilation of benchmark circuits

## Project Structure
The structure of the package follows the research process involved in development. The progression can be viewed in the following order:

### PyGSTi_Mitiq
This folder shows the use of PyGSTi and Mitiq to carry out gate set tomography on a processor and use these to create QPD representations of quantum channels. Canonical noise scaling can be applied to these representations to apply PER to these circuits. Although gate set tomography is not scalable, a current area of expansion of this project is using assumptions about the level of crosstalk to reduce the scaling of the GST to constant in the number of qubits.
* `GetGSTData` - This notebook demonstrates how to use PyGSTi to generate QUIL circuits to carry out GST on an example gate set.
* `ProcessGSTData` - This shows how to process the data to obtain superoperator representations of noisy channels.
* `MitiqQPDRepresentation` - Here the data obtained from the example gate set tomography is combined with the tools in Mitiq to arrive at a QPD representation of an ideal quantum channel.

### SingleQubit
This folder contains an illustration of the sparse Pauli-Lindblad noise learning process for single qubit gates and a proof-of-concept demonstration of the application of different methods for PER applied to this model.
* `LearningTheModel` - This notebook demonstrates the technique for efficiently carrying out noise twirling and measurement of Pauli fidelities on a single qubit, and then shows how to use the obtained fidelities to fit the sparse noise model.
* `OneQubitCanonicalNoiseScaling` - This shows how canonical noise scaling can be applied to the sparse model obtained through the Pauli tomography process, and explores some of the issues that the canonical noise scaling model poses for scalability of the technique.
* `OneQubitParameterScaling` - Here, the issues with canonical noise scaling are resolved by proposing a new technique called *parameter scaling* to apply PER to the sparse Pauli model. It is also shown how virtual zero-noise extrapolation (VZNE) can be used to improve the accuracy of PER.

### MultiQubit
This folder contains notebooks which extend the learning procedure to an arbitrary number of qubits.
* `SingleQubitGateLearning` - This notebook carries out a simplified learning procedure on a layer of arbitrary single-qubit gates in simulation. It is shown that the twirled noise can accurately approximate a non-pauli amplitude-damping noise model.
* `TwoQubitGateLearning` - This notebook shows how several modifications of the same procedure can extend it to include two-qubit self-adjoint Clifford gates. This enables the procedure to by applied to a complete gate set. A test noise model is used to demonstrate the efficacy of the procedure.

### TomographyProcedure
This notebook combines all of the parts of the learning procedure into a program which can be used to easily implement the sparse model learning procedure and return the model coefficients associated with an arbitrary circuit layer.
* `TomographyProcedure` - This notebook gives a step-by-step walkthrough of how the sparse noise model learning procedure is implemented for an arbitrary circuit layer.
* `QiskitImplementation` - This packages the procedure outlined in the previous notebook into a set of classes which can easily be imported and run to abstract the details of the learning procedure.
* `PyQuilImplementation` - This package removes all of the Qiskit dependencies and implements the same procedure natively for Rigetti backends

### ArbitraryCircuit

* `CircuitDecomposition` - This notebook shows how an arbitrary `QuantumCircuit` object, complete with measurements, can be parsed to create a sequence of layers satisfying the requirements for benchmarking using the sparse Pauli tomography procedure
* `ProcedureGeneration` - Here, the procedure generation for individual layers and the circuit parsing routine are put together to generate a full sparse Pauli tomography experiment for the layers in an arbitrary circuit. Once the analysis is integrated, this will make the benchmarking procedure fully autonomous. This notebook is not complete, so it may be disorganized and confusing!

## Credits
Project Advisor: [Dr. Peter Orth](https://faculty.sites.iastate.edu/porth/)

Collaborators:
* Anrea Mari
* Nathan Shammah
* Nathaniel T. Stemen
* Misty Wahl
* William J. Zeng

My thanks also go to Ewout van den Berg, Zlatko K. Minev, Abhinav Kandala, and Kristan Temme, whose work [Probabilistic error cancellation with sparse Pauli-Lindblad models on noisy quantum processors](https://arxiv.org/abs/2201.09866) heavily influenced this project, for graciously donating their time to answer my questions.

## References

[1] Ewout van den Berg, Zlatko K Minev, Abhinav Kandala, and Kristan Temme. Probabilistic error cancel-
lation with sparse pauli-lindblad models on noisy quantum processors. arXiv preprint arXiv:2201.09866,
2022.

[2] Andrea Mari, Nathan Shammah, and William J Zeng. Extending quantum probabilistic error cancella-
tion by noise scaling. Physical Review A, 104(5):052607, 2021.

[3] Ewout van den Berg, Zlatko K Minev, and Kristan Temme. Model-free readout-error mitigation for
quantum expectation values. arXiv preprint arXiv:2012.09738, 2020.

[4] R LaRose, A Mari, N Shammah, P Karalekas, and W Zeng. Mitiq: A software package for error
mitigation on near-term quantum computers, 2020.

[5] Steven T Flammia and Joel J Wallman. Efficient estimation of pauli channels. ACM Transactions on
Quantum Computing, 1(1):1–32, 2020.

[6] Michael A Nielsen and Isaac Chuang. Quantum computation and quantum information, 2002.

[7] Erik Nielsen, Kenneth Rudinger, Timothy Proctor, Antonio Russo, Kevin Young, and Robin Blume-
Kohout. Probing quantum processor performance with pygsti. Quantum science and technology,
5(4):044002, 2020.
