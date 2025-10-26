# pq_sign_demo.py
import oqs

def gen_dilithium():
    """Generate Dilithium keypair and return the signature object and keys."""
    sig_obj = oqs.Signature('Dilithium2')
    public_key = sig_obj.generate_keypair()  # Returns public key
    secret_key = sig_obj.export_secret_key()  # Get secret key separately
    return sig_obj, public_key, secret_key

def sign_and_verify(msg: bytes):
    """Sign a message and verify the signature using Dilithium."""
    print(f"Signing message: {msg}")
    
    # Create signature instance
    sig_impl = oqs.Signature('Dilithium2')
    
    # Generate keypair - generate_keypair() returns public key only
    public_key = sig_impl.generate_keypair()
    secret_key = sig_impl.export_secret_key()
    
    print(f"Public key length: {len(public_key)} bytes")
    print(f"Secret key length: {len(secret_key)} bytes")
    
    # Sign the message
    signature = sig_impl.sign(msg)  # Note: sign() uses internal secret key
    print(f"Signature length: {len(signature)} bytes")
    
    # Verify the signature
    is_valid = sig_impl.verify(msg, signature, public_key)
    
    return is_valid, public_key, secret_key, signature

if __name__ == "__main__":
    print("=== Post-Quantum Digital Signature Demo ===")
    print("Algorithm: Dilithium2 (CRYSTALS-Dilithium)")
    print()
    
    # Test with a simple message
    test_message = b"hello pq"
    is_valid, public_key, secret_key, signature = sign_and_verify(test_message)
    
    print(f"\nResults:")
    print(f"Message: {test_message}")
    print(f"Signature valid: {is_valid}")
    print(f"Public key (hex): {public_key[:32].hex()}...")  # Show first 32 bytes
    print(f"Signature (hex): {signature[:32].hex()}...")    # Show first 32 bytes
    
    # Test with multiple messages
    print(f"\n=== Testing Multiple Messages ===")
    test_messages = [
        b"Hello, Post-Quantum World!",
        b"Quantum-safe cryptography",
        b"CRYSTALS-Dilithium signature scheme"
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\nTest {i}:")
        is_valid, _, _, _ = sign_and_verify(msg)
        print(f"✅ Valid" if is_valid else "❌ Invalid")
    
    # Demo the gen_dilithium function as well
    print(f"\n=== Alternative Key Generation Demo ===")
    sig_obj, pub_key, priv_key = gen_dilithium()
    print(f"Generated keypair using gen_dilithium():")
    print(f"Public key length: {len(pub_key)} bytes")
    print(f"Private key length: {len(priv_key)} bytes")
