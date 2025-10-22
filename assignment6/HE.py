# Testing
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

def can_donate(donor, recipient):
    donor_index = blood_type_encoding[donor]
    recipient_index = blood_type_encoding[recipient]
    return truth_table[recipient_index][donor_index]

blood_type_encoding_HE = {
    'o-': (0,0,0),
    'o+': (0,0,1),
    'a-': (0,1,0),
    'a+': (0,1,1),
    'b-': (1,0,0),
    'b+': (1,0,1),
    'ab-': (1,1,0),
    'ab+': (1,1,1)
}

# Blood test compatability circuit (depth three)
# (¬dA OR rA) AND (¬dB OR rB) AND (¬dRh OR rRh)

def bloodtype_compatability_depth3(donor_bt, recipient_bt):
    dRh = donor_bt[2]
    rRh = recipient_bt[2]
    dBit0 = donor_bt[0]
    rBit0 = recipient_bt[0]
    dBit1 = donor_bt[1]
    rBit1 = recipient_bt[1]

    P = 1 - dRh * (1 - rRh) # Depth 1
    T1 = (1 - dBit0) + rBit0 - (1 - dBit0) * rBit0 # Depth 1
    T2 = (1 - dBit1) + rBit1 - (1 - dBit1) * rBit1 # Depth 1
    Q = T1 * T2 # Depth 2
    return Q * P # Depth 3

## MOVE TO BOTTOM FOR TESTING PURPOSES ##
if __name__ == "__main__":
  # Example usage of the can_donate function
  for donor in range(8):
      for recipient in range(8):
          if can_donate(list(blood_type_encoding.keys())[donor], list(blood_type_encoding.keys())[recipient]) == bloodtype_compatability_depth3(blood_type_encoding_HE[list(blood_type_encoding.keys())[donor]], blood_type_encoding_HE[list(blood_type_encoding.keys())[recipient]]):
              if can_donate(list(blood_type_encoding.keys())[donor], list(blood_type_encoding.keys())[recipient]): ## if -||- == our new function ##
                  print(f"Both functions agree that: {list(blood_type_encoding.keys())[donor]} can donate to {list(blood_type_encoding.keys())[recipient]}")
              else:
                  print(f"Both functions agree that: {list(blood_type_encoding.keys())[donor]} cannot donate to {list(blood_type_encoding.keys())[recipient]}")
          else:
              print(f"Functions disagree on: {list(blood_type_encoding.keys())[donor]} to {list(blood_type_encoding.keys())[recipient]}")