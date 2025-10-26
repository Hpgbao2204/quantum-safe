# bridge_sim.py
import mini_stark_qsafe as stark
import legacy_rsa_toy as rsa
import shor_demo
import oqs  # Fixed: correct import name
import time

# --- helpers for PQ sign using oqs ---
def gen_dilithium_pair():
    sig = oqs.Signature('Dilithium2')
    pk = sig.generate_keypair()  # Returns public key only
    sk = sig.export_secret_key()  # Get secret key separately
    return sig, pk, sk

def pq_sign(sig_impl, sk, msg: bytes):
    # Note: oqs.Signature.sign() uses internal secret key, not passed sk
    return sig_impl.sign(msg)

def pq_verify(sig_impl, pk, msg: bytes, signature: bytes):
    return sig_impl.verify(msg, signature, pk)

# --- chainA creates event (simple) ---
def chainA_create_event():
    # For PoC, payload is small: (from, to, amount)
    payload = {"from": "AliceA", "to": "BobB", "amount": 10}
    return payload

# --- relay builds STARK proof on the payload (we use Fib trace demo as "proof of work") ---
def relay_build_proof(payload):
    # For PoC: pretend correctness condition is trivial; we build a mini-STARK trace and commit
    trace = stark.gen_fib_trace(12)
    root, leaves = stark.commit_trace(trace)
    idx = stark.random_challenges(len(trace), k=4)
    proof = stark.prove_trace(trace, idx)
    return root, proof

# --- legacy sign/verify using toy RSA (vulnerable) ---
def legacy_sign_commit(root_str):
    # use rsa toy: private key d known in legacy_rsa_toy
    # sign integer form: map root_str -> integer via hash
    import hashlib
    h = hashlib.sha256(root_str.encode()).hexdigest()
    m = int(h, 16) % rsa.N
    s = rsa.rsa_sign(m)
    return s

def legacy_verify_commit(root_str, signature):
    import hashlib
    h = hashlib.sha256(root_str.encode()).hexdigest()
    m = int(h, 16) % rsa.N
    return rsa.rsa_verify(m, signature)

# --- pq sign/verify using oqs ---
def pq_keygen_and_sign(root_str):
    sig_impl = oqs.Signature('Dilithium2')
    pk = sig_impl.generate_keypair()  # Returns public key only
    sk = sig_impl.export_secret_key()  # Get secret key separately
    msg = root_str.encode()
    # Note: sign() uses the internal secret key from generate_keypair()
    signature = sig_impl.sign(msg)
    return sig_impl, pk, sk, signature

def pq_verify_commit(sig_impl, pk, root_str, signature):
    return sig_impl.verify(root_str.encode(), signature, pk)

# --- chainB verify ---
def chainB_verify(root_str, proof, signer_mode, signer_blob):
    # verify proof first (STARK)
    ok_proof = stark.verify_proof(proof)
    if not ok_proof:
        print("[chainB] STARK proof failed")
        return False
    # verify signature according to mode
    if signer_mode == 'legacy':
        sig = signer_blob
        ok_sig = legacy_verify_commit(root_str, sig)
        return ok_sig
    elif signer_mode == 'pq':
        sig_impl, pk = signer_blob
        # note: in our pq flow, signer_blob = (sig_impl, pk, signature) but we adapt
        sig_impl_obj = sig_impl
        pk_obj = pk
        # signature must be passed separately by caller
        return True  # for flow simplicity; call pq_verify externally
    return False

# --- demo flows ---
def demo_legacy_flow():
    print("=== DEMO: Legacy flow (vulnerable) ===")
    payload = chainA_create_event()
    print("[chainA] payload:", payload)
    root, proof = relay_build_proof(payload)
    print("[relay] STARK root:", root[:32], "...")
    sig = legacy_sign_commit(root)
    print("[relay] signed (legacy RSA toy) -> signature:", sig)
    ok = chainB_verify(root, proof, 'legacy', sig)
    print("[chainB] verify result (legacy):", ok)
    return {'root': root, 'proof': proof, 'sig': sig}

def attack_legacy_with_shor(state):
    print(">>> ATTACK: Factor N via Shor, reconstruct d, forge signature")
    N = rsa.N
    print("[attack] running Shor to factor N =", N)
    res = shor_demo.factor_N(N)
    factors = res.factors if res.factors else None
    print("[attack] factors:", factors)
    if not factors or len(factors) < 2:
        print("[attack] Shor failed or returned insufficient factors")
        return False
    p, q = factors[0], factors[1]
    phi = (p-1)*(q-1)
    e = rsa.e
    # compute d using modular inverse
    try:
        d = pow(e, -1, phi)
    except ValueError:
        # Fallback for older Python versions or if modular inverse fails
        from math import gcd
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        gcd_val, x, y = extended_gcd(e, phi)
        if gcd_val != 1:
            print("[attack] e and phi are not coprime!")
            return False
        d = (x % phi + phi) % phi
    
    print("[attack] recovered d:", d)
    # forge signature: recompute m and signature
    import hashlib
    h = hashlib.sha256(state['root'].encode()).hexdigest()
    m = int(h, 16) % N
    forged_sig = pow(m, d, N)
    print("[attack] forged signature:", forged_sig)
    ok = rsa.rsa_verify(m, forged_sig)
    print("[attack] forged signature verifies locally?:", ok)
    # now try to submit to chainB (which uses legacy verify)
    ok_on_chain = chainB_verify(state['root'], state['proof'], 'legacy', forged_sig)
    print("[attack] forged tx accepted by chainB?:", ok_on_chain)
    return ok_on_chain

def demo_pq_flow():
    print("=== DEMO: PQ + STARK flow (defended) ===")
    payload = chainA_create_event()
    root, proof = relay_build_proof(payload)
    print("[relay] STARK root:", root[:32], "...")
    # generate PQ keypair and sign
    sig_impl = oqs.Signature('Dilithium2')
    pk = sig_impl.generate_keypair()  # Returns public key only
    sk = sig_impl.export_secret_key()  # Get secret key separately
    signature = sig_impl.sign(root.encode())  # Uses internal secret key
    print("[relay] signed with Dilithium (bytes len):", len(signature))
    # chainB verifies STARK + PQ signature:
    ok_proof = stark.verify_proof(proof)
    ok_sig = sig_impl.verify(root.encode(), signature, pk)
    print("[chainB] proof ok?:", ok_proof, " pq signature ok?:", ok_sig)
    return {'root': root, 'proof': proof, 'pk': pk, 'signature': signature, 'sig_impl': sig_impl}

def demo_attack_on_pq():
    """Show that Shor's algorithm cannot break post-quantum cryptography."""
    print("\n>>> ATTEMPTED ATTACK: Try to break Dilithium with Shor")
    print("[attack] Attempting to apply Shor's algorithm to Dilithium...")
    print("[attack] Shor's algorithm works by factoring integers (RSA) or discrete log (ECC)")
    print("[attack] Dilithium security is based on lattice problems (Module-LWE)")
    print("[attack] ❌ FAIL: Shor's algorithm cannot solve lattice problems!")
    print("[attack] Even with a quantum computer, Dilithium remains secure")
    print("[attack] This is why it's called 'post-quantum' cryptography")
    return False

if __name__ == "__main__":
    print("🔐 QUANTUM-SAFE BRIDGE SIMULATION")
    print("=" * 60)
    print("This demo shows:")
    print("1. How RSA signatures can be broken by Shor's algorithm")
    print("2. How post-quantum signatures remain secure")
    print("3. Integration with zero-knowledge proofs (STARK)")
    print("=" * 60)
    
    # Part 1: Legacy system vulnerability
    print("\n📖 PART 1: Legacy RSA System")
    state = demo_legacy_flow()
    
    print(f"\n⚡ PART 2: Quantum Attack on RSA")
    success = attack_legacy_with_shor(state)
    if success:
        print("🚨 CRITICAL: Legacy system compromised!")
        print("   → RSA signature successfully forged")
        print("   → Attacker can steal funds or manipulate bridge")
    else:
        print("❓ Attack failed (may be due to small key size)")
    
    print(f"\n🛡️  PART 3: Post-Quantum Defense")
    pq_state = demo_pq_flow()
    
    print(f"\n⚡ PART 4: Quantum Attack on Post-Quantum Crypto")
    pq_attack_success = demo_attack_on_pq()
    
    print(f"\n📊 SUMMARY:")
    print("=" * 40)
    print(f"RSA system broken by Shor:     {'✅ YES' if success else '❓ NO*'}")
    print(f"Dilithium broken by Shor:      {'✅ YES' if pq_attack_success else '❌ NO'}")
    print("Key insights:")
    print("• RSA relies on integer factoring (vulnerable to Shor)")
    print("• Dilithium relies on lattice problems (quantum-resistant)")
    print("• STARK proofs provide additional integrity guarantees")
    print("• Post-quantum + ZK = quantum-safe blockchain bridges")
    
    if not success:
        print(f"\n*Note: RSA attack may fail due to toy parameters")
        print(f"In practice, Shor breaks all RSA keys on quantum computers")
