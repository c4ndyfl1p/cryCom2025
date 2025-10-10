# Mapping blood types to bits (x2, x1, x0)
bits = {
    "O-":  (0, 0, 0),
    "O+":  (0, 0, 1),
    "A-":  (0, 1, 0),
    "A+":  (0, 1, 1),
    "B-":  (1, 0, 0),
    "B+":  (1, 0, 1),
    "AB-": (1, 1, 0),
    "AB+": (1, 1, 1)
}

# Truth table from standard medical compatibility (rows = receiver, cols = donor)
truth_table = [
    [1,0,0,0,0,0,0,0],  # O-  can receive from: O-
    [1,1,0,0,0,0,0,0],  # O+  can receive from: O-, O+
    [1,0,1,0,0,0,0,0],  # A-  from: O-, A-
    [1,1,1,1,0,0,0,0],  # A+  from: O-,O+,A-,A+
    [1,0,0,0,1,0,0,0],  # B-  from: O-, B-
    [1,1,0,0,1,1,0,0],  # B+  from: O-,O+,B-,B+
    [1,0,1,0,1,0,1,0],  # AB- from: O-,A-,B-,AB-
    [1,1,1,1,1,1,1,1]   # AB+ from all
]

blood_order = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]

def compatible_bits(rx, dy):
    x2, x1, x0 = rx
    y2, y1, y0 = dy
    return ((x2 or not y2) and
            (x1 or not y1) and
            (x0 or not y0))

def check_all():
    errors = []
    for i, receiver in enumerate(blood_order):
        for j, donor in enumerate(blood_order):
            rx_bits = bits[receiver]
            dy_bits = bits[donor]
            expected = truth_table[i][j]
            got = 1 if compatible_bits(rx_bits, dy_bits) else 0
            if expected != got:
                errors.append((receiver, donor, expected, got))
    if not errors:
        print("✅ All 64 combinations match the truth table!")
    else:
        print("❌ Mismatches found:")
        for (r, d, e, g) in errors:
            print(f"Receiver={r}, Donor={d}, Expected={e}, Got={g}")

if __name__ == "__main__":
    check_all()
