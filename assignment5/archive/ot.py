import elgamal
import random
from typing import Tuple  # for Python < 3.9

class Alice:
    def __init__(self, blood_type: str):
        self.blood_type = blood_type  # Alice's blood type (receiver type)
        self.blood_type_encoding = {
            'o-': 0,
            'o+': 1,
            'a-': 2,
            'a+': 3,
            'b-': 4,
            'b+': 5,
            'ab-': 6,
            'ab+': 7
        }
        self.sk = None  # Alice's private key

        self.compatibility = {
            0: [1,1,1,1,1,1,1,1],  # O- can donate to all
            1: [0,1,0,1,0,1,0,1],  # O+ can donate to +ve blood types
            2: [0,0,1,1,0,0,1,1],  # B- can donate to B and AB
            3: [0,0,0,1,0,0,0,1],  # B+ can donate to B+ and AB+
            4: [0,0,0,0,1,1,1,1],  # A- can donate to A and AB
            5: [0,0,0,0,0,1,0,1],  # A+ can donate to A+ and AB+
            6: [0,0,0,0,0,0,1,1],  # AB- can donate to AB only
            7: [0,0,0,0,0,0,0,1],  # AB+ can donate to AB+ only
        }

        self.pk_list = []  # List of public keys (one real, others oblivious)

    def __repr__(self):
        return (
            f"Alice(blood_type={self.blood_type}, "
            f"blood_type_encoding={self.blood_type_encoding[self.blood_type]}, "
            f"sk={self.sk},\n "
            f"b/pk_list={self.pk_list})"
        )
    
    def get_blood_type_index(self) -> int:
        return self.blood_type_encoding[self.blood_type]
    
    def get_compatibility(self, donor_blood_type: str) -> int:
        donor_index = self.blood_type_encoding[donor_blood_type]
        recipient_index = self.get_blood_type_index()
        return self.truth_table[recipient_index][donor_index]
    
    def choose_b(self):
        # choose bit b i.e send 7 random public keys and one real public key. The real pk is at index b
        b = self.get_blood_type_index()

        G = elgamal.elgamal_safe_GGen() # generate a safe group
        # print(f"Using group G: {G}")

        # generate one real public/private key pair
        pk, sk = elgamal.elgamal_Gen(G) # generate a public/private key pair

        #generate 7 oblivious public keys
        opk = elgamal.elgamal_OGen( G, random.randint(1, G[1]-1)) # generate an oblivious public key with random r

        # create a list of 8 public keys with the real pk at index b

        for i in range(0,8):
            if i ==b:
                pk, sk = elgamal.elgamal_Gen(G) # generate a public/private key pair
                self.pk_list.append(pk)
                self.sk = sk

            else:
                opk = elgamal.elgamal_OGen( G, random.randint(1, G[1]-1)) # generate an oblivious public key with random r
                self.pk_list.append(opk)

        print("Alice: sending b to bob, b is 7 random public keys and one real public key. The real pk is at index b")
        print("Alice: b/pk_list =", self.pk_list) 
        return self.pk_list
    
    def retreive(self, c:list):
        # decrypt the ciphertext at index b using her private key sk
        b = self.get_blood_type_index()
        print(f"Alice: receiving ciphertexts c from Bob, c = {c}")
        
        m = elgamal.elgamal_Dec(c[b], self.sk, self.pk_list[b])
        print(f"Alice: decrypted m = {m}")
        if m == 1:
            print(f"Alice: Yes, I  can receive blood from a Bob, even though I dont know his blood type")
        else:
            print(f"Alice: No, I cannot receive blood from Bob, even though I dont know his blood type")
                

class Bob:
    def __init__(self, blood_type: str):
        self.blood_type = blood_type  # Bob's blood type (donor type)
        self.blood_type_encoding = {
            'o-': 0,
            'o+': 1,
            'a-': 2,
            'a+': 3,
            'b-': 4,
            'b+': 5,
            'ab-': 6,
            'ab+': 7
        }
    
        self.compatibility = {
            0: [1,1,1,1,1,1,1,1],  # O- can donate to all
            1: [0,1,0,1,0,1,0,1],  # O+ can donate to +ve blood types
            2: [0,0,1,1,0,0,1,1],  # B- can donate to B and AB
            3: [0,0,0,1,0,0,0,1],  # B+ can donate to B+ and AB+
            4: [0,0,0,0,1,1,1,1],  # A- can donate to A and AB
            5: [0,0,0,0,0,1,0,1],  # A+ can donate to A+ and AB+
            6: [0,0,0,0,0,0,1,1],  # AB- can donate to AB only
            7: [0,0,0,0,0,0,0,1],  # AB+ can donate to AB+ only
        }

        self.c = []

    def __repr__(self):
        return (
            f"Bob(blood_type={self.blood_type}, "
            f"blood_type_encoding={self.blood_type_encoding[self.blood_type]},\n "
            f"c_like={self.c_like})"
        )
    
    def can_donate(self,d: str) -> bool:
        donor_index = self.blood_type_encoding[d]
        recipient_index = self.blood_type_encoding[self.blood_type]
        return self.truth_table[recipient_index][donor_index]
    
    def transfer_c(self, pk_list):
        # encode his vector and then encrypt with the public keys
        m = self.compatibility[self.blood_type_encoding[self.blood_type]]
        m_encoded = [elgamal.encode_message(bit, elgamal.elgamal_safe_GGen()) for bit in m]
        # print(f"Bob: m_encoded = {m_encoded}")

        self.c = [elgamal.elgamal_Enc(pk, me) for pk, me in zip(pk_list, m_encoded)]

        print(f"Bob: sending ciphertexts c to Alice, c = {self.c}")
        return self.c



        

        

#
bob = Bob('a-') # donor
alice = Alice('ab-') # recipent
pk_list = alice.choose_b()


c = bob.transfer_c(pk_list)

m = alice.retreive(c)


