import secrets
import pickle
import gmpy2

def random_subset(n):
    """
    Return a random subset of indices 0..n-1 of size n//2
    """
    indices = list(range(n))
    subset_size = n // 20
    # Use secrets.SystemRandom for secure random sampling
    S = secrets.SystemRandom().sample(indices, subset_size)
    return S



def FHE_keygen(p_bits, q_bits, r_bits, n, pub_key_file):
    """
    Generate d-HE / FHE keys with gmpy2 for big integers and pickle for storage.
    Saves the public key (yi values) to a file, returns the secret key p.
    """
    # Secret key: big odd integer
    p = gmpy2.mpz(secrets.randbits(p_bits) | 1)

    # Open file in binary write mode
    with open(pub_key_file, "wb") as f:
        # Generate and store each yi
        for _ in range(n):
            qi = gmpy2.mpz(secrets.randbits(q_bits))
            ri = gmpy2.mpz(secrets.randbits(r_bits))
            
            # Compute yi = p * qi + 2 * ri
            yi = p * qi + 2 * ri
            
            # Save yi immediately using pickle (streaming)
            pickle.dump(yi, f)

    return p

def FHE_enc(m:int, pub_key_file, n:int):
    """
    Encrypt message m (0 or 1) using a subset of public keys stored in pub_key_file.
    """
    if m not in (0, 1):
        raise ValueError("Message m must be 0 or 1.")
    
    #choose a subset S of the public key elements between 1 and n elements
    # let size of S be n//2 
    S = random_subset(n)
    
    # Initialize ciphertext
    c = gmpy2.mpz(0)
    with open(pub_key_file, "rb") as f:
        for i in range(n):
            yi = pickle.load(f)
            if i in S:
                c += yi

    # Add m to the ciphertext
    c += m
    return c

def FHE_dec(c, p):
    """
    Decrypt ciphertext c using secret key p.
    Returns the decrypted message (0 or 1).
    """
    m_prime = gmpy2.t_mod(c, p)
    m = gmpy2.t_mod(m_prime, 2)
    return m

