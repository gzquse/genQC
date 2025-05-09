# AUTOGENERATED! DO NOT EDIT! File to edit: ../../../src/platform/simulation/qcircuit_sim.ipynb.

# %% auto 0
__all__ = ['get_number_of_gate_params', 'gate_pool_to_gate_classes', 'instruction_name_to_qiskit_gate', 'schmidt_rank_vector',
           'rnd_circuit', 'optimize_circuit', 'plot_svr_stat']

# %% ../../../src/platform/simulation/qcircuit_sim.ipynb 2
from ...imports import *
from ...config_loader import *

import qiskit.quantum_info as qi
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.gate import Gate
import qiskit.circuit.library as ql

# %% ../../../src/platform/simulation/qcircuit_sim.ipynb 4
def get_number_of_gate_params(gate_cls):
    return gate_cls.__init__.__code__.co_argcount - len(gate_cls.__init__.__defaults__) - 1 # python: gives you the number of any arguments BEFORE *args, minus ones that have a default, -1 for self parameter of classes

# %% ../../../src/platform/simulation/qcircuit_sim.ipynb 5
def gate_pool_to_gate_classes(gate_pool: list[Gate]): 
    """Creates a vocabulary from a gate pool."""
    classes = {}
    
    for i,cls in enumerate(gate_pool):
        num_of_paramters = get_number_of_gate_params(cls)
        name = cls(*[0]*num_of_paramters).name
        classes[name] = (i+1)
        
    return classes

# %% ../../../src/platform/simulation/qcircuit_sim.ipynb 6
def instruction_name_to_qiskit_gate(name: str) -> Gate:
    match name:
        case "swap": name = "Swap"
        case "cp":   name = "CPhase"
        case _:      name = name.upper()
        
    return get_obj_from_str(f"qiskit.circuit.library.standard_gates.{name}Gate")

# %% ../../../src/platform/simulation/qcircuit_sim.ipynb 7
def schmidt_rank_vector(densityMatrix: qi.DensityMatrix):   
    """Return the SRV of a `qi.DensityMatrix`."""
    systems_cnt = len(densityMatrix.dims())   
    total_trace = set(range(systems_cnt))    
    rank_vector = []
    
    for i in range(systems_cnt): 
        trace = list(total_trace - {i})
        red_densityMatrix = qi.partial_trace(densityMatrix, trace)        
        # r = np.count_nonzero(np.linalg.eigvals(red_densityMatrix) > 1e-14) # was slower during testing   
        r = np.linalg.matrix_rank(red_densityMatrix, hermitian=True).item()       
        rank_vector.append(r)
    
    return rank_vector

# %% ../../../src/platform/simulation/qcircuit_sim.ipynb 8
def rnd_circuit(num_of_qubits, num_of_gates, gate_pool: list[Gate], rng):
    """Create a random circuit."""
    qc = QuantumCircuit(num_of_qubits)    
    gate_indices = rng.choice(len(gate_pool), num_of_gates)
    
    for gate_index in gate_indices:
        gate_qiskit_class = gate_pool[gate_index]
        
        num_of_paramters = get_number_of_gate_params(gate_qiskit_class)
        params           = rng.uniform(low=0, high=2*np.pi, size=num_of_paramters) if num_of_paramters > 0 else [] # random between 0 and 2pi
        
        gate = gate_qiskit_class(*params)      
        act_qubits = rng.choice(num_of_qubits, gate.num_qubits, replace=False) # order: (*act_qubits)=(*control_qubits, *target_qubits)   
        qc.append(gate, [*act_qubits], [])
    
    return qc

# %% ../../../src/platform/simulation/qcircuit_sim.ipynb 9
def optimize_circuit(qc: QuantumCircuit, gate_pool: list[Gate], optimization_level=2):
    """Use qiskit.compiler.transpile to optimize a circuit."""
    basis_gates = gate_pool_to_gate_classes(gate_pool).keys()
    
    while optimization_level > 0:
        try:
            qc_opt = transpile(qc, optimization_level=optimization_level, basis_gates=basis_gates) #target=target
            return qc_opt
        except Exception as er: pass
  
        optimization_level -= 1

    return qc

# %% ../../../src/platform/simulation/qcircuit_sim.ipynb 11
def plot_svr_stat(num_of_qubits, min_gates, max_gates, gs, samples, sort=False, opt=True, rng=np.random.default_rng()):    
    svr_list = list()
    for i in range(samples):
        qc = rnd_circuit(num_of_qubits, rng.integers(min_gates, max_gates+1), gs, rng) 
        if opt: qc = optimize_circuit(qc, gs)
        svr = schmidt_rank_vector(qi.DensityMatrix(qc))
        if sort: svr = sorted(svr)
        svr_list.append(svr)           
    df = pd.DataFrame(data={"svr":svr_list})   
    cnts = df['svr'].value_counts(normalize=True)
    for n,v in zip(cnts.index, cnts.values): print(f"{n}: {v*100:.1f}%")    
    df['svr'].value_counts().plot(kind='bar')   
