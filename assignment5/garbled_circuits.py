from Enc_scheme import enc, dec
import random
from typing import Tuple  # for Python < 3.9
import secrets
import pprint

K= 128

def generate_random_key(k) -> bytes:
    """Generate a random k-bit key."""
    return secrets.token_bytes(k // 8)

class Gate:
    # def __init__(self, number:int, bool_function, A_wire_number:int, B_wire_number:int, A_keys:list, B_keys:list, ciphertexts:list, out_keys:list ):
    def __init__(self ):
        self.number = None
        self.bool_function = None
        self.A_wire_number = None
        self.B_wire_number = None
        self.A_keys = None 
        self.B_keys = None
        self.ciphertexts = None
        self.out_keys = None


class Circuit:
    def __init__(self,n:int,m:int, q:int, gates:list[int], A:list[int], B:list[int], gate_func:list):
        self.n = n
        self.m = m
        self.q = q
        self.gates = gates
        self.A = A
        self.B = B 
        self.gate_func = gate_func 
        self.keys = []
        

def yao_garble(circuit:Circuit, garbled_gates:list[Gate]):
    
    for i in range(1, circuit.n + circuit.q + 1):
        k_0 = generate_random_key(K)
        k_1 = generate_random_key(K)
        wire_keys = [k_0, k_1]
        circuit.keys.append(wire_keys)

    gc = []
    
    for i in range(len(circuit.gates)):
        gate = Gate()
        gate.bool_function = circuit.gate_func[i]
        gate.A_wire_number = circuit.A[i]
      
        gate.A_keys = circuit.keys[gate.A_wire_number - 1]
        gate.B_wire_number = circuit.B[i]
        gate.B_keys = circuit.keys[gate.B_wire_number - 1]
        gate.number = circuit.gates[i]
        gate.out_keys = circuit.keys[gate.number - 1]

        if gate.bool_function == "AND":
            C00 = enc(gate.A_keys[0], gate.B_keys[0], gate.number, gate.out_keys[0])
            C01 = enc(gate.A_keys[0], gate.B_keys[1], gate.number, gate.out_keys[0])
            C10 = enc(gate.A_keys[1], gate.B_keys[0], gate.number, gate.out_keys[0])
            C11 = enc(gate.A_keys[1], gate.B_keys[1], gate.number, gate.out_keys[1])
            
        elif gate.bool_function == "OR":
            C00 = enc(gate.A_keys[0], gate.B_keys[0], gate.number, gate.out_keys[0])
            C01 = enc(gate.A_keys[0], gate.B_keys[1], gate.number, gate.out_keys[1])
            C10 = enc(gate.A_keys[1], gate.B_keys[0], gate.number, gate.out_keys[1])
            C11 = enc(gate.A_keys[1], gate.B_keys[1], gate.number, gate.out_keys[1])
            
      
        elif gate.bool_function == "A_OR_NOT_B":
            C00 = enc(gate.A_keys[0], gate.B_keys[0], gate.number, gate.out_keys[1])  # 0,0 -> 1
            C01 = enc(gate.A_keys[0], gate.B_keys[1], gate.number, gate.out_keys[0])  # 0,1 -> 0
            C10 = enc(gate.A_keys[1], gate.B_keys[0], gate.number, gate.out_keys[1])  # 1,0 -> 1
            C11 = enc(gate.A_keys[1], gate.B_keys[1], gate.number, gate.out_keys[1])  # 1,1 -> 1
            
            
            
        
        else:
            raise ValueError("Unsupported gate function")
        
        gate.ciphertexts = [C00, C01, C10, C11]
        gc.append(gate.ciphertexts)
        garbled_gates.append(gate)

    e = circuit.keys[:circuit.n]
    d = circuit.keys[-circuit.m:]
   

    return gc, e, d



def yao_En(e: list[list[bytes]], x:list[int]) -> list[bytes]:
    """
    Args:
        e: [  [k^0_i, k^1_i] : i=1..n ]
        x: [x_1, x_2, ..., x_n]  each x_i in {0,1}

    return:
        X: [ k^w_i  : i=i...n   ]
    """
    assert(all([n == 0 or n == 1 for n in x]))
    X = []
    for i in range(len(e)):
        input_bit = x[i]
        encoding_keys = e[i]
        garbled_key = encoding_keys[input_bit]
        X.append(garbled_key)
    return X
    

def yao_eval(X:list[bytes], gc:list[list[bytes]] ,circuit:Circuit):
    """
    Args:
        X: [ k^w_i  : i=i...n   ]  garbled input keys
        gc: [ [C_00, C_01, C_10, C_11] : for each gate ]

    return:
        Y: [ k^w_j  : j=n+1...n+m ] garbled output keys
    """
    gates = circuit.gates
    A = circuit.A
    B = circuit.B

    for i in range(len(gc)):
        print(f"len(gc): {len(gc)}")
        
        K_l_num = A[i] #wire number of the left side
        K_r_num = B[i] #wire number of the right side
        l_key = X[K_l_num-1]
        r_key = X[K_r_num-1]

        gate_num = gates[i]

        print(f" for i = {i}, evaluating gate number{gate_num} with l_wire_number {K_l_num}, r_wire_number {K_r_num}\n")

        for j in range(4):
            C = gc[i][j]
            try:
                out_key = dec(l_key, r_key, gate_num, C)
                X.append(out_key)
                break
            except ValueError:
                continue
    
    Y = X[-circuit.m:]
    return Y

def yao_de(Y, d):
    output_key = Y[0] # Assuming single output
    decoding_keys = d[0] # Assuming single output
    if output_key == decoding_keys[0]:
        return 0
    elif output_key == decoding_keys[1]:
        return 1
    else:
        "you fucked up, go cry"






#========================================

# toggle this to test with different inputs for Alice and Bob
Alice= [1,0,1]
Bob = [1,1,0]

#======================================================

#circuit1 = Circuit(3,1,2, [4,5], [1,4], [2,3], ["OR", "AND"]) # easy trest circuit

circuit1 = Circuit(n=6, m=1, q=5, gates=[7,8,9,10,11], A=[1,2,3,7,10], B=[4,5,6,8,10], gate_func=["A_OR_NOT_B", "A_OR_NOT_B", "A_OR_NOT_B", "OR", "OR"])
garbled_gates = []

print(f"Alice: 1. Generating garbled circuit:")
gc, e, d = yao_garble(circuit1, garbled_gates)

print("Alice:  gc, e, d <- yao_garble(circuit)\n")

print(f"Alice: 2.1 Generating encoding info for my bits x_2, x-1, x_1, and sendign them to bob")

X = yao_En(e,x=[1,0,1,1,0,1] )
X = yao_En(e[:3],x=Alice )
print(f"Alice: 2.1 - X[:half] = yao_En(e, x=[x_2, x_1, x_0]) = {X}\n")

print(f"Alice: doing OT with bob to give him encoding keys for his bits y_2, y_1, y_0(which i do not know)")
X_bob = yao_En(e[3:], x=Bob)

X = X + X_bob


print(f"Bob: 3. Evaluating the garbled circuit(gc) on garbled inputs(X) to get garbled outputs(Y):")
print(f"Bob: 3. sending y to alice Y <- yao_eval(X, gc)")
Y = yao_eval(X, gc, circuit1)
print(f"Y={Y}\n")

print(f"Alice: 4. Decoding the garbled outputs(Y) to get output bits(output):")

output = yao_de(Y, d)
print(f"output={output}")



