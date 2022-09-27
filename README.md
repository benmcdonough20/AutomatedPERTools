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
* Proposal of noise scaling technique for Sparse Pauli-Lindblad model
* Creation of python package to automate tomography + PER for Sparse-Pauli model on arbitrary circuits
* Tutorial notebooks illustrating details of procedure

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
