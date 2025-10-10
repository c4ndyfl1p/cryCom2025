import hashlib
import secrets
import random
from typing import Tuple, List, Dict, Callable

# Security parameter (key length in bits)
K = 128

#enc scheme with special correctness property
def G(key_a: bytes, key_b: bytes, gate_id: int) -> bytes:
    """
    Pseudorandom generator (PRG) using cryptographic hash.
    Takes two keys and gate identifier, outputs a pseudorandom string.
    
    digest = F_k_2(K_1, gate_number)

    """
    h = hashlib.sha256()
    h.update(key_a)
    h.update(key_b)
    h.update(gate_id.to_bytes(4, 'big')) 
    # return h.digest()[:K // 8]
    return h.digest() # 32 bytes


def generate_random_key() -> bytes:
    """Generate a random k-bit key."""
    return secrets.token_bytes(K // 8)


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two byte strings."""
    return bytes(x ^ y for x, y in zip(a, b))


#=======================================================


def enc(k_1: bytes, k_2:bytes , gate_number :int, m: bytes) -> bytes:
    """
    Encrypt message m(k_3) using two keys k_1 and k_2, and gate number.

    c = F_k_2(K_1, gate_number) xor (x || 0^16)
    
    Args:
        k_1: 16-byte key
        k_2: 16-byte key
        gate_number: Gate identifier
        m: 16-byte key
    
    Returns:
        32-byte ciphertext
    """
    c_1 = G(k_1, k_2, gate_number) # 32 bytes
    # generate 16 byes of 0s and pad it to message
    pad = bytes([0]*16)    
    m = m + pad
    print(f"m after padding: {m}, len: {len(m)}")
    c_2 = xor_bytes(c_1, m)
    return c_2


def dec(k_1: bytes, k_2:bytes , gate_number :int, c: bytes) -> bytes:

    """
    Decrypt ciphertext c using two keys k_1 and k_2, and gate number
    
    m = c xor F_k_2(K_1, gate_number)
    if m = (x || 0^16) 
        return x 
    else;
        return BOT symbol
    
    Args:                
        k_1: 16-byte key
        k_2: 16-byte key
        gate_number: Gate identifier
        c: 32-byte ciphertext
        
    """

    c_2 = G(k_1, k_2, gate_number) # 32 bytes
    m = xor_bytes(c, c_2)

    #if the last 16 bytes are not 0s, then return bot
    # else return first 16 bytes 
    if m[16:] != bytes([0]*16):
        raise ValueError("Decryption failed: return BOT symbol")
    else:
        return m[:16] # return first 16 bytes(that would be the output key)
    


