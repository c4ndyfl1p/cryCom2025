import random
import pprint

#defining
n=3

# define encoding for blood types
blood_type_encoding = {
    'o-': 0,
    'o+': 1,
    'a-': 2,
    'a+': 3,
    'b-': 4,
    'b+': 5,
    'ab-': 6,
    'ab+': 7
}

#       Donor: o- o+ a- a+ b- b+ ab- ab+
truth_table = [[1,0,0,0,0,0,0,0],  # o-  recipients
               [1,1,0,0,0,0,0,0],  # o+
               [1,0,1,0,0,0,0,0],  # a-
               [1,1,1,1,0,0,0,0],  # a+
               [1,0,0,0,1,0,0,0],  # b-
               [1,1,0,0,1,1,0,0],  # b+
               [1,0,1,0,1,0,1,0],  # ab-
               [1,1,1,1,1,1,1,1]]  # ab+


def can_donate(donor: str, recipient: str)-> bool:
    """Returns True if donor can donate to recipient, False otherwise.
        can_donate('o+', 'ab-') # Example usage
    """
    donor_index = blood_type_encoding[donor]
    recipient_index = blood_type_encoding[recipient]
    return truth_table[recipient_index][donor_index]


def permute_truth_table(truth_table: list[list[int]], r:int, s:int)-> list[list[int]]:
    # permute truth table by r and
    
    T_perm = [[0 for _ in range(2**n)] for _ in range(2**n)]
    # pprint.pprint(T_perm)


    for i in range(0, 2**n):
        for j in range(0, 2**n):
            k= truth_table[(i-r) % 2**n][(j-s) % 2**n]
            # print(k)
            T_perm[i][j] = k
    
    return T_perm

def xor_tperm_rm(t_perm:list[list[int]], M_b:list[list[int]])-> list[list[int]]:
    # permute truth table by r and
    
    M_a = [[0 for _ in range(2**n)] for _ in range(2**n)]
    # pprint.pprint(T_perm)


    for i in range(0, 2**n):
        for j in range(0, 2**n):
            k= t_perm[i][j] ^ M_b[i][j]
            # print(k)
            M_a[i][j] = k
    
    return M_a



#===============
#write main function

if __name__ == "__main__":

    alice_blood_type = 'b-' # Alice's blood type ( reciever type)
    bob_blood_type = 'a+' # Bob's blood type (donor type)

    # Dealar:
    r = random.randint(0, 2**n - 1) # 1. (r)_2 in {0,1}^n OR (r)_10 in {0,...,2^n-1}
    s = random.randint(0, 2**n - 1) # 1. (s)_2 in {0,1}^n OR (s)_10 in {0,...,2^n-1}
    M_b = [[random.randint(0, 1) for _ in range(2**n)] for _ in range(2**n)] # 2. M_b in {0,1}^{2^n * 2^n}

    T_perm = permute_truth_table(truth_table, r, s)
    M_a = xor_tperm_rm(T_perm, M_b)

    # Alice recieves (r, M_a) and Bob recieves (s, M_b)

    # Alice:
    x_string = alice_blood_type # Alice's blood type ( reciever type)
    x = blood_type_encoding[x_string] # Alice's blood type
    u = (x + r) % 2**n
    # send u to Bob

    # Bob:
    y_string = bob_blood_type # Bob's blood type (donor type)
    y = blood_type_encoding[y_string] # Bob's blood type
    v = (y + s) % 2**n
    z_b = M_b[u][v]
    # send v and z_b to Alice

    # Alice:
    z = M_a[u][v] ^ z_b


     
    print("can bob donate to Aice?(comuted through table lookup)", can_donate(donor=y_string, recipient=x_string) )


    print("z(computed through OTT scheme):", z) # z = 1 if Bob can donate to Alice, else 0

    if z == can_donate(donor=y_string, recipient=x_string):
        print("Success! z is correct")
