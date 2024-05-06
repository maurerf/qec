from qiskit import QuantumCircuit
from itertools import product
from qiskit_aer import AerSimulator
import numpy as np
from scipy.optimize import minimize

def init_A(n, shots, basis):
    A = np.zeros((2**n, 2**n))
    #gesamt_counts = [] #TODO: what is this for?
    for a, element in enumerate(basis):
        qc = QuantumCircuit(n)
        for num, i in enumerate(element):
            if i==1:
                qc.x(num)
        qc.measure_all()
        simulator = AerSimulator(method="statevector")
        counts = simulator.run(qc, shots=shots).result().get_counts(qc)
        for b, component in enumerate(basis):
            # component must be inverted due to qiskit counts being inverted
            component = ''.join([str(i) for i in component][::-1])
            if component in counts:
                A[a][b] = counts[component]/shots
            
        #gesamt_counts.append(counts)
    return A

#for task b)
def minimize_scalar_function_with_norm_constraint(func, initial_guess, norm_constraint=1):
    # Define the norm constraint function
    def norm_constraint_function(x):
        return np.linalg.norm(x) - norm_constraint
    bounds = [(0, None) for _ in range(len(initial_guess))]
    # Define the optimization problem with constraints
    constraints = [{'type': 'eq', 'fun': norm_constraint_function}]
    result = minimize(lambda x: func(x), initial_guess, bounds=bounds, constraints=constraints)

    return result.x, result.fun

def p_mit_optimization(p):
    #p_true = np.array([0.34,0.34,0.34,0.34,0.34,0.34,0.34,0.34])
    p_true = np.array([1,0,0,0,0,0,0,0]) #TODO: move this?
    p_raw = A@p_true
    return np.linalg.norm(A @ p - p_raw)


# for task c)
def measure_bell(measurements):
    counts = []
    for measurement in measurements:
        # Init Bell State
        qc = QuantumCircuit(2,2)
        qc.h(0)
        qc.cx(0,1)
        
        # Measure
        for a, op in enumerate(measurement):
            if op == 'X':
                qc.h(a)
                qc.measure(a,a)
            if op == 'Z':
                qc.measure(a,a)
            if op == 'Y':
                qc.sdg(a)
                qc.h(a)
                qc.measure(a,a)
        simulator = AerSimulator(method="statevector")
        count = simulator.run(qc, shots=shots).result().get_counts(qc)
        
        counts.append(count)
    return counts

if __name__ == "__main__":
    # a)
    n = 3
    shots = 1000
    basis=[]
    for i in product([0,1], repeat = n):
        basis.append(i)
    A = init_A(n, shots, basis)
    
    # b)
    # Simulate readout error
    A[0][0] = 0.9
    A[1][0] = 0.05
    A[2][0] = 0.05
    A[2][2] = 0.9
    A[3][2] = 0.05
    A[5][2] = 0.05
    initial_guess = np.array([0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125])
    print(minimize_scalar_function_with_norm_constraint(p_mit_optimization, initial_guess))
    print(A)
    
    # c)
    c_result = measure_bell(['XI', 'IX', 'XX', 'YI', 'IY', 'YY', 'ZI', 'IZ', 'ZZ'])
    print(c_result)
    
    # d)
    
    # e)