from d_fhe_scheme import FHE_keygen, FHE_enc, FHE_dec
import gmpy2
import secrets      
import pickle

# Example usage
p_bits = 2000  # size of secret key p in bits
q_bits = 10**7  # size of big random integers qi in bits
r = 60
n = 2000  # number of public key elements
pub_key_file = "FHE_pubkey.pkl"

secret_key = FHE_keygen(p_bits, q_bits, r, n, pub_key_file="FHE_pubkey.pkl")

print("Secret Key (p):", secret_key)



m1 = 1  # message to encrypt
m2 = 1
m3 = 0

c1 = FHE_enc(m1, pub_key_file, n)
c2 = FHE_enc(m2, pub_key_file, n)
c3 = FHE_enc(m3, pub_key_file, n)

cA = c1 + c2 + c3  # homomorphic addition
cB = c1 * c2 * c3  # homomorphic multiplication




# Example usage
dA = FHE_dec(cA, secret_key) # Decrypt the sum
print("Decrypted Message (sum):", dA)

dB = FHE_dec(cB, secret_key) # Decrypt the product
print("Decrypted Message(mult):", dB)

#delete the pub key file
import os
os.remove(pub_key_file)
