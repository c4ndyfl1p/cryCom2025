from d_fhe_scheme import FHE_keygen, FHE_enc, FHE_dec
import gmpy2
import secrets      
import pickle
from HE import blood_type_encoding_HE, blood_type_encoding, bloodtype_compatability_depth3, can_donate, truth_table

# Example usage
p_bits = 2000  # size of secret key p in bits
q_bits = 10**7  # size of big random integers qi in bits
r = 60
n = 2000  # number of public key elements
pub_key_file = "FHE_pubkey.pkl"

secret_key = FHE_keygen(p_bits, q_bits, r, n, pub_key_file="FHE_pubkey.pkl")

print("Secret Key (p):", secret_key)

# m1 = 1  # message to encrypt
# m2 = 1
# m3 = 0

# c1 = FHE_enc(m1, pub_key_file, n)
# c2 = FHE_enc(m2, pub_key_file, n)
# c3 = FHE_enc(m3, pub_key_file, n)

# cA = c1 + c2 + c3  # homomorphic addition
# cB = c1 * c2 * c3  # homomorphic multiplication

# Example usage
# dA = FHE_dec(cA, secret_key) # Decrypt the sum
# print("Decrypted Message (sum):", dA)

# dB = FHE_dec(cB, secret_key) # Decrypt the product
# print("Decrypted Message(mult):", dB)

for donor in range(8):
  # Donor Encrypts their blood type and sends to Recipient
  m1, m2, m3 = blood_type_encoding_HE[list(blood_type_encoding.keys())[donor]]
  c1 = FHE_enc(m1, pub_key_file, n)
  c2 = FHE_enc(m2, pub_key_file, n)
  c3 = FHE_enc(m3, pub_key_file, n)
  donorblood_enc = (c1, c2, c3)
  for recipient in range(8):
      # Recipient Encrypts their blood type, Checks Compatibility and sends back result
      recipientblood = blood_type_encoding_HE[list(blood_type_encoding.keys())[recipient]]
      m1, m2, m3 = recipientblood
      c1 = FHE_enc(m1, pub_key_file, n)
      c2 = FHE_enc(m2, pub_key_file, n)
      c3 = FHE_enc(m3, pub_key_file, n)
      recipientblood_enc = (c1, c2, c3)
      compat = bloodtype_compatability_depth3(donorblood_enc, recipientblood_enc)

      # Donor Decrypts the result
      compat_dec = FHE_dec(compat, secret_key)

      if can_donate(list(blood_type_encoding.keys())[donor], list(blood_type_encoding.keys())[recipient]) == compat_dec: # Compare Lookup Table with HE Result
          if can_donate(list(blood_type_encoding.keys())[donor], list(blood_type_encoding.keys())[recipient]): # Check if can donate
              print(f"Both functions agree that: {list(blood_type_encoding.keys())[donor]} can donate to {list(blood_type_encoding.keys())[recipient]}") # Print if can Donate
          else:
              print(f"Both functions agree that: {list(blood_type_encoding.keys())[donor]} cannot donate to {list(blood_type_encoding.keys())[recipient]}") # Print if cannot Donate
      else:
          print(f"Functions disagree on: {list(blood_type_encoding.keys())[donor]} to {list(blood_type_encoding.keys())[recipient]}") # Print if functions Disagree

#delete the pub key file
import os
os.remove(pub_key_file)
