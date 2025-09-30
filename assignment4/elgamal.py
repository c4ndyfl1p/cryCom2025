import random
from typing import Tuple  # for Python < 3.9

PublicKey = tuple[int, int, int, int]  # or Tuple[int, int, int, int]
Ciphertext = tuple[int, int]           # or Tuple[int, int]
GroupDescription = Tuple[int, int, int]  # or Tuple[int, int, int]

def elgamal_safe_GGen():
    # hardcoding a safe group
    p = 11
    q = 5
    r = 2
    #choose x randomly from 1... q-1
    g = 3 # generator of G, hardcoding it
    return p, q, g

def elgamal_Gen(G:GroupDescription)-> Tuple[PublicKey, int]:
    p, q, g = G
    x = random.randint(1, q - 1)
    h = pow(g, x, p)  # y = g^x mod p
    pk = (p, q, g, h)
    sk = x
    return pk, sk


def elgamal_OGen(G: GroupDescription, r: int) -> PublicKey:
    """
    Generate an oblivious public key using randomness r.
    We create h such that we DON'T know log_g(h).
    
    For safe prime p = 2q + 1:
    - Sample s from randomness r
    - Output h = s^2 mod p (ensures h is in subgroup of order q)
    - We don't know log_g(h) = the discrete log of h base g
    """
    p, q, g = G
    
    # Use randomness r to generate s in range [1, p-1]
    if r < 1 or r >= p:
        raise ValueError(f"r should be in range [1, {p-1}], you gave r = {r}")
    
    s = r  # or derive s from r in some way
    h = pow(s, 2, p)  # h = s^2 mod p
    
    return (p, q, g, h)

def encode_message(msg, G: GroupDescription) -> int:
    """ need to map 1's and 0s to group elements """
    if msg == 1:
        return 1
    elif msg == 0:
        return G[2]  # g
    

def elgamal_Enc(pk:PublicKey, m:int)-> Ciphertext:
    p,q, g, h = pk
    # choose y randomly from 1... q-1
    y = random.randint(1, q-1)
    s = pow(h, y, p)  # a = g^k mod p
    c1 = pow(g, y, p)
    c2 = (m * s) % p
    c = c1, c2
    return c

def elgamal_Dec(c: Ciphertext, sk:int, pk:PublicKey) -> int:
    # 1. s: = c
    s = pow(c[0], sk, pk[0])  # s = c1^x mod p
    # 2. compute s^-1 mod p
    s_inv = pow(s, -1, pk[0])  # modular inverse of
    # 3. m = c2 * s^-1 mod p
    m = (c[1] * s_inv) % pk[0]
    return m


# m = 9
# G = elgamal_safe_GGen()
# pk, sk = elgamal_Gen(G)
# c = elgamal_Enc(pk, m)
# m2 = elgamal_Dec(c, sk, pk)
# print(f"m={m}, m2={m2}, equal? {m==m2}")

# opk = elgamal_OGen(G, 3)
# print(f"oblivious pk with r=3: {opk}")

