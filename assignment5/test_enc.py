"""
Test suite for crypto module.
Run with: pytest tests/test_crypto.py
"""
import unittest
from Enc_scheme import enc, dec, generate_random_key, G, xor_bytes

class TestBasicCorrectness(unittest.TestCase):
    """Test basic encrypt-decrypt correctness."""
    
    def test_encrypt_decrypt_correctness(self):

        """Test that dec(enc(m)) = m."""
        k1 = generate_random_key()
        k2 = generate_random_key()
        message = generate_random_key()
        
        ct = enc(k1, k2, 42, message)
        decrypted = dec(k1, k2, 42, ct)
        
        assert decrypted == message
    
    def test_multiple_messages(self):
        """Test with 20 random messages."""
        k1 = generate_random_key()
        k2 = generate_random_key()
        
        for gate in range(20):
            message = generate_random_key()
            ct = enc(k1, k2, gate, message)
            decrypted = dec(k1, k2, gate, ct)
            assert decrypted == message

    def test_special_correctness(self):
        """Test special correctness property of enc scheme."""
        k1 = generate_random_key()
        k2 = generate_random_key()
        message1 = generate_random_key()
        gate_number1 = 1
        c = enc(k1, k2, gate_number1, message1)
        
        try: 
            m_decrypted1 = dec(k1, k2, gate_number1+2, c)
        except ValueError as e:
            print(f"Decryption failed as expected with error: {e}")
            return  # Exit the test if decryption fails

        
       

# class TestSecurity:
#     """Test security properties."""
    
#     def test_wrong_key_fails(self):
#         """Wrong key should fail decryption."""
#         k1 = generate_random_key()
#         k2 = generate_random_key()
#         wrong_k = generate_random_key()
#         message = generate_random_key()
        
#         ct = enc(k1, k2, 42, message)
        
#         with pytest.raises(ValueError, match="invalid padding"):
#             dec(wrong_k, k2, 42, ct)
    
#     def test_tampered_ciphertext_fails(self):
#         """Tampering should be detected."""
#         k1 = generate_random_key()
#         k2 = generate_random_key()
#         message = generate_random_key()
        
#         ct = enc(k1, k2, 42, message)
#         tampered = bytearray(ct)
#         tampered[0] ^= 0xFF
        
#         with pytest.raises(ValueError):
#             dec(k1, k2, 42, bytes(tampered))

# Run with: pytest -v tests/test_crypto.py

if __name__ == '__main__':
    unittest.main()
