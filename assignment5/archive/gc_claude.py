import hashlib
import secrets
import random
from typing import Tuple, List, Dict, Callable

# Security parameter (key length in bits)
K = 128

def generate_random_key() -> bytes:
    """Generate a random k-bit key."""
    return secrets.token_bytes(K // 8)

def G(key_a: bytes, key_b: bytes, gate_id: int) -> bytes:
    """
    Pseudorandom generator (PRG) using cryptographic hash.
    Takes two keys and gate identifier, outputs a pseudorandom string.
    """
    h = hashlib.sha256()
    h.update(key_a)
    h.update(key_b)
    h.update(gate_id.to_bytes(4, 'big'))
    return h.digest()[:K // 8]

def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte strings."""
    return bytes(x ^ y for x, y in zip(a, b))

class Gate:
    """Represents a gate in the Boolean circuit."""
    def __init__(self, gate_id: int, left_wire: int, right_wire: int, 
                 logic_func: Callable[[bool, bool], bool], gate_type: str):
        self.gate_id = gate_id
        self.left_wire = left_wire  # L(i)
        self.right_wire = right_wire  # R(i)
        self.logic_func = logic_func
        self.gate_type = gate_type

class GarbledCircuit:
    """Implementation of garbled circuit generation."""
    
    def __init__(self, n_inputs: int, gates: List[Gate], output_wire: int):
        """
        Args:
            n_inputs: Number of input wires
            gates: List of Gate objects
            output_wire: Index of the output wire (T)
        """
        self.n_inputs = n_inputs
        self.gates = gates
        self.output_wire = output_wire
        
        # Calculate total number of wires
        self.n_wires = max(output_wire, 
                          max(g.left_wire for g in gates),
                          max(g.right_wire for g in gates)) + 1
        
        # Wire keys: K[wire_id][bit_value]
        self.wire_keys: Dict[int, Tuple[bytes, bytes]] = {}
        
        # Garbled tables for each gate
        self.garbled_tables: Dict[int, List[bytes]] = {}
        
        # Encoding and decoding information
        self.e = None  # encoding info
        self.d = None  # decoding info
    
    def generate_garbled_circuit(self) -> Tuple[Dict, Dict, Tuple]:
        """
        Generate the garbled circuit.
        
        Returns:
            F: Garbled tables for all gates
            e: Encoding information (input wire keys)
            d: Decoding information (output wire keys)
        """
        print("=== Garbled Circuit Generation ===\n")
        
        # Step 1: Generate wire keys
        print(f"Step 1: Generating keys for {self.n_wires} wires...")
        for wire_id in range(self.n_wires):
            K0 = generate_random_key()
            K1 = generate_random_key()
            self.wire_keys[wire_id] = (K0, K1)
            print(f"  Wire {wire_id}: K⁰={K0.hex()[:16]}..., K¹={K1.hex()[:16]}...")
        
        # Define encoding information (input wire keys)
        self.e = {i: self.wire_keys[i] for i in range(self.n_inputs)}
        
        # Define decoding information (output wire keys)
        self.d = self.wire_keys[self.output_wire]
        
        print(f"\nEncoding info (e): {self.n_inputs} input wires")
        print(f"Decoding info (d): Output wire {self.output_wire}")
        
        # Step 2: Generate garbled tables for each gate
        print(f"\nStep 2: Generating garbled tables for {len(self.gates)} gates...")
        
        for gate in self.gates:
            self._garble_gate(gate)
        
        return self.garbled_tables, self.e, self.d
    
    def _garble_gate(self, gate: Gate):
        """Generate garbled table for a single gate."""
        print(f"\n  Gate {gate.gate_id} ({gate.gate_type}):")
        print(f"    Input wires: L={gate.left_wire}, R={gate.right_wire}")
        print(f"    Output wire: {gate.gate_id}")
        
        # Get keys for left and right input wires
        KL0, KL1 = self.wire_keys[gate.left_wire]
        KR0, KR1 = self.wire_keys[gate.right_wire]
        
        # Get keys for output wire
        Ki0, Ki1 = self.wire_keys[gate.gate_id]
        
        # Create garbled table entries (before permutation)
        C_prime = {}
        
        # For all (a, b) ∈ {0, 1} × {0, 1}
        for a in [0, 1]:
            for b in [0, 1]:
                # Get input keys
                KL_a = KL0 if a == 0 else KL1
                KR_b = KR0 if b == 0 else KR1
                
                # Compute gate output
                output_bit = 1 if gate.logic_func(bool(a), bool(b)) else 0
                
                # Get output key corresponding to the gate's output
                Ki_out = Ki0 if output_bit == 0 else Ki1
                
                # Compute C'_{a,b} = G(KL_a, KR_b, i) ⊕ (Ki_out, 0^k)
                prg_output = G(KL_a, KR_b, gate.gate_id)
                
                # XOR with output key (the 0^k is implicit padding)
                C_prime[(a, b)] = xor_bytes(prg_output, Ki_out)
                
                print(f"    Input ({a},{b}) → Output {output_bit}: "
                      f"C'[{a},{b}] = {C_prime[(a, b)].hex()[:16]}...")
        
        # Step 2b: Random permutation
        # Create mapping from {0,1,2,3} to {(0,0), (0,1), (1,0), (1,1)}
        indices = [(0, 0), (0, 1), (1, 0), (1, 1)]
        random.shuffle(indices)
        
        # Apply permutation
        garbled_table = [C_prime[indices[j]] for j in range(4)]
        
        self.garbled_tables[gate.gate_id] = garbled_table
        
        print(f"    Permuted table: [{', '.join(c.hex()[:8] + '...' for c in garbled_table)}]")


# Example usage: 2-input AND gate circuit
def example_and_circuit():
    """Example: Simple circuit with one AND gate."""
    print("\n" + "="*60)
    print("EXAMPLE: 2-input AND gate circuit")
    print("="*60)
    
    # Define AND gate logic
    def and_gate(a: bool, b: bool) -> bool:
        return a and b
    
    # Circuit with 2 inputs (wires 0, 1) and 1 gate (wire 2 = output)
    gates = [
        Gate(gate_id=2, left_wire=0, right_wire=1, 
             logic_func=and_gate, gate_type="AND")
    ]
    
    gc = GarbledCircuit(n_inputs=2, gates=gates, output_wire=2)
    F, e, d = gc.generate_garbled_circuit()
    
    print("\n=== Final Garbled Circuit ===")
    print(f"Number of gates: {len(F)}")
    print(f"Input encoding keys: {len(e)} wires")
    print(f"Output decoding keys: Wire {gc.output_wire}")
    
    return gc, F, e, d


# Example with more complex circuit: (A AND B) OR C
def example_complex_circuit():
    """Example: (A AND B) OR C circuit."""
    print("\n" + "="*60)
    print("EXAMPLE: (A AND B) OR C circuit")
    print("="*60)
    
    def and_gate(a: bool, b: bool) -> bool:
        return a and b
    
    def or_gate(a: bool, b: bool) -> bool:
        return a or b
    
    # Circuit structure:
    # Wires 0, 1, 2 = inputs A, B, C
    # Wire 3 = A AND B
    # Wire 4 = (A AND B) OR C (output)
    gates = [
        Gate(gate_id=3, left_wire=0, right_wire=1, 
             logic_func=and_gate, gate_type="AND"),
        Gate(gate_id=4, left_wire=3, right_wire=2, 
             logic_func=or_gate, gate_type="OR")
    ]
    
    gc = GarbledCircuit(n_inputs=3, gates=gates, output_wire=4)
    F, e, d = gc.generate_garbled_circuit()
    
    print("\n=== Final Garbled Circuit ===")
    print(f"Number of gates: {len(F)}")
    print(f"Input encoding keys: {len(e)} wires")
    print(f"Output decoding keys: Wire {gc.output_wire}")
    
    return gc, F, e, d


if __name__ == "__main__":
    # Run simple AND gate example
    gc1, F1, e1, d1 = example_and_circuit()
    
    # Run complex circuit example
    gc2, F2, e2, d2 = example_complex_circuit()