# Python implementation (visible) of the approximate-GCD d-HE scheme (toy/demo parameters)
# This notebook code implements KeyGen, Enc, Eval (multiply three ciphertexts), and Dec.
# IMPORTANT: Real CLT-style parameters (p ~ 2000 bits, q_i enormous, n ~ 2000) are heavy to generate.
# For the demo here we use much smaller "toy" parameters so the code runs quickly. 
# At the end I show how to set the "real" parameters, with a warning about runtime & memory.

import secrets, math, sys, time

# --- Utility: generate random signed integer of given bit-length (non-zero) ---
def rand_signed(bits):
    if bits <= 0:
        return 0
    x = secrets.randbits(bits)
    # Ensure top bit set for exact bit length (except if bits small)
    x |= (1 << (bits-1))
    sign = 1 if secrets.randbits(1) == 0 else -1
    return sign * x

# --- Scheme implementation ---
class ApproxGCDdHE:
    def __init__(self, p_bits=200, q_bits=1000, r_bits=20, n=512, s=None):
        """
        p_bits, q_bits, r_bits: bit-lengths for secret p, q_i, and r_i respectively.
        n: number of public samples y_i.
        s: subset size used in encryption (if None, uses n//4).
        
        NOTE: These defaults are toy parameters for demo speed. For CLT-like parameters
        you would set p_bits≈2000, q_bits≈1_000_000 (or larger), r_bits≈60, n≈2000 —
        but generating that many huge integers will be very slow / memory intensive.
        """
        self.p_bits = p_bits
        self.q_bits = q_bits
        self.r_bits = r_bits
        self.n = n
        self.s = s if s is not None else max(1, n//4)
        self.pk = None
        self.sk = None
        self.ys = None

    def keygen(self):
        # Secret odd integer p
        # ensure odd by OR 1
        p = secrets.randbits(self.p_bits) | 1
        # Generate public samples y_i = p*q_i + 2*r_i
        ys = []
        qs = []
        rs = []
        for i in range(self.n):
            q_i = rand_signed(self.q_bits)
            r_i = rand_signed(self.r_bits)
            y_i = p * q_i + 2 * r_i
            ys.append(y_i)
            qs.append(q_i)
            rs.append(r_i)
        self.pk = (self.n, list(ys))
        self.sk = p
        self.ys = ys
        # keep qs and rs for introspection in demo
        self._qs = qs
        self._rs = rs
        return (self.pk, self.sk)

    def encrypt_bit(self, m):
        """Encrypt bit m (0/1). Picks random subset S of size s and returns integer ciphertext c."""
        if self.pk is None or self.sk is None:
            raise ValueError("Keypair not generated")
        if m not in (0,1):
            raise ValueError("Message must be bit 0/1")
        # choose subset indices
        S = secrets.SystemRandom().sample(range(self.n), self.s)
        total = m
        for i in S:
            total += self.ys[i]
        # return tuple (c, S) so we can inspect noise later (S not required normally)
        return total, S

    def decrypt(self, c):
        """Decrypt integer ciphertext c returning bit m' = ((c mod p) mod 2)"""
        p = self.sk
        m_mod = (c % p) % 2
        return int(m_mod)

    def eval_mult_three(self, c1, c2, c3):
        """Evaluate product c1*c2*c3 as integer product (no modulus reduction during eval)."""
        return c1 * c2 * c3

    # helper to compute noise term R for a ciphertext given the subset S used at encryption
    def compute_noise_term(self, c, S):
        """Return R where c = m + 2*R + p*Q (we return m and R by solving mod p and modulo 2)"""
        p = self.sk
        m = (c % p) % 2
        # c mod p = m + 2*R (assuming no wrap due to p)
        cmodp = c % p
        R_times_2 = (cmodp := cmodp) - m
        # if negative adjust representation
        # R = R_times_2 // 2
        return m, R_times_2 // 2


# --- Demo run with toy parameters ---
print("Running demo with toy parameters (fast).")
params = {
    "p_bits": 200,   # toy secret size (change to 2000 for closer-to-CLT, but slower)
    "q_bits": 1000,  # toy large q (CLT suggests much larger)
    "r_bits": 20,    # noise bits
    "n": 512,        # number of public samples
    "s": 128         # subset size used in encryption
}
scheme = ApproxGCDdHE(**params)
start = time.time()
(pk, sk) = scheme.keygen()
print(f"Generated keys. secret p bit-length ~ {sk.bit_length()} bits; n = {params['n']}. Time: {time.time()-start:.2f}s")

# Encrypt three bits
m1, m2, m3 = 1, 1, 0  # example bits (product should be 0)
c1, S1 = scheme.encrypt_bit(m1)
c2, S2 = scheme.encrypt_bit(m2)
c3, S3 = scheme.encrypt_bit(m3)
print("Encrypted bits m1,m2,m3 -> ciphertexts c1,c2,c3 (integers).")
print("Message bits:", (m1,m2,m3))

# Evaluate product c = c1*c2*c3
c_prod = scheme.eval_mult_three(c1, c2, c3)

# Decrypt product
m_out = scheme.decrypt(c_prod)

# Compute and show some noise diagnostics (approx)
m1_calc, R1 = scheme.compute_noise_term(c1, S1)
m2_calc, R2 = scheme.compute_noise_term(c2, S2)
m3_calc, R3 = scheme.compute_noise_term(c3, S3)
# For product ciphertext, we can't directly retrieve a single S, but we can inspect magnitude
prod_noise_bits = (abs((c_prod % sk) - m_out) // 2).bit_length() if sk != 0 else None

print("Decrypted product bit (should equal m1*m2*m3):", m_out)
print("Per-ciphertext noise bit-lengths:", R1.bit_length(), R2.bit_length(), R3.bit_length())
print("Approx product-noise (in bits, from c_prod mod p):", prod_noise_bits)

# Show how to switch to the CLT-like parameters (warning)
print("\n--- WARNING & HOW TO USE CLT-LIKE PARAMS ---")
print("CLT suggested params (your message): p ~ 2000 bits, r_i ~ 60 bits, n ~ 2000, q_i extremely large (1M bits).")
print("To try those, change the params above. But note: generating n=2000 integers each q_i ~ 1,000,000 bits is heavy (memory/time).")
print("If you still want to run close-to-CLT params on a powerful machine, set p_bits=2000, q_bits=1000000, r_bits=60, n=2000, s ~ 1000")
print("Expect extremely long runtime and huge memory usage; not suitable for this interactive demo.")

# Return variables to the notebook output so the user can inspect if desired.
scheme_info = {
    "params": params,
    "p_bitlen": sk.bit_length(),
    "m_bits": (m1,m2,m3),
    "decrypted_product": m_out,
    "R_bits": (R1.bit_length(), R2.bit_length(), R3.bit_length()),
    "product_noise_bits_modp": prod_noise_bits
}
scheme_info

