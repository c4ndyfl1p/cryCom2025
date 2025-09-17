import random

# Define Encoding for Blood Types
blood_type_encoding = {
    'o-': (0,0,0),
    'o+': (0,0,1),
    'a-': (0,1,0),
    'a+': (0,1,1),
    'b-': (1,0,0),
    'b+': (1,0,1),
    'ab-': (1,1,0),
    'ab+': (1,1,1)
}

# Making the Shares
def share(secret: int) -> tuple[int, int]:
    # Secret share a bit 'secret' between Alice and Bob.
    x_b = random.randint(0, 1)  # Bob's share
    x_a = secret ^ x_b           # Alice's share
    return (x_a, x_b)

# Reconstructing the secret from shares
def reconstruct(share: tuple[int, int]) -> int:
    # Reconstruct the bit from a sharing [x] = (xA, xB).
    x_a, x_b = share
    return x_a ^ x_b

# Individual Gates
def xor_const(share: tuple[int, int], const: int) -> tuple[int, int]:
    # const = 1 is the NOT gate
    x_a, x_b = share
    z_a = x_a ^ const
    z_b = x_b
    return (z_a, z_b)

def and_const(share: tuple[int, int], const: int) -> tuple[int, int]:
    # const = 0, zeros the gate
    x_a, x_b = share
    z_a = const * x_a
    z_b = const * x_b
    return (z_a, z_b)

# Two-Wire Gates
def xor_gate(share1: tuple[int, int], share2: tuple[int, int]) -> tuple[int, int]:
    x_a, x_b = share1
    y_a, y_b = share2
    z_a = x_a ^ y_a
    z_b = x_b ^ y_b
    return (z_a, z_b)

# Dealer Gates
def dealer() -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    # Dealer provides random bits u, v, w such that w = u * v
    u = random.randint(0, 1)
    v = random.randint(0, 1)
    w = u * v
    return share(u), share(v), share(w)

def and_gate(share1: tuple[int, int], share2: tuple[int, int]) -> tuple[int, int]:
    # u, v, w are from the dealer
    (x_a, x_b), (y_a, y_b) = share1, share2
    (u_a, u_b), (v_a, v_b), (w_a, w_b) = dealer()

    d = xor_gate((x_a, x_b), (u_a, u_b))
    e = xor_gate((y_a, y_b), (v_a, v_b))

    # d and e become public
    d = reconstruct(d)
    e = reconstruct(e)

    z_a = w_a ^ (e * x_a) ^ (d * y_a) ^ (d * e)
    z_b = w_b ^ (e * x_b) ^ (d * y_b)
    return (z_a, z_b)

def or_gate(share1: tuple[int, int], share2: tuple[int, int]) -> int:
    # Using De Morgan's law: x OR y = NOT(NOT x AND NOT y)
    not_x = xor_const(share1, 1)
    not_y = xor_const(share2, 1)
    and_not = and_gate(not_x, not_y)
    return xor_const(and_not, 1)

def blood_type_compatibility_tester(recipient: tuple[tuple[int, int], tuple[int, int], tuple[int, int]], donor: tuple[tuple[int, int], tuple[int, int], tuple[int, int]]) -> int:
    # test Rh compatibility
    Rh_compatibility = or_gate(xor_const(donor[2], 1), recipient[2])

    # test ABO compatibility
    # CHECK IF DONOR IS O
    donor_is_O = or_gate(xor_const(donor[0], 1), xor_const(donor[1], 1))
    
    A_type = and_gate(donor[1], recipient[1])  # donor A and recipient A
    B_type = and_gate(donor[0], recipient[0])  # donor B and recipient B
    
    ABO_compatibility = or_gate(donor_is_O, or_gate(A_type, B_type))

    # final compatibility
    compatibility = and_gate(Rh_compatibility, ABO_compatibility)

    return reconstruct(compatibility)  # 1 if compatible, 0 if not

#===============
# Write Main Function

if __name__ == "__main__":
  Alice_Blood_Type = 'o-' # Alice's blood type (recipient type)
  Bob_Blood_Type = 'ab-' # Bob's blood type (donor type)

  Alice_input = blood_type_encoding[Alice_Blood_Type]  # Alice's input bit
  Bob_input = blood_type_encoding[Bob_Blood_Type]  # Bob's input bit

  # Alice and Bob create shares of their input bits and send to each other
  alice_share = (share(Alice_input[0]), share(Alice_input[1]), share(Alice_input[2]))
  bob_share = (share(Bob_input[0]), share(Bob_input[1]), share(Bob_input[2]))

  # Each share is a tuple of (Alice's share, Bob's share)
  
  # Least Significant Bit (LSB) represents Rh of the blood type
  # 0 = Rh-, 1 = Rh+
  # The Two Most Significant Bits (MSB) represents ABO of the blood type
  # O = 00, A = 01, B = 10, AB = 11
  # Example: A+ = 011, O- = 000, AB+ = 111

  # After exchanging shares, they can compute the compatibility
  # They do so by sending the tuples of shares to the function
  status = blood_type_compatibility_tester(alice_share, bob_share)

  print("Can Bob donate to Alice? (computed through secure MPC)", end=" ")
  print("Yes" if status == 1 else "No")