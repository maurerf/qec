from qiskit import *
from qiskit_aer import AerSimulator
from qiskit.visualization import *
import matplotlib.pyplot as plt
# from qiskit import IBMQ
from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler


def create_shor(clbits: int = 0):
    if clbits == 0:
        qc = QuantumCircuit(9)
    else:
        qc = QuantumCircuit(9, clbits)
    qc.cx(0,3)
    qc.cx(0,6)
    qc.h(0)
    qc.h(3)
    qc.h(6)
    qc.cx(0,1)
    qc.cx(3,4)
    qc.cx(6,7)
    qc.cx(0,2)
    qc.cx(3,5)
    qc.cx(6,8)
    return qc

def measureZstab(qc, n1: int, n2: int):
    qcz = qc.copy()
    qcz.measure(n1,0)
    qcz.measure(n2,1)
    simulator = AerSimulator(method="statevector")
    counts = simulator.run(qcz, shots=10000).result().get_counts(qcz)
    return counts

def measure_all_zstab(qc):
    print(f"Z1Z2 result is:\n {measureZstab(qc,0,1)}")
    print(f"Z1Z3 result is:\n {measureZstab(qc,0,2)}")
    print(f"Z4Z5 result is:\n {measureZstab(qc,3,4)}")
    print(f"Z4Z6 result is:\n {measureZstab(qc,3,5)}")
    print(f"Z7Z8 result is:\n {measureZstab(qc,6,7)}")
    print(f"Z7Z9 result is:\n {measureZstab(qc,6,8)}")
    return True

def measureXstab(qc, start: int, stop: int):
    qcx = qc.copy()
    for i in range(start, stop):
        qcx.h(i)
        qcx.measure(i, i-start)
    simulator = AerSimulator(method="statevector")
    counts = simulator.run(qcx, shots=10000).result().get_counts(qcx)
    return counts

def measure_all_xstab(qc):
    print(f"X1X2X3X4X5X6 result is:\n {measureXstab(qc,0,6)}")
    print(f"X4X5X6X7X8X9 result is:\n {measureXstab(qc,3,9)}")
    return True

def create_measured_zstab(n1, n2):
    qc = create_shor(2)
    qc.measure(n1, 0)
    qc.measure(n2, 1)
    return qc
def create_measured_xstab(start, stop):
    qc = create_shor(6)
    for i in range(start, stop):
        qc.h(i)
        qc.measure(i, i-start)
    return qc

def create_y_fault_circ():
    qc = create_shor(9)
    qc.y(0)
    return qc

def main():
    
    circs = []

    # Exercise a)
    qc1 = create_shor()
    qc1.measure_all()
    circs.append(qc1)
    simulator = AerSimulator(method="statevector")
    counts = simulator.run(qc1, shots=10000).result().get_counts(qc1)
    qc1.draw(output="mpl", filename="./qc1.png")

    # Exercise b)
    qc2 = create_shor(2)
    measure_all_zstab(qc2)
    # As expected, these all have even parity => expectation value is 1.
    qcbe1 = create_measured_zstab(0,1)
    qcbe2 = create_measured_zstab(1,2)
    qcbe3 = create_measured_zstab(3,4)
    qcbe4 = create_measured_zstab(3,5)
    qcbe5 = create_measured_zstab(6,7)
    qcbe6 = create_measured_zstab(6,8)
    circs.append(qcbe1)
    circs.append(qcbe2)
    circs.append(qcbe3)
    circs.append(qcbe4)
    circs.append(qcbe5)
    circs.append(qcbe6)

    # Exercise c)
    print("Exercise c):")
    qc3 = create_shor(6)
    measure_all_xstab(qc3)
    # Same as above, even parity and expectation value is 1.
    qcce1 = create_measured_xstab(0,6)
    qcce2 = create_measured_xstab(3,9)
    circs.append(qcce1)
    circs.append(qcce2)

    # Exercise d)
    qc4 = create_shor(6)
    qc4.y(0)
    measure_all_zstab(qc4)
    measure_all_xstab(qc4)
    # All stabilizers adjacent to qubit 0 have parity 0, that means a Y error (i.e. a ZX error) occured.
    qcd1 = create_y_fault_circ()
    qcd1.measure(0,0)
    qcd1.measure(1,1)
    qcd2 = create_y_fault_circ()
    qcd2.measure(0,0)
    qcd2.measure(2,1)
    qcd3 = create_y_fault_circ()
    qcd3.measure(3,4)
    qcd3.measure(3,5)
    qcd4 = create_y_fault_circ()
    qcd4.measure(6,7)
    qcd4.measure(6,8)
    qcd5 = create_y_fault_circ()
    for i in range(6):
        qcd5.h(i)
        qcd5.measure(i, i)
    qcd6 = create_y_fault_circ()
    for i in range(6):
        qcd6.h(i+3)
        qcd6.measure(i+3, i)
    circs.append(qcd1)
    circs.append(qcd2)
    circs.append(qcd3)
    circs.append(qcd4)
    circs.append(qcd5)
    circs.append(qcd6)

    # Exercise e
    token = '<redacted>'
    service = QiskitRuntimeService(channel="ibm_quantum", token= token)
    backend = service.least_busy(min_num_qubits=9, operational=True, simulator=False)
    t_circs = [transpile(i, backend=backend) for i in circs]
    print(backend.name)
    with Session(service=service, backend=backend) as session:
        sampler = Sampler(session=session)
        job = sampler.run(t_circs, shots=10000)
        result = job.result()
        print(result)

if __name__ == "__main__":
    main()
